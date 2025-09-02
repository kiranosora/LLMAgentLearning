import sys
from typing import List, Tuple
from database import ExpenseDatabase
from datetime import datetime

def add_expense_interactive(db: ExpenseDatabase):
    """Interactive function to add an expense"""
    print("\n=== Add New Expense ===")
    
    # Get amount
    while True:
        try:
            amount = float(input("Enter amount: "))
            if amount <= 0:
                print("Amount must be positive.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")
    
    # Show categories
    categories = db.get_categories()
    print("\nAvailable categories:")
    for i, (cat_id, name) in enumerate(categories, 1):
        print(f"{i}. {name}")
    
    # Get category
    while True:
        try:
            choice = int(input("Select category (number): "))
            if 1 <= choice <= len(categories):
                category_id = categories[choice-1][0]
                break
            else:
                print(f"Please enter a number between 1 and {len(categories)}.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get description
    description = input("Enter description (optional): ")
    
    # Get date
    date_input = input("Enter date (YYYY-MM-DD, press Enter for today): ").strip()
    if date_input:
        try:
            datetime.strptime(date_input, "%Y-%m-%d")
            date = date_input
        except ValueError:
            print("Invalid date format. Using today's date.")
            date = None
    else:
        date = None
    
    # Add expense
    if db.add_expense(amount, category_id, description, date):
        print("Expense added successfully!")
    else:
        print("Failed to add expense.")

def view_expenses_interactive(db: ExpenseDatabase):
    """Interactive function to view expenses"""
    print("\n=== View Expenses ===")
    
    # Get year
    while True:
        try:
            year = int(input("Enter year (e.g., 2024): "))
            break
        except ValueError:
            print("Please enter a valid year.")
    
    # Get month
    while True:
        try:
            month = int(input("Enter month (1-12): "))
            if 1 <= month <= 12:
                break
            else:
                print("Please enter a month between 1 and 12.")
        except ValueError:
            print("Please enter a valid month.")
    
    # Show expenses
    expenses = db.get_expenses_by_month(year, month)
    if not expenses:
        print(f"No expenses found for {year}-{month:02d}.")
        return
    
    print(f"\n=== Expenses for {year}-{month:02d} ===")
    total = 0
    print(f"{'ID':<5} {'Amount':<10} {'Category':<15} {'Date':<12} {'Description'}")
    print("-" * 60)
    for expense in expenses:
        exp_id, amount, category, description, date = expense
        print(f"{exp_id:<5} {amount:<10.2f} {category:<15} {date:<12} {description}")
        total += amount
    
    print("-" * 60)
    print(f"{'Total':<5} {total:<10.2f}")
    
    # Show summary by category
    summary = db.get_monthly_summary(year, month)
    if summary:
        print(f"\n=== Summary by Category ===")
        print(f"{'Category':<15} {'Total':<10}")
        print("-" * 25)
        for category, total in summary:
            print(f"{category:<15} {total:<10.2f}")

def add_category_interactive(db: ExpenseDatabase):
    """Interactive function to add a category"""
    print("\n=== Add New Category ===")
    name = input("Enter category name: ").strip()
    
    if not name:
        print("Category name cannot be empty.")
        return
    
    if db.add_category(name):
        print(f"Category '{name}' added successfully!")
    else:
        print(f"Category '{name}' already exists.")

def main_menu(db: ExpenseDatabase):
    """Main menu function"""
    while True:
        print("\n=== Expense Tracker ===")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Add Category")
        print("4. Exit")
        
        choice = input("Select an option (1-4): ").strip()
        
        if choice == "1":
            add_expense_interactive(db)
        elif choice == "2":
            view_expenses_interactive(db)
        elif choice == "3":
            add_category_interactive(db)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please select 1-4.")

if __name__ == "__main__":
    # Initialize database
    db = ExpenseDatabase()
    print("Expense Tracker Database initialized.")
    
    # Run main menu
    if len(sys.argv) > 1:
        # Command line mode
        if sys.argv[1] == "add":
            add_expense_interactive(db)
        elif sys.argv[1] == "view":
            view_expenses_interactive(db)
        else:
            print("Usage: python expense_tracker.py [add|view]")
    else:
        # Interactive mode
        main_menu(db)