import sys
import os
from datetime import date

# Ensure local backend package imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import (
    User,
    VolunteerProfile,
    OrganizationProfile,
    Event,
)

app = create_app()


def reset_and_seed():
    with app.app_context():
        print("🔴 Dropping all database tables...")
        db.drop_all()
        print("✅ Tables dropped.")

        print("✨ Creating all tables based on new models.py...")
        db.create_all()
        print("✅ New tables created.")

        print("🌱 Seeding the new database with compatible sample data...")

        # Create a volunteer user
        vol = User(email="volunteer@example.com", user_type="volunteer")
        vol.set_password("password123")
        db.session.add(vol)

        # Create an organization user
        org_user = User(email="org@example.com", user_type="organization")
        org_user.set_password("password123")
        db.session.add(org_user)

        db.session.commit()

        # Create profiles
        volunteer_profile = VolunteerProfile(
            user_id=vol.id,
            first_name="Alex",
            last_name="Volunteer",
            bio="Enthusiastic community volunteer",
            city="Houston",
            state="TX",
        )

        organization_profile = OrganizationProfile(
            user_id=org_user.id,
            organization_name="Community Helpers",
            description="Local nonprofit organizing volunteer events",
            city="Houston",
            state="TX",
            verification_status=None,
        )

        db.session.add(volunteer_profile)
        db.session.add(organization_profile)
        db.session.commit()

        # Create a sample event linked to the organization_profile
        sample_event = Event(
            organization_id=organization_profile.id,
            title="Community Park Cleanup",
            description="Help clean up the neighborhood park and make it beautiful.",
            category="Environment",
            start_date=date.today(),
            location_name="Riverside Park",
            city="Houston",
            latitude=29.7604,
            longitude=-95.3698,
            status="published",
            source="seed",
        )

        db.session.add(sample_event)
        db.session.commit()

        print("🚀 Database reset and seeded successfully!")


if __name__ == "__main__":
    reset_and_seed()
