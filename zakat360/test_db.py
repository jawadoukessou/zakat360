import sys
import os

print("Starting test_db.py")
try:
    from zakat360 import create_app
    print("Imported create_app")
    app = create_app()
    print("Created app")
    from zakat360.extensions import db
    print("Imported db")
    with app.app_context():
        print("Creating all tables...")
        db.create_all()
        print("Tables created.")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
