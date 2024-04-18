from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from models import db


class Transaction(db.Model):
    __tablename__ = "transaction"

    transaction_id = db.Column(db.String, primary_key=True)
    transaction_date = db.Column(db.DateTime)
    transaction_amount = db.Column(db.String)
    transaction_status = db.Column(db.String)
    card_receiver_number = db.Column(db.String, db.ForeignKey("card.card_number"))
    card_sender_number = db.Column(db.String, db.ForeignKey("card.card_number"))

    card_receiver = db.relationship(
        "Card", foreign_keys=[card_receiver_number], backref="received_transactions"
    )

    # Update the card_sender relationship with the 'foreign_keys' argument:
    card_sender = db.relationship(
        "Card", foreign_keys=[card_sender_number], backref="sent_transactions"
    )

    transaction_confirmation = relationship(
        "transaction_confirmation", backref="transaction", lazy=True
    )

    def __repr__(self) -> str:
        return f"<Transaction {self.transaction_id}>"
