import transaction_db

trans = transaction_db.TransactionDb()

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
        trans.add_transaction()
    elif choice == '2':
        transaction_id = input("Enter the ID of the transaction to edit: ")
        trans.edit_transaction(transaction_id)
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