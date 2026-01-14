import os
import sys
from sqlalchemy import text

# Ensure app import works
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zakat360 import create_app
from zakat360.extensions import db


def column_exists(table, column):
    # SQLite PRAGMA table_info returns rows with 'name' field
    result = db.session.execute(text(f"PRAGMA table_info('{table}')"))
    cols = [row[1] for row in result.fetchall()]  # index 1 is 'name'
    return column in cols


def add_column_if_missing(table, column, sql_type):
    if not column_exists(table, column):
        db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}"))
        db.session.commit()
        print(f"[OK] Ajout colonne {table}.{column} ({sql_type})")
    else:
        print(f"[SKIP] Colonne {table}.{column} déjà présente")


def main():
    app = create_app()
    with app.app_context():
        add_column_if_missing('causes', 'name_fr', 'TEXT')
        add_column_if_missing('causes', 'description_fr', 'TEXT')
        add_column_if_missing('causes', 'category_fr', 'TEXT')
        print('[DONE] Vérification/Ajout des colonnes FR pour causes')


if __name__ == '__main__':
    main()
