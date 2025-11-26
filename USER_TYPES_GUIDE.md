# User Types Guide - Volunteer & Organization Accounts

## Overview

Tapin Correct now supports two types of user accounts:

1. **Volunteer** - Individual users looking for volunteer opportunities
2. **Organization** - Organizations posting volunteer events

## API Usage

### Register as a Volunteer

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "volunteer@example.com",
    "password": "[REDACTED]",
    "user_type": "volunteer"
  }'
```

**Response:**

```json
{
  "message": "volunteer account created successfully",
  "user": {
    "id": 1,
    "email": "volunteer@example.com",
    "role": "volunteer",
    "user_type": "volunteer"
  },
  "access_token": "[REDACTED_TOKEN]",
  "refresh_token": "[REDACTED_TOKEN]"
}
```

### Register as an Organization

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "org@example.com",
    "password": "[REDACTED]",
    "user_type": "organization"
  }'
```

**Response:**

```json
{
  "message": "organization account created successfully",
  "user": {
    "id": 2,
    "email": "org@example.com",
    "role": "organization",
    "user_type": "organization"
  },
  "access_token": "[REDACTED_TOKEN]",
  "refresh_token": "[REDACTED_TOKEN]"
}
```

### Login (Works for Both Types)

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "volunteer@example.com",
    "password": "[REDACTED]"
  }'
```

**Response:**

```json
{
  "message": "login successful",
  "user": {
    "id": 1,
    "email": "volunteer@example.com",
    "role": "volunteer",
    "user_type": "volunteer"
  },
  "access_token": "[REDACTED_TOKEN]",
  "refresh_token": "[REDACTED_TOKEN]"
}
```

## Frontend Implementation

### Registration Form

```javascript
// Volunteer Registration
const registerVolunteer = async (email, password) => {
  const response = await fetch("http://localhost:5000/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email,
      password,
      user_type: "volunteer", // <-- Key difference
    }),
  });
  return response.json();
};

// Organization Registration
const registerOrganization = async (email, password) => {
  const response = await fetch("http://localhost:5000/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email,
      password,
      user_type: "organization", // <-- Key difference
    }),
  });
  return response.json();
};
```

### Checking User Type After Login

```javascript
const login = async (email, password) => {
  const response = await fetch("http://localhost:5000/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  // Store tokens
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("refresh_token", data.refresh_token);

  // Check user type and redirect accordingly
  if (data.user.user_type === "organization") {
    // Redirect to organization dashboard
    window.location.href = "/organization-dashboard";
  } else {
    // Redirect to volunteer dashboard
    window.location.href = "/volunteer-dashboard";
  }
};
```

### Protected Routes Based on User Type

```javascript
const checkUserType = async () => {
  const token = localStorage.getItem("access_token");

  const response = await fetch("http://localhost:5000/me", {
    headers: { Authorization: `Bearer ${token}` },
  });

  const data = await response.json();
  return data.user_type; // 'volunteer' or 'organization'
};
```

## User Type Features

### Volunteers Can:

- ✅ Search for events
- ✅ Register for events
- ✅ Track event participation
- ✅ Earn achievements
- ✅ Get personalized recommendations
- ✅ Use AI-powered event discovery

### Organizations Can:

- ✅ Create event listings
- ✅ Edit/update events
- ✅ Delete events
- ✅ View registrations
- ✅ Manage volunteer signups
- ✅ Post opportunities

## Database Schema

The `user` table has a `role` field that stores the user type:

```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',  -- 'volunteer' or 'organization'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Example UI Flow

### Registration Page

```
┌─────────────────────────────────────┐
│  Register for Tapin Correct         │
├─────────────────────────────────────┤
│                                     │
│  I am a:                            │
│  ○ Volunteer                        │
│  ● Organization                     │
│                                     │
│  Email: [___________________]       │
│  Password: [___________________]    │
│                                     │
│         [Create Account]            │
│                                     │
│  Already have an account? Login     │
└─────────────────────────────────────┘
```

### After Login - Organization View

```
┌─────────────────────────────────────┐
│  Organization Dashboard             │
├─────────────────────────────────────┤
│                                     │
│  Welcome, org@example.com           │
│                                     │
│  Your Events:                       │
│  • Community Cleanup - 15 signups   │
│  • Food Bank - 8 signups            │
│                                     │
│  [+ Create New Event]               │
│                                     │
└─────────────────────────────────────┘
```

### After Login - Volunteer View

```
┌─────────────────────────────────────┐
│  Volunteer Dashboard                │
├─────────────────────────────────────┤
│                                     │
│  Welcome, volunteer@example.com     │
│                                     │
│  Recommended Events:                │
│  🌟 Community Cleanup - Tomorrow    │
│  🍽️  Food Bank - This Weekend       │
│                                     │
│  [Discover More Events]             │
│                                     │
└─────────────────────────────────────┘
```

## Testing

```bash
# Test volunteer registration
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"email":"vol@test.com","password":"test123","user_type":"volunteer"}'

# Test organization registration
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"email":"org@test.com","password":"test123","user_type":"organization"}'

# Test login and check user_type in response
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"vol@test.com","password":"test123"}'
```

## Migration Guide

Existing users in the database will have `role='user'`. To update them:

```sql
-- Set all existing users to volunteers
UPDATE user SET role = 'volunteer' WHERE role = 'user';

-- Or manually set specific users as organizations
UPDATE user SET role = 'organization' WHERE email = 'org@example.com';
```

## Next Steps for Frontend

1. **Update Registration Form**
   - Add radio buttons for Volunteer/Organization
   - Send `user_type` in registration request

2. **Update Login Flow**
   - Check `user_type` from response
   - Route to appropriate dashboard

3. **Create Separate Dashboards**
   - Volunteer Dashboard - Browse events, track participation
   - Organization Dashboard - Manage events, view signups

4. **Conditional UI Elements**
   - Show "Create Event" only for organizations
   - Show "Browse Events" prominently for volunteers

---

**Backend is ready! Frontend integration needed to complete the feature.** 🚀
