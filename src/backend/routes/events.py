from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
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


@events_bp.route("/<event_id>", methods=["GET"])
@jwt_required()
def get_event(event_id):
    """
    Fetch a single event by ID. Attempts to fetch from external APIs if needed.

    For Ticketmaster events, event_id format: ticketmaster_<id>
    For Google events, event_id format: google_<id>
    For internal events, event_id is just the integer ID
    """
    try:
        # Check if it's an external event from Ticketmaster
        if event_id.startswith("ticketmaster_") or (
            not event_id.startswith("google_") and len(event_id) > 10
        ):
            # This is likely a Ticketmaster event ID
            # We can't fetch single events from Ticketmaster easily, so return a helpful error
            return (
                jsonify(
                    {
                        "error": "Event not found in cache. Please return to discovery page."
                    }
                ),
                404,
            )

        # Check if it's a Google search event
        if event_id.startswith("google_"):
            return (
                jsonify(
                    {
                        "error": "Event not found in cache. Please return to discovery page."
                    }
                ),
                404,
            )

        # Try to fetch from internal database for org-created events
        from backend.models import Event as DBEvent

        db_event = DBEvent.query.get(int(event_id))
        if db_event:
            return (
                jsonify(
                    {
                        "id": db_event.id,
                        "title": db_event.title,
                        "description": db_event.description,
                        "date": (
                            db_event.start_date.isoformat()
                            if db_event.start_date
                            else None
                        ),
                        "time": (
                            db_event.start_time.isoformat()
                            if db_event.start_time
                            else None
                        ),
                        "location": db_event.location_name,
                        "city": db_event.city,
                        "lat": db_event.latitude,
                        "lng": db_event.longitude,
                        "image": db_event.image_url,
                        "category": db_event.category,
                        "source": "internal",
                        "max_volunteers": db_event.max_volunteers,
                        "current_volunteers": db_event.current_volunteers,
                    }
                ),
                200,
            )

        return jsonify({"error": "Event not found"}), 404

    except Exception as e:
        print(f"Error fetching event {event_id}: {e}")
        return jsonify({"error": "Failed to fetch event"}), 500


@events_bp.route("/register", methods=["POST"])
@jwt_required()
def register_for_event():
    """Register a user for an event (save as 'register' interaction).

    POST body: {event_id, event_title, category, source, ...other event details}
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    required_keys = ["event_id", "event_title", "category", "source"]
    if not all(k in data for k in required_keys):
        return jsonify({"error": "Missing required event data"}), 400

    try:
        # Save as a 'register' interaction
        interaction = UserEventInteraction(
            user_id=user_id,
            event_id=str(data["event_id"]),
            event_title=data.get("event_title"),
            category=data.get("category"),
            interaction_type="register",
            source=data.get("source"),
            timestamp=datetime.utcnow(),
        )

        db.session.add(interaction)
        db.session.commit()

        return (
            jsonify({"success": True, "message": "Successfully registered for event!"}),
            200,
        )
    except Exception as e:
        db.session.rollback()
        print("Registration error:", e)
        return jsonify({"error": "Could not register for event"}), 500


@events_bp.route("/interact", methods=["POST"])
@jwt_required()
def interact():
    """Log a user's interaction (like/dislike/view/save) with an event.

    POST body must include: event_id, event_title, category, interaction, source
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
            event_title=data.get("event_title"),
            category=data.get("category"),
            interaction_type=data.get("interaction"),
            source=data.get("source"),
            timestamp=datetime.utcnow(),
        )

        db.session.add(interaction)
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        print("Interaction error:", e)
        return jsonify({"error": "Could not save interaction"}), 500
