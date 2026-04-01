import json
import os
import datetime

DB_FILE_PATH = "data/data.json"


class TransactionManager:
    def __init__(self, file_path=DB_FILE_PATH):
        self.file_path = file_path

        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        self.file_db = self._load_db()

    def _load_db(self):
        if not os.path.exists(self.file_path):
            return {"users": {}}
        with open(file=self.file_path, mode="r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"users": {}}

    def _get_new_user_id(self):
        user_ids = self.file_db.get("users", {}).keys()

        if not user_ids:
            return 1

        num_ids = [int(u_id) for u_id in user_ids]
        return str(max(num_ids) + 1)

    def _get_new_transaction_id(self, user_id):
        user = self.getUser(user_id)
        transactions = user.get("transactions", [])

        if not transactions:
            return "1"

        num_ids = [int(t_id["id"]) for t_id in transactions]
        return str(max(num_ids) + 1)

    def getallUsers(self):
        return self.file_db.get("users", {})

    def getUser(self, user_id):
        return self.file_db.get("users", {}).get(str(user_id), None)

    def getTransactions(self, user_id):
        user = self.getUser(user_id)
        return user.get("transactions", []) if user else None

    def getStats(self, user_id):
        user = self.getUser(user_id)
        if not user:
            return None

        transactions = user.get("transactions", [])
        current_balance = user.get("metadata", {}).get("current_balance", 0)

        income = sum(t["amount"] for t in transactions if t["type"] == "income")
        expense = sum(t["amount"] for t in transactions if t["type"] == "expense")

        return {"income": income, "expense": expense, "balance": current_balance}

    def addUser(
        self,
        user_name,
        user_currency="INR",
        user_balance=0,
    ):
        user_id = self._get_new_user_id()

        self.file_db["users"][user_id] = {
            "metadata": {
                "name": user_name,
                "currency": user_currency,
                "current_balance": user_balance,
            },
            "transactions": [],
        }
        return 1

    def addTransaction(self, user_id, tx_amount: int, tx_catagory, tx_type):
        user = self.getUser(user_id)
        if not user:
            return 0

        user_balance = user.get("metadata", {}).get("current_balance")

        tx_id = self._get_new_transaction_id(user_id)
        tx_date = datetime.datetime.now().strftime("%Y-%m-%d")

        new_tx = {
            "id": tx_id,
            "date": tx_date,
            "amount": tx_amount,
            "category": tx_catagory,
            "type": tx_type,
        }

        if tx_type == "income":
            user["metadata"]["current_balance"] += tx_amount
        else:
            user["metadata"]["current_balance"] -= tx_amount

        user["transactions"].append(new_tx)
        return 1

    def commitChanges(self):
        if os.path.exists(self.file_path):
            with open(file=self.file_path, mode="w") as f:
                json.dump(self.file_db, f, indent=4)
            return 2
        else:
            with open(file=self.file_path, mode="w") as f:
                json.dump(self.file_db, f, indent=4)
            return 1
