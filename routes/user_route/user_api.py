import re
import uuid
from flask import Blueprint, make_response, jsonify, request
from flask_restful import Api, Resource, reqparse, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_refresh_token, create_access_token, jwt_required
from models import *

userBlueprint = Blueprint("User", __name__, url_prefix="/api/v1/user")
userApi = Api(userBlueprint)


class SignupResource(Resource):

    def post(self):
        """function creates Api for signing up the user"""
        required_fields = [
            "email",
            "name",
            "password",
            "gender",
            "nid",
            "phonenumber",
            "username",
        ]

        for field in required_fields:
            if field not in request.json:
                abort(400, message=f"Field '{field}' is required.")

        email = request.json["email"]
        name = request.json["name"]
        password = request.json["password"]
        gender = request.json["gender"]
        nid = request.json["nid"]
        phonenumber = request.json["phonenumber"]
        username = request.json["username"]

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            abort(400, message="Invalid email format.")

        if len(password) < 8:
            abort(400, message="Password must be at least 8 characters long.")

        if len(nid) != 16:
            abort(400, message="NID must be exactly 16 characters long.")

        if not re.match(r"\+250\d{9}", phonenumber):
            abort(
                400,
                message="Invalid phone number format. It should be in the format: +250700000000",
            )

        if User.query.filter_by(Email=email).first():
            abort(400, message="Email is already in use.")

        if User.query.filter_by(Phonenumber=phonenumber).first():
            abort(400, message="Phone number is already in use.")

        if User.query.filter_by(NID=nid).first():
            abort(400, message="NID is already in use.")

        if User.query.filter_by(username=username).first():
            abort(400, message="Username is already in use.")

        try:
            userid = str(uuid.uuid4())
            hashed_password = generate_password_hash(password)

            user = User(
                UserId=userid,
                password=hashed_password,
                username=username,
                Name=name,
                Email=email,
                Phonenumber=phonenumber,
                NID=nid,
                Gender=gender,
            )

            db.session.add(user)

            db.session.commit()

            return {"message": "User created successfully."}, 201

        except ValueError as e:
            abort(400, message=str(e))

        except Exception as e:
            abort(500, message="Internal server error. Please try again later. ")


class LoginResource(Resource):
    def post(self):

        required_fields = ["password", "email"]
        for field in required_fields:
            if field not in request.json:
                abort(400, message=f"Field '{field}' is required.")

        email = request.json["email"]
        password = request.json["password"]

        user = User.query.filter_by(Email=email).first()

        if not user or not check_password_hash(user.password, password):
            abort(401, message="Invalid username or password.")

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            abort(400, message="Invalid email format.")

        if len(password) < 8:
            abort(400, message="Password must be at least 8 characters long.")

        identity = {
            "UserId": user.UserId,
            "Email": user.Email,
        }

        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)

        return {
            "message": "User Logged in successfully.",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, 200


userApi.add_resource(SignupResource, "/signup")
userApi.add_resource(LoginResource, "/login")
