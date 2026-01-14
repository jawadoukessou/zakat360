import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'zakat360/zakat360_dev.db')
print(f"Connecting to database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    columns_to_add = {
        'name_fr': 'VARCHAR(100)',
        'description_fr': 'TEXT',
        'category_fr': 'VARCHAR(50)'
    }

    # Get existing columns
    cursor.execute("PRAGMA table_info(causes)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    print(f"Existing columns: {existing_columns}")

    for col, dtype in columns_to_add.items():
        if col not in existing_columns:
            print(f"Adding column {col}...")
            cursor.execute(f"ALTER TABLE causes ADD COLUMN {col} {dtype}")
        else:
            print(f"Column {col} already exists.")

    conn.commit()
    print("Columns added successfully.")
    
    # Verify
    cursor.execute("PRAGMA table_info(causes)")
    new_columns = [row[1] for row in cursor.fetchall()]
    print(f"New columns: {new_columns}")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
