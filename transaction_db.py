import sqlite3
from decimal import Decimal

class EntryExistsError(Exception):
    "Raised when a category already exists"
    pass

class TransactionExists(Exception):
    "Raised when a transaction already exists"
    pass

class Transaction:

    def __init__(self, id=None, account=None, vendor=None, amount=0, category=None, memo=None, date=None):
        self.id = id
        self.vendor = vendor
        self.account = account
        self.amount = Decimal(str(amount))
        self.category = category
        self.memo = memo
        self.date = date

    def print(self):
        # Print the transaction details
        print("Transaction Details:")
        print(f"ID: {self.id}")
        print(f"Vendor: {self.vendor}")
        print(f"Amount: {float(self.amount)}")
        print(f"Category: {self.category}")
        print(f"Memo: {self.memo}")
        print(f"Date: {self.date}")

class TransactionDb:

    def __init__(self):

        # Connect to the SQLite database
        self.conn   = sqlite3.connect('budget_app.db')
        self.cursor = self.conn.cursor()

        # Create the categories table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                balance DECIMAL DEFAULT 0
            )
        ''')

        # Check if "uncategorized" category exists, and create it if it doesn't
        self.cursor.execute('SELECT * FROM categories WHERE name=?', ('uncategorized',))
        if not self.cursor.fetchone():
            self.cursor.execute('INSERT INTO categories (name) VALUES (?)', ('uncategorized',))

        # Create the accounts table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                balance DECIMAL DEFAULT 0
            )
        ''')

        # Create the transactions table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account TEXT,
                vendor TEXT,
                amount DECIMAL,
                category TEXT,
                memo TEXT,
                t_date DATE NOT NULL DEFAULT (date('now'))
            )
        ''')

        self.conn.commit()

    def close_database(self):
        # Close the database connection
        self.cursor.close()
        self.conn.close()


    def add_category(self, name):
        # Convert the category name to lowercase
        lowercase_name = name.lower()

        # Check if the category already exists
        self.cursor.execute('SELECT * FROM categories WHERE LOWER(name)=?', (lowercase_name,))
        if self.cursor.fetchone():
            raise EntryExistsError

        # Insert the lowercase category name into the database
        self.cursor.execute('INSERT INTO categories (name) VALUES (?)', (lowercase_name,))
        self.conn.commit()

    def add_account(self, name):
        # Convert the category name to lowercase
        lowercase_name = name.lower()

        # Check if the category already exists
        self.cursor.execute('SELECT * FROM accounts WHERE LOWER(name)=?', (lowercase_name,))
        if self.cursor.fetchone():
            raise EntryExistsError

        # Insert the lowercase category name into the database
        self.cursor.execute('INSERT INTO accounts (name) VALUES (?)', (lowercase_name,))
        self.conn.commit()

    def remove_category(self, name):
        # Check if the category exists
        self.cursor.execute('SELECT * FROM categories WHERE name=?', (name.lower(),))
        category = self.cursor.fetchone()
        if not category:
            raise EntryExistsError

        # Retrieve the category ID
        category_id = category[0]

        # Update transactions with the specified category to "uncategorized"
        self.cursor.execute('UPDATE transactions SET category="uncategorized" WHERE category=?', (name,))

        # Full category rebalance
        self.recalculate_category_balances()

        # Remove the category from the database
        self.cursor.execute('DELETE FROM categories WHERE id=?', (category_id,))
        self.conn.commit()

    def remove_account(self, name):
        # Check if the account exists
        self.cursor.execute('SELECT * FROM accounts WHERE name=?', (name.lower(),))
        account = self.cursor.fetchone()
        if not account:
            raise EntryExistsError

        self.cursor.execute('DELETE FROM transactions WHERE account = ?', (account,))
        self.conn.commit()

        # Retrieve the category ID
        category_id = account[0]

        # Remove the account from the database
        self.cursor.execute('DELETE FROM accounts WHERE id=?', (category_id,))
        self.conn.commit()

        # Full category rebalance
        self.recalculate_category_balances()

    def get_categories(self):
        # Retrieve categories from the database
        self.cursor.execute('SELECT * FROM categories')
        rows = self.cursor.fetchall()
        categories = [row[1] for row in rows]
        categories = [category.lower() for category in categories]  # Convert category names to lowercase
        return categories

    def get_accounts(self):
        # Retrieve categories from the database
        self.cursor.execute('SELECT * FROM accounts')
        rows = self.cursor.fetchall()
        accounts = [row[1].lower() for row in rows]
        return accounts

    def get_category_balances(self):
        self.cursor.execute("SELECT categories.id, categories.name, SUM(transactions.amount) "
                            "FROM categories "
                            "LEFT JOIN transactions ON categories.name = transactions.category "
                            "GROUP BY categories.id, categories.name")
        category_balances = self.cursor.fetchall()

        resolved_balances = []

        for id, name, balance in category_balances:
            if balance is None:
                resolved_balance = Decimal(0)
            else:
                resolved_balance = Decimal(str(balance))
            resolved_balances.append([id, name, resolved_balance])

        return resolved_balances

    def add_transaction(self, account, vendor, amount, category, memo, date):

        # Check if account exists
        self.cursor.execute('SELECT * FROM accounts WHERE name=?', (account.lower(),))
        account = self.cursor.fetchone()
        if not account:
            print(f"Account {account} does not exist!")
            raise EntryExistsError

        account_name = account[1]
        print(f"{account_name}")

        # Pull existing transactions and see if any are a match
        db_trans = self.filter_transactions(vendor=vendor, amount=amount, category=category, memo=memo, date=date)

        if db_trans:
            print("-------------------------------------------")
            print(" Transaction already exists, skipping . . .")
            print("-------------------------------------------")
            raise TransactionExists

        # Insert the transaction into the database
        self.cursor.execute('''
            INSERT INTO transactions (account, vendor, amount, category, memo, t_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (str(account_name).lower(), str(vendor), str(amount), str(category).lower(), str(memo), date))

        self.conn.commit()

        self.update_category_balance(category, amount)

    def update_category_balance(self, category, amount):
        print(f"Attempting to update balance for category: {category} by amount: {amount}")

        # Retrieve the current balance for the category from the categories table
        self.cursor.execute('SELECT balance FROM categories WHERE name=?', (str(category).lower(),))
        current_balance = self.cursor.fetchone()[0]

        # If current balance doesn't exist, set to 0
        if current_balance == None:
            current_balance = Decimal(0)
        else:
            current_balance = Decimal(str(current_balance))

        # Calculate the updated balance by adding or subtracting the transaction amount
        updated_balance = current_balance + amount

        # Update the category's balance in the categories table
        self.cursor.execute('UPDATE categories SET balance=? WHERE name=?', (str(updated_balance), category))
        self.conn.commit()

    def recalculate_category_balances(self):
        categories = self.get_categories()

        for category in categories:
          # Calculate the balance for the category from transactions
          self.cursor.execute('SELECT SUM(amount) FROM transactions WHERE category=?', (category,))
          result = self.cursor.fetchone()
          balance = Decimal(result[0] or 0)

          # Update the category's balance in the categories table
          self.cursor.execute('UPDATE categories SET balance=? WHERE name=?', (str(balance), category))

        self.conn.commit()

    def edit_transaction(self, transaction_id, vendor=None, amount=None, category=None, memo=None, date=None):

        old_trans = self.get_transaction(transaction_id)

        # Update the vendor field if needed
        if vendor:
            self.cursor.execute('UPDATE transactions SET vendor=? WHERE id=?', (vendor, transaction_id))

        # Update the amount field if needed
        if amount:
            self.cursor.execute('UPDATE transactions SET amount=? WHERE id=?', (amount, transaction_id))
            self.update_category_balance(old_trans.category, amount-old_trans.amount)

        # Update the memo field if needed
        if memo:
            self.cursor.execute('UPDATE transactions SET memo=? WHERE id=?', (memo, transaction_id))

        # Update the date field if needed
        if date:
            self.cursor.execute('UPDATE transactions SET date=? WHERE id=?', (date, transaction_id))

        self.conn.commit()

    def display_transactions(self):
        # Prompt for category selection
        categories = self.get_categories()
        print("Available Categories:")
        for index, category in enumerate(categories, start=1):
            print(f"{index}. {category}")
        print(f"{len(categories)+1}. All Categories")
        category_index = int(input("Select a category (Enter the corresponding number): ")) - 1

        if category_index < 0 or category_index >= len(categories):
            # Retrieve all transactions
            self.cursor.execute('SELECT * FROM transactions')
        else:
            # Retrieve transactions for the selected category
            selected_category = categories[category_index]
            self.cursor.execute('SELECT * FROM transactions WHERE category=?', (selected_category,))

        rows = self.cursor.fetchall()

        if len(rows) == 0:
            print("No transactions found.")
        else:
            print("-------------------------")
            print("Transactions:")
            print("-------------------------")
            for row in rows:
                print("ID:", row[0])
                print("Account:", row[1])
                print("Vendor:", row[2])
                print("Amount:", float(row[3]))
                print("Category:", row[4])
                print("Memo:", row[5])
                print("Date:", row[6])
                print("-----------------------")

    def filter_transactions(self, id=None, vendor=None, amount=None, category=None, memo=None, date=None):
        query = 'SELECT * FROM transactions WHERE '
        conditions = []
        params = []

        if id is not None:
            conditions.append('id = ?')
            params.append(str(id))
        if vendor is not None:
            conditions.append('vendor = ?')
            params.append(str(vendor))
        if amount is not None:
            conditions.append('amount = ?')
            params.append(str(amount))
        if category is not None:
            conditions.append('category = ?')
            params.append(str(category))
        if memo is not None:
            conditions.append('memo = ?')
            params.append(str(memo))
        if date is not None:
            conditions.append('t_date = ?')
            params.append(str(date))

        if conditions:
            query += ' AND '.join(conditions)

        self.cursor.execute(query, params)

        transactions = self.cursor.fetchall()

        return_trans = []

        for transaction in transactions:
            id = transaction[0]
            account = transaction[1]
            vendor = transaction[2]
            amount = Decimal(str(transaction[3]))
            category = transaction[4]
            memo = transaction[5]
            date = transaction[6]

            return_trans.append(Transaction(id, account, vendor, amount, category, memo, date))

        return return_trans

    def get_transaction(self, id):
        # Retrieve the transaction from the database
        self.cursor.execute('SELECT * FROM transactions WHERE id=?', (id,))
        transaction = self.cursor.fetchone()

        # Check if the transaction exists
        if not transaction:
            raise IndexError

        # Extract transaction details
        id = transaction[0]
        vendor = transaction[1]
        amount = Decimal(str(transaction[2]))
        category = transaction[3]
        memo = transaction[4]
        date = transaction[5]

        return Transaction( id, vendor, amount, category, memo, date)