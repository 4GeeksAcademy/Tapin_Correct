#!/usr/bin/env python3
"""
Backfill missing UserProfile rows for existing users.
Run this inside the project's virtualenv or from a machine that has DB access (e.g., via Fly remote run).
"""
from backend.app import create_app
from backend.models import db, User, UserProfile
import json

app = create_app()

DEFAULT_PROFILE = {
    "category_preferences": {},
    "hour_preferences": {},
    "price_sensitivity": "medium",
    "adventure_level": 0.5,
    "favorite_venues": [],
    "average_lead_time": 7,
}

with app.app_context():
    users = User.query.all()
    created = 0
    for u in users:
        exists = UserProfile.query.filter_by(user_id=u.id).first()
        if exists:
            continue
        profile = UserProfile(
            user_id=u.id,
            taste_profile=json.dumps(DEFAULT_PROFILE),
            adventure_level=DEFAULT_PROFILE["adventure_level"],
            price_sensitivity=DEFAULT_PROFILE["price_sensitivity"],
            favorite_venues=json.dumps(DEFAULT_PROFILE["favorite_venues"]),
        )
        db.session.add(profile)
        created += 1
    if created:
        db.session.commit()
    print(f"Backfill complete. Created {created} UserProfile records.")
