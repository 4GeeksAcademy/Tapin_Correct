"""Update the password_hash column to be larger"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import app, db  # noqa: E402
from models import User, Organization, Item, Listing, Review, UserValues


with app.app_context():
    print("Updating password_hash column to VARCHAR(256)...")
    try:
        # Using raw SQL to alter the column
        sql = 'ALTER TABLE "user" ALTER COLUMN password_hash TYPE VARCHAR(256)'
        db.session.execute(db.text(sql))
        db.session.commit()
        print("✓ Column updated successfully!")
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database schema updated.")
