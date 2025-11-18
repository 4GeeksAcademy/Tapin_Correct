"""
End-to-end workflow tests covering complete user journeys through the application.
Tests the full user experience from registration to event discovery and interaction.
"""
import pytest
from backend.app import app, db, User, Listing, Event


@pytest.fixture
def client():
    """Create test client with in-memory database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    app.config['SECRET_KEY'] = 'test-secret'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


class TestVolunteerCompleteJourney:
    """Test complete volunteer user journey."""

    def test_volunteer_full_workflow(self, client):
        """Test complete volunteer workflow from registration to event interaction."""
        # Step 1: Registration
        register_response = client.post('/register', json={
            'email': 'volunteer@example.com',
            'password': 'secure_password123',
            'role': 'volunteer'
        })
        assert register_response.status_code == 201
        assert 'message' in register_response.json

        # Step 2: Login
        login_response = client.post('/login', json={
            'email': 'volunteer@example.com',
            'password': 'secure_password123'
        })
        assert login_response.status_code == 200
        assert 'access_token' in login_response.json
        access_token = login_response.json['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}

        # Step 3: View profile
        me_response = client.get('/me', headers=headers)
        assert me_response.status_code == 200
        assert me_response.json['user']['email'] == 'volunteer@example.com'
        assert me_response.json['user']['role'] == 'volunteer'

        # Step 4: Browse listings (empty at first)
        listings_response = client.get('/listings')
        assert listings_response.status_code == 200
        assert isinstance(listings_response.json, list)

        # Step 5: Create a listing
        create_listing_response = client.post('/listings',
            headers=headers,
            json={
                'title': 'Community Garden Volunteers Needed',
                'description': 'Help us maintain our community garden',
                'location': 'Austin, TX',
                'category': 'Environment',
                'latitude': 30.2672,
                'longitude': -97.7431
            }
        )
        assert create_listing_response.status_code == 201
        listing_id = create_listing_response.json['id']

        # Step 6: View the created listing
        view_listing_response = client.get(f'/listings/{listing_id}')
        assert view_listing_response.status_code == 200
        assert view_listing_response.json['title'] == 'Community Garden Volunteers Needed'

        # Step 7: Update the listing
        update_response = client.put(f'/listings/{listing_id}',
            headers=headers,
            json={'description': 'Updated description with more details'}
        )
        assert update_response.status_code == 200

        # Step 8: View all listings (should have 1)
        all_listings_response = client.get('/listings')
        assert len(all_listings_response.json) == 1

        # Step 9: Check initial achievements
        achievements_response = client.get('/api/achievements', headers=headers)
        assert achievements_response.status_code == 200

        # Step 10: Delete the listing
        delete_response = client.delete(f'/listings/{listing_id}', headers=headers)
        assert delete_response.status_code == 200


class TestOrganizationCompleteJourney:
    """Test complete organization user journey."""

    def test_organization_full_workflow(self, client):
        """Test complete organization workflow."""
        # Step 1: Registration as organization
        register_response = client.post('/register', json={
            'email': 'org@nonprofit.org',
            'password': 'org_password123',
            'role': 'organization',
            'organization_name': 'Green Earth Foundation'
        })
        assert register_response.status_code == 201

        # Step 2: Login
        login_response = client.post('/login', json={
            'email': 'org@nonprofit.org',
            'password': 'org_password123'
        })
        assert login_response.status_code == 200
        access_token = login_response.json['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}

        # Step 3: View profile (should show organization)
        me_response = client.get('/me', headers=headers)
        assert me_response.status_code == 200
        assert me_response.json['user']['role'] == 'organization'
        assert me_response.json['user']['organization_name'] == 'Green Earth Foundation'

        # Step 4: Create multiple listings
        listing_ids = []
        listings_data = [
            {
                'title': 'Beach Cleanup Event',
                'description': 'Help clean local beaches',
                'location': 'Miami, FL',
                'category': 'Environment',
                'latitude': 25.7617,
                'longitude': -80.1918
            },
            {
                'title': 'Food Distribution',
                'description': 'Distribute meals to those in need',
                'location': 'Miami, FL',
                'category': 'Community',
                'latitude': 25.7617,
                'longitude': -80.1918
            }
        ]

        for listing_data in listings_data:
            response = client.post('/listings', headers=headers, json=listing_data)
            assert response.status_code == 201
            listing_ids.append(response.json['id'])

        # Step 5: View organization's listings
        all_listings = client.get('/listings').json
        assert len(all_listings) >= 2

        # Step 6: Check organization achievements/metrics
        achievements_response = client.get('/api/achievements', headers=headers)
        assert achievements_response.status_code == 200


class TestVolunteerSignupWorkflow:
    """Test volunteer signing up for organization's listings."""

    def test_volunteer_signup_flow(self, client):
        """Test volunteer signing up for events."""
        # Create organization
        client.post('/register', json={
            'email': 'org@test.com',
            'password': 'password123',
            'role': 'organization',
            'organization_name': 'Test Org'
        })
        org_token = client.post('/login', json={
            'email': 'org@test.com',
            'password': 'password123'
        }).json['access_token']
        org_headers = {'Authorization': f'Bearer {org_token}'}

        # Organization creates listing
        listing_response = client.post('/listings',
            headers=org_headers,
            json={
                'title': 'Tree Planting Event',
                'description': 'Plant trees in local park',
                'location': 'Portland, OR',
                'category': 'Environment'
            }
        )
        listing_id = listing_response.json['id']

        # Create volunteer
        client.post('/register', json={
            'email': 'volunteer@test.com',
            'password': 'password123',
            'role': 'volunteer'
        })
        vol_token = client.post('/login', json={
            'email': 'volunteer@test.com',
            'password': 'password123'
        }).json['access_token']
        vol_headers = {'Authorization': f'Bearer {vol_token}'}

        # Volunteer signs up
        signup_response = client.post(f'/listings/{listing_id}/signup',
            headers=vol_headers,
            json={'message': 'I would love to help!'}
        )
        assert signup_response.status_code == 201
        signup_id = signup_response.json['id']

        # Organization views signups
        signups_response = client.get(f'/listings/{listing_id}/signups',
            headers=org_headers
        )
        assert signups_response.status_code == 200
        assert len(signups_response.json) == 1

        # Organization accepts signup
        accept_response = client.put(f'/signups/{signup_id}',
            headers=org_headers,
            json={'status': 'accepted'}
        )
        assert accept_response.status_code == 200
        assert accept_response.json['status'] == 'accepted'


