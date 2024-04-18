from models import db


class User(db.Model):
    __tablename__ = "users"

    UserId = db.Column(db.String, primary_key=True)
    Name = db.Column(db.String)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    Email = db.Column(db.String, unique=True)
    Phonenumber = db.Column(db.String, unique=True)
    NID = db.Column(db.String(16))
    Gender = db.Column(db.String)
    cards = db.relationship("Card", backref="user", lazy=True)

    def __repr__(self) -> str:
        return f"<User {self.Gender}, {self.Phonenumber}>"
