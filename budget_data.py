import sqlite3


# Connect to the SQLite database
conn = sqlite3.connect('budget_app.db')
cursor = conn.cursor()

# Create the categories table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
''')
conn.commit()

# Create the transactions table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor TEXT,
        amount REAL,
        category TEXT,
        memo TEXT
    )
''')
conn.commit()

def add_category(name):
    # Convert the category name to lowercase
    lowercase_name = name.lower()

    # Check if the category already exists
    cursor.execute('SELECT * FROM categories WHERE LOWER(name)=?', (lowercase_name,))
    if cursor.fetchone():
        print("Category already exists.")
        return
    
    # Insert the lowercase category name into the database
    cursor.execute('INSERT INTO categories (name) VALUES (?)', (lowercase_name,))
    conn.commit()
    print("Category added successfully.")

def remove_category(name):
    # Check if the category exists
    cursor.execute('SELECT * FROM categories WHERE name=?', (name,))
    category = cursor.fetchone()
    if not category:
        print("Category does not exist.")
        return
    
    category_id = category[0]
    
    # Update transactions with the specified category to "Uncategorized"
    cursor.execute('UPDATE transactions SET category="Uncategorized" WHERE category=?', (name,))
    
    # Remove the category from the database
    cursor.execute('DELETE FROM categories WHERE id=?', (category_id,))
    conn.commit()
    print("Category removed successfully.")

def get_categories():
    # Retrieve categories from the database
    cursor.execute('SELECT * FROM categories')
    rows = cursor.fetchall()
    categories = [row[1] for row in rows]
    categories = [category.lower() for category in categories]  # Convert category names to lowercase
    return categories

def add_transaction():
    print("Enter transaction details:")
    vendor = input("Vendor: ")
    amount = float(input("Amount: "))
    memo = input("Memo: ")
    
    # Display existing categories and prompt for selection
    categories = get_categories()
    print("Available Categories:")
    for index, category in enumerate(categories, start=1):
        print(f"{index}. {category}")
    category_index = int(input("Select a category (Enter the corresponding number): ")) - 1
    
    if category_index < 0 or category_index >= len(categories):
        category = "Uncategorized"
    else:
        category = categories[category_index]
    
    # Insert the transaction into the database
    cursor.execute('''
        INSERT INTO transactions (vendor, amount, category, memo)
        VALUES (?, ?, ?, ?)
    ''', (vendor, amount, category, memo))
    conn.commit()
    print("Transaction added successfully.")

def edit_transaction(transaction_id):
    # Retrieve the transaction from the database
    cursor.execute('SELECT * FROM transactions WHERE id=?', (transaction_id,))
    transaction = cursor.fetchone()
    
    # Check if the transaction exists
    if not transaction:
        print("Transaction not found.")
        return
    
    # Extract transaction details
    old_vendor = transaction[1]
    old_amount = transaction[2]
    old_category = transaction[3]
    old_memo = transaction[4]
    
    # Display prompt for each field
    print(f"ID: {transaction_id}")
    new_vendor = input(f"Update Vendor? (Press ENTER to leave as \"{old_vendor}\")\n> ")
    new_amount = input(f"Update Amount? (Press ENTER to leave as \"{old_amount}\")\n> ")
    new_category = input(f"Update Category? (Press ENTER to leave as \"{old_category}\")\nAvailable Categories:\n1. pants\n2. food\n> ")
    new_memo = input(f"Update Memo? (Press ENTER to leave as \"{old_memo}\")\n> ")
    
    # Update the transaction in the database if any changes were made
    if new_vendor or new_amount or new_category or new_memo:
        # Validate and update the vendor field
        if new_vendor:
            cursor.execute('UPDATE transactions SET vendor=? WHERE id=?', (new_vendor, transaction_id))
        
        # Validate and update the amount field
        if new_amount:
            cursor.execute('UPDATE transactions SET amount=? WHERE id=?', (new_amount, transaction_id))
        
        # Validate and update the category field
        if new_category:
            if new_category.isdigit() and int(new_category) in [1, 2]:
                cursor.execute('UPDATE transactions SET category=? WHERE id=?', (new_category, transaction_id))
            else:
                print("Invalid category. Please select a valid category or press ENTER to leave as is.")
        
        # Validate and update the memo field
        if new_memo:
            cursor.execute('UPDATE transactions SET memo=? WHERE id=?', (new_memo, transaction_id))
        
        conn.commit()
        print("Transaction updated successfully!")
    else:
        print("No changes made to the transaction.")


def display_transactions():
    # Prompt for category selection
    categories = get_categories()
    print("Available Categories:")
    for index, category in enumerate(categories, start=1):
        print(f"{index}. {category}")
    print(f"{len(categories)+1}. All Categories")
    category_index = int(input("Select a category (Enter the corresponding number): ")) - 1
    
    if category_index < 0 or category_index >= len(categories):
        # Retrieve all transactions
        cursor.execute('SELECT * FROM transactions')
    else:
        # Retrieve transactions for the selected category
        selected_category = categories[category_index]
        cursor.execute('SELECT * FROM transactions WHERE category=?', (selected_category,))
    
    rows = cursor.fetchall()
    
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

# Main program loop
while True:
    print("\nBudgeting App Menu:")
    print("1. Add Transaction")
    print("2. Edit Transaction")
    print("3. Display Transactions")
    print("4. Add Category")
    print("5. Display All Categories")
    print("6. Remove Category")
    print("7. Quit")
    
    choice = input("Enter your choice (1-7): ")
    
    if choice == '1':
        add_transaction()
    elif choice == '2':
        transaction_id = input("Enter the ID of the transaction to edit: ")
        edit_transaction(transaction_id)
    elif choice == '3':
        display_transactions()
    elif choice == '4':
        category_name = input("Enter category name: ")
        add_category(category_name)
    elif choice == '5':
        categories = get_categories()
        print("All Categories:")
        for category in categories:
            print(category)
    elif choice == '6':
        category_name = input("Enter category name to remove: ")
        remove_category(category_name)
    elif choice == '7':
        break
    else:
        print("Invalid choice. Please try again.")

# Close the database connection
cursor.close()
conn.close()