class TestReviewWorkflow:
    """Test complete review and rating workflow."""

    def test_review_submission_flow(self, client):
        """Test submitting reviews for listings."""
        # Create organization and listing
        client.post('/register', json={
            'email': 'org@test.com',
            'password': 'password123',
            'role': 'organization',
            'organization_name': 'Test Org'
        })
        org_token = client.post('/login', json={
            'email': 'org@test.com',
            'password': 'password123'
        }).json['access_token']
        org_headers = {'Authorization': f'Bearer {org_token}'}

        listing_response = client.post('/listings',
            headers=org_headers,
            json={
                'title': 'Animal Shelter Help',
                'description': 'Help care for animals',
                'location': 'Seattle, WA',
                'category': 'Animals'
            }
        )
        listing_id = listing_response.json['id']

        # Create multiple volunteers and have them review
        for i in range(3):
            email = f'volunteer{i}@test.com'
            client.post('/register', json={
                'email': email,
                'password': 'password123',
                'role': 'volunteer'
            })
            token = client.post('/login', json={
                'email': email,
                'password': 'password123'
            }).json['access_token']
            headers = {'Authorization': f'Bearer {token}'}

            # Submit review
            rating = 4 + (i % 2)  # Ratings 4 or 5
            review_response = client.post(f'/listings/{listing_id}/reviews',
                headers=headers,
                json={
                    'rating': rating,
                    'comment': f'Great experience! Review #{i+1}'
                }
            )
            assert review_response.status_code == 201

        # Check average rating
        avg_response = client.get(f'/listings/{listing_id}/average-rating')
        assert avg_response.status_code == 200
        assert 'average_rating' in avg_response.json
        assert 4.0 <= avg_response.json['average_rating'] <= 5.0

        # Get all reviews
        reviews_response = client.get(f'/listings/{listing_id}/reviews')
        assert reviews_response.status_code == 200
        assert len(reviews_response.json) == 3


