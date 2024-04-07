from models import db


class transaction_confirmation(db.Model):
    transaction_confirmationID = db.Column(db.String, primary_key=True)
    transaction_id = db.Column(db.String, db.ForeignKey("transaction.TransactionId"))
    date = db.Column(db.DateTime)
    code = db.Column(db.String)
    status = db.Column(db.String)
    expiry_date_time = db.Column(db.String)

    def __repr__(self) -> str:
        return f"<transactionConfirmation {self.transaction_confirmation_id}"
