"""
Seed database with sample organizations and volunteer events
for major US cities: Houston, Dallas, New York, Los Angeles
"""

import sys
import os
from datetime import datetime, timedelta, timezone
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app, db, Event
import pygeohash as geohash

# Sample organizations with real contact info structure
ORGANIZATIONS = {
    "Houston": [
        {
            "name": "Houston Food Bank",
            "contact_person": "Sarah Martinez",
            "contact_email": "volunteer@houstonfoodbank.org",
            "contact_phone": "(713) 547-8607",
            "events": [
                {
                    "title": "Weekend Food Sorting & Packaging",
                    "description": "Help sort and package food donations for families in need. No experience necessary - training provided. Great for groups and individuals!",
                    "category": "Hunger Relief",
                    "venue": "Houston Food Bank Warehouse",
                    "address": "535 Portwall St, Houston, TX 77029",
                    "lat": 29.7604,
                    "lon": -95.3698,
                },
                {
                    "title": "Mobile Pantry Distribution Helper",
                    "description": "Assist with our mobile food pantry distribution events in underserved neighborhoods. Help unload trucks and distribute food to families.",
                    "category": "Community",
                    "venue": "Moody Park",
                    "address": "3725 Fulton St, Houston, TX 77009",
                    "lat": 29.7964,
                    "lon": -95.3865,
                },
            ],
        },
        {
            "name": "BARC Animal Shelter",
            "contact_person": "Michael Chen",
            "contact_email": "volunteers@houstontx.gov",
            "contact_phone": "(713) 229-7300",
            "events": [
                {
                    "title": "Dog Walking & Socialization",
                    "description": "Spend time with shelter dogs! Walk, play, and socialize with dogs waiting for their forever homes. Must be 18+ or accompanied by adult.",
                    "category": "Animal Welfare",
                    "venue": "BARC Animal Shelter",
                    "address": "3300 Carr St, Houston, TX 77026",
                    "lat": 29.7752,
                    "lon": -95.3435,
                },
                {
                    "title": "Cat Care & Enrichment",
                    "description": "Help care for shelter cats by cleaning, feeding, and providing enrichment activities. Perfect for cat lovers who can't have pets at home!",
                    "category": "Animal Welfare",
                    "venue": "BARC Animal Shelter",
                    "address": "3300 Carr St, Houston, TX 77026",
                    "lat": 29.7752,
                    "lon": -95.3435,
                },
            ],
        },
        {
            "name": "Buffalo Bayou Partnership",
            "contact_person": "Jennifer Rodriguez",
            "contact_email": "info@buffalobayou.org",
            "contact_phone": "(713) 752-0314",
            "events": [
                {
                    "title": "Bayou Clean-Up Day",
                    "description": "Join us for our monthly bayou clean-up! Help remove trash and debris from Houston's beautiful waterways. Gloves and bags provided.",
                    "category": "Environment",
                    "venue": "Buffalo Bayou Park",
                    "address": "1800 Allen Pkwy, Houston, TX 77019",
                    "lat": 29.7633,
                    "lon": -95.3871,
                },
            ],
        },
    ],
    "Dallas": [
        {
            "name": "North Texas Food Bank",
            "contact_person": "David Thompson",
            "contact_email": "volunteer@ntfb.org",
            "contact_phone": "(214) 330-1396",
            "events": [
                {
                    "title": "Food Sorting Volunteer Shift",
                    "description": "Help sort donated food items and prepare them for distribution to local partner agencies. Shifts available morning and afternoon.",
                    "category": "Hunger Relief",
                    "venue": "North Texas Food Bank",
                    "address": "3677 Mapleshade Ln, Plano, TX 75075",
                    "lat": 33.0198,
                    "lon": -96.6989,
                },
                {
                    "title": "Community Garden Volunteer Day",
                    "description": "Help maintain our community garden that provides fresh produce for food bank clients. Learn about urban farming while giving back!",
                    "category": "Environment",
                    "venue": "NTFB Community Garden",
                    "address": "3677 Mapleshade Ln, Plano, TX 75075",
                    "lat": 33.0198,
                    "lon": -96.6989,
                },
            ],
        },
        {
            "name": "Dallas Pets Alive",
            "contact_person": "Amanda Wilson",
            "contact_email": "volunteer@dallaspetsalive.org",
            "contact_phone": "(214) 741-1122",
            "events": [
                {
                    "title": "Weekend Dog Foster Orientation",
                    "description": "Learn how to become a weekend foster for dogs awaiting adoption. Make a huge difference in a dog's life with just a weekend commitment!",
                    "category": "Animal Welfare",
                    "venue": "Dallas Pets Alive Adoption Center",
                    "address": "2719 Manor Way, Dallas, TX 75235",
                    "lat": 32.7767,
                    "lon": -96.7970,
                },
                {
                    "title": "Adoption Event Helper",
                    "description": "Assist at our weekend adoption events. Help set up, answer questions, and support families finding their perfect pet match!",
                    "category": "Animal Welfare",
                    "venue": "Klyde Warren Park",
                    "address": "2012 Woodall Rodgers Fwy, Dallas, TX 75201",
                    "lat": 32.7895,
                    "lon": -96.8017,
                },
            ],
        },
        {
            "name": "Dallas Education Foundation",
            "contact_person": "Robert Garcia",
            "contact_email": "tutors@dallaseducation.org",
            "contact_phone": "(214) 932-2200",
            "events": [
                {
                    "title": "After-School Tutoring Program",
                    "description": "Help elementary students with homework and reading. No teaching experience required - just patience and enthusiasm! Tuesdays and Thursdays 4-6pm.",
                    "category": "Education",
                    "venue": "Oak Cliff Recreation Center",
                    "address": "223 W 10th St, Dallas, TX 75208",
                    "lat": 32.7357,
                    "lon": -96.8197,
                },
            ],
        },
    ],
    "New York": [
        {
            "name": "City Harvest NYC",
            "contact_person": "Emily Johnson",
            "contact_email": "volunteer@cityharvest.org",
            "contact_phone": "(646) 412-0600",
            "events": [
                {
                    "title": "Mobile Market Distribution",
                    "description": "Help distribute fresh fruits and vegetables at our mobile market locations throughout NYC. Great outdoor volunteer opportunity!",
                    "category": "Hunger Relief",
                    "venue": "City Harvest Harlem Market",
                    "address": "425 W 144th St, New York, NY 10031",
                    "lat": 40.8231,
                    "lon": -73.9449,
                },
                {
                    "title": "Food Rescue Volunteer",
                    "description": "Join our team collecting surplus food from restaurants and grocery stores. Must have valid driver's license. Evening shifts available.",
                    "category": "Hunger Relief",
                    "venue": "City Harvest Warehouse",
                    "address": "150 52nd St, Brooklyn, NY 11232",
                    "lat": 40.6537,
                    "lon": -74.0099,
                },
            ],
        },
        {
            "name": "NYC Audubon Society",
            "contact_person": "Patricia Lee",
            "contact_email": "volunteer@nycaudubon.org",
            "contact_phone": "(212) 691-7483",
            "events": [
                {
                    "title": "Central Park Bird Count",
                    "description": "Join our monthly bird count in Central Park! No experience necessary - we provide binoculars and field guides. Perfect for nature lovers!",
                    "category": "Environment",
                    "venue": "Central Park Ramble",
                    "address": "Central Park West & 79th St, New York, NY 10024",
                    "lat": 40.7769,
                    "lon": -73.9681,
                },
                {
                    "title": "Harbor Cleanup & Wildlife Monitoring",
                    "description": "Help clean up harbor areas while learning about local wildlife. Kayaking experience helpful but not required!",
                    "category": "Environment",
                    "venue": "Hudson River Park",
                    "address": "Pier 40, New York, NY 10014",
                    "lat": 40.7308,
                    "lon": -74.0092,
                },
            ],
        },
        {
            "name": "New York Cares",
            "contact_person": "Marcus Brown",
            "contact_email": "info@newyorkcares.org",
            "contact_phone": "(212) 228-5000",
            "events": [
                {
                    "title": "Coat Drive Collection Event",
                    "description": "Help collect, sort, and distribute winter coats to New Yorkers in need. Indoor volunteer opportunity, all ages welcome!",
                    "category": "Community",
                    "venue": "New York Cares HQ",
                    "address": "214 W 29th St, New York, NY 10001",
                    "lat": 40.7478,
                    "lon": -73.9937,
                },
                {
                    "title": "Community Garden Beautification",
                    "description": "Join us to plant flowers, build garden beds, and create green spaces in underserved neighborhoods. No gardening experience needed!",
                    "category": "Environment",
                    "venue": "East Village Community Garden",
                    "address": "E 6th St & Avenue B, New York, NY 10009",
                    "lat": 40.7248,
                    "lon": -73.9810,
                },
            ],
        },
    ],
    "Los Angeles": [
        {
            "name": "Los Angeles Regional Food Bank",
            "contact_person": "Carlos Mendez",
            "contact_email": "volunteer@lafoodbank.org",
            "contact_phone": "(323) 234-3030",
            "events": [
                {
                    "title": "Warehouse Food Sorting",
                    "description": "Sort and package food for distribution to LA families. Great team-building activity! Shifts available daily, morning and afternoon.",
                    "category": "Hunger Relief",
                    "venue": "LA Food Bank Warehouse",
                    "address": "1734 E 41st St, Los Angeles, CA 90058",
                    "lat": 34.0051,
                    "lon": -118.2437,
                },
                {
                    "title": "Mobile Food Pantry Helper",
                    "description": "Assist with mobile food distributions at parks and community centers across LA County. Outdoor work, very rewarding!",
                    "category": "Community",
                    "venue": "Various LA Locations",
                    "address": "MacArthur Park, Los Angeles, CA 90057",
                    "lat": 34.0579,
                    "lon": -118.2774,
                },
            ],
        },
        {
            "name": "Best Friends Animal Society LA",
            "contact_person": "Jessica Kim",
            "contact_email": "volunteer@bestfriends.org",
            "contact_phone": "(818) 643-3989",
            "events": [
                {
                    "title": "Weekend Dog Playgroups",
                    "description": "Help socialize shelter dogs through supervised playgroups. Fun, active volunteer work perfect for dog lovers! Saturdays and Sundays.",
                    "category": "Animal Welfare",
                    "venue": "Best Friends Lifesaving Center",
                    "address": "1845 Pontius Ave, Los Angeles, CA 90025",
                    "lat": 34.0522,
                    "lon": -118.4437,
                },
                {
                    "title": "Cat Comfort & Care",
                    "description": "Spend quality time with shelter cats - grooming, playing, and providing TLC. Great for all ages (12+ with adult).",
                    "category": "Animal Welfare",
                    "venue": "Best Friends Adoption Center",
                    "address": "1845 Pontius Ave, Los Angeles, CA 90025",
                    "lat": 34.0522,
                    "lon": -118.4437,
                },
            ],
        },
        {
            "name": "TreePeople LA",
            "contact_person": "Rachel Green",
            "contact_email": "volunteer@treepeople.org",
            "contact_phone": "(818) 753-4600",
            "events": [
                {
                    "title": "Community Tree Planting Day",
                    "description": "Help plant trees throughout LA to combat climate change and beautify neighborhoods. All tools and training provided. Wear sturdy shoes!",
                    "category": "Environment",
                    "venue": "Coldwater Canyon Park",
                    "address": "12601 Mulholland Dr, Beverly Hills, CA 90210",
                    "lat": 34.1184,
                    "lon": -118.4109,
                },
                {
                    "title": "Trail Maintenance & Restoration",
                    "description": "Help maintain hiking trails and restore native plant habitats in the Santa Monica Mountains. Moderate physical activity required.",
                    "category": "Environment",
                    "venue": "Franklin Canyon Park",
                    "address": "2600 Franklin Canyon Dr, Beverly Hills, CA 90210",
                    "lat": 34.1168,
                    "lon": -118.4109,
                },
            ],
        },
        {
            "name": "LA Works",
            "contact_person": "Daniel Park",
            "contact_email": "info@laworks.com",
            "contact_phone": "(323) 419-1222",
            "events": [
                {
                    "title": "School Beautification Project",
                    "description": "Help paint murals, build playground equipment, and beautify public schools. Perfect for corporate groups and individuals!",
                    "category": "Education",
                    "venue": "Various LAUSD Schools",
                    "address": "Downtown LA Schools",
                    "lat": 34.0407,
                    "lon": -118.2468,
                },
                {
                    "title": "Homeless Outreach Street Team",
                    "description": "Join our street team distributing care packages, information about services, and showing compassion to unhoused neighbors.",
                    "category": "Community",
                    "venue": "Skid Row",
                    "address": "San Julian St & 5th St, Los Angeles, CA 90013",
                    "lat": 34.0454,
                    "lon": -118.2465,
                },
            ],
        },
    ],
}


