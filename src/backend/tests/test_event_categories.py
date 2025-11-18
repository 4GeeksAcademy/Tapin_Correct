"""
Tests for event_categories.py - Unified event category system
"""
import pytest
from backend.event_discovery.event_categories import (
    EVENT_CATEGORIES,
    categorize_event,
    get_category_info,
    get_all_categories,
    get_categories_by_type,
)


class TestEventCategories:
    """Test suite for event category system"""

    def test_event_categories_exist(self):
        """Test that EVENT_CATEGORIES is properly defined"""
        assert EVENT_CATEGORIES is not None
        assert isinstance(EVENT_CATEGORIES, dict)
        assert len(EVENT_CATEGORIES) > 0

    def test_all_categories_have_required_fields(self):
        """Test that all categories have icon, color, keywords, description"""
        required_fields = ['icon', 'color', 'keywords', 'description']

        for category_name, category_data in EVENT_CATEGORIES.items():
            assert isinstance(category_data, dict), f"{category_name} is not a dict"

            for field in required_fields:
                assert field in category_data, f"{category_name} missing {field}"

            # Validate field types
            assert isinstance(category_data['icon'], str)
            assert isinstance(category_data['color'], str)
            assert isinstance(category_data['keywords'], list)
            assert isinstance(category_data['description'], str)

            # Validate color format (hex color)
            assert category_data['color'].startswith('#')
            assert len(category_data['color']) == 7

            # Keywords should be non-empty
            assert len(category_data['keywords']) > 0

    def test_categorize_event_music(self):
        """Test categorization of music events"""
        result = categorize_event(
            "Live Jazz Concert Tonight",
            "Join us for an amazing jazz performance"
        )
        assert result == "Music & Concerts"

    def test_categorize_event_food(self):
        """Test categorization of food events"""
        result = categorize_event(
            "Restaurant Food Tasting Event",
            "Sample delicious cuisine and dining from local restaurants"
        )
        assert result == "Food & Dining"

    def test_categorize_event_tech(self):
        """Test categorization of tech events"""
        result = categorize_event(
            "AI/ML Developer Meetup",
            "Discuss latest trends in artificial intelligence and machine learning"
        )
        assert result == "Tech & Innovation"

    def test_categorize_event_volunteer(self):
        """Test categorization of volunteer events"""
        result = categorize_event(
            "Community Cleanup Day",
            "Help us clean up local parks and streets"
        )
        # Could be Environment or Community
        assert result in ["Environment", "Community", "Volunteer"]

    def test_categorize_event_default(self):
        """Test categorization with no matching keywords"""
        result = categorize_event(
            "Random Event",
            "This is a very generic event"
        )
        assert result == "Community"  # Default category

    def test_categorize_event_multiple_keywords(self):
        """Test categorization with multiple keyword matches"""
        result = categorize_event(
            "Comedy Night at Local Bar",
            "Stand up comedy show with drinks and dancing"
        )
        # Should match strongest category
        assert result in ["Comedy", "Nightlife"]

    def test_get_category_info_valid(self):
        """Test getting metadata for valid category"""
        info = get_category_info("Music & Concerts")

        assert 'icon' in info
        assert 'color' in info
        assert 'description' in info
        assert info['icon'] == "🎵"
        assert info['color'] == "#673AB7"

    def test_get_category_info_invalid(self):
        """Test getting metadata for invalid category"""
        info = get_category_info("NonExistent Category")

        # Should return default
        assert 'icon' in info
        assert 'color' in info
        assert 'description' in info
        assert info['icon'] == "📅"

    def test_get_all_categories(self):
        """Test getting list of all categories"""
        categories = get_all_categories()

        assert isinstance(categories, list)
        assert len(categories) > 20  # We have 23 categories
        assert "Music & Concerts" in categories
        assert "Tech & Innovation" in categories
        assert "Volunteer" in categories

    def test_get_categories_by_type(self):
        """Test getting categories grouped by type"""
        grouped = get_categories_by_type()

        assert isinstance(grouped, dict)
        assert "Entertainment & Culture" in grouped
        assert "Volunteer & Social Impact" in grouped
        assert "Food & Drink" in grouped

        # Check that each group has categories
        assert len(grouped["Entertainment & Culture"]) > 0
        assert "Music & Concerts" in grouped["Entertainment & Culture"]

        # Check volunteer group
        assert "Volunteer" in grouped["Volunteer & Social Impact"]
        assert "Hunger Relief" in grouped["Volunteer & Social Impact"]

    def test_category_count(self):
        """Test that we have the expected number of categories"""
        categories = get_all_categories()
        assert len(categories) == 22  # Current category count

    def test_no_duplicate_categories(self):
        """Test that there are no duplicate category names"""
        categories = get_all_categories()
        assert len(categories) == len(set(categories))

    def test_all_categories_in_groups(self):
        """Test that all categories are included in groups"""
        all_cats = set(get_all_categories())
        grouped = get_categories_by_type()

        grouped_cats = set()
        for group_categories in grouped.values():
            grouped_cats.update(group_categories)

        assert all_cats == grouped_cats

    def test_keyword_uniqueness(self):
        """Test that keywords are meaningful and not too generic"""
        for category_name, category_data in EVENT_CATEGORIES.items():
            keywords = category_data['keywords']

            # Each category should have unique keywords
            assert len(keywords) == len(set(keywords))

            # Keywords should be lowercase
            for keyword in keywords:
                assert keyword.islower() or ' ' in keyword

    def test_color_variety(self):
        """Test that categories have varied colors"""
        colors = [cat['color'] for cat in EVENT_CATEGORIES.values()]

        # Should have at least 15 unique colors for 23 categories
        unique_colors = set(colors)
        assert len(unique_colors) >= 15

    def test_description_quality(self):
        """Test that all descriptions are meaningful"""
        for category_name, category_data in EVENT_CATEGORIES.items():
            description = category_data['description']

            # Description should be substantial
            assert len(description) > 20
            assert description[0].isupper()  # Should start with capital
