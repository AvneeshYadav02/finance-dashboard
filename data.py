import json
import os
from datetime import datetime

"""
Usage:
tm = TransactionManager(file_path=<str:path/to/file>)

file_path - (default value = "data/data.json")
"""

DB_FILE_PATH = "data/data.json"


class TransactionManager:
    def __init__(self, file_path=DB_FILE_PATH):
        self.file_path = file_path

        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        self.file_db = self.__load_db()

    # Helper Methods
    # Loads JSON
    def __load_db(self):
        if not os.path.exists(self.file_path):
            return {"users": {}}
        with open(file=self.file_path, mode="r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"users": {}}

    # gets the highest latest user-id
    def __get_new_user_id(self):
        user_ids = self.file_db.get("users", {}).keys()

        if not user_ids:
            return 1

        num_ids = [int(u_id) for u_id in user_ids]
        return str(max(num_ids) + 1)

    # gets the latest transaction id
    def __get_new_transaction_id(self, user_id):
        user = self.getUser(user_id)
        transactions = user.get("transactions", [])

        if not transactions:
            return "1"

        num_ids = [int(t_id["id"]) for t_id in transactions]
        return str(max(num_ids) + 1)

    # Public Methods

    # returns a dictionary of a user by their user-id
    def getUser(self, user_id):
        return self.file_db.get("users", {}).get(str(user_id), None)

    # returns a list of user transactions
    def getTransactions(self, user_id):
        user = self.getUser(user_id)
        return user.get("transactions", []) if user else None

    # returns user income, expense, and balance
    def getStats(self, user_id):
        user = self.getUser(user_id)
        if not user:
            return None

        first_of_month = datetime.today().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        transactions = user.get("transactions", [])
        current_balance = user.get("metadata", {}).get("current_balance", 0)
        currency = user.get("metadata", {}).get("currency", "INR")

        income = 0
        expense = 0

        for t in transactions:
            try:
                tx_date = datetime.strptime(t["date"], "%Y-%m-%d")
                if tx_date >= first_of_month:
                    if t["type"] == "income":
                        income += t["amount"]
                    elif t["type"] == "expense":
                        expense += t["amount"]
            except ValueError:
                continue

        old_balance = int(current_balance) + int(expense) - int(income)

        current_balance = int(current_balance)
        if old_balance != 0:
            balance_change = ((current_balance - old_balance) / old_balance) * 100
            balance_change = round(balance_change, 2)
        else:
            balance_change = round(current_balance, 2)
        return {
            "income": income,
            "expense": expense,
            "balance": current_balance,
            "change": balance_change,
        }

    # commits changes to a db, return 0 for success and 1 for failure
    def commitChanges(self):
        try:
            with open(file=self.file_path, mode="w") as f:
                json.dump(self.file_db, f, indent=4)

            self.file_db = self.__load_db()
            return 0
        except Exception as e:
            print(f"Disk write error: {e}")
            return 1

    # catagorical breakdown of user expenditure, return a dictionary where key=catagory, value=total_expenditure
    def catBreakdown(self, user_id):
        user = self.getUser(user_id)
        if not user:
            return {}
        transactions = user.get("transactions", [])
        breakdown = {}

        for t in transactions:
            current_cat = t.get("category", "other")
            if t["type"] == "expense":
                amount = t["amount"]

                breakdown[t["category"]] = breakdown.get(current_cat, 0) + amount
        return breakdown

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Admin Exclusive Functions - Only~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`#

    # returns a dictionary of all users
    def getAllUsers(self):
        return self.file_db.get("users", {})

    # adds a new transaction for a user, returns transaction-id in case of success and 0 for failure
    def addTransaction(self, user_id, tx_amount: int, tx_category, tx_type):
        user = self.getUser(user_id)
        if not user:
            return 0

        tx_id = self.__get_new_transaction_id(user_id)
        tx_date = datetime.now().strftime("%Y-%m-%d")

        new_tx = {
            "id": tx_id,
            "date": tx_date,
            "amount": tx_amount,
            "category": tx_category,
            "type": tx_type,
        }

        if tx_type == "income":
            user["metadata"]["current_balance"] += tx_amount
        else:
            user["metadata"]["current_balance"] -= tx_amount

        user["transactions"].append(new_tx)

        self.commitChanges()
        return {"transaction_id": str(tx_id)}

    # adds a new user to the JSON database, returns user_id in case of successs
    def addUser(
        self,
        user_name,
        user_balance=0,
        user_currency="INR",
    ):
        user_id = self.__get_new_user_id()

        new_user = {
            "metadata": {
                "name": user_name,
                "currency": user_currency,
                "current_balance": user_balance,
            },
            "transactions": [],
        }

        self.file_db["users"][str(user_id)] = new_user

        self.commitChanges()

        return new_user

    # Return full user stats as dictionary with keys: total_users and total_volume
    def getFullStats(self):
        users = self.getAllUsers()
        users_items = users.items()

        output = {
            "total_volume": 0,
            "total_users": 0,
            "total_incoming": 0,
            "total_outgoing": 0,
            "total_transactions": 0,
            "categorical_volume": {},
        }

        if not users:
            return output

        for user_tup in users_items:
            user_data = user_tup[1]
            output["total_users"] += 1

            user_transactions = user_data.get("transactions", [])

            for t in user_transactions:
                output["total_transactions"] += 1

                transaction_type = t.get("type", None)
                transaction_category = t.get("category", "")
                transaction_amount = t.get("amount", "")

                if transaction_type == "income":
                    output["total_incoming"] += transaction_amount
                elif transaction_type == "expense":
                    output["total_outgoing"] += transaction_amount

                if transaction_category not in output["categorical_volume"]:
                    output["categorical_volume"][
                        transaction_category
                    ] = transaction_amount
                else:
                    output["categorical_volume"][
                        transaction_category
                    ] += transaction_amount

                output["total_volume"] += t.get("amount", 0)

        return output

    # Retrieve user data in the format [{"id": user_id, "name": user_name, "balance": user_balance, "user_income":user_income, "user_expense": user_expense}]
    def getUserLogs(self):
        users = self.getAllUsers()

        output = []

        for user in users:
            user_id = user
            user_name = users[user]["metadata"]["name"]
            user_balance = users[user]["metadata"]["current_balance"]

            user_transactions = self.getTransactions(user_id)
            user_income = sum(
                [
                    transaction["amount"]
                    for transaction in user_transactions
                    if transaction["type"] == "income"
                ]
            )
            user_expense = sum(
                [
                    transaction["amount"]
                    for transaction in user_transactions
                    if transaction["type"] == "expense"
                ]
            )

            user_data = {
                "id": user_id,
                "name": user_name,
                "balance": user_balance,
                "income": user_income,
                "expense": user_expense,
            }

            output.append(user_data)

        return output

    def removeUser(self, user_id):
        try:
            del self.file_db["users"][str(user_id)]
            self.commitChanges()

            return 0
        except:
            return 1


"""
TODO:
- implement deleteTransaction(tx_id)
- implement deleteUser(user_id)e
"""