def create_sample_events():
    """Create sample volunteer events for major cities"""

    with app.app_context():
        print("🌟 Creating sample organization events...")

        cities = {
            "Houston": {"city": "Houston", "state": "TX"},
            "Dallas": {"city": "Dallas", "state": "TX"},
            "New York": {"city": "New York", "state": "NY"},
            "Los Angeles": {"city": "Los Angeles", "state": "CA"},
        }

        events_created = 0

        for city_name, orgs in ORGANIZATIONS.items():
            city_info = cities[city_name]
            print(f"\n📍 {city_name}, {city_info['state']}")

            for org in orgs:
                org_name = org["name"]
                contact_person = org["contact_person"]
                contact_email = org["contact_email"]
                contact_phone = org["contact_phone"]

                print(f"  🏢 {org_name} - Contact: {contact_person}")

                for event_data in org["events"]:
                    # Check if event already exists
                    existing = Event.query.filter_by(
                        title=event_data["title"], organization=org_name
                    ).first()

                    if existing:
                        print(f"    ⏭️  Skipping (exists): {event_data['title']}")
                        continue

                    # Create event with dates (this weekend)
                    today = datetime.now(timezone.utc)
                    # Next Saturday
                    days_until_saturday = (5 - today.weekday()) % 7
                    if days_until_saturday == 0:
                        days_until_saturday = 7
                    event_date = today + timedelta(days=days_until_saturday)
                    event_date = event_date.replace(
                        hour=10, minute=0, second=0, microsecond=0
                    )

                    # Generate geohash
                    lat = event_data["lat"]
                    lon = event_data["lon"]
                    gh_4 = geohash.encode(lat, lon, precision=4)
                    gh_6 = geohash.encode(lat, lon, precision=6)

                    event = Event(
                        id=str(uuid.uuid4()),
                        title=event_data["title"],
                        organization=org_name,
                        description=event_data["description"],
                        date_start=event_date,
                        location_address=event_data["address"],
                        location_city=city_info["city"],
                        location_state=city_info["state"],
                        latitude=lat,
                        longitude=lon,
                        geohash_4=gh_4,
                        geohash_6=gh_6,
                        category=event_data["category"],
                        venue=event_data["venue"],
                        price="Free",
                        source="Volunteer Platform",
                        contact_person=contact_person,
                        contact_email=contact_email,
                        contact_phone=contact_phone,
                        url=f"https://example.com/volunteer/{org_name.lower().replace(' ', '-')}",
                        image_url=f"https://picsum.photos/seed/{uuid.uuid4()}/800/600",
                    )

                    db.session.add(event)
                    events_created += 1
                    print(f"    ✅ Created: {event_data['title']}")

        db.session.commit()
        print(f"\n🎉 Successfully created {events_created} sample volunteer events!")
        print(
            f"\n💡 Tip: These events have contact info, so the 'Volunteer' button will appear!"
        )


if __name__ == "__main__":
    create_sample_events()
