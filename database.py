import sqlite3
from typing import List, Tuple, Optional
from datetime import datetime
import os

class ExpenseDatabase:
    def __init__(self, db_path: str = "expenses.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category_id INTEGER NOT NULL,
                description TEXT,
                date DATE NOT NULL DEFAULT (DATE('now')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # Insert default categories if they don't exist
        default_categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare', 'Other']
        for category in default_categories:
            cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
        
        conn.commit()
        conn.close()
    
    def add_category(self, name: str) -> bool:
        """Add a new category"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO categories (name) VALUES (?)', (name,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False  # Category already exists
    
    def get_categories(self) -> List[Tuple[int, str]]:
        """Get all categories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM categories')
        categories = cursor.fetchall()
        conn.close()
        return categories
    
    def add_expense(self, amount: float, category_id: int, description: str = "", date: str = None) -> bool:
        """Add a new expense"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO expenses (amount, category_id, description, date)
                VALUES (?, ?, ?, ?)
            ''', (amount, category_id, description, date))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_expenses_by_month(self, year: int, month: int) -> List[Tuple]:
        """Get all expenses for a specific month"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.id, e.amount, c.name, e.description, e.date
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE strftime('%Y', e.date) = ? AND strftime('%m', e.date) = ?
            ORDER BY e.date DESC
        ''', (str(year), f"{month:02d}"))
        expenses = cursor.fetchall()
        conn.close()
        return expenses
    
    def get_monthly_summary(self, year: int, month: int) -> List[Tuple]:
        """Get monthly summary by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.name, SUM(e.amount) as total
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE strftime('%Y', e.date) = ? AND strftime('%m', e.date) = ?
            GROUP BY c.name
            ORDER BY total DESC
        ''', (str(year), f"{month:02d}"))
        summary = cursor.fetchall()
        conn.close()
        return summary
    
    def get_total_monthly_expense(self, year: int, month: int) -> float:
        """Get total expense for a specific month"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(amount) FROM expenses
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
        ''', (str(year), f"{month:02d}"))
        result = cursor.fetchone()[0]
        conn.close()
        return result if result else 0.0