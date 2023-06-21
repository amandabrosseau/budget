import transaction_db
import datetime
from decimal import Decimal
import quicken

trans = transaction_db.TransactionDb()

def prompt_account_name():
    # Display existing categories and prompt for selection
    accounts = trans.get_accounts()
    if accounts is None:
        print("No accounts defined! Add a target account first!")
        raise ValueError

    print("----------------------------")
    print("Available Accounts:")
    print("----------------------------")
    for index, account in enumerate(accounts, start=1):
        print(f"{index}. {account}")
    account_idx = str(input("Select an account (Enter the corresponding number): "))

    if account_idx.isdigit() and int(account_idx) in range(1, len(accounts)+1):
        return accounts[int(account_idx) - 1]
    else:
        print(f"Invalid account selected. Valid {range(1, len(accounts))}")
        raise ValueError

def prompt_input_file():
    file_path = 'activity.qfx'

    try:
        account_name = prompt_account_name()
    except ValueError:
        print("Please enter a valid account.")
        return

    all_import_trans = quicken.import_quicken_transactions(file_path)
    for import_trans in all_import_trans:
        print("----------------------------------------------------")
        print(f"vendor: {import_trans.vendor}, amount: {float(import_trans.amount)}, memo: {import_trans.memo}")
        print("----------------------------------------------------")
        trans.add_transaction(account_name, import_trans.vendor, import_trans.amount, import_trans.category, import_trans.memo, import_trans.date)


def prompt_edit_transaction(transaction_id):
    # Fetch the transaction data
    old_trans = trans.get_transaction(transaction_id)

    if old_trans is None:
        print("Transaction does not exist")
        return

    old_trans.print()

    # Display prompt for each field
    print(f"ID: {transaction_id}")
    new_vendor = input(f"Update Vendor? (Press ENTER to leave as \"{old_trans.vendor}\")\n> ")
    new_amount = Decimal(input(f"Update Amount? (Press ENTER to leave as \"float({old_trans.amount})\")\n> "))

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
        print("Transaction updated successfully!")
    else:
        print("No changes made to the transaction.")

def prompt_add_transaction():

    try:
        account_name = prompt_account_name()
    except ValueError:
        print("Please enter a valid account.")
        return

    print("Enter transaction details:")
    vendor = input("Vendor: ")
    amount = Decimal(input("Amount: "))
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
    print("----------------------------")
    print("Available Categories:")
    print("----------------------------")
    for index, category in enumerate(categories, start=1):
        print(f"{index}. {category}")
    category_idx = int(input("Select a category (Enter the corresponding number): ")) - 1

    if category_idx < 0 or category_idx >= len(categories):
        category = "Uncategorized"
    else:
        category = categories[category_idx]

    try:
        trans.add_transaction(account_name, vendor, amount, category, memo, date)
    except transaction_db.TransactionExists:
        return

    print("Transaction added successfully.")

def prompt_add_category(name):
    try:
        trans.add_category(name)
    except transaction_db.EntryExistsError:
        print("Category already exists.")
        return

    print("Category added successfully.")

def prompt_add_account(name):
    try:
        trans.add_account(name)
    except transaction_db.EntryExistsError:
        print("Account already exists.")
        return

    print("Category added successfully.")

def prompt_remove_category(name):
    try:
        trans.remove_category(category_name)
    except transaction_db.EntryExistsError:
        print("Category does not exist.")
        return

    print("Category removed successfully.")

def display_all_categories():
    category_balances = trans.get_category_balances()

    print("------------------")
    print("Category Balances:")
    print("------------------")

    for category_id, name, balance in category_balances:
        print(f"Category ID: {category_id}")
        print(f"Name: {name}")
        print(f"Balance: {float(balance)}")
        print("------------------")


# Main program loop
while True:
    print("\nBudgeting App Menu:")
    print("1. Add Transaction")
    print("2. Edit Transaction")
    print("3. Display Transactions")
    print("4. Add Category")
    print("5. Display All Categories")
    print("6. Remove Category")
    print("7. Recalculate Category Balances")
    print("8. Import transactions from Quicken File (.qfx)")
    print("9. Add account")
    print("10. Quit")

    choice = input("Enter your choice (1-10): ")

    if choice == '1':
        prompt_add_transaction()
    elif choice == '2':
        transaction_id = input("Enter the ID of the transaction to edit: ")
        prompt_edit_transaction(transaction_id)
    elif choice == '3':
        trans.display_transactions()
    elif choice == '4':
        category_name = input("Enter category name: ")
        prompt_add_category(category_name)
    elif choice == '5':
        display_all_categories()
    elif choice == '6':
        category_name = input("Enter category name to remove: ")
        trans.remove_category(category_name)
    elif choice == '7':
        trans.recalculate_category_balances()
        print("Category balances successfuly recalculated")
    elif choice == '8':
        prompt_input_file()
    elif choice == '9':
        account_name = input("Enter account name: ")
        prompt_add_account(account_name)
    elif choice == '10':
        break
    else:
        print("Invalid choice. Please try again.")

# Close the database connection
trans.close_database()