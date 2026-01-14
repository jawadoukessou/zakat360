import sqlite3
import os

# Correct path per .env
db_path = os.path.join(os.getcwd(), 'zakat360/zakat360/zakat360_dev.db')
print(f"Checking DB at: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT id, name, name_fr FROM causes")
    rows = cursor.fetchall()
    
    print("ID | Name (repr) | Name FR (repr)")
    print("-" * 60)
    for row in rows:
        print(f"{row[0]} | {repr(row[1])} | {repr(row[2])}")

except Exception as e:
    print(f"Error: {e}")

conn.close()
