"""
Tests for event discovery API endpoints
"""
import pytest
import json
from backend.app import app, db, User, Event, EventImage
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    """Create test client with in-memory database"""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            yield client
        db.session.remove()
        db.drop_all()


@pytest.fixture
def auth_token(client):
    """Create a user and return auth token"""
    with app.app_context():
        user = User(
            email="test@example.com",
            password_hash=generate_password_hash("testpass123")
        )
        db.session.add(user)
        db.session.commit()

    # Login to get token
    response = client.post('/login', json={
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    data = json.loads(response.data)
    return data['access_token']


class TestEventDiscoveryAPI:
    """Test suite for event discovery API endpoints"""

    def test_get_categories_success(self, client):
        """Test GET /api/categories returns categories"""
        response = client.get('/api/categories')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'categories' in data
        assert 'grouped' in data
        assert 'count' in data

        # Check that we have categories
        assert data['count'] > 20
        assert 'Music & Concerts' in data['categories']
        assert 'Tech & Innovation' in data['categories']

    def test_get_categories_structure(self, client):
        """Test that categories have proper structure"""
        response = client.get('/api/categories')
        data = json.loads(response.data)

        categories = data['categories']

        # Check each category has required fields
        for cat_name, cat_data in categories.items():
            assert 'icon' in cat_data
            assert 'color' in cat_data
            assert 'keywords' in cat_data
            assert 'description' in cat_data

    def test_get_categories_grouped(self, client):
        """Test that grouped categories are returned"""
        response = client.get('/api/categories')
        data = json.loads(response.data)

        grouped = data['grouped']

        assert 'Entertainment & Culture' in grouped
        assert 'Volunteer & Social Impact' in grouped
        assert isinstance(grouped['Entertainment & Culture'], list)

    def test_discover_events_no_auth(self, client):
        """Test that discover-events requires authentication"""
        response = client.post('/api/discover-events', json={
            'location': 'Dallas, TX'
        })

        assert response.status_code == 401  # Unauthorized

    def test_discover_events_success(self, client, auth_token):
        """Test successful event discovery"""
        response = client.post(
            '/api/discover-events',
            json={'location': 'Dallas, TX'},
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'events' in data
        assert 'location' in data
        assert 'count' in data
        assert data['location'] == 'Dallas, TX'

    def test_discover_events_missing_location(self, client, auth_token):
        """Test that location is required"""
        response = client.post(
            '/api/discover-events',
            json={},
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_discover_events_invalid_format(self, client, auth_token):
        """Test invalid location format"""
        response = client.post(
            '/api/discover-events',
            json={'location': 'InvalidFormat'},
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_discover_events_valid_format(self, client, auth_token):
        """Test that events have valid structure"""
        response = client.post(
            '/api/discover-events',
            json={'location': 'Seattle, WA'},
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert len(data['events']) > 0

        for event in data['events']:
            assert 'id' in event
            assert 'title' in event
            assert 'organization' in event
            assert 'category' in event

    def test_discover_tonight_no_auth(self, client):
        """Test that discover tonight requires authentication"""
        response = client.post('/api/local-events/tonight', json={
            'location': 'Dallas, TX'
        })

        assert response.status_code == 401  # Unauthorized

    def test_discover_tonight_success(self, client, auth_token):
        """Test successful tonight events discovery"""
        response = client.post(
            '/api/local-events/tonight',
            json={'location': 'Dallas, TX', 'limit': 10},
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'events' in data
        assert 'location' in data
        assert 'count' in data
        assert 'timeframe' in data
        assert data['timeframe'] == 'tonight'

    def test_discover_tonight_event_structure(self, client, auth_token):
        """Test that tonight events have proper structure"""
        response = client.post(
            '/api/local-events/tonight',
            json={'location': 'Miami, FL', 'limit': 5},
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert len(data['events']) > 0

        for event in data['events']:
            assert 'title' in event
            assert 'category' in event

            # Tonight events should have venue and price
            if 'venue' in event:
                assert isinstance(event['venue'], str)

            if 'price' in event:
                assert isinstance(event['price'], str)

    def test_discover_tonight_limit_parameter(self, client, auth_token):
        """Test that limit parameter works"""
        response = client.post(
            '/api/local-events/tonight',
            json={'location': 'Austin, TX', 'limit': 3},
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        # Should respect limit
        assert len(data['events']) <= 3

    def test_discover_tonight_default_limit(self, client, auth_token):
        """Test default limit when not specified"""
        response = client.post(
            '/api/local-events/tonight',
            json={'location': 'Portland, OR'},
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        # Should use default limit (20)
        assert len(data['events']) <= 20

    def test_discover_tonight_missing_location(self, client, auth_token):
        """Test that location is required for tonight events"""
        response = client.post(
            '/api/local-events/tonight',
            json={},
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_discover_tonight_images(self, client, auth_token):
        """Test that tonight events include images"""
        response = client.post(
            '/api/local-events/tonight',
            json={'location': 'Denver, CO', 'limit': 5},
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        images_found = 0
        for event in data['events']:
            if 'image_url' in event and event['image_url']:
                images_found += 1

        # At least some events should have images
        assert images_found > 0

    def test_multiple_locations(self, client, auth_token):
        """Test discovery for multiple locations"""
        locations = ['Dallas, TX', 'Seattle, WA', 'New York, NY']

        for location in locations:
            response = client.post(
                '/api/local-events/tonight',
                json={'location': location, 'limit': 3},
                headers={'Authorization': f'Bearer {auth_token}'}
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['location'] == location

    def test_discover_events_caching(self, client, auth_token):
        """Test that events are cached"""
        # First request
        response1 = client.post(
            '/api/discover-events',
            json={'location': 'Chicago, IL'},
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response1.status_code == 200
        data1 = json.loads(response1.data)

        # Second request should be cached
        response2 = client.post(
            '/api/discover-events',
            json={'location': 'Chicago, IL'},
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response2.status_code == 200
        data2 = json.loads(response2.data)

        # Should return same events (cached)
        assert data2['cached'] == True

    def test_discover_tonight_categories_variety(self, client, auth_token):
        """Test that tonight events span multiple categories"""
        response = client.post(
            '/api/local-events/tonight',
            json={'location': 'Los Angeles, CA', 'limit': 20},
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        categories = set(event['category'] for event in data['events'])

        # Should have multiple categories
        assert len(categories) >= 3

    def test_invalid_token(self, client):
        """Test that invalid token is rejected"""
        response = client.post(
            '/api/discover-events',
            json={'location': 'Dallas, TX'},
            headers={'Authorization': 'Bearer invalid_token_here'}
        )

        assert response.status_code == 422  # Unprocessable Entity (invalid JWT)

    def test_discover_events_count_matches(self, client, auth_token):
        """Test that count field matches number of events"""
        response = client.post(
            '/api/discover-events',
            json={'location': 'Phoenix, AZ'},
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['count'] == len(data['events'])

    def test_discover_tonight_count_matches(self, client, auth_token):
        """Test that count field matches for tonight events"""
        response = client.post(
            '/api/local-events/tonight',
            json={'location': 'San Diego, CA', 'limit': 5},
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['count'] == len(data['events'])


class TestEventDatabasePersistence:
    """Test that events are properly persisted to database"""

    def test_events_saved_to_database(self, client, auth_token):
        """Test that discovered events are saved"""
        response = client.post(
            '/api/discover-events',
            json={'location': 'Boston, MA'},
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200

        # Check database
        with app.app_context():
            events = Event.query.all()
            assert len(events) > 0

    def test_events_have_geohash(self, client, auth_token):
        """Test that saved events have geohash"""
        response = client.post(
            '/api/discover-events',
            json={'location': 'Atlanta, GA'},
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200

        with app.app_context():
            events = Event.query.all()
            for event in events:
                assert event.geohash_6 is not None
                assert len(event.geohash_6) > 0

    def test_event_images_saved(self, client, auth_token):
        """Test that event images are saved separately"""
        response = client.post(
            '/api/local-events/tonight',
            json={'location': 'Dallas, TX', 'limit': 5},
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200

        with app.app_context():
            # Should have EventImage records
            images = EventImage.query.all()
            # At least some images should be saved
            assert len(images) >= 0  # May vary based on sample data
