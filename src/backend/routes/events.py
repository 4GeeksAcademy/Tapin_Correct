from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import asyncio
import json

from backend.event_discovery.cache_manager import EventCacheManager
from backend.event_discovery.ticketmaster_service import fetch_ticketmaster_events
from backend.models import db, UserEventInteraction


events_bp = Blueprint("events", __name__)


@events_bp.route("/search", methods=["GET"])
@jwt_required()
def search_events():
    """Search events by city/state and return cached or freshly scraped results.

    Query params: ?city=CityName&state=ST
    """
    city = request.args.get("city")
    state = request.args.get("state")
    if not state:
        return jsonify({"error": "state parameter required (e.g. CA, TX)"}), 400

    manager = EventCacheManager()
    try:
        events = asyncio.run(manager.search_by_location(city or "", state))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"events": events}), 200


@events_bp.route("/personalized", methods=["POST"])
@jwt_required()
def personalized_events():
    """Return combined personalized events from Ticketmaster (and other sources).

    POST body: {"location": "City, ST"}
    """
    data = request.get_json() or {}
    location = data.get("location", "Houston, TX")

    try:
        tm_events = fetch_ticketmaster_events(location=location)
        # TODO: combine with other sources (google, local scraper) as available
        all_events = tm_events
        return jsonify({"events": all_events}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@events_bp.route("/interact", methods=["POST"])
@jwt_required()
def interact():
    """Log a user's interaction (like/dislike) with an event.

    POST body should include: event_id, event_title, event_category, interaction ('like'|'dislike'), source
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    event_id = data.get("event_id")
    if not event_id:
        return jsonify({"error": "event_id is required"}), 400

    try:
        interaction = UserEventInteraction(
            user_id=user_id,
            event_id=event_id,
            interaction_type=data.get("interaction", "unknown"),
            interaction_metadata=json.dumps(
                {
                    "title": data.get("event_title"),
                    "category": data.get("event_category"),
                    "source": data.get("source"),
                }
            ),
        )

        db.session.add(interaction)
        db.session.commit()

        # Optionally, trigger gamification checks here
        return jsonify({"status": "success"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
