import sqlite3

class CategoryExistsError(Exception):
    "Raised when a category already exists"
    pass

class Transaction:
    
    def __init__(self, id, vendor, amount, category, memo, date):
        self.id = id
        self.vendor = vendor
        self.amount = amount
        self.category = category
        self.memo = memo
        self.date = date

    def print(self):
        # Print the transaction details
        print("Transaction Details:")
        print(f"ID: {self.id}")
        print(f"Vendor: {self.vendor}")
        print(f"Amount: {self.amount}")
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
                name TEXT
            )
        ''')
        self.conn.commit()
    
        # Create the transactions table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor TEXT,
                amount REAL,
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
            raise CategoryExistsError
        
        # Insert the lowercase category name into the database
        self.cursor.execute('INSERT INTO categories (name) VALUES (?)', (lowercase_name,))
        self.conn.commit()
    
    def remove_category(self, name):
        # Check if the category exists
        self.cursor.execute('SELECT * FROM categories WHERE name=?', (name.lower(),))
        self.category = self.cursor.fetchone()
        if not self.category:
            raise CategoryExistsError
        
        # Retrieve the category ID
        category_id = self.category[0]
        
        # Update transactions with the specified category to "Uncategorized"
        self.cursor.execute('UPDATE transactions SET category="Uncategorized" WHERE category=?', (name,))
        
        # Remove the category from the database
        self.cursor.execute('DELETE FROM categories WHERE id=?', (category_id,))
        self.conn.commit()
    
    def get_categories(self):
        # Retrieve categories from the database
        self.cursor.execute('SELECT * FROM categories')
        rows = self.cursor.fetchall()
        categories = [row[1] for row in rows]
        categories = [category.lower() for category in categories]  # Convert category names to lowercase
        return categories
    
    def add_transaction(self, vendor, amount, category, memo, date):
        
        # Insert the transaction into the database
        self.cursor.execute('''
            INSERT INTO transactions (vendor, amount, category, memo, t_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (vendor, amount, category, memo, date))
        self.conn.commit()
    
    def edit_transaction(self, transaction_id, vendor=None, amount=None, category=None, memo=None, date=None):
        
        # Update the vendor field if needed
        if vendor:
            self.cursor.execute('UPDATE transactions SET vendor=? WHERE id=?', (vendor, transaction_id))
        
        # Update the amount field if needed
        if amount:
            self.cursor.execute('UPDATE transactions SET amount=? WHERE id=?', (amount, transaction_id))
        
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
            print("Transactions:")
            for row in rows:
                print("ID:", row[0])
                print("Vendor:", row[1])
                print("Amount:", row[2])
                print("Category:", row[3])
                print("Memo:", row[4])
                print("Date:", row[5])
                print("-----------------------")

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
        amount = transaction[2]
        category = transaction[3]
        memo = transaction[4]
        date = transaction[5]

        return Transaction( id, vendor, amount, category, memo, date)