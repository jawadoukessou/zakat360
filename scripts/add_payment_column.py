import sqlite3
import os

# Path to the database
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'zakat360', 'zakat360_dev.db')

def add_column():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE donations ADD COLUMN payment_method VARCHAR(50) DEFAULT 'card'")
        conn.commit()
        print("Column 'payment_method' added successfully.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column 'payment_method' already exists.")
        else:
            print(f"Error adding column: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    add_column()
