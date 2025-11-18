"""
Unified event category system for Tapin

Covers all types of events: volunteer opportunities and local events
"""

# Master category list with icons, colors, and keywords
EVENT_CATEGORIES = {
    # Volunteer & Social Impact
    "Volunteer": {
        "icon": "🤝",
        "color": "#4CAF50",
        "keywords": [
            "volunteer",
            "help",
            "serve",
            "nonprofit",
            "charity",
            "community service",
        ],
        "description": "Give back to your community through volunteer opportunities",
    },
    "Hunger Relief": {
        "icon": "🍎",
        "color": "#4CAF50",
        "keywords": ["food bank", "hunger", "meal", "food distribution", "feeding"],
        "description": "Help fight hunger and food insecurity",
    },
    "Animal Welfare": {
        "icon": "🐕",
        "color": "#FF9800",
        "keywords": ["animal", "shelter", "rescue", "pets", "wildlife", "dog", "cat"],
        "description": "Support animals and wildlife conservation",
    },
    "Environment": {
        "icon": "🌱",
        "color": "#2196F3",
        "keywords": [
            "environment",
            "cleanup",
            "sustainability",
            "recycling",
            "tree planting",
            "nature",
        ],
        "description": "Protect our planet through environmental action",
    },
    "Education": {
        "icon": "📚",
        "color": "#9C27B0",
        "keywords": [
            "education",
            "tutoring",
            "mentoring",
            "teaching",
            "workshop",
            "class",
            "seminar",
            "training",
        ],
        "description": "Learn new skills or help others learn",
    },
    "Seniors": {
        "icon": "👴",
        "color": "#F44336",
        "keywords": ["senior", "elderly", "aging", "retirement", "companion"],
        "description": "Support and companionship for seniors",
    },
    # Entertainment & Culture
    "Music & Concerts": {
        "icon": "🎵",
        "color": "#673AB7",
        "keywords": [
            "concert",
            "live music",
            "band",
            "dj",
            "festival",
            "performance",
            "jazz",
            "rock",
        ],
        "description": "Live music performances and concerts",
    },
    "Comedy": {
        "icon": "😄",
        "color": "#FF5722",
        "keywords": ["comedy", "stand up", "improv", "comedy show", "laughs"],
        "description": "Stand-up comedy and improv shows",
    },
    "Arts & Theater": {
        "icon": "🎭",
        "color": "#E91E63",
        "keywords": [
            "art",
            "gallery",
            "theater",
            "performance",
            "exhibit",
            "museum",
            "dance",
        ],
        "description": "Visual arts, theater, and cultural performances",
    },
    "Film & Media": {
        "icon": "🎬",
        "color": "#3F51B5",
        "keywords": ["movie", "film", "screening", "cinema", "documentary"],
        "description": "Movie screenings and film festivals",
    },
    "Books & Literature": {
        "icon": "📖",
        "color": "#795548",
        "keywords": ["book", "author", "reading", "literature", "poetry", "writing"],
        "description": "Book clubs, author talks, and literary events",
    },
    # Food & Drink
    "Food & Dining": {
        "icon": "🍽️",
        "color": "#FF9800",
        "keywords": [
            "restaurant",
            "food",
            "dining",
            "tasting",
            "culinary",
            "chef",
            "cooking",
        ],
        "description": "Food festivals, tastings, and culinary experiences",
    },
    "Wine & Beer": {
        "icon": "🍺",
        "color": "#FFC107",
        "keywords": ["wine", "beer", "brewery", "winery", "craft beer", "tasting"],
        "description": "Wine tastings and craft beer events",
    },
    # Active & Sports
    "Sports": {
        "icon": "⚽",
        "color": "#4CAF50",
        "keywords": [
            "sports",
            "game",
            "match",
            "tournament",
            "athletic",
            "basketball",
            "soccer",
        ],
        "description": "Sports games, tournaments, and athletic events",
    },
    "Fitness": {
        "icon": "💪",
        "color": "#8BC34A",
        "keywords": ["yoga", "workout", "fitness", "running", "cycling", "exercise"],
        "description": "Yoga, fitness classes, and active lifestyle events",
    },
    "Outdoor": {
        "icon": "🏔️",
        "color": "#009688",
        "keywords": ["hiking", "outdoor", "nature", "park", "adventure", "camping"],
        "description": "Outdoor adventures and nature activities",
    },
    # Social & Professional
    "Nightlife": {
        "icon": "🌃",
        "color": "#673AB7",
        "keywords": ["club", "bar", "dance", "party", "happy hour", "trivia"],
        "description": "Nightlife, bars, and social gatherings",
    },
    "Networking": {
        "icon": "👥",
        "color": "#2196F3",
        "keywords": ["networking", "business", "professional", "meetup", "career"],
        "description": "Professional networking and business events",
    },
    "Tech & Innovation": {
        "icon": "💻",
        "color": "#00BCD4",
        "keywords": [
            "tech",
            "startup",
            "innovation",
            "hackathon",
            "coding",
            "ai",
            "ml",
        ],
        "description": "Technology meetups and innovation events",
    },
    # Family & Community
    "Family": {
        "icon": "👨‍👩‍👧‍👦",
        "color": "#FF9800",
        "keywords": ["family", "kids", "children", "family-friendly", "parents"],
        "description": "Family-friendly activities for all ages",
    },
    "Community": {
        "icon": "🏘️",
        "color": "#607D8B",
        "keywords": ["community", "local", "neighborhood", "town hall", "civic"],
        "description": "Community gatherings and local events",
    },
    "Markets & Fairs": {
        "icon": "🛍️",
        "color": "#FF5722",
        "keywords": ["market", "fair", "bazaar", "festival", "vendor", "craft"],
        "description": "Markets, fairs, and craft shows",
    },
}


