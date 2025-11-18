"""
Seed database with volunteer events and organizations for 5 major US cities.
Includes contact information for each organization.
"""
import sys
sys.path.insert(0, 'src')

from backend.app import app, db, Event, EventImage, User
from datetime import datetime, timedelta
import random
import uuid

# 5 Major Cities with coordinates
CITIES = {
    'Dallas': {'state': 'TX', 'lat': 32.7767, 'lon': -96.7970},
    'Los Angeles': {'state': 'CA', 'lat': 34.0522, 'lon': -118.2437},
    'New York': {'state': 'NY', 'lat': 40.7128, 'lon': -74.0060},
    'Chicago': {'state': 'IL', 'lat': 41.8781, 'lon': -87.6298},
    'Houston': {'state': 'TX', 'lat': 29.7604, 'lon': -95.3698},
}

# Organizations with contact info
ORGANIZATIONS = {
    'Food Banks': [
        {
            'name': 'North Texas Food Bank',
            'contact_person': 'Sarah Johnson',
            'contact_email': 'volunteer@ntfb.org',
            'contact_phone': '(214) 555-1234',
            'category': 'Hunger Relief'
        },
        {
            'name': 'Los Angeles Regional Food Bank',
            'contact_person': 'Michael Chen',
            'contact_email': 'volunteers@lafoodbank.org',
            'contact_phone': '(323) 555-5678',
            'category': 'Hunger Relief'
        },
        {
            'name': 'City Harvest NYC',
            'contact_person': 'Jennifer Williams',
            'contact_email': 'getinvolved@cityharvest.org',
            'contact_phone': '(212) 555-9012',
            'category': 'Hunger Relief'
        },
        {
            'name': 'Greater Chicago Food Depository',
            'contact_person': 'David Martinez',
            'contact_email': 'volunteer@chicagosfoodbank.org',
            'contact_phone': '(773) 555-3456',
            'category': 'Hunger Relief'
        },
        {
            'name': 'Houston Food Bank',
            'contact_person': 'Lisa Anderson',
            'contact_email': 'volunteers@houstonfoodbank.org',
            'contact_phone': '(713) 555-7890',
            'category': 'Hunger Relief'
        },
    ],
    'Animal Shelters': [
        {
            'name': 'Dallas Animal Services',
            'contact_person': 'Emma Rodriguez',
            'contact_email': 'volunteer@dallasanimalservices.org',
            'contact_phone': '(214) 555-2468',
            'category': 'Animal Welfare'
        },
        {
            'name': 'LA Animal Rescue',
            'contact_person': 'James Taylor',
            'contact_email': 'help@laanimalrescue.org',
            'contact_phone': '(310) 555-1357',
            'category': 'Animal Welfare'
        },
        {
            'name': 'NYC Animal Care Centers',
            'contact_person': 'Sophia Lee',
            'contact_email': 'volunteer@nycacc.org',
            'contact_phone': '(212) 555-8024',
            'category': 'Animal Welfare'
        },
        {
            'name': 'PAWS Chicago',
            'contact_person': 'Robert Kim',
            'contact_email': 'volunteers@pawschicago.org',
            'contact_phone': '(773) 555-6891',
            'category': 'Animal Welfare'
        },
        {
            'name': 'Houston Humane Society',
            'contact_person': 'Amanda White',
            'contact_email': 'volunteer@houstonhumane.org',
            'contact_phone': '(713) 555-4826',
            'category': 'Animal Welfare'
        },
    ],
    'Environmental': [
        {
            'name': 'Trinity River Conservancy',
            'contact_person': 'Daniel Green',
            'contact_email': 'getinvolved@trinityriver.org',
            'contact_phone': '(214) 555-7531',
            'category': 'Environment'
        },
        {
            'name': 'LA Conservation Corps',
            'contact_person': 'Maria Garcia',
            'contact_email': 'volunteer@lacorps.org',
            'contact_phone': '(323) 555-9246',
            'category': 'Environment'
        },
        {
            'name': 'NYC Parks Department',
            'contact_person': 'Christopher Brown',
            'contact_email': 'volunteer@nycparks.org',
            'contact_phone': '(212) 555-3579',
            'category': 'Environment'
        },
        {
            'name': 'Friends of the Chicago River',
            'contact_person': 'Jessica Davis',
            'contact_email': 'info@chicagoriver.org',
            'contact_phone': '(312) 555-1593',
            'category': 'Environment'
        },
        {
            'name': 'Buffalo Bayou Partnership',
            'contact_person': 'Kevin Wilson',
            'contact_email': 'volunteer@buffalobayou.org',
            'contact_phone': '(713) 555-7842',
            'category': 'Environment'
        },
    ],
    'Education': [
        {
            'name': 'Big Brothers Big Sisters of Dallas',
            'contact_person': 'Nicole Thompson',
            'contact_email': 'volunteer@bbbs-dallas.org',
            'contact_phone': '(214) 555-9513',
            'category': 'Education'
        },
        {
            'name': 'LA Tutoring Initiative',
            'contact_person': 'Brandon Hall',
            'contact_email': 'tutor@latutoringinitiative.org',
            'contact_phone': '(310) 555-7264',
            'category': 'Education'
        },
        {
            'name': '826NYC Youth Writing',
            'contact_person': 'Rachel Moore',
            'contact_email': 'volunteer@826nyc.org',
            'contact_phone': '(718) 555-4682',
            'category': 'Education'
        },
        {
            'name': 'Chicago Literacy Alliance',
            'contact_person': 'Andrew Jackson',
            'contact_email': 'info@chicagoliteracy.org',
            'contact_phone': '(312) 555-8157',
            'category': 'Education'
        },
        {
            'name': 'Houston Reads',
            'contact_person': 'Samantha Carter',
            'contact_email': 'volunteer@houstonreads.org',
            'contact_phone': '(713) 555-2936',
            'category': 'Education'
        },
    ],
    'Community': [
        {
            'name': 'Habitat for Humanity Dallas',
            'contact_person': 'Timothy Allen',
            'contact_email': 'build@habitatdallas.org',
            'contact_phone': '(214) 555-3197',
            'category': 'Community'
        },
        {
            'name': 'LA Mission',
            'contact_person': 'Patricia Martinez',
            'contact_email': 'volunteer@lamission.org',
            'contact_phone': '(323) 555-8426',
            'category': 'Community'
        },
        {
            'name': 'Coalition for the Homeless NYC',
            'contact_person': 'Gregory Scott',
            'contact_email': 'getinvolved@cfthomeless.org',
            'contact_phone': '(212) 555-7159',
            'category': 'Community'
        },
        {
            'name': 'Chicago Cares',
            'contact_person': 'Michelle Young',
            'contact_email': 'volunteer@chicagocares.org',
            'contact_phone': '(312) 555-4862',
            'category': 'Community'
        },
        {
            'name': 'Houston Habitat',
            'contact_person': 'Steven Lewis',
            'contact_email': 'build@houstonhabitat.org',
            'contact_phone': '(713) 555-6273',
            'category': 'Community'
        },
    ],
}

