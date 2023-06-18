import sqlite3

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
                memo TEXT
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
            print("Category already exists.")
            return
        
        # Insert the lowercase category name into the database
        self.cursor.execute('INSERT INTO categories (name) VALUES (?)', (lowercase_name,))
        self.conn.commit()
        print("Category added successfully.")
    
    def remove_category(self, name):
        # Check if the category exists
        self.cursor.execute('SELECT * FROM categories WHERE name=?', (name,))
        self.category = self.cursor.fetchone()
        if not self.category:
            print("Category does not exist.")
            return
        
        category_id = category[0]
        
        # Update transactions with the specified category to "Uncategorized"
        self.cursor.execute('UPDATE transactions SET category="Uncategorized" WHERE category=?', (name,))
        
        # Remove the category from the database
        self.cursor.execute('DELETE FROM categories WHERE id=?', (category_id,))
        self.conn.commit()
        print("Category removed successfully.")
    
    def get_categories(self):
        # Retrieve categories from the database
        self.cursor.execute('SELECT * FROM categories')
        rows = self.cursor.fetchall()
        categories = [row[1] for row in rows]
        categories = [category.lower() for category in categories]  # Convert category names to lowercase
        return categories
    
    def add_transaction(self):
        print("Enter transaction details:")
        vendor = input("Vendor: ")
        amount = float(input("Amount: "))
        memo = input("Memo: ")
        
        # Display existing categories and prompt for selection
        categories = self.get_categories()
        print("Available Categories:")
        for index, category in enumerate(categories, start=1):
            print(f"{index}. {category}")
        category_index = int(input("Select a category (Enter the corresponding number): ")) - 1
        
        if category_index < 0 or category_index >= len(categories):
            category = "Uncategorized"
        else:
            category = categories[category_index]
        
        # Insert the transaction into the database
        self.cursor.execute('''
            INSERT INTO transactions (vendor, amount, category, memo)
            VALUES (?, ?, ?, ?)
        ''', (vendor, amount, category, memo))
        self.conn.commit()
        print("Transaction added successfully.")
    
    def edit_transaction(self, transaction_id):
        # Retrieve the transaction from the database
        self.cursor.execute('SELECT * FROM transactions WHERE id=?', (transaction_id,))
        transaction = self.cursor.fetchone()
        
        # Check if the transaction exists
        if not transaction:
            print("Transaction not found.")
            return
        
        # Extract transaction details
        old_vendor = transaction[1]
        old_amount = transaction[2]
        old_category = transaction[3]
        old_memo = transaction[4]
        
        # Retrieve existing categories from the database
        self.cursor.execute('SELECT name FROM categories')
        categories = self.cursor.fetchall()
        category_options = [f"{index}. {category[0]}" for index, category in enumerate(categories, start=1)]
    
        self.print_transaction(transaction_id)
        
        # Display prompt for each field
        print(f"ID: {transaction_id}")
        new_vendor = input(f"Update Vendor? (Press ENTER to leave as \"{old_vendor}\")\n> ")
        new_amount = input(f"Update Amount? (Press ENTER to leave as \"{old_amount}\")\n> ")
        
        # Display available categories
        print("Available Categories:")
        for option in category_options:
            print(option)
        
        new_category = input(f"Update Category? (Press ENTER to leave as \"{old_category}\")\n> ")
        
        # Validate and update the category field
        if new_category:
            if new_category.isdigit() and int(new_category) in range(1, len(categories) + 1):
                new_category_name = categories[int(new_category) - 1][0]
                self.cursor.execute('UPDATE transactions SET category=? WHERE id=?', (new_category_name, transaction_id))
            else:
                print("Invalid category. Please select a valid category or press ENTER to leave as is.")
        
        new_memo = input(f"Update Memo? (Press ENTER to leave as \"{old_memo}\")\n> ")
        
        # Update the transaction in the database if any changes were made
        if new_vendor or new_amount or new_memo:
            # Validate and update the vendor field
            if new_vendor:
                self.cursor.execute('UPDATE transactions SET vendor=? WHERE id=?', (new_vendor, transaction_id))
            
            # Validate and update the amount field
            if new_amount:
                self.cursor.execute('UPDATE transactions SET amount=? WHERE id=?', (new_amount, transaction_id))
            
            # Validate and update the memo field
            if new_memo:
                self.cursor.execute('UPDATE transactions SET memo=? WHERE id=?', (new_memo, transaction_id))
            
            conn.commit()
            print("Transaction updated successfully!")
        else:
            print("No changes made to the transaction.")
    
    def print_transaction(self, transaction_id):
        # Retrieve the transaction from the database
        self.cursor.execute('SELECT * FROM transactions WHERE id=?', (transaction_id,))
        transaction = self.cursor.fetchone()
    
        # Check if the transaction exists
        if not transaction:
            print("Transaction not found.")
            return
    
        # Extract transaction details
        transaction_id = transaction[0]
        vendor = transaction[1]
        amount = transaction[2]
        category = transaction[3]
        memo = transaction[4]
    
        # Print the transaction details
        print("Transaction Details:")
        print(f"ID: {transaction_id}")
        print(f"Vendor: {vendor}")
        print(f"Amount: {amount}")
        print(f"Category: {category}")
        print(f"Memo: {memo}")
    
    
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
                print("-----------------------")