class TestEventDiscoveryWorkflow:
    """Test event discovery and interaction workflow."""

    def test_event_discovery_and_personalization(self, client):
        """Test discovering events and building personalization profile."""
        # Register and login volunteer
        client.post('/register', json={
            'email': 'volunteer@test.com',
            'password': 'password123',
            'role': 'volunteer'
        })
        token = client.post('/login', json={
            'email': 'volunteer@test.com',
            'password': 'password123'
        }).json['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        # Create sample events in database
        import uuid
        from datetime import datetime
        with app.app_context():
            events = [
                Event(
                    id=str(uuid.uuid4()),
                    title='Music Festival',
                    organization='Music Council',
                    description='Live music event',
                    category='Music',
                    location_city='Austin',
                    location_state='TX',
                    date_start=datetime(2025, 12, 15),
                    url='https://example.com/music',
                    source='test'
                ),
                Event(
                    id=str(uuid.uuid4()),
                    title='Art Gallery Opening',
                    organization='Art Center',
                    description='New art exhibition',
                    category='Arts & Culture',
                    location_city='Austin',
                    location_state='TX',
                    date_start=datetime(2025, 12, 16),
                    url='https://example.com/art',
                    source='test'
                )
            ]
            for event in events:
                db.session.add(event)
            db.session.commit()
            event_ids = [e.id for e in events]

        # Step 1: Check initial taste profile (empty)
        initial_taste = client.get('/api/profile/taste', headers=headers)
        assert initial_taste.status_code == 200

        # Step 2: Interact with events
        for event_id in event_ids:
            # View event
            client.post('/api/events/interact',
                headers=headers,
                json={'event_id': event_id, 'interaction_type': 'view'}
            )

        # Like first event
        client.post('/api/events/interact',
            headers=headers,
            json={'event_id': event_ids[0], 'interaction_type': 'like'}
        )

        # Step 3: Get personalized recommendations
        personalized_response = client.post('/api/events/personalized',
            headers=headers,
            json={'location': 'Austin, TX', 'limit': 10}
        )
        assert personalized_response.status_code == 200

        # Step 4: Try surprise me feature
        surprise_response = client.post('/api/events/surprise-me',
            headers=headers,
            json={
                'location': 'Austin, TX',
                'mood': 'creative',
                'budget': 50
            }
        )
        assert surprise_response.status_code in [200, 404]

        # Step 5: Check updated taste profile
        updated_taste = client.get('/api/profile/taste', headers=headers)
        assert updated_taste.status_code == 200

        # Step 6: Check achievements (should reflect activity)
        achievements = client.get('/api/achievements', headers=headers)
        assert achievements.status_code == 200


class TestPasswordResetWorkflow:
    """Test password reset in context of user workflow."""

    def test_password_reset_integration(self, client):
        """Test password reset as part of user workflow."""
        email = 'user@test.com'
        original_password = 'original_pass123'
        new_password = 'new_pass456'

        # Step 1: Register
        client.post('/register', json={
            'email': email,
            'password': original_password,
            'role': 'volunteer'
        })

        # Step 2: Login with original password
        login1 = client.post('/login', json={
            'email': email,
            'password': original_password
        })
        assert login1.status_code == 200
        original_token = login1.json['access_token']

        # Step 3: Use the account (create listing)
        headers = {'Authorization': f'Bearer {original_token}'}
        client.post('/listings',
            headers=headers,
            json={
                'title': 'Test Listing',
                'description': 'Test',
                'location': 'Test City',
                'category': 'Community'
            }
        )

        # Step 4: Request password reset
        reset_request = client.post('/reset-password', json={'email': email})
        assert reset_request.status_code == 200

        # Step 5: Complete password reset
        if 'reset_url' in reset_request.json:
            token = reset_request.json['reset_url'].split('/reset-password/confirm/')[-1]
            confirm = client.post(f'/reset-password/confirm/{token}',
                json={'password': new_password}
            )
            assert confirm.status_code == 200

            # Step 6: Login with new password
            login2 = client.post('/login', json={
                'email': email,
                'password': new_password
            })
            assert login2.status_code == 200
            new_token = login2.json['access_token']

            # Step 7: Verify can still access account
            me_response = client.get('/me', headers={'Authorization': f'Bearer {new_token}'})
            assert me_response.status_code == 200
            assert me_response.json['user']['email'] == email

            # Step 8: Verify old token still works (JWT doesn't invalidate)
            old_me = client.get('/me', headers=headers)
            assert old_me.status_code == 200


class TestTokenRefreshWorkflow:
    """Test token refresh in user workflow."""

    def test_token_refresh_integration(self, client):
        """Test using refresh token in normal workflow."""
        # Register and login
        client.post('/register', json={
            'email': 'user@test.com',
            'password': 'password123',
            'role': 'volunteer'
        })

        login_response = client.post('/login', json={
            'email': 'user@test.com',
            'password': 'password123'
        })
        assert 'access_token' in login_response.json
        assert 'refresh_token' in login_response.json

        refresh_token = login_response.json['refresh_token']

        # Use refresh token to get new access token
        refresh_response = client.post('/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'}
        )
        assert refresh_response.status_code == 200
        assert 'access_token' in refresh_response.json

        new_access_token = refresh_response.json['access_token']

        # Use new access token
        me_response = client.get('/me',
            headers={'Authorization': f'Bearer {new_access_token}'}
        )
        assert me_response.status_code == 200


