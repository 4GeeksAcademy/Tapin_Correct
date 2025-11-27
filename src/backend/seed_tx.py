"""
Lightweight seed script to populate demo organizations (claimed and unclaimed).
Run with: PYTHONPATH=src venv/bin/python src/backend/seed_tx.py
"""

import json
import os
import sys
from werkzeug.security import generate_password_hash

# Ensure backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app import create_app
from backend.models import db, User, OrganizationProfile, VerificationStatus


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    # seed files are located next to this script in `src/backend/seed_data`
    data_dir = os.path.join(os.path.dirname(__file__), "seed_data")
    tx_file = os.path.join(data_dir, "tx_nonprofits.json")
    unclaimed_file = os.path.join(data_dir, "unclaimed_orgs.json")

    app = create_app()
    with app.app_context():
        print(
            "Starting seeding: clearing existing OrganizationProfile and Users for demo orgs..."
        )
        # WARNING: this is destructive for demo data; keep minimal
        try:
            # Only remove org users that match seed emails to avoid deleting other accounts
            tx_data = load_json(tx_file)
            emails = [o.get("email") for o in tx_data if o.get("email")]

            for em in emails:
                if not em:
                    continue
                u = User.query.filter_by(email=em).first()
                if u:
                    # remove linked organization profile and user
                    if getattr(u, "organization_profile", None):
                        OrganizationProfile.query.filter_by(user_id=u.id).delete()
                    db.session.delete(u)

            db.session.commit()
        except Exception as e:
            print("Warning during cleanup:", e)
            db.session.rollback()

        # Create claimed organizations (with user accounts)
        try:
            for org in load_json(tx_file):
                email = org.get("email")
                password = org.get("password", "password123")
                if not email:
                    continue
                existing = User.query.filter_by(email=email).first()
                if existing:
                    print(f"Skipping existing user {email}")
                    continue
                user = User(email=email)
                user.password_hash = generate_password_hash(password)
                # mark as organization
                try:
                    user.user_type = (
                        User.user_type.type if hasattr(User, "user_type") else None
                    )
                except Exception:
                    pass
                db.session.add(user)
                db.session.flush()

                profile = OrganizationProfile(
                    user_id=user.id,
                    organization_name=org.get("organization_name"),
                    organization_type=org.get("organization_type"),
                    city=org.get("city"),
                    description=org.get("description"),
                    verification_status=VerificationStatus.VERIFIED,
                )
                db.session.add(profile)

            db.session.commit()
            print("✓ Created claimed orgs from tx_nonprofits.json")
        except Exception as e:
            print("Error creating claimed orgs:", e)
            db.session.rollback()

        # Create unclaimed organization profiles
        try:
            for org in load_json(unclaimed_file):
                # Create an OrganizationProfile with no user_id and UNCLAIMED status
                profile = OrganizationProfile(
                    user_id=None,
                    organization_name=org.get("organization_name"),
                    organization_type=org.get("organization_type"),
                    city=org.get("city"),
                    description=org.get("description"),
                    verification_status=VerificationStatus.UNCLAIMED,
                )
                db.session.add(profile)

            db.session.commit()
            print("✓ Created unclaimed orgs from unclaimed_orgs.json")
        except Exception as e:
            print("Error creating unclaimed orgs:", e)
            db.session.rollback()

    print("Seeding complete.")


if __name__ == "__main__":
    main()
