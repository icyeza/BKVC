from datetime import timedelta
from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from models import *
from routes import *
import uuid

import os

# initializing flask application
app = Flask(__name__)
jwt = JWTManager()

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# initializing sqlachemy for database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure JWT
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)


db.init_app(app)
migrate = Migrate(app, db)
jwt.init_app(app)


app.register_blueprint(userBlueprint)
app.register_blueprint(card_blueprint)
