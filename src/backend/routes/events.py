from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from datetime import datetime

from backend.event_discovery.cache_manager import EventCacheManager
from backend.event_discovery.ticketmaster_service import fetch_ticketmaster_events
from backend.event_discovery.google_maps_service import fetch_google_events
from backend.models import db, UserEventInteraction


events_bp = Blueprint("events", __name__)


@events_bp.route("/search", methods=["GET"])
@jwt_required()
def search_events():
    """Search events by city/state and return cached or cached/fresh results.

    Query params: ?city=CityName&state=ST
    """
    city = request.args.get("city")
    state = request.args.get("state")
    if not state:
        return jsonify({"error": "state parameter required (e.g. CA, TX)"}), 400

    manager = EventCacheManager()
    try:
        events = manager.search_by_location(city or "", state)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"events": events}), 200


@events_bp.route("/personalized", methods=["POST"])
@jwt_required()
def personalized_events():
    """Return combined events from Ticketmaster and Google as a fallback.

    POST body: {"location": "City, ST", "limit": 20}
    """
    data = request.get_json() or {}
    location = data.get("location", "Houston, TX")
    try:
        limit = min(int(data.get("limit", 20)), 50)
    except Exception:
        limit = 20

    try:
        tm_events = fetch_ticketmaster_events(city=location, limit=limit)
    except Exception as e:
        tm_events = []
        print("Ticketmaster fetch error:", e)

    try:
        google_events = fetch_google_events(city=location, limit=limit)
    except Exception as e:
        google_events = []
        print("Google fetch error:", e)

    combined = (tm_events or []) + (google_events or [])
    combined = combined[:limit]

    return jsonify({"events": combined}), 200


@events_bp.route("/live", methods=["POST"])
@jwt_required()
def get_live_events():
    """
    Fetch LIVE events from external APIs (Ticketmaster, Google, etc.).
    This endpoint specifically fetches fresh data from live services,
    separate from seeded/cached data for safety.

    POST body: {"location": "City, ST", "limit": 20}
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    location = data.get("location", "Houston, TX")

    try:
        limit = min(int(data.get("limit", 20)), 50)
    except Exception:
        limit = 20

    # 1. Fetch from Ticketmaster
    live_events = fetch_ticketmaster_events(city=location, limit=limit)

    # 2. (Optional) Fetch from Google if service is ready
    try:
        google_events = fetch_google_events(city=location, limit=limit)
        live_events += google_events
    except Exception as e:
        print(f"Google events fetch failed (non-critical): {e}")

    # 3. Remove duplicates (if fetching from multiple sources)
    seen_ids = set()
    unique_events = []
    for event in live_events:
        if event["id"] not in seen_ids:
            unique_events.append(event)
            seen_ids.add(event["id"])

    print(f"✅ Fetched {len(unique_events)} live events for {location}.")

    return jsonify({"events": unique_events}), 200


@events_bp.route("/interact", methods=["POST"])
@jwt_required()
def interact():
    """Log a user's interaction (like/dislike) with an event.

    POST body must include: event_id, event_title, category, interaction ('like'|'dislike'), source
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    required_keys = ["event_id", "event_title", "category", "interaction", "source"]
    if not all(k in data for k in required_keys):
        return jsonify({"error": "Missing data"}), 400

    try:
        interaction = UserEventInteraction(
            user_id=user_id,
            event_id=str(data["event_id"]),
            interaction_type=data.get("interaction"),
            interaction_metadata=json.dumps(
                {
                    "title": data.get("event_title"),
                    "category": data.get("category"),
                    "source": data.get("source"),
                }
            ),
            timestamp=datetime.utcnow(),
        )

        db.session.add(interaction)
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        print("Interaction error:", e)
        return jsonify({"error": "Could not save interaction"}), 500
