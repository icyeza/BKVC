from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Api, Resource, abort
from models import Card, db, User
from models.transaction import Transaction
from util import card_number_generator
from datetime import datetime


card_blueprint = Blueprint("Card", __name__, url_prefix="/api/v1/card")
Card_api = Api(card_blueprint)


class CardResource(Resource):
    @jwt_required()
    def post(self):

        required_fields = [
            "card_name",
            "cvv",
            "expire_date",
            "limit_money",
            "card_type",
            "card_status",
            "balance",
        ]

        for field in required_fields:
            if field not in request.json:
                abort(400, message=f"Field '{field}' is required.")

        try:

            expire_date_json = datetime.strptime(
                request.json["expire_date"], "%Y-%m-%d"
            ).date()

            card_number = card_number_generator()
            userId = get_jwt_identity()["UserId"]
            card_name = request.json["card_name"]
            cvv = request.json["cvv"]
            expire_date = expire_date_json
            limit_money = request.json["limit_money"]
            card_type = request.json["card_type"]
            card_status = request.json["card_status"]
            balance = request.json["balance"]

            card = Card(
                card_number=card_number,
                userId=userId,
                card_name=card_name,
                cvv=generate_password_hash(str(cvv)),
                expire_date=expire_date,
                limit_money=limit_money,
                card_type=card_type,
                card_status=card_status,
                balance=balance,
            )
            db.session.add(card)
            db.session.commit()

            return {"message": "Card created successfully."}, 201

        except ValueError as e:
            abort(ValueError, message=e)
        except Exception as e:
            print(e)
            abort(500, message="Internal server error. Please try again later.")

    @jwt_required()
    def get(self):
        try:
            user_id = get_jwt_identity()["UserId"]

            cards = Card.query.filter_by(userId=user_id, card_status="active").all()

            if not cards:
                return {"message": "No cards found for this user."}, 404

            cards_data = []
            for card in cards:
                card_data = {
                    "card_number": card.card_number,
                    "card_name": card.card_name,
                    "expire_date": str(card.expire_date),
                    "limit_money": card.limit_money,
                    "card_type": card.card_type,
                    "card_status": card.card_status,
                    "balance": card.balance,
                }
                cards_data.append(card_data)

            return {"cards": cards_data}, 200
        except Exception as e:
            print(e)
            abort(500, message="Internal server error. Please try again later.")

    @jwt_required()
    def put(self):
        required_fields = ["amount", "card_number"]

        for field in required_fields:
            if field not in request.json:
                abort(400, message=f"Field '{field}' is required.")

        balance = request.json["amount"]
        cardNumber = request.json["card_number"]

        if float(balance) < 0:
            abort(400, message="Balance can't be less than 0")

        card = Card.query.filter_by(card_number=cardNumber).first()

        if not card:
            abort(404, message=f"Card is not found")

        if card.card_status == "inactive":
            abort(400, message=f" You can not update a card that is inactive")

        try:
            card.balance += balance

            db.session.add(card)
            db.session.commit()

            return {"message": "Money added successfully."}, 200

        except ValueError as e:
            abort(ValueError, message=e)
        except Exception as e:
            print(e)
            abort(500, message="Internal server error. Please try again later.")


class change_card_status(Resource):

    @jwt_required()
    def patch(self, cardNumber):

        required_fields = [
            "status",
        ]

        for field in required_fields:
            if field not in request.json:
                abort(400, message=f"Field '{field}' is required.")

        status = request.json["status"]

        card = Card.query.filter_by(card_number=cardNumber).first()

        if not card:
            abort(404, message=f"Card is not found")

        try:
            card.card_status = status

            db.session.add(card)
            db.session.commit()

            return {"message": "Card status updated successfully."}, 200

        except ValueError as e:
            abort(ValueError, message=e)
        except Exception as e:
            print(e)
            abort(500, message="Internal server error. Please try again later.")


class get_inactive_cards(Resource):
    @jwt_required()
    def get(self):
        try:
            user_id = get_jwt_identity()["UserId"]

            cards = Card.query.filter_by(userId=user_id, card_status="inactive").all()

            if not cards:
                return {"message": "No cards found for this user."}, 404

            cards_data = []
            for card in cards:
                card_data = {
                    "card_number": card.card_number,
                    "card_name": card.card_name,
                    "expire_date": str(card.expire_date),
                    "limit_money": card.limit_money,
                    "card_type": card.card_type,
                    "card_status": card.card_status,
                    "balance": card.balance,
                }
                cards_data.append(card_data)

            return {"cards": cards_data}, 200
        except Exception as e:
            print(e)
            abort(500, message="Internal server error. Please try again later.")


class getStatement(Resource):
    @jwt_required()
    def get(self, cardNumber):

        transactions = (
            Transaction.query.filter(
                (
                    (Transaction.card_receiver_number == cardNumber)
                    | (Transaction.card_sender_number == cardNumber)
                )
                & (Transaction.transaction_status == "approved")
            )
            .order_by(Transaction.transaction_date.desc())
            .all()
        )

        transactions_json = []

        for transaction in transactions:
            if transaction.card_receiver_number == cardNumber:
                transaction_type = "deposit"
            else:
                transaction_type = "withdrawal"

            transaction_dict = {
                "transaction_id": transaction.transaction_id,
                "transaction_amount": transaction.transaction_amount,
                "transaction_date": str(transaction.transaction_date),
                "transaction_status": transaction.transaction_status,
                "card_receiver_number": transaction.card_receiver_number,
                "card_sender_number": transaction.card_sender_number,
                "transaction_type": transaction_type,
            }

            transactions_json.append(transaction_dict)

        return {"statements": transactions_json}, 200


Card_api.add_resource(CardResource, "/")
Card_api.add_resource(get_inactive_cards, "/get_inactive")
Card_api.add_resource(change_card_status, "/<cardNumber>/update_status")
Card_api.add_resource(getStatement, "/<cardNumber>/get_statement")
