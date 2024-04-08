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

    @jwt_required()
    def get(self):
        try:
            user_id = get_jwt_identity()["UserId"]
            cards = Card.query.filter_by(userId=user_id).all()
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


class add_money(Resource):

    @jwt_required()
    def post(self, cardNumber):
        required_fields = [
            "amount",
        ]

        for field in required_fields:
            if field not in request.json:
                abort(400, message=f"Field '{field}' is required.")

        try:

            balance = request.json["amount"]

            card = Card.query.filter_by(card_number=cardNumber).first()

            if not card:
                abort(404, message=f"Card is not found")

            card.balance += balance

            db.session.add(card)
            db.session.commit()

            return {"message": " New amount was added."}, 201

        except ValueError as e:
            abort(ValueError, message=e)
        except Exception as e:
            print(e)
            abort(500, message="Internal server error. Please try again later.")


class change_card_status(Resource):

    @jwt_required()
    def post(self, cardNumber):

        required_fields = [
            "status",
        ]

        for field in required_fields:
            if field not in request.json:
                abort(400, message=f"Field '{field}' is required.")

        try:

            status = request.json["status"]

            card = Card.query.filter_by(card_number=cardNumber).first()

            if not card:
                abort(404, message=f"Card is not found")

            card.card_status = status

            db.session.add(card)
            db.session.commit()

            return {"message": "Card status updated successfully."}, 201

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


# class statement_of_card(Resource):

Card_api.add_resource(CardResource, "/")
Card_api.add_resource(add_money, "/<cardNumber>")
Card_api.add_resource(get_inactive_cards, "/get_inactive")
Card_api.add_resource(change_card_status, "/<cardNumber>/update_status")
