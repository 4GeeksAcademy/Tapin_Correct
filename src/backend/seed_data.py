"""
Seed script to populate the database with sample data for UI testing
Run with: python backend/seed_data.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from models import (
    db,
    User,
    Listing,
    Item,
    Review,
    UserValues,
    Achievement,
    UserAchievement,
    SignUp,
    Organization,
)

from werkzeug.security import generate_password_hash
from categories import CATEGORIES


def clear_database():
    """Clear all data from the database"""
    print("🗑️  Clearing existing data...")
    with app.app_context():
        UserAchievement.query.delete()
        Achievement.query.delete()
        UserValues.query.delete()
        Review.query.delete()
        Item.query.delete()
        Listing.query.delete()
        User.query.delete()
        db.session.commit()
    print("✓ Database cleared")


def create_sample_users():
    """Create sample users"""
    print("\n👥 Creating sample users...")

    users_data = [
        {"email": "volunteer1@example.com", "password": "password123", "role": "user"},
        {"email": "volunteer2@example.com", "password": "password123", "role": "user"},
        {"email": "volunteer3@example.com", "password": "password123", "role": "user"},
        {"email": "org1@example.com", "password": "password123", "role": "user"},
        {"email": "org2@example.com", "password": "password123", "role": "user"},
        {"email": "org3@example.com", "password": "password123", "role": "user"},
    ]

    users = []
    with app.app_context():
        for data in users_data:
            user = User(
                email=data["email"],
                password_hash=generate_password_hash(data["password"]),
                role=data["role"],
            )
            db.session.add(user)
            users.append(user)

        db.session.commit()
        # Refresh to get IDs
        for user in users:
            db.session.refresh(user)
        print(f"✓ Created {len(users)} users")
        return [u.id for u in users]


def create_sample_organizations(user_ids):
    """Create sample organizations"""
    print("\n🏢 Creating sample organizations...")

    orgs_data = [
        {
            "name": "Good Deeds Inc.",
            "description": "A non-profit dedicated to doing good deeds.",
            "user_id": user_ids[3],
        },
        {
            "name": "Helping Hands",
            "description": "Lending a helping hand to those in need.",
            "user_id": user_ids[4],
        },
        {
            "name": "Community Builders",
            "description": "Building a better community, one project at a time.",
            "user_id": user_ids[5],
        },
    ]

    orgs = []
    with app.app_context():
        for data in orgs_data:
            org = Organization(
                name=data["name"],
                description=data["description"],
            )
            db.session.add(org)
            orgs.append(org)

        db.session.commit()
        # Refresh to get IDs
        for org in orgs:
            db.session.refresh(org)
        print(f"✓ Created {len(orgs)} organizations")
        return [o.id for o in orgs]


def create_real_organizations():
    """Create real organizations"""
    print("\n🏢 Creating real organizations...")

    orgs_data = [
        {
            "name": "American Red Cross",
            "description": "A humanitarian organization that provides emergency assistance, disaster relief, and disaster preparedness education in the United States.",
        },
        {
            "name": "Habitat for Humanity",
            "description": "A nonprofit organization that helps families build and improve places to call home.",
        },
        {
            "name": "Doctors Without Borders",
            "description": "An international humanitarian medical non-governmental organization best known for its projects in conflict zones and in countries affected by endemic diseases.",
        },
        {
            "name": "The Humane Society",
            "description": "An organization dedicated to promoting the welfare of animals.",
        },
        {
            "name": "United Way",
            "description": "A nonprofit organization that works to improve the health, education, and financial stability of every person in every community.",
        },
    ]

    orgs = []
    with app.app_context():
        for data in orgs_data:
            org = Organization(
                name=data["name"],
                description=data["description"],
            )
            db.session.add(org)
            orgs.append(org)

        db.session.commit()
        # Refresh to get IDs
        for org in orgs:
            db.session.refresh(org)
        print(f"✓ Created {len(orgs)} organizations")
        return [o.id for o in orgs]


def create_sample_listings(user_ids, org_ids):
    """Create sample volunteer opportunity listings"""
    print("\n📋 Creating sample listings...")

    listings_data = [
        {
            "title": "Community Beach Cleanup",
            "description": (
                "Join us for a morning beach cleanup! Help keep our shores "
                "clean and protect marine life. All supplies provided. "
                "Perfect for individuals, families, and groups. No "
                "experience necessary."
            ),
            "location": "Pasadena Senior Center",
            "latitude": 34.1478,
            "longitude": -118.1445,
            "category": "Health",
            "image_url": (
                "https://images.unsplash.com/photo-1581579438747-1dc8d17bbce4"
                "?w=800&h=600&fit=crop"
            ),
        },
        {
            "title": "Animal Shelter Dog Walker",
            "description": (
                "Love dogs? Help socialize our shelter dogs by taking them "
                "for walks. Must be comfortable with dogs of all sizes. "
                "Orientation required. Flexible schedule - even 1 hour helps!"
            ),
            "location": "LA County Animal Shelter",
            "latitude": 34.2081,
            "longitude": -118.1708,
            "category": "Animals",
            "image_url": (
                "https://images.unsplash.com/photo-1450778869180-41d0601e046e"
                "?w=800&h=600&fit=crop"
            ),
        },
        {
            "title": "Youth Tutoring Program",
            "description": (
                "Tutor middle and high school students in math, science, or "
                "English. Make a lasting impact on a young person's "
                "education. 2-3 hours per week commitment. Virtual or "
                "in-person options."
            ),
            "location": "Inglewood Community Center",
            "latitude": 33.9617,
            "longitude": -118.3531,
            "category": "Education",
            "image_url": (
                "https://images.unsplash.com/photo-1497633762265-9d179a990aa6"
                "?w=800&h=600&fit=crop"
            ),
        },
        {
            "title": "Community Garden Maintenance",
            "description": (
                "Help maintain our thriving community garden! Plant, water, "
                "weed, and harvest fresh produce. Learn sustainable "
                "gardening practices. All produce shared with local families "
                "and volunteers."
            ),
            "location": "Venice Community Garden",
            "latitude": 33.9850,
            "longitude": -118.4695,
            "category": "Environment",
            "image_url": (
                "https://images.unsplash.com/photo-1464226184884-fa280b87c399"
                "?w=800&h=600&fit=crop"
            ),
        },
        {
            "title": "Homeless Outreach Team",
            "description": (
                "Join our street outreach team to distribute meals, hygiene "
                "kits, and connect people with resources. Training and "
                "supervision provided. Must be 18+ and compassionate."
            ),
            "location": "Skid Row, Downtown LA",
            "latitude": 34.0443,
            "longitude": -118.2420,
            "category": "Community",
            "image_url": (
                "https://images.unsplash.com/photo-1532629345422-7515f3d16bb6"
                "?w=800&h=600&fit=crop"
            ),
        },
        {
            "title": "Hospital Visit Program",
            "description": (
                "Bring comfort to hospital patients through friendly visits "
                "and conversation. Background check required. Weekday and "
                "weekend opportunities. Meaningful connections that brighten "
                "someone's day."
            ),
            "location": "Cedars-Sinai Medical Center",
            "latitude": 34.0754,
            "longitude": -118.3776,
            "category": "Health",
            "image_url": (
                "https://images.unsplash.com/photo-1516549655169-df83a0774514"
                "?w=800&h=600&fit=crop"
            ),
        },
        {
            "title": "Trail Restoration Project",
            "description": (
                "Help restore hiking trails in Griffith Park. Remove "
                "invasive plants, repair erosion, and plant native species. "
                "Outdoor work, good exercise, and beautiful views. Tools "
                "provided."
            ),
            "location": "Griffith Park",
            "latitude": 34.1341,
            "longitude": -118.2942,
            "category": "Environment",
            "image_url": (
                "https://images.unsplash.com/photo-1551632811-561732d1e306"
                "?w=800&h=600&fit=crop"
            ),
        },
        {
            "title": "Literacy Program Reading Buddy",
            "description": (
                "Read with elementary students to improve their literacy "
                "skills. One-on-one or small group sessions. Patient"
            ),
            "location": "Getty Center",
            "latitude": 34.0780,
            "longitude": -118.4741,
            "category": "Education",
            "image_url": (
                "https://images.unsplash.com/photo-1554907984-15263bfd63bd"
                "?w=800&h=600&fit=crop"
            ),
        },
        {
            "title": "Pet Shelter Adoption Events",
            "description": (
                "Help facilitate pet adoption events! Assist potential "
                "adopters, answer questions about our animals, and help with "
                "event setup/cleanup. Must love animals and people equally!"
            ),
            "location": "West LA Animal Shelter",
            "latitude": 34.0522,
            "longitude": -118.4437,
            "category": "Animals",
            "image_url": (
                "https://images.unsplash.com/photo-1601758228041-f3b2795255f1"
                "?w=800&h=600&fit=crop"
            ),
        },
        {
            "title": "Meal Delivery for Homebound Seniors",
            "description": (
                "Deliver hot, nutritious meals to seniors who cannot leave "
                "their homes. Brief friendly visits brighten their day. "
                "Flexible morning schedule, reliable transportation required."
            ),
            "location": "Santa Monica Meals on Wheels",
            "latitude": 34.0194,
            "longitude": -118.4912,
            "category": "Health",
            "image_url": (
                "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c"
                "?w=800&h=600&fit=crop"
            ),
        },
        {
            "title": "Wildlife Rescue Assistant",
            "description": (
                "Support our wildlife rehabilitation center. Help prepare "
                "food for animals, clean enclosures, and assist with release "
                "preparations. Training provided. Nature lovers welcome!"
            ),
            "location": "Malibu Canyon Wildlife Center",
            "latitude": 34.0369,
            "longitude": -118.7004,
            "category": "Animals",
            "image_url": (
                "https://images.unsplash.com/photo-1425082661705-1834bfd09dca"
                "?w=800&h=600&fit=crop"
            ),
        },
    ]

    listings = []
    with app.app_context():
        for i, data in enumerate(listings_data):
            listing = Listing(
                title=data["title"],
                description=data["description"],
                location=data["location"],
                latitude=data.get("latitude"),
                longitude=data.get("longitude"),
                category=data.get("category"),
                image_url=data.get("image_url"),
                owner_id=user_ids[i % len(user_ids)],  # Distribute among users
            )
            db.session.add(listing)
            listings.append(listing)

        db.session.commit()
        print(f"✓ Created {len(listings)} listings")
        return [listing.id for listing in listings]


def create_sample_signups(user_ids, listing_ids):
    """Create sample volunteer sign-ups"""
    print("\n✋ Creating sample sign-ups...")

    signups = []
    used_pairs = set()

    with app.app_context():
        # Create some accepted sign-ups
        for i in range(8):
            user_idx = i % len(user_ids)
            listing_idx = (i + 3) % len(listing_ids)  # Offset to avoid conflicts
            pair = (user_ids[user_idx], listing_ids[listing_idx])

            if pair not in used_pairs:
                used_pairs.add(pair)
                msg = (
                    "I'd love to volunteer! I have experience with "
                    "similar activities."
                )
                signup = SignUp(
                    user_id=pair[0], listing_id=pair[1], message=msg, status="accepted"
                )
                db.session.add(signup)
                signups.append(signup)

        # Create some pending sign-ups
        for i in range(5):
            user_idx = (i + 2) % len(user_ids)
            listing_idx = (i * 2) % len(listing_ids)  # Different offset
            pair = (user_ids[user_idx], listing_ids[listing_idx])

            if pair not in used_pairs:
                used_pairs.add(pair)
                signup = SignUp(
                    user_id=pair[0],
                    listing_id=pair[1],
                    message="Count me in! What should I bring?",
                    status="pending",
                )
                db.session.add(signup)
                signups.append(signup)

        db.session.commit()
        print(f"✓ Created {len(signups)} sign-ups")


def create_sample_reviews(user_ids, listing_ids):
    """Create sample reviews"""
    print("\n⭐ Creating sample reviews...")

    reviews_data = [
        {
            "rating": 5,
            "comment": (
                "Amazing experience! The organizers were so welcoming and "
                "everything was well-planned."
            ),
        },
        {
            "rating": 5,
            "comment": (
                "Loved volunteering here. Made a real difference and met "
                "great people!"
            ),
        },
        {
            "rating": 4,
            "comment": (
                "Great opportunity! Very fulfilling. Would have liked "
                "clearer instructions at the start."
            ),
        },
        {
            "rating": 5,
            "comment": "Highly recommend! Perfect for first-time volunteers.",
        },
        {
            "rating": 4,
            "comment": (
                "Good experience overall. Looking forward to volunteering "
                "again next month."
            ),
        },
        {
            "rating": 5,
            "comment": (
                "The best volunteer experience I've had. Staff was "
                "incredibly supportive."
            ),
        },
        {
            "rating": 3,
            "comment": (
                "Decent opportunity but a bit disorganized. Still glad I "
                "participated."
            ),
        },
        {
            "rating": 5,
            "comment": (
                "Wonderful cause and wonderful people. Can't wait to come " "back!"
            ),
        },
        {
            "rating": 4,
            "comment": "Really enjoyed it! Great way to spend a Saturday morning.",
        },
        {
            "rating": 5,
            "comment": (
                "Exceeded my expectations. Very professionally run and "
                "impactful work."
            ),
        },
    ]

    reviews = []
    with app.app_context():
        for i, data in enumerate(reviews_data):
            # Only create reviews where user signed up (simulating completion)
            review = Review(
                user_id=user_ids[i % len(user_ids)],
                listing_id=listing_ids[i % len(listing_ids)],
                rating=data["rating"],
                comment=data["comment"],
            )
            db.session.add(review)
            reviews.append(review)

        db.session.commit()
        print(f"✓ Created {len(reviews)} reviews")


def create_achievements():
    """Create sample achievements"""
    print("\n🏆 Creating sample achievements...")

    achievements_data = [
        {
            "name": "First Steps",
            "description": "Completed your first volunteer opportunity.",
            "icon": "fa-shoe-prints",
        },
        {
            "name": "Helping Hand",
            "description": "Completed 5 volunteer opportunities.",
            "icon": "fa-hands-helping",
        },
        {
            "name": "Community Champion",
            "description": "Completed 10 volunteer opportunities.",
            "icon": "fa-trophy",
        },
        {
            "name": "Good Samaritan",
            "description": "Received a 5-star rating on a review.",
            "icon": "fa-star",
        },
        {
            "name": "Superstar Volunteer",
            "description": "Received 5 5-star ratings.",
            "icon": "fa-meteor",
        },
    ]

    achievements = []
    with app.app_context():
        for data in achievements_data:
            achievement = Achievement(
                name=data["name"],
                description=data["description"],
                icon=data["icon"],
            )
            db.session.add(achievement)
            achievements.append(achievement)

        db.session.commit()
        # Refresh to get IDs
        for achievement in achievements:
            db.session.refresh(achievement)
        print(f"✓ Created {len(achievements)} achievements")
        return [a.id for a in achievements]


def create_superstar_volunteers_and_assign_achievements(user_ids, achievement_ids):
    """Create superstar volunteers and assign achievements"""
    print("\n🌟 Creating superstar volunteers and assigning achievements...")

    with app.app_context():
        # Assign "First Steps" and "Helping Hand" to volunteer1
        db.session.add(
            UserAchievement(user_id=user_ids[0], achievement_id=achievement_ids[0])
        )
        db.session.add(
            UserAchievement(user_id=user_ids[0], achievement_id=achievement_ids[1])
        )

        # Assign "Community Champion" and "Good Samaritan" to volunteer2
        db.session.add(
            UserAchievement(user_id=user_ids[1], achievement_id=achievement_ids[2])
        )
        db.session.add(
            UserAchievement(user_id=user_ids[1], achievement_id=achievement_ids[3])
        )

        # Assign "Superstar Volunteer" to volunteer3
        db.session.add(
            UserAchievement(user_id=user_ids[2], achievement_id=achievement_ids[4])
        )

        db.session.commit()
        print("✓ Superstar volunteers created and achievements assigned")


def assign_user_values(user_ids):
    """Assign values to users"""
    print("\n💖 Assigning user values...")

    with app.app_context():
        for i, user_id in enumerate(user_ids):
            # Assign a few values to each user
            for j in range(3):
                value = CATEGORIES[(i + j) % len(CATEGORIES)]
                db.session.add(UserValues(user_id=user_id, value=value))

        db.session.commit()
        print("✓ User values assigned")


def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    print("=" * 50)

    # Clear existing data
    clear_database()

    # Create sample data
    user_ids = create_sample_users()
    org_ids = create_real_organizations()
    listing_ids = create_sample_listings(user_ids, org_ids)
    create_sample_signups(user_ids, listing_ids)
    create_sample_reviews(user_ids, listing_ids)
    achievement_ids = create_achievements()
    create_superstar_volunteers_and_assign_achievements(user_ids, achievement_ids)
    assign_user_values(user_ids)

    print("\n" + "=" * 50)
    print("✅ Database seeding completed successfully!")
    print("\n📝 Sample Accounts:")
    print("   Volunteers:")
    print("   - volunteer1@example.com / password123")
    print("   - volunteer2@example.com / password123")
    print("   - volunteer3@example.com / password123")
    print("\n   Organizations:")
    print("   - org1@example.com / password123")
    print("   - org2@example.com / password123")
    print("   - org3@example.com / password123")
    print("\n🌐 You can now test the UI with realistic data!")


if __name__ == "__main__":
    main()
