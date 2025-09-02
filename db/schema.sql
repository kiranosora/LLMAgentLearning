-- Categories table to store expense categories
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Expenses table to store expense records
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount DECIMAL(10, 2) NOT NULL,
    category_id INTEGER NOT NULL,
    description TEXT,
    expense_date DATE NOT NULL DEFAULT (date('now')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories (id)
);

-- Insert default categories
INSERT OR IGNORE INTO categories (name) VALUES ('Food');
INSERT OR IGNORE INTO categories (name) VALUES ('Transportation');
INSERT OR IGNORE INTO categories (name) VALUES ('Entertainment');
INSERT OR IGNORE INTO categories (name) VALUES ('Utilities');
INSERT OR IGNORE INTO categories (name) VALUES ('Shopping');
INSERT OR IGNORE INTO categories (name) VALUES ('Healthcare');
INSERT OR IGNORE INTO categories (name) VALUES ('Education');
INSERT OR IGNORE INTO categories (name) VALUES ('Other');

-- Monthly summaries view for easier querying
CREATE VIEW IF NOT EXISTS monthly_expenses AS
SELECT 
    strftime('%Y-%m', e.expense_date) as month,
    c.name as category,
    SUM(e.amount) as total_amount,
    COUNT(e.id) as transaction_count
FROM expenses e
JOIN categories c ON e.category_id = c.id
GROUP BY strftime('%Y-%m', e.expense_date), c.name
ORDER BY month DESC, total_amount DESC;