from flask import Blueprint, make_response, jsonify, request
from flask_restful import Api, Resource, reqparse, abort

# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_jwt_extended import create_refresh_token, create_access_token

from models import Card, db

transaction_Blueprint = Blueprint(
    "transaction", __name__, url_prefix="/api/v1/transaction"
)
transaction_api = Api(transaction_Blueprint)


class transaction_resource(Resource):
    '"""Class docstrings go here."""'

    def post(self):

        try:
            required_fields = [
                "transaction_id",
                "transaction_date",
                "transaction_amount",
                "transaction_status",
                "cardreceiver_number",
                "cardsender_number",
            ]
            for field in required_fields:
                if field not in request.json:
                    abort(400, message=f"Field '{field}' is required.")

            transaction_id = request.json["transaction_id"]
            transaction_date = request.json["transaction_date"]
            transaction_amount = request.json["transaction_amount"]
            transaction_status = request.json["transaction_status"]
            card_receiver_number = request.json["card_receiver_number"]
            card_sender_number = request.json["card_sender_number"]

            return {"message": "Transaction created successfully."}, 201
        except Exception as e:
            print(e)
            abort(500, message="Internal server error. Please try again later.")


transaction_api.add_resource(transaction_resource, "/create")
