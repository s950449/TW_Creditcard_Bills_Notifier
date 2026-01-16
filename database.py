import sqlite_utils
from config import Config
from datetime import datetime

class Database:
    def __init__(self):
        self.db = sqlite_utils.Database(Config.DB_PATH)
        self.init_db()

    def init_db(self):
        if "bills" not in self.db.table_names():
            self.db["bills"].create({
                "id": str,
                "bank": str,
                "amount": float,
                "currency": str,
                "due_date": str,
                "bill_date": str,
                "notified": int # 0: False, 1: True
            }, pk="id")

    def upsert_bill(self, bill_data):
        # bill_data: {id, bank, amount, currency, due_date, bill_date}
        bill_data["notified"] = 0
        self.db["bills"].upsert(bill_data, pk="id")

    def mark_as_notified(self, bill_id):
        self.db["bills"].update(bill_id, {"notified": 1})
