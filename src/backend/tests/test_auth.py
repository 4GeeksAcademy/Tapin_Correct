from auth import token_for


def test_register_and_login(client):
    # register
    creds = {'email': 'a1@example.com', 'password': 'pw'}
    resp = client.post('/register', json=creds)
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'access_token' in data

    # login
    resp2 = client.post('/login', json=creds)
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    assert 'access_token' in data2


def test_me_requires_jwt(client, create_user):
    user_id = create_user('me@example.com')
    token = token_for(user_id)
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.get('/me', headers=headers)
    assert resp.status_code == 200
    assert 'user' in resp.get_json()


def test_register_volunteer(client):
    """Test registering as a volunteer."""
    creds = {'email': 'volunteer@example.com', 'password': 'pw', 'user_type': 'volunteer'}
    resp = client.post('/register', json=creds)
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'access_token' in data
    assert 'user' in data
    assert data['user']['role'] == 'volunteer'
    assert data['user']['user_type'] == 'volunteer'
    assert 'volunteer account created successfully' in data['message']


def test_register_organization(client):
    """Test registering as an organization."""
    creds = {'email': 'org@example.com', 'password': 'pw', 'user_type': 'organization'}
    resp = client.post('/register', json=creds)
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'access_token' in data
    assert 'user' in data
    assert data['user']['role'] == 'organization'
    assert data['user']['user_type'] == 'organization'
    assert 'organization account created successfully' in data['message']


def test_register_defaults_to_volunteer(client):
    """Test that registration without user_type defaults to volunteer."""
    creds = {'email': 'default@example.com', 'password': 'pw'}
    resp = client.post('/register', json=creds)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['user']['role'] == 'volunteer'
    assert data['user']['user_type'] == 'volunteer'


def test_register_invalid_user_type(client):
    """Test that invalid user_type returns an error."""
    creds = {'email': 'invalid@example.com', 'password': 'pw', 'user_type': 'admin'}
    resp = client.post('/register', json=creds)
    assert resp.status_code == 400
    data = resp.get_json()
    assert 'error' in data
    assert "must be 'volunteer' or 'organization'" in data['error']


def test_login_returns_user_type(client):
    """Test that login returns the user's type."""
    # Register an organization
    creds = {'email': 'org2@example.com', 'password': 'pw', 'user_type': 'organization'}
    client.post('/register', json=creds)

    # Login and verify user_type is returned
    resp = client.post('/login', json={'email': 'org2@example.com', 'password': 'pw'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['user']['role'] == 'organization'
    assert data['user']['user_type'] == 'organization'