# Reverse mapping: keyword -> category
KEYWORD_TO_CATEGORY = {}
for category, data in EVENT_CATEGORIES.items():
    for keyword in data["keywords"]:
        KEYWORD_TO_CATEGORY[keyword.lower()] = category


def categorize_event(title: str, description: str = "") -> str:
    """
    Auto-categorize event based on title and description.

    Args:
        title: Event title
        description: Event description

    Returns:
        Category name from EVENT_CATEGORIES
    """
    text = f"{title} {description}".lower()

    # Score each category
    category_scores = {}
    for category, data in EVENT_CATEGORIES.items():
        score = sum(1 for keyword in data["keywords"] if keyword in text)
        if score > 0:
            category_scores[category] = score

    if category_scores:
        # Return category with highest score
        return max(category_scores, key=category_scores.get)

    return "Community"  # Default category


def get_category_info(category: str) -> dict:
    """
    Get category metadata (icon, color, description).

    Args:
        category: Category name

    Returns:
        Dictionary with icon, color, description
    """
    return EVENT_CATEGORIES.get(
        category,
        {
            "icon": "📅",
            "color": "#607D8B",
            "description": "Community events",
        },
    )


def get_all_categories() -> list:
    """
    Get list of all category names.

    Returns:
        List of category names
    """
    return list(EVENT_CATEGORIES.keys())


def get_categories_by_type() -> dict:
    """
    Get categories grouped by type.

    Returns:
        Dictionary with category groups
    """
    return {
        "Volunteer & Social Impact": [
            "Volunteer",
            "Hunger Relief",
            "Animal Welfare",
            "Environment",
            "Education",
            "Seniors",
        ],
        "Entertainment & Culture": [
            "Music & Concerts",
            "Comedy",
            "Arts & Theater",
            "Film & Media",
            "Books & Literature",
        ],
        "Food & Drink": [
            "Food & Dining",
            "Wine & Beer",
        ],
        "Active & Sports": [
            "Sports",
            "Fitness",
            "Outdoor",
        ],
        "Social & Professional": [
            "Nightlife",
            "Networking",
            "Tech & Innovation",
        ],
        "Family & Community": [
            "Family",
            "Community",
            "Markets & Fairs",
        ],
    }
