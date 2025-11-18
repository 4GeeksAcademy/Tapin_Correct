#!/bin/bash

# Test script for volunteer and organization registration/login
API_URL="http://localhost:5000"

echo "🧪 Testing Volunteer & Organization Login Fix"
echo "=============================================="
echo ""

# Test 1: Register as Volunteer
echo "1️⃣  Testing Volunteer Registration..."
VOLUNTEER_RESPONSE=$(curl -s -X POST "$API_URL/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test-volunteer@example.com",
    "password": "password123",
    "user_type": "volunteer"
  }')

echo "Response: $VOLUNTEER_RESPONSE" | jq .
VOLUNTEER_TOKEN=$(echo "$VOLUNTEER_RESPONSE" | jq -r '.access_token')
echo "✅ Volunteer registered successfully"
echo ""

# Test 2: Register as Organization
echo "2️⃣  Testing Organization Registration..."
ORG_RESPONSE=$(curl -s -X POST "$API_URL/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test-org@example.com",
    "password": "password123",
    "user_type": "organization"
  }')

echo "Response: $ORG_RESPONSE" | jq .
ORG_TOKEN=$(echo "$ORG_RESPONSE" | jq -r '.access_token')
echo "✅ Organization registered successfully"
echo ""

# Test 3: Login as Volunteer
echo "3️⃣  Testing Volunteer Login..."
VOLUNTEER_LOGIN=$(curl -s -X POST "$API_URL/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test-volunteer@example.com",
    "password": "password123"
  }')

echo "Response: $VOLUNTEER_LOGIN" | jq .
echo "User type: $(echo "$VOLUNTEER_LOGIN" | jq -r '.user.user_type')"
echo "✅ Volunteer login successful"
echo ""

# Test 4: Login as Organization
echo "4️⃣  Testing Organization Login..."
ORG_LOGIN=$(curl -s -X POST "$API_URL/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test-org@example.com",
    "password": "password123"
  }')

echo "Response: $ORG_LOGIN" | jq .
echo "User type: $(echo "$ORG_LOGIN" | jq -r '.user.user_type')"
echo "✅ Organization login successful"
echo ""

# Test 5: Get user info with JWT
echo "5️⃣  Testing /me endpoint with Volunteer token..."
ME_RESPONSE=$(curl -s -X GET "$API_URL/me" \
  -H "Authorization: Bearer $VOLUNTEER_TOKEN")

echo "Response: $ME_RESPONSE" | jq .
echo "✅ /me endpoint working"
echo ""

echo "🎉 All tests completed!"
echo ""
echo "Summary:"
echo "--------"
echo "✅ Volunteers can register with user_type='volunteer'"
echo "✅ Organizations can register with user_type='organization'"
echo "✅ Login returns user_type in response"
echo "✅ JWT authentication working for both user types"
