from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Api, Resource, abort
from models import Card, db, User
from util import card_number_generator
from datetime import datetime


card_blueprint = Blueprint("Card", __name__, url_prefix="/api/v1/card")
Card_api = Api(card_blueprint)


class CardResource(Resource):
    @jwt_required()
    def post(self):

        try:
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
                cvv=cvv,
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


Card_api.add_resource(CardResource, "/")