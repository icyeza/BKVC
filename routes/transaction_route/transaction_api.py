from datetime import datetime, timedelta
import uuid
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Api, Resource, abort
from flask_mail import Message


from models import Card, db, transaction_confirmation
from models.transaction import Transaction
from routes import mail
from util.otp_code_generator import otp_code_generator

transaction_Blueprint = Blueprint(
    "transaction", __name__, url_prefix="/api/v1/transaction"
)
transaction_api = Api(transaction_Blueprint)


class TransactionResource(Resource):
    @jwt_required()
    def post(self):
        required_fields = [
            "transaction_amount",
            "card_receiver_number",
            "card_sender_number",
        ]

        for field in required_fields:
            if field not in request.json:
                abort(400, message=f"Missing '{field}' in request data.")

        card_sender_number = request.json["card_sender_number"]
        card_receiver_number = request.json["card_receiver_number"]

        if card_sender_number == card_receiver_number:
            abort(400, message="Sender and receiver cards cannot be the same.")

        sender_card = Card.query.get(card_sender_number)
        receiver_card = Card.query.get(card_receiver_number)

        if not sender_card or not receiver_card:
            abort(
                404,
                message="One of the cards involved in the transaction was not found.",
            )

        try:
            transaction_amount = float(request.json["transaction_amount"])
        except ValueError:
            abort(400, message="Invalid transaction amount. It should be a decimal.")

        if sender_card.balance < float(request.json["transaction_amount"]):
            abort(400, message="Sender has insufficient funds.")

        if sender_card.limit_money < float(request.json["transaction_amount"]):
            abort(400, message="Transaction amount exceeds sender's limit money.")

        try:
            transaction_id = uuid.uuid4()
            transaction_confirmation_id = uuid.uuid4()
            current_date = datetime.now()
            three_minutes_later = datetime.now() + timedelta(minutes=3)
            generated_code = otp_code_generator()

            transaction = Transaction(
                transaction_id=transaction_id,
                transaction_date=current_date,
                transaction_amount=transaction_amount,
                transaction_status="pending",
                card_sender_number=card_sender_number,
                card_receiver_number=card_receiver_number,
            )

            transactionConfirmation = transaction_confirmation(
                transaction_confirmation_id=transaction_confirmation_id,
                transaction_id=transaction.transaction_id,
                date=current_date,
                code=generated_code,
                status="pending",
                expiry_date_time=three_minutes_later,
            )

            db.session.add(transaction)
            db.session.add(transactionConfirmation)
            db.session.commit()

            sender_email = get_jwt_identity()["Email"]
            msg = Message("OTP Verification", recipients=[sender_email])
            msg.body = "Your OTP for transaction verification is: {}".format(
                generated_code
            )
            msg.html = f"Here is your OTP: <strong>{generated_code}</strong>, click <a href='http://127.0.0.1:5000/api/v1/transaction/{transaction_confirmation_id}/verify_code'>here</a> to verify."
            mail.send(msg)

            return {"message": "Transaction initiated successfully."}, 201
        except Exception as e:
            abort(500, message="Internal server error. Please try again later.")


class VerifyTransaction(Resource):
    @jwt_required()
    def post(self, transaction_confirmation_id):
        required_fields = ["code"]

        for field in required_fields:
            if field not in request.json:
                abort(400, message=f"Missing '{field}' in request data.")

        entered_code = str(request.json["code"])
        confirmation = transaction_confirmation.query.get(transaction_confirmation_id)

        if not confirmation:
            abort(
                404,
                message=f"Transaction confirmation not found.",
            )

        if confirmation.status == "expired":
            abort(400, message="Transaction confirmation has already been expired.")

        if confirmation.status == "used":
            abort(400, message="Transaction confirmation has already been used.")

        if (
            confirmation.expiry_date_time
            and datetime.now() > confirmation.expiry_date_time
        ):
            try:
                confirmation.status = "expired"
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                abort(500, message="Transaction failed. Please try again later.")
            abort(
                400,
                message=f"Transaction confirmation has expired.",
            )

        if entered_code != confirmation.code:
            abort(400, message="Invalid verification code.")

        transaction = Transaction.query.get(confirmation.transaction_id)

        if not transaction:
            abort(404, message="Transaction not found.")

        sender_card = Card.query.get(transaction.card_sender_number)
        receiver_card = Card.query.get(transaction.card_receiver_number)

        if not sender_card or not receiver_card:
            abort(
                400,
                message="One of the cards involved in the transaction was not found.",
            )

        try:
            sender_card.balance -= float(transaction.transaction_amount)
            receiver_card.balance += float(transaction.transaction_amount)
            confirmation.status = "used"
            transaction.transaction_status = "approved"
            db.session.commit()

            msg = Message("Transaction Success", recipients=[receiver_card.user.Email])
            msg.body = "You have received {} from {}".format(
                float(transaction.transaction_amount), sender_card.card_name
            )
            msg.html = f"<p>You have received {float(transaction.transaction_amount)} from {sender_card.card_name}</p>"
            mail.send(msg)

            return {"message": "Transaction successful."}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, message="Transaction failed. Please try again later.")


transaction_api.add_resource(TransactionResource, "/")
transaction_api.add_resource(
    VerifyTransaction, "/<transaction_confirmation_id>/verify_code"
)
