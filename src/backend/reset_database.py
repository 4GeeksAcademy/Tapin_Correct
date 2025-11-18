"""Reset database - Drop all tables and recreate with current schema."""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

print("⚠️  WARNING: This will DELETE ALL DATA in the database!")
print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
print()

response = input("Are you sure you want to continue? (yes/no): ")
if response.lower() != "yes":
    print("Aborted.")
    sys.exit(0)

with app.app_context():
    print("\n🗑️  Dropping all tables...")
    db.drop_all()
    print("✅ All tables dropped")

    print("\n📝 Creating tables with current schema...")
    db.create_all()
    print("✅ Tables created successfully")

    print("\n✨ Database reset complete!")
    print("\nNext steps:")
    print("1. Restart your backend server")
    print("2. Seed the database: curl -X POST http://127.0.0.1:5000/api/seed-events")
