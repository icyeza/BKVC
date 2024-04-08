from models import db


class Card(db.Model):

    __tablename__ = "card"

    card_number = db.Column(db.String, primary_key=True)  # card_number
    userId = db.Column(db.String, db.ForeignKey("users.UserId"))
    card_name = db.Column(db.String)
    cvv = db.Column(db.String(3))
    expire_date = db.Column(db.DateTime)
    limit_money = db.Column(db.Float)  # limit_money
    card_type = db.Column(db.String)
    card_status = db.Column(db.String)
    balance = db.Column(db.Float)
    Transactions = db.relationship("Transaction", backref="card", lazy=True)

    def __repr__(self) -> str:
        return f"<Card {self.card_number}>"
