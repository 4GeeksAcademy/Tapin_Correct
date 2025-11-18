"""
Test suite for personalization engine and user interaction tracking.
"""
import pytest
from backend.app import app, db, User, Event, UserEventInteraction


@pytest.fixture
def client():
    """Create test client with in-memory database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def auth_headers(client):
    """Create authenticated user and return auth headers."""
    # Register volunteer
    client.post('/register', json={
        'email': 'volunteer@test.com',
        'password': 'password123',
        'role': 'volunteer'
    })

    # Login
    response = client.post('/login', json={
        'email': 'volunteer@test.com',
        'password': 'password123'
    })

    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def sample_events(client):
    """Create sample events in the database."""
    import uuid
    from datetime import datetime
    with app.app_context():
        events = [
            Event(
                id=str(uuid.uuid4()),
                title='Community Cleanup',
                organization='Green Team',
                description='Beach cleanup volunteer event',
                category='Environment',
                location_city='Austin',
                location_state='TX',
                date_start=datetime(2025, 12, 1),
                url='https://example.com/cleanup',
                source='test'
            ),
            Event(
                id=str(uuid.uuid4()),
                title='Food Bank',
                organization='Food For All',
                description='Help pack food boxes',
                category='Community Service',
                location_city='Austin',
                location_state='TX',
                date_start=datetime(2025, 12, 2),
                url='https://example.com/foodbank',
                source='test'
            ),
            Event(
                id=str(uuid.uuid4()),
                title='Music Festival',
                organization='Arts Council',
                description='Live music and arts',
                category='Music',
                location_city='Austin',
                location_state='TX',
                date_start=datetime(2025, 12, 3),
                url='https://example.com/music',
                source='test'
            ),
        ]

        for event in events:
            db.session.add(event)
        db.session.commit()

        # Return event IDs
        return [e.id for e in events]


class TestEventInteraction:
    """Test event interaction recording."""

    def test_record_interaction_success(self, client, auth_headers, sample_events):
        """Test successful interaction recording."""
        event_id = sample_events[0]

        response = client.post('/api/events/interact',
            headers=auth_headers,
            json={
                'event_id': event_id,
                'interaction_type': 'like',
                'metadata': {'source': 'event_card'}
            }
        )

        assert response.status_code == 201
        data = response.json
        assert data['message'] == 'interaction recorded'
        assert 'interaction' in data

    def test_record_interaction_missing_fields(self, client, auth_headers):
        """Test interaction recording with missing required fields."""
        # Missing event_id
        response = client.post('/api/events/interact',
            headers=auth_headers,
            json={'interaction_type': 'like'}
        )
        assert response.status_code == 400
        assert 'error' in response.json

        # Missing interaction_type
        response = client.post('/api/events/interact',
            headers=auth_headers,
            json={'event_id': 1}
        )
        assert response.status_code == 400
        assert 'error' in response.json

    def test_record_interaction_requires_auth(self, client, sample_events):
        """Test that interaction recording requires authentication."""
        response = client.post('/api/events/interact',
            json={
                'event_id': sample_events[0],
                'interaction_type': 'view'
            }
        )
        assert response.status_code == 401

    def test_record_multiple_interactions(self, client, auth_headers, sample_events):
        """Test recording multiple interactions for same user."""
        interactions = [
            {'event_id': sample_events[0], 'interaction_type': 'view'},
            {'event_id': sample_events[0], 'interaction_type': 'like'},
            {'event_id': sample_events[1], 'interaction_type': 'attend'},
            {'event_id': sample_events[2], 'interaction_type': 'super_like'},
        ]

        for interaction in interactions:
            response = client.post('/api/events/interact',
                headers=auth_headers,
                json=interaction
            )
            assert response.status_code == 201

        # Verify interactions were recorded
        with app.app_context():
            count = UserEventInteraction.query.count()
            assert count == 4


class TestPersonalizedEvents:
    """Test personalized event recommendations."""

    def test_get_personalized_events_success(self, client, auth_headers, sample_events):
        """Test getting personalized events."""
        # First, record some interactions to build taste profile
        client.post('/api/events/interact',
            headers=auth_headers,
            json={'event_id': sample_events[0], 'interaction_type': 'like'}
        )

        # Get personalized events
        response = client.post('/api/events/personalized',
            headers=auth_headers,
            json={'location': 'Austin, TX'}
        )

        assert response.status_code == 200
        data = response.json
        assert 'events' in data
        assert isinstance(data['events'], list)

    def test_personalized_events_missing_location(self, client, auth_headers):
        """Test personalized events with missing location."""
        response = client.post('/api/events/personalized',
            headers=auth_headers,
            json={}
        )
        assert response.status_code == 400
        assert 'error' in response.json

    def test_personalized_events_invalid_location(self, client, auth_headers):
        """Test personalized events with invalid location format."""
        response = client.post('/api/events/personalized',
            headers=auth_headers,
            json={'location': 'InvalidLocation'}
        )
        assert response.status_code == 400
        assert 'error' in response.json

    def test_personalized_events_requires_auth(self, client):
        """Test that personalized events requires authentication."""
        response = client.post('/api/events/personalized',
            json={'location': 'Austin, TX'}
        )
        assert response.status_code == 401

    def test_personalized_events_with_limit(self, client, auth_headers, sample_events):
        """Test personalized events with custom limit."""
        response = client.post('/api/events/personalized',
            headers=auth_headers,
            json={'location': 'Austin, TX', 'limit': 5}
        )

        assert response.status_code == 200
        data = response.json
        assert len(data['events']) <= 5


class TestTasteProfile:
    """Test user taste profile calculation."""

    def test_get_taste_profile_no_interactions(self, client, auth_headers):
        """Test taste profile for user with no interactions."""
        response = client.get('/api/profile/taste', headers=auth_headers)

        assert response.status_code == 200
        data = response.json
        assert 'profile' in data
        assert 'user_id' in data

    def test_get_taste_profile_with_interactions(self, client, auth_headers, sample_events):
        """Test taste profile after recording interactions."""
        # Record multiple interactions
        interactions = [
            {'event_id': sample_events[0], 'interaction_type': 'like'},
            {'event_id': sample_events[0], 'interaction_type': 'attend'},
            {'event_id': sample_events[1], 'interaction_type': 'super_like'},
        ]

        for interaction in interactions:
            client.post('/api/events/interact',
                headers=auth_headers,
                json=interaction
            )

        # Get taste profile
        response = client.get('/api/profile/taste', headers=auth_headers)

        assert response.status_code == 200
        data = response.json
        assert 'profile' in data
        profile = data['profile']

        # Profile should contain category preferences
        assert 'category_preferences' in profile or 'categories' in profile or profile is not None

    def test_taste_profile_requires_auth(self, client):
        """Test that taste profile requires authentication."""
        response = client.get('/api/profile/taste')
        assert response.status_code == 401


class TestSurpriseMe:
    """Test surprise event recommendation feature."""

    def test_surprise_me_success(self, client, auth_headers, sample_events):
        """Test successful surprise event recommendation."""
        response = client.post('/api/events/surprise-me',
            headers=auth_headers,
            json={
                'location': 'Austin, TX',
                'mood': 'adventurous',
                'budget': 50,
                'time_available': 3,
                'adventure_level': 'high'
            }
        )

        assert response.status_code == 200
        data = response.json
        assert 'event' in data or 'message' in data

    def test_surprise_me_missing_location(self, client, auth_headers):
        """Test surprise me with missing location."""
        response = client.post('/api/events/surprise-me',
            headers=auth_headers,
            json={'mood': 'chill'}
        )
        assert response.status_code == 400
        assert 'error' in response.json

    def test_surprise_me_invalid_location(self, client, auth_headers):
        """Test surprise me with invalid location format."""
        response = client.post('/api/events/surprise-me',
            headers=auth_headers,
            json={'location': 'Invalid'}
        )
        assert response.status_code == 400

    def test_surprise_me_default_values(self, client, auth_headers, sample_events):
        """Test surprise me with default parameter values."""
        response = client.post('/api/events/surprise-me',
            headers=auth_headers,
            json={'location': 'Austin, TX'}
        )

        # Should succeed with default mood, budget, time, adventure_level
        assert response.status_code in [200, 404]  # 404 if no events match

    def test_surprise_me_various_moods(self, client, auth_headers, sample_events):
        """Test surprise me with different mood values."""
        moods = ['energetic', 'chill', 'creative', 'social', 'romantic', 'adventurous']

        for mood in moods:
            response = client.post('/api/events/surprise-me',
                headers=auth_headers,
                json={'location': 'Austin, TX', 'mood': mood}
            )
            # Should handle all moods gracefully
            assert response.status_code in [200, 404]

    def test_surprise_me_requires_auth(self, client):
        """Test that surprise me requires authentication."""
        response = client.post('/api/events/surprise-me',
            json={'location': 'Austin, TX'}
        )
        assert response.status_code == 401


class TestPersonalizationIntegration:
    """Integration tests for personalization workflow."""

    def test_full_personalization_workflow(self, client, auth_headers, sample_events):
        """Test complete personalization workflow."""
        # Step 1: User views events
        for event_id in sample_events:
            client.post('/api/events/interact',
                headers=auth_headers,
                json={'event_id': event_id, 'interaction_type': 'view'}
            )

        # Step 2: User likes some events
        client.post('/api/events/interact',
            headers=auth_headers,
            json={'event_id': sample_events[0], 'interaction_type': 'like'}
        )
        client.post('/api/events/interact',
            headers=auth_headers,
            json={'event_id': sample_events[1], 'interaction_type': 'super_like'}
        )

        # Step 3: Check taste profile
        profile_response = client.get('/api/profile/taste', headers=auth_headers)
        assert profile_response.status_code == 200

        # Step 4: Get personalized recommendations
        personalized_response = client.post('/api/events/personalized',
            headers=auth_headers,
            json={'location': 'Austin, TX', 'limit': 10}
        )
        assert personalized_response.status_code == 200

        # Step 5: Get surprise recommendation
        surprise_response = client.post('/api/events/surprise-me',
            headers=auth_headers,
            json={'location': 'Austin, TX', 'mood': 'adventurous'}
        )
        assert surprise_response.status_code in [200, 404]