# Event templates
EVENT_TEMPLATES = [
    {
        'title': 'Weekend Food Sorting',
        'description': 'Help sort and package food donations for families in need. No experience necessary - we provide training and all supplies.',
        'venue': '{org_name} Warehouse',
        'price': 'Free',
    },
    {
        'title': 'Community Meal Service',
        'description': 'Serve hot meals to community members. Shifts available for breakfast, lunch, and dinner service.',
        'venue': '{org_name} Community Kitchen',
        'price': 'Free',
    },
    {
        'title': 'Animal Shelter Care',
        'description': 'Walk dogs, socialize cats, and help with general animal care. Perfect for animal lovers!',
        'venue': '{org_name} Shelter',
        'price': 'Free',
    },
    {
        'title': 'Dog Walking & Playtime',
        'description': 'Take shelter dogs for walks and play sessions. Help them stay active and socialized while awaiting adoption.',
        'venue': '{org_name} Adoption Center',
        'price': 'Free',
    },
    {
        'title': 'Park Cleanup Day',
        'description': 'Join us for a community park cleanup! Gloves, bags, and refreshments provided.',
        'venue': '{city} Community Park',
        'price': 'Free',
    },
    {
        'title': 'Tree Planting Initiative',
        'description': 'Help plant native trees to beautify our city and improve air quality. Tools and training provided.',
        'venue': '{city} Green Space',
        'price': 'Free',
    },
    {
        'title': 'Youth Tutoring Session',
        'description': 'Tutor students in math, reading, or science. Make a direct impact on a child\'s education.',
        'venue': '{org_name} Learning Center',
        'price': 'Free',
    },
    {
        'title': 'After-School Mentoring',
        'description': 'Be a positive role model for youth in our community. Help with homework and life skills.',
        'venue': '{city} Community Center',
        'price': 'Free',
    },
    {
        'title': 'Home Building Day',
        'description': 'Help build affordable housing for families. No construction experience required!',
        'venue': '{city} Build Site',
        'price': 'Free',
    },
    {
        'title': 'Community Garden Work',
        'description': 'Help maintain our community garden. Fresh produce goes to local food banks.',
        'venue': '{city} Community Garden',
        'price': 'Free',
    },
]

