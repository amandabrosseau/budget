import transaction_db
import datetime

trans = transaction_db.TransactionDb()

def prompt_edit_transaction(transaction_id):
    # Fetch the transaction data
    old_trans = trans.get_transaction(transaction_id)

    # Display prompt for each field
    print(f"ID: {transaction_id}")
    new_vendor = input(f"Update Vendor? (Press ENTER to leave as \"{old_trans.vendor}\")\n> ")
    new_amount = input(f"Update Amount? (Press ENTER to leave as \"{old_trans.amount}\")\n> ")

    categories = trans.get_categories()

    # Display available categories
    print("Available Categories:")
    for index, category in enumerate(categories, start=1):
        print(f"{index}. {category}")
            
    new_category = input(f"Update Category? (Press ENTER to leave as \"{old_trans.category}\")\n> ")
            
    # Validate and update the category field
    if new_category:
        if new_category.isdigit() and int(new_category) in range(1, len(categories) + 1):
            new_category_name = categories[int(new_category) - 1][0]
    else:
        print("Invalid category. Please select a valid category or press ENTER to leave as is.")
        new_category_name = None
            
    new_memo = input(f"Update Memo? (Press ENTER to leave as \"{old_trans.memo}\")\n> ")
    new_date = input(f"Update Date? (Press ENTER to leave as \"{old_trans.date}\")\n> ")

    if new_vendor or new_amount or new_category or new_memo or new_date:
        trans.edit_transaction(transaction_id, new_vendor, new_amount, new_category_name, new_memo, new_date)
    else:
        print("No changes made to the transaction.")

def prompt_add_transaction():
    print("Enter transaction details:")
    vendor = input("Vendor: ")
    amount = float(input("Amount: "))
    memo = input("Memo: ")
    date = input("Enter Date (YYYY-MM-DD) or press ENTER for today's date: ")

    if not date:
        # Use today's date if no date is provided
        date = datetime.date.today()
    else:
        # Parse the provided date
        try:
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Transaction not added.")
            return
    
    # Display existing categories and prompt for selection
    categories = trans.get_categories()
    print("Available Categories:")
    for index, category in enumerate(categories, start=1):
        print(f"{index}. {category}")
    category_idx = int(input("Select a category (Enter the corresponding number): ")) - 1    

    if category_idx < 0 or category_idx >= len(categories):
        category = "Uncategorized"
    else:
        category = categories[category_idx]

    trans.add_transaction(vendor, amount, category, memo, date)

    print("Transaction added successfully.")


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
        prompt_add_transaction()
    elif choice == '2':
        transaction_id = input("Enter the ID of the transaction to edit: ")
        prompt_edit_transaction(transaction_id)
    elif choice == '3':
        trans.display_transactions()
    elif choice == '4':
        category_name = input("Enter category name: ")
        trans.add_category(category_name)
    elif choice == '5':
        categories = trans.get_categories()
        print("All Categories:")
        for category in categories:
            print(category)
    elif choice == '6':
        category_name = input("Enter category name to remove: ")
        trans.remove_category(category_name)
    elif choice == '7':
        break
    else:
        print("Invalid choice. Please try again.")

# Close the database connection
trans.close_database()