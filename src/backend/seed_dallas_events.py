"""
Seed Dallas, TX volunteer opportunities
Run with: python seed_dallas_events.py
"""
import sys
from app import app, db, Listing, User
from werkzeug.security import generate_password_hash


def seed_dallas_events():
    """Create sample volunteer opportunities in Dallas, TX area"""
    with app.app_context():
        print("Creating Dallas test user...")

        # Create Dallas organization user
        dallas_org = User.query.filter_by(email="dallas@volunteer.org").first()
        if not dallas_org:
            dallas_org = User(
                email="dallas@volunteer.org",
                password_hash=generate_password_hash("dallas123")
            )
            db.session.add(dallas_org)
            db.session.commit()
            print("✓ Created Dallas organization user")
        else:
            print("✓ Dallas organization user already exists")

        # Dallas volunteer opportunities with real coordinates
        dallas_listings = [
            {
                "title": "Dallas Food Bank - Food Sorter",
                "description": (
                    "Help sort and package food donations for families in "
                    "need. No experience required. Flexible 4-hour shifts."
                ),
                "location": "Dallas, TX 75203",
                "latitude": 32.7555,
                "longitude": -96.7888,
                "category": "Community"
            },
            {
                "title": "Animal Shelter - Dog Walker",
                "description": (
                    "Walk and socialize shelter dogs waiting for adoption. "
                    "Must be comfortable with large dogs. Weekend shifts."
                ),
                "location": "Dallas, TX 75219",
                "latitude": 32.7881,
                "longitude": -96.8067,
                "category": "Animals"
            },
            {
                "title": "Senior Center - Activity Coordinator",
                "description": (
                    "Lead activities like bingo, crafts, and exercise "
                    "classes for seniors. Patient and energetic "
                    "volunteers needed."
                ),
                "location": "Dallas, TX 75206",
                "latitude": 32.8412,
                "longitude": -96.7746,
                "category": "Community"
            },
            {
                "title": "Dallas Arboretum - Garden Helper",
                "description": (
                    "Maintain beautiful gardens, plant seasonal flowers, "
                    "and help with educational programs. Great for "
                    "nature lovers."
                ),
                "location": "Dallas, TX 75218",
                "latitude": 32.8209,
                "longitude": -96.7166,
                "category": "Environment"
            },
            {
                "title": "Reading Buddy - Elementary School",
                "description": (
                    "Read with elementary students to improve literacy. "
                    "Weekday mornings, 1 hour per week minimum."
                ),
                "location": "Dallas, TX 75214",
                "latitude": 32.8412,
                "longitude": -96.7574,
                "category": "Education"
            },
            {
                "title": "Hospital - Patient Visitor",
                "description": (
                    "Visit and chat with patients who have few visitors. "
                    "Bring comfort and companionship. Background check "
                    "required."
                ),
                "location": "Dallas, TX 75246",
                "latitude": 32.8156,
                "longitude": -96.7697,
                "category": "Health"
            },
            {
                "title": "Trinity River Cleanup Crew",
                "description": (
                    "Join monthly river cleanup events. Remove trash and "
                    "debris from the Trinity River. All supplies provided."
                ),
                "location": "Dallas, TX 75212",
                "latitude": 32.7831,
                "longitude": -96.8491,
                "category": "Environment"
            },
            {
                "title": "Cat Rescue - Foster Coordinator",
                "description": (
                    "Help coordinate foster families for rescued cats. "
                    "Administrative work, no heavy lifting. Work from home."
                ),
                "location": "Dallas, TX 75225",
                "latitude": 32.8668,
                "longitude": -96.8046,
                "category": "Animals"
            },
            {
                "title": "Homeless Shelter - Meal Server",
                "description": (
                    "Serve meals to individuals experiencing homelessness. "
                    "Evening shifts available. Compassionate volunteers "
                    "welcome."
                ),
                "location": "Dallas, TX 75201",
                "latitude": 32.7831,
                "longitude": -96.8067,
                "category": "Community"
            },
            {
                "title": "Youth Mentorship Program",
                "description": (
                    "Mentor at-risk youth through educational activities "
                    "and positive role modeling. 6-month commitment."
                ),
                "location": "Dallas, TX 75215",
                "latitude": 32.7412,
                "longitude": -96.7946,
                "category": "Education"
            }
        ]

        print(f"\nCreating {len(dallas_listings)} Dallas listings...")
        created_count = 0

        for listing_data in dallas_listings:
            # Check if listing already exists
            existing = Listing.query.filter_by(
                title=listing_data["title"]).first()
            if not existing:
                listing = Listing(
                    **listing_data,
                    owner_id=dallas_org.id
                )
                db.session.add(listing)
                created_count += 1

        db.session.commit()
        print(f"✓ Created {created_count} new Dallas listings")

        total_listings = Listing.query.filter(
            Listing.location.like('%Dallas%')).count()
        print(f"✓ Total Dallas listings in database: {total_listings}")

        print("\n=== Dallas Volunteer Opportunities Created ===")
        print("Test user: dallas@volunteer.org / dallas123")
        print(f"Location focus: Dallas, TX area")
        print(f"Categories: Community, Animals, Environment, "
              f"Education, Health")
        print("\nTest queries:")
        print("  - All Dallas: GET /listings?location=Dallas")
        print("  - By category: GET /listings?q=Community")
        print("  - All listings: GET /listings")


if __name__ == "__main__":
    seed_dallas_events()