# Event images
EVENT_IMAGES = [
    'https://images.unsplash.com/photo-1559027615-cd4628902d4a?w=800',  # volunteers
    'https://images.unsplash.com/photo-1593113598332-cd288d649433?w=800',  # food bank
    'https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=800',  # dogs
    'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800',  # park
    'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800',  # community
    'https://images.unsplash.com/photo-1532629345422-7515f3d16bb6?w=800',  # tutoring
    'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=800',  # building
]


def seed_events():
    """Seed database with volunteer events for 5 major cities."""

    with app.app_context():
        print("🌱 Seeding database with volunteer events...")

        # Clear existing events
        Event.query.delete()
        EventImage.query.delete()
        db.session.commit()
        print("   Cleared existing events")

        events_created = 0

        # For each city
        for city_name, city_data in CITIES.items():
            print(f"\n📍 Creating events for {city_name}, {city_data['state']}...")

            # For each organization type
            for org_type, orgs in ORGANIZATIONS.items():
                # Get organization for this city (use index based on city order)
                city_index = list(CITIES.keys()).index(city_name)
                org = orgs[city_index]

                # Create 2 events per organization (10 events per city)
                for i in range(2):
                    template = random.choice(EVENT_TEMPLATES)

                    # Calculate date (next 30 days)
                    days_ahead = random.randint(1, 30)
                    event_date = datetime.now() + timedelta(days=days_ahead)
                    event_date = event_date.replace(hour=random.choice([9, 10, 13, 14, 15, 18, 19]), minute=0, second=0)

                    # Create event
                    event = Event(
                        id=str(uuid.uuid4()),
                        title=template['title'],
                        description=template['description'].format(
                            org_name=org['name'],
                            city=city_name
                        ),
                        location_city=city_name,
                        location_state=city_data['state'],
                        latitude=city_data['lat'] + random.uniform(-0.1, 0.1),
                        longitude=city_data['lon'] + random.uniform(-0.1, 0.1),
                        date_start=event_date,
                        venue=template['venue'].format(
                            org_name=org['name'],
                            city=city_name
                        ),
                        price=template['price'],
                        category=org['category'],
                        organization=org['name'],
                        contact_person=org['contact_person'],
                        contact_email=org['contact_email'],
                        contact_phone=org['contact_phone'],
                        source='Community Partner',
                        url=f"https://www.{org['name'].lower().replace(' ', '')}.org/volunteer"
                    )

                    db.session.add(event)
                    db.session.flush()  # Get event ID

                    # Add event image
                    image_url = random.choice(EVENT_IMAGES)
                    event_image = EventImage(
                        event_id=event.id,
                        url=image_url,
                        position=0
                    )
                    db.session.add(event_image)

                    events_created += 1
                    print(f"   ✓ {event.title} - {org['name']}")

        db.session.commit()
        print(f"\n✅ Created {events_created} volunteer events across 5 cities!")
        print(f"   Cities: Dallas, Los Angeles, New York, Chicago, Houston")
        print(f"   Organizations: {sum(len(orgs) for orgs in ORGANIZATIONS.values())} total")
        print(f"   All events include contact information for volunteering")


if __name__ == '__main__':
    seed_events()
