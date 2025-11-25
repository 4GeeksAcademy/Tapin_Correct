"""Test script for Google Custom Search categorization."""

from google_search import refine_and_categorize

# Test data simulating Google Custom Search results
test_items = [
    {
        "title": "Animal Shelter Volunteers Needed",
        "snippet": "Help care for dogs and cats at our local animal rescue shelter.",
        "link": "https://example.com/animal-shelter",
    },
    {
        "title": "Tech Coding Workshop for Kids",
        "snippet": "Teach children programming and robotics skills.",
        "link": "https://example.com/tech-workshop",
    },
    {
        "title": "Community Food Bank Seeking Volunteers",
        "snippet": "Help distribute food to families in need at our soup kitchen.",
        "link": "https://example.com/food-bank",
    },
    {
        "title": "Senior Center Activities Coordinator",
        "snippet": "Organize activities and events for elderly residents.",
        "link": "https://example.com/senior-center",
    },
    {
        "title": "Environmental Cleanup Drive",
        "snippet": "Join us for a beach cleanup and conservation effort.",
        "link": "https://example.com/cleanup",
    },
    {
        "title": "Museum Art Exhibition Guide",
        "snippet": "Lead tours at our gallery and cultural heritage exhibitions.",
        "link": "https://example.com/museum",
    },
    {
        "title": "Youth Mentoring Program",
        "snippet": "Mentor and tutor children after school.",
        "link": "https://example.com/mentoring",
    },
    {
        "title": "Health Clinic Medical Assistant",
        "snippet": "Support healthcare providers at our community clinic.",
        "link": "https://example.com/clinic",
    },
]

print("Testing Google Custom Search Categorization")
print("=" * 60)

results = refine_and_categorize(test_items)

for i, result in enumerate(results, 1):
    print(f"\n{i}. {result['title']}")
    print(f"   Category: {result['category']}")
    print(f"   Snippet: {result['snippet'][:60]}...")

print("\n" + "=" * 60)
print("Categorization test complete!")