class TestMultiUserInteraction:
    """Test interactions between multiple users."""

    def test_multi_user_collaboration(self, client):
        """Test multiple users interacting with same listing."""
        # Create organization
        client.post('/register', json={
            'email': 'org@test.com',
            'password': 'password123',
            'role': 'organization',
            'organization_name': 'Community Org'
        })
        org_token = client.post('/login', json={
            'email': 'org@test.com',
            'password': 'password123'
        }).json['access_token']
        org_headers = {'Authorization': f'Bearer {org_token}'}

        # Create listing
        listing = client.post('/listings',
            headers=org_headers,
            json={
                'title': 'Community Event',
                'description': 'Everyone welcome',
                'location': 'Austin, TX',
                'category': 'Community'
            }
        )
        listing_id = listing.json['id']

        # Create multiple volunteers
        volunteers = []
        for i in range(3):
            email = f'vol{i}@test.com'
            client.post('/register', json={
                'email': email,
                'password': 'password123',
                'role': 'volunteer'
            })
            token = client.post('/login', json={
                'email': email,
                'password': 'password123'
            }).json['access_token']
            volunteers.append({'email': email, 'token': token})

        # All volunteers sign up
        for vol in volunteers:
            headers = {'Authorization': f'Bearer {vol["token"]}'}
            signup = client.post(f'/listings/{listing_id}/signup',
                headers=headers,
                json={'message': f'Sign up from {vol["email"]}'}
            )
            assert signup.status_code == 201

        # Organization views all signups
        signups = client.get(f'/listings/{listing_id}/signups', headers=org_headers)
        assert signups.status_code == 200
        assert len(signups.json) == 3

        # All volunteers leave reviews
        for vol in volunteers:
            headers = {'Authorization': f'Bearer {vol["token"]}'}
            review = client.post(f'/listings/{listing_id}/reviews',
                headers=headers,
                json={'rating': 5, 'comment': 'Great event!'}
            )
            assert review.status_code == 201

        # Check final average rating
        avg = client.get(f'/listings/{listing_id}/average-rating')
        assert avg.status_code == 200
        assert avg.json['average_rating'] == 5.0
