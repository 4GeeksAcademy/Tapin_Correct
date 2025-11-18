from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import asyncio

from backend.event_discovery.cache_manager import EventCacheManager

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
