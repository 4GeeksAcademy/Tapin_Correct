from flask import request, jsonify, url_for, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import os
import json
from datetime import datetime, timezone
import smtplib
from email.message import EmailMessage


def register_routes(
    app,
    db,
    User,
    Event,
    UserEventInteraction,
    EventRegistration,
):

    def get_serializer():
        """Helper to get a URL-safe serializer with the app's secret key."""
        # This function needs the app context to access config
        from flask import current_app

        return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

    @app.route("/api/health", methods=["GET"])
    def api_health():
        """Enhanced health check including database connectivity."""
        health_status = {"status": "ok", "components": {}}

        # Check database connection
        try:
            db.session.execute(db.text("SELECT 1"))
            health_status["components"]["database"] = {
                "status": "connected",
                "uri_prefix": app.config["SQLALCHEMY_DATABASE_URI"][:20] + "...",
                "pool_size": (
                    db.engine.pool.size() if hasattr(db.engine.pool, "size") else "N/A"
                ),
            }
        except Exception as e:
            health_status["status"] = "degraded"
            health_status["components"]["database"] = {
                "status": "error",
                "error": str(e),
            }
            return jsonify(health_status), 503

        return jsonify(health_status), 200

    @app.route("/api/items", methods=["GET"])
    def api_list_items():
        # Return all items from the database
        items = Item.query.order_by(Item.id.asc()).all()
        return jsonify({"items": [i.to_dict() for i in items]}), 200

    @app.route("/api/items", methods=["POST"])
    @jwt_required()
    def api_create_item():
        data = request.get_json() or {}
        name = data.get("name")
        if not name:
            return jsonify({"error": "name required"}), 400
        item = Item(name=name, description=data.get("description"))
        db.session.add(item)
        db.session.commit()
        return jsonify(item.to_dict()), 201

    @app.route("/register", methods=["POST"])
    def register_user():
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")
        user_type = data.get("user_type", "volunteer")  # 'volunteer' or 'organization'
        organization_name = data.get("organization_name")
        name = data.get("name") or data.get("full_name") or "New User"

        if not email or not password:
            return jsonify({"error": "email and password required"}), 400

        # Validate user_type
        if user_type not in ["volunteer", "organization"]:
            return (
                jsonify({"error": "user_type must be 'volunteer' or 'organization'"}),
                400,
            )

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "user already exists"}), 400

        # Create user in DB using the available model API (supports older/newer User)
        user = User(email=email)
        # prefer set_password if available
        if hasattr(user, "set_password"):
            user.set_password(password)
        else:
            user.password_hash = generate_password_hash(password)

        # Handle user_type field compatibility (enum vs role string)
        try:
            from backend.models import UserType, VolunteerProfile, OrganizationProfile

            if user_type == "volunteer":
                # set enum value if attribute exists
                if hasattr(user, "user_type"):
                    user.user_type = UserType.VOLUNTEER
            else:
                if hasattr(user, "user_type"):
                    user.user_type = UserType.ORGANIZATION
        except Exception:
            # fallback to legacy role attribute
            if user_type == "volunteer" and hasattr(user, "role"):
                user.role = "volunteer"
            elif hasattr(user, "role"):
                user.role = "organization"

        # organization_name compatibility
        if hasattr(user, "organization_name") and organization_name:
            user.organization_name = organization_name

        db.session.add(user)
        db.session.flush()

        # Auto-create profile record to avoid dashboard crashes
        try:
            # Attempt to import modern profile models
            from backend.models import (
                VolunteerProfile,
                OrganizationProfile,
                UserProfile,
            )

            if user_type == "volunteer":
                # split provided name
                parts = name.split(" ", 1)
                first = parts[0]
                last = parts[1] if len(parts) > 1 else ""
                v = VolunteerProfile(
                    user_id=user.id,
                    first_name=first,
                    last_name=last,
                    total_hours_volunteered=0,
                    city="Houston",
                )
                db.session.add(v)
            else:
                o = OrganizationProfile(
                    user_id=user.id,
                    organization_name=organization_name or name,
                    organization_type="Nonprofit",
                    city="Houston",
                )
                db.session.add(o)

            # Also ensure the Taste/UserProfile exists if model present
            try:
                default_profile = {
                    "category_preferences": {},
                    "hour_preferences": {},
                    "price_sensitivity": "medium",
                    "adventure_level": 0.5,
                    "favorite_venues": [],
                    "average_lead_time": 7,
                }
                up = UserProfile(
                    user_id=user.id,
                    taste_profile=json.dumps(default_profile),
                    adventure_level=default_profile["adventure_level"],
                    price_sensitivity=default_profile["price_sensitivity"],
                    favorite_venues=json.dumps(default_profile["favorite_venues"]),
                )
                db.session.add(up)
            except Exception:
                # ignore
                pass

            db.session.commit()
        except Exception as e:
            # If profile creation fails, rollback profile-specific additions but keep user
            try:
                db.session.rollback()
            except Exception:
                pass
            # commit user alone
            try:
                db.session.add(user)
                db.session.commit()
            except Exception:
                db.session.rollback()
                return jsonify({"error": "registration failed"}), 500

        # return both access and refresh tokens (identity stored as string)
        from auth import token_pair

        tokens = token_pair(user)
        # Provide legacy `token` key (access token) for frontend compatibility
        response_payload = {
            "message": f"{user_type} account created successfully",
            "user": user.to_dict(),
            **tokens,
            "token": tokens.get("access_token"),
        }
        return jsonify(response_payload), 201

    # Alias for frontend compatibility
    @app.route("/api/auth/register", methods=["POST", "OPTIONS"])
    def api_auth_register():
        if request.method == "OPTIONS":
            return "", 200
        return register_user()

    @app.route("/login", methods=["POST"])
    def login_user():
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "invalid credentials"}), 401
        # return both access and refresh tokens to the client
        from auth import token_pair

        tokens = token_pair(user)
        return jsonify(
            {"message": "login successful", "user": user.to_dict(), **tokens}
        )

    # Backwards-compatible alias used by frontend: /api/auth/login
    @app.route("/api/auth/login", methods=["POST", "OPTIONS"])
    def api_auth_login():
        # Handle CORS preflight
        if request.method == "OPTIONS":
            return "", 200
        return login_user()

    @app.route("/refresh", methods=["POST"])
    @jwt_required(refresh=True)
    def refresh_token():
        """Exchange a valid refresh token for a new access token."""
        uid = get_jwt_identity()
        try:
            uid_int = int(uid)
        except Exception:
            uid_int = uid
        user = db.session.get(User, uid_int)
        if not user:
            return jsonify({"error": "user not found"}), 404
        from auth import token_for

        access_token = token_for(uid_int)
        return jsonify({"access_token": access_token})

    @app.route("/me", methods=["GET"])
    @jwt_required()
    def me():
        uid = get_jwt_identity()
        # convert back to int because tokens store identity as string
        try:
            uid_int = int(uid)
        except Exception:
            uid_int = uid
        # Use Session.get() which is the modern SQLAlchemy API (avoids
        # LegacyAPIWarning)
        user = db.session.get(User, uid_int)
        if not user:
            return jsonify({"error": "user not found"}), 404
        return jsonify({"user": user.to_dict()})

    def send_reset_email(to_email, reset_url):
        smtp_host = os.environ.get("SMTP_HOST")
        if not smtp_host:
            return False, "SMTP not configured"
        smtp_port = int(os.environ.get("SMTP_PORT", 587))
        smtp_user = os.environ.get("SMTP_USER")
        smtp_pass = os.environ.get("SMTP_PASS")
        use_tls = os.environ.get("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")

        msg = EmailMessage()
        msg["Subject"] = "Tapin Password Reset"
        msg["From"] = smtp_user or f"no-reply@{smtp_host}"
        msg["To"] = to_email
        msg.set_content(f"Use the link to reset your password: {reset_url}")

        try:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            server.ehlo()
            if use_tls:
                server.starttls()
                server.ehlo()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            server.quit()
            return True, "sent"
        except Exception as e:
            return False, str(e)

    @app.route("/reset-password", methods=["POST"])
    def reset_password():
        data = request.get_json() or {}
        email = data.get("email")
        if not email:
            return jsonify({"error": "email required"}), 400
        user = User.query.filter_by(email=email).first()
        if not user:
            # Do not reveal whether the email exists
            msg = "If an account exists for that email, a reset link was sent."
            return jsonify({"message": msg})

        serializer = get_serializer()
        token = serializer.dumps(email, salt=app.config["SECURITY_PASSWORD_SALT"])
        reset_url = url_for("confirm_reset", token=token, _external=True)

        sent, info = send_reset_email(email, reset_url)
        if sent:
            return jsonify({"message": "reset email sent"})
        else:
            # Fallback in dev: return the reset_url so developers can use it
            return jsonify(
                {
                    "message": "smtp not configured, returning reset link (dev)",
                    "reset_url": reset_url,
                    "error": info,
                }
            )

    @app.route("/reset-password/confirm/<token>", methods=["POST"])
    def confirm_reset(token):
        data = request.get_json() or {}
        new_password = data.get("password")
        if not new_password:
            return jsonify({"error": "password required"}), 400
        serializer = get_serializer()
        try:
            email = serializer.loads(
                token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=3600
            )
        except SignatureExpired:
            return jsonify({"error": "token expired"}), 400
        except BadSignature:
            return jsonify({"error": "invalid token"}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "no such user"}), 404
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({"message": "password updated"})

    @app.route("/listings", methods=["GET"])
    def get_listings():
        # Support simple filtering via query params: q (text search on
        # title/description or category), location
        q = request.args.get("q", type=str)
        location = request.args.get("location", type=str)

        query = Listing.query
        if q:
            # Check if q matches a category exactly (case-insensitive)
            categories = ["Community", "Environment", "Education", "Health", "Animals"]
            if q.lower() in [c.lower() for c in categories]:
                # Filter by category
                query = query.filter(Listing.category.ilike(q))
            else:
                # Text search on title/description
                like = f"%{q}%"
                query = query.filter(
                    (Listing.title.ilike(like)) | (Listing.description.ilike(like))
                )
        if location:
            query = query.filter(Listing.location.ilike(f"%{location}%"))

        listings = query.order_by(Listing.created_at.desc()).all()
        return jsonify([lst.to_dict() for lst in listings])

    @app.route("/listings", methods=["POST"])
    @jwt_required()
    def create_listing():
        data = request.get_json() or {}
        title = data.get("title")
        if not title:
            return jsonify({"error": "title required"}), 400
        # JWT identity is stored as string; convert back to int for DB foreign key
        owner_id = int(get_jwt_identity())
        # Validate optional category
        category = data.get("category")
        allowed = ["Community", "Environment", "Education", "Health", "Animals"]
        if category and category not in allowed:
            return jsonify({"error": "invalid category"}), 400

        # Parse optional coordinates
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        try:
            latitude = float(latitude) if latitude is not None else None
            longitude = float(longitude) if longitude is not None else None
        except (TypeError, ValueError):
            return jsonify({"error": "invalid coordinates"}), 400

        listing = Listing(
            title=title,
            description=data.get("description"),
            location=data.get("location"),
            latitude=latitude,
            longitude=longitude,
            category=category,
            image_url=data.get("image_url"),
            owner_id=owner_id,
        )
        db.session.add(listing)
        db.session.commit()
        return jsonify(listing.to_dict()), 201

    @app.route("/listings/<int:id>", methods=["GET"])
    def get_listing_detail(id):
        listing = Listing.query.get_or_404(id)
        return jsonify(listing.to_dict())

    @app.route("/listings/<int:id>", methods=["PUT"])
    @jwt_required()
    def update_listing(id):
        listing = Listing.query.get_or_404(id)
        # Verify ownership
        owner_id = int(get_jwt_identity())
        if listing.owner_id != owner_id:
            return jsonify({"error": "unauthorized - you don't own this listing"}), 403
        data = request.get_json() or {}
        listing.title = data.get("title", listing.title)
        listing.description = data.get("description", listing.description)
        listing.location = data.get("location", listing.location)
        # Optional fields
        if "category" in data:
            category = data.get("category")
            allowed = ["Community", "Environment", "Education", "Health", "Animals"]
            if category and category not in allowed:
                return jsonify({"error": "invalid category"}), 400
            listing.category = category
        if "image_url" in data:
            listing.image_url = data.get("image_url")
        if "latitude" in data or "longitude" in data:
            try:
                if "latitude" in data:
                    listing.latitude = (
                        float(data.get("latitude"))
                        if data.get("latitude") is not None
                        else None
                    )
                if "longitude" in data:
                    listing.longitude = (
                        float(data.get("longitude"))
                        if data.get("longitude") is not None
                        else None
                    )
            except (TypeError, ValueError):
                return jsonify({"error": "invalid coordinates"}), 400
        db.session.commit()
        return jsonify(listing.to_dict())

    @app.route("/listings/<int:id>", methods=["DELETE"])
    @jwt_required()
    def delete_listing(id):
        listing = Listing.query.get_or_404(id)
        # Verify ownership
        owner_id = int(get_jwt_identity())
        if listing.owner_id != owner_id:
            return jsonify({"error": "unauthorized - you don't own this listing"}), 403
        db.session.delete(listing)
        db.session.commit()
        return jsonify({"message": "deleted"})

    @app.route("/listings/<int:id>/signup", methods=["POST"])
    @jwt_required()
    def signup_for_listing(id):
        """Volunteer signs up for a listing."""
        _listing = Listing.query.get_or_404(id)  # noqa: F841 validate exists
        user_id = int(get_jwt_identity())

        # Check if already signed up
        existing = SignUp.query.filter_by(user_id=user_id, listing_id=id).first()
        if existing:
            return jsonify({"error": "already signed up for this listing"}), 400

        data = request.get_json() or {}
        signup = SignUp(
            user_id=user_id,
            listing_id=id,
            message=data.get("message"),
            status="pending",
        )
        db.session.add(signup)
        db.session.commit()

        return jsonify(signup.to_dict()), 201

    @app.route("/listings/<int:id>/signups", methods=["GET"])
    @jwt_required()
    def get_listing_signups(id):
        """Get all sign-ups for a listing (owner only)."""
        listing = Listing.query.get_or_404(id)
        owner_id = int(get_jwt_identity())

        # Verify ownership
        if listing.owner_id != owner_id:
            return jsonify({"error": "unauthorized - you don't own this listing"}), 403

        signups = (
            SignUp.query.filter_by(listing_id=id)
            .order_by(SignUp.created_at.desc())
            .all()
        )

        # Include user email with each sign-up
        results = []
        for signup in signups:
            signup_dict = signup.to_dict()
            user = db.session.get(User, signup.user_id)
            if user:
                signup_dict["user_email"] = user.email
            results.append(signup_dict)

        return jsonify(results)

    @app.route("/signups/<int:id>", methods=["PUT"])
    @jwt_required()
    def update_signup_status(id):
        """Update sign-up status (owner accept/decline, volunteer cancel)."""
        signup = SignUp.query.get_or_404(id)
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        new_status = data.get("status")

        if not new_status:
            return jsonify({"error": "status required"}), 400

        # Get the listing to check ownership
        listing = db.session.get(Listing, signup.listing_id)
        if not listing:
            return jsonify({"error": "listing not found"}), 404

        # Owner can accept/decline, volunteer can cancel
        if listing.owner_id == user_id:
            if new_status not in ["accepted", "declined"]:
                err = "owner can only set status to accepted or declined"
                return jsonify({"error": err}), 400
        elif signup.user_id == user_id:
            if new_status != "cancelled":
                return jsonify({"error": "volunteer can only cancel sign-up"}), 400
        else:
            return jsonify({"error": "unauthorized"}), 403

        signup.status = new_status
        db.session.commit()
        return jsonify(signup.to_dict())

    @app.route("/listings/<int:id>/reviews", methods=["POST"])
    @jwt_required()
    def create_review(id):
        """Create a review for a listing."""
        _listing = Listing.query.get_or_404(id)  # noqa: F841 validate exists
        user_id = int(get_jwt_identity())

        # Check if already reviewed
        existing = Review.query.filter_by(user_id=user_id, listing_id=id).first()
        if existing:
            return jsonify({"error": "you have already reviewed this listing"}), 400

        data = request.get_json() or {}
        rating = data.get("rating")

        if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            err = "rating must be an integer between 1 and 5"
            return jsonify({"error": err}), 400

        review = Review(
            user_id=user_id, listing_id=id, rating=rating, comment=data.get("comment")
        )
        db.session.add(review)
        db.session.commit()

        return jsonify(review.to_dict()), 201

    @app.route("/listings/<int:id>/reviews", methods=["GET"])
    def get_listing_reviews(id):
        """Get all reviews for a listing."""
        _listing = Listing.query.get_or_404(id)  # noqa: F841 validate exists
        reviews = (
            Review.query.filter_by(listing_id=id)
            .order_by(Review.created_at.desc())
            .all()
        )

        # Include user email with each review
        results = []
        for review in reviews:
            review_dict = review.to_dict()
            user = db.session.get(User, review.user_id)
            if user:
                review_dict["user_email"] = user.email
            results.append(review_dict)

        return jsonify(results)

    @app.route("/listings/<int:id>/average-rating", methods=["GET"])
    def get_listing_average_rating(id):
        """Get average rating for a listing."""
        _listing = Listing.query.get_or_404(id)  # noqa: F841 validate exists
        reviews = Review.query.filter_by(listing_id=id).all()

        if not reviews:
            return jsonify({"average_rating": 0, "review_count": 0})

        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        return jsonify(
            {"average_rating": round(avg_rating, 1), "review_count": len(reviews)}
        )

    @app.route("/api/discover-events", methods=["POST"])
    @jwt_required()
    def discover_events():
        """Discover volunteer opportunities using hybrid LLM and web scraping.

        Searches for volunteer events by city/state, using EventCacheManager
        which automatically caches results in the Event table with geohash.
        """
        import asyncio
        from backend.event_discovery import EventCacheManager

        data = request.get_json() or {}
        location = data.get("location")

        if not location:
            return jsonify({"error": "location required"}), 400

        # Parse location into city and state
        parts = [p.strip() for p in location.split(",")]
        if len(parts) < 2:
            return (
                jsonify(
                    {"error": "location must be 'City, ST' format (e.g., 'Dallas, TX')"}
                ),
                400,
            )

        city = parts[0]
        state = parts[1]

        try:
            # EventCacheManager uses async/await
            # Pass db and models explicitly to avoid app context issues
            manager = EventCacheManager(
                db=db, event_model=Event, event_image_model=EventImage
            )

            # Create a new event loop and run async code
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # Push Flask app context for database operations
                ctx = app.app_context()
                ctx.push()

                try:
                    # Run async code with app context active
                    events = loop.run_until_complete(
                        manager.search_by_location(city, state)
                    )
                finally:
                    ctx.pop()
            finally:
                loop.close()

            return (
                jsonify(
                    {
                        "events": events,
                        "location": f"{city}, {state}",
                        "count": len(events),
                        "cached": True,  # EventCacheManager auto-caches to DB
                    }
                ),
                200,
            )

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route("/api/categories", methods=["GET"])
    @jwt_required()
    def get_categories():
        """Get all event categories with metadata (icons, colors, descriptions)."""
        from backend.event_discovery.event_categories import (
            EVENT_CATEGORIES,
            get_categories_by_type,
        )

        return (
            jsonify(
                {
                    "categories": EVENT_CATEGORIES,
                    "grouped": get_categories_by_type(),
                    "count": len(EVENT_CATEGORIES),
                }
            ),
            200,
        )

    @app.route("/api/events/search", methods=["POST"])
    @jwt_required()
    def search_events_simple():
        """Simple event search from database - returns current/future events only.

        No Facebook scraping or external calls - just fast database queries.
        """
        from datetime import datetime, timezone

        data = request.get_json() or {}
        location = data.get("location")
        category = data.get("category")
        limit = data.get("limit", 50)

        if not location:
            return jsonify({"error": "location required"}), 400

        # Parse location
        parts = [p.strip() for p in location.split(",")]
        if len(parts) < 2:
            return jsonify({"error": "location must be 'City, ST' format"}), 400

        city = parts[0]
        state = parts[1]

        try:
            # Query database directly - only future volunteer events (exclude Ticketmaster)
            query = Event.query.filter(
                Event.location_city.ilike(city),
                Event.date_start >= datetime.now(timezone.utc),
                Event.source != "Ticketmaster",  # Exclude Ticketmaster events
            )

            # Filter by category if provided
            if category and category != "All":
                query = query.filter(Event.category == category)

            # Order by date and limit
            events = query.order_by(Event.date_start.asc()).limit(limit).all()

            # Convert to dict with images
            result = []
            for event in events:
                event_dict = {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "organization": event.organization,
                    "category": event.category,
                    "date_start": (
                        event.date_start.isoformat() if event.date_start else None
                    ),
                    "venue": event.venue,
                    "price": event.price,
                    "location_city": event.location_city,
                    "location_state": event.location_state,
                    "latitude": event.latitude,
                    "longitude": event.longitude,
                    "contact_person": event.contact_person,
                    "contact_email": event.contact_email,
                    "contact_phone": event.contact_phone,
                    "source": event.source,
                    "url": event.url,
                }

                # Get images
                images = (
                    EventImage.query.filter_by(event_id=event.id)
                    .order_by(EventImage.position)
                    .all()
                )
                if images:
                    event_dict["image_url"] = images[0].url
                    event_dict["image_urls"] = json.dumps([img.url for img in images])

                result.append(event_dict)

            return (
                jsonify(
                    {
                        "events": result,
                        "location": f"{city}, {state}",
                        "count": len(result),
                        "source": "database",
                    }
                ),
                200,
            )

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route("/api/web-search", methods=["POST"])
    @jwt_required()
    def web_search():
        """Search for volunteer opportunities using Google Custom Search API.

        Saves results as Event records in the database and returns them with contact info.
        """
        try:
            data = request.get_json() or {}
            query = data.get("query")
            location = data.get("location")  # Optional: {city: "...", state: "..."}

            if not query:
                return jsonify({"error": "query parameter required"}), 400

            app.logger.info(f"Web search request: {query}")

            from google_search import (
                search_events,
                create_events_from_search_results,
                enrich_events_with_contact_info,
                enrich_events_with_values,
            )

            # Call the Google Custom Search API
            results = search_events(query)

            # Check for errors
            if isinstance(results, dict) and "error" in results:
                app.logger.error(f"Web search error: {results['error']}")
                return jsonify({"error": results["error"]}), 500

            app.logger.info(
                f"Web search returned {len(results) if isinstance(results, list) else 0} results"
            )

            # Convert search results to Event records
            event_dicts = create_events_from_search_results(results, query, location)

            # Enrich events with contact information (limit to first 3 to avoid too many requests)
            event_dicts = enrich_events_with_contact_info(event_dicts, max_to_enrich=3)

            # Enrich events with values using Google Gemini LLM (limit to first 5)
            event_dicts = enrich_events_with_values(event_dicts, max_to_enrich=5)

            # Save events to database (using merge to avoid duplicates)
            saved_events = []
            for event_dict in event_dicts:
                # Check if event already exists
                existing_event = Event.query.get(event_dict["id"])

                if existing_event:
                    # Update existing event
                    for key, value in event_dict.items():
                        if key != "id":  # Don't update the ID
                            setattr(existing_event, key, value)
                    saved_events.append(existing_event.to_dict())
                else:
                    # Create new event
                    event = Event(**event_dict)
                    db.session.add(event)
                    saved_events.append(event_dict)

            db.session.commit()
            app.logger.info(f"Saved {len(saved_events)} events to database")

            return (
                jsonify(
                    {
                        "events": saved_events,
                        "query": query,
                        "count": len(saved_events),
                        "source": "google_custom_search",
                        "message": f"Found and saved {len(saved_events)} volunteer opportunities",
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Web search exception: {str(e)}")
            import traceback

            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route("/api/local-events/tonight", methods=["POST"])
    @jwt_required()
    def discover_tonight():
        """Discover ALL types of local events happening tonight (not just volunteer).

        Uses LocalEventsScraper to find events across multiple platforms:
        - Eventbrite
        - Meetup
        - Facebook local events
        - City event calendars

        Returns events with images, sorted by start time.
        """
        import asyncio
        from backend.event_discovery import EventCacheManager

        data = request.get_json() or {}
        location = data.get("location")
        limit = data.get("limit", 20)

        if not location:
            return jsonify({"error": "location required"}), 400

        # Parse location into city and state
        parts = [p.strip() for p in location.split(",")]
        if len(parts) < 2:
            return (
                jsonify(
                    {"error": "location must be 'City, ST' format (e.g., 'Dallas, TX')"}
                ),
                400,
            )

        city = parts[0]
        state = parts[1]

        try:
            # EventCacheManager uses async/await
            manager = EventCacheManager(
                db=db, event_model=Event, event_image_model=EventImage
            )

            # Create a new event loop and run async code
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # Push Flask app context for database operations
                ctx = app.app_context()
                ctx.push()

                try:
                    # Run async code with app context active
                    events = loop.run_until_complete(
                        manager.discover_tonight(city, state, limit)
                    )
                finally:
                    ctx.pop()
            finally:
                loop.close()

            return (
                jsonify(
                    {
                        "events": events,
                        "location": f"{city}, {state}",
                        "count": len(events),
                        "timeframe": "tonight",
                        "cached": True,  # EventCacheManager auto-caches to DB
                    }
                ),
                200,
            )

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route("/api/events/interact", methods=["POST"])
    @jwt_required()
    def record_event_interaction():
        """Record user interaction with an event (like, dislike, view, attend, etc.)."""
        uid = get_jwt_identity()
        try:
            uid_int = int(uid)
        except Exception:
            uid_int = uid

        data = request.get_json() or {}
        event_id = data.get("event_id")
        interaction_type = data.get(
            "interaction_type"
        )  # view, like, dislike, attend, skip, super_like
        metadata = data.get("metadata", {})

        if not event_id or not interaction_type:
            return jsonify({"error": "event_id and interaction_type required"}), 400

        # Record interaction
        interaction = UserEventInteraction(
            user_id=uid_int,
            event_id=event_id,
            interaction_type=interaction_type,
            interaction_metadata=json.dumps(metadata) if metadata else None,
        )
        db.session.add(interaction)
        db.session.commit()

        # Update user achievements based on interaction (volunteers only)
        user = User.query.get(uid_int)
        if user and user.role == "volunteer":
            from backend.event_discovery.gamification import GamificationEngine

            gamification = GamificationEngine(
                db, User, UserAchievement, UserEventInteraction
            )
            gamification.check_achievements(uid_int)

        return (
            jsonify(
                {
                    "message": "interaction recorded",
                    "interaction": interaction.to_dict(),
                }
            ),
            201,
        )

    @app.route("/api/events/personalized", methods=["POST"])
    @jwt_required()
    def get_personalized_events():
        """Get personalized event feed with match scores."""
        uid = get_jwt_identity()
        try:
            uid_int = int(uid)
        except Exception:
            uid_int = uid

        data = request.get_json() or {}
        location = data.get("location")
        limit = data.get("limit", 20)

        if not location:
            return jsonify({"error": "location required"}), 400

        # Parse location
        parts = [p.strip() for p in location.split(",")]
        if len(parts) < 2:
            return (
                jsonify(
                    {"error": "location must be 'City, ST' format (e.g., 'Dallas, TX')"}
                ),
                400,
            )

        city = parts[0]
        state = parts[1]

        try:
            # Get events
            import asyncio
            from backend.event_discovery import EventCacheManager

            manager = EventCacheManager(
                db=db, event_model=Event, event_image_model=EventImage
            )

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                ctx = app.app_context()
                ctx.push()

                try:
                    events = loop.run_until_complete(
                        manager.discover_tonight(
                            city, state, limit=100
                        )  # Get more events for personalization
                    )
                finally:
                    ctx.pop()
            finally:
                loop.close()

            # Also get Google Custom Search volunteer opportunities
            web_events = []
            try:
                web_query = f"volunteer opportunities {city} {state}"
                from google_search import (
                    search_events,
                    create_events_from_search_results,
                    enrich_events_with_contact_info,
                    enrich_events_with_values,
                )

                search_results = search_events(web_query)

                if isinstance(search_results, list) and len(search_results) > 0:
                    event_dicts = create_events_from_search_results(
                        search_results,
                        web_query,
                        location={"city": city, "state": state},
                    )
                    # Enrich with values for better personalization
                    event_dicts = enrich_events_with_values(
                        event_dicts, max_to_enrich=5
                    )
                    web_events = event_dicts
                    app.logger.info(
                        f"Personalized feed: added {len(web_events)} web search results"
                    )
            except Exception as web_error:
                app.logger.info(
                    f"Web search error in personalized feed (non-fatal): {web_error}"
                )

            # Combine database events with web events before personalization
            all_events = events + web_events
            app.logger.info(
                f"Personalized: {len(events)} database + {len(web_events)} web = {len(all_events)} total"
            )

            # Personalize the feed with AI
            from backend.event_discovery.personalization import PersonalizationEngine

            engine = PersonalizationEngine(db, User, Event, UserEventInteraction)

            # Use AI-powered personalization
            loop2 = asyncio.new_event_loop()
            asyncio.set_event_loop(loop2)

            try:
                ctx2 = app.app_context()
                ctx2.push()

                try:
                    personalized = loop2.run_until_complete(
                        engine.get_ai_personalized_recommendations(
                            uid_int, all_events, limit=limit
                        )
                    )
                finally:
                    ctx2.pop()
            finally:
                loop2.close()

            return (
                jsonify(
                    {
                        "events": personalized,
                        "location": f"{city}, {state}",
                        "count": len(personalized),
                        "personalized": True,
                    }
                ),
                200,
            )

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route("/api/profile/taste", methods=["GET"])
    @jwt_required()
    def get_taste_profile():
        """Get user's taste profile (category preferences, etc.)."""
        uid = get_jwt_identity()
        try:
            uid_int = int(uid)
        except Exception:
            uid_int = uid

        from backend.event_discovery.personalization import PersonalizationEngine

        engine = PersonalizationEngine(db, User, Event, UserEventInteraction)
        profile = engine.calculate_user_taste_profile(uid_int)

        return jsonify({"profile": profile, "user_id": uid_int}), 200

    @app.route("/api/events/surprise-me", methods=["POST"])
    @jwt_required()
    def surprise_me():
        """Get surprise event recommendation based on mood and constraints."""
        uid = get_jwt_identity()
        try:
            uid_int = int(uid)
        except Exception:
            uid_int = uid

        data = request.get_json() or {}
        location = data.get("location")
        mood = data.get(
            "mood", "adventurous"
        )  # energetic, chill, creative, social, romantic, adventurous
        budget = data.get("budget", 50)  # max price
        time_available = data.get("time_available", 3)  # hours
        adventure_level = data.get("adventure_level", "high")  # low, medium, high

        if not location:
            return jsonify({"error": "location required"}), 400

        parts = [p.strip() for p in location.split(",")]
        if len(parts) < 2:
            return jsonify({"error": "location must be 'City, ST' format"}), 400

        city = parts[0]
        state = parts[1]

        try:
            # Get events from both volunteer opportunities AND Ticketmaster
            import asyncio
            from backend.event_discovery import EventCacheManager
            from backend.ticketmaster_api import TicketmasterAPI

            manager = EventCacheManager(
                db=db, event_model=Event, event_image_model=EventImage
            )

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                ctx = app.app_context()
                ctx.push()

                try:
                    # Get volunteer events
                    volunteer_events = loop.run_until_complete(
                        manager.discover_tonight(city, state, limit=50)
                    )
                finally:
                    ctx.pop()
            finally:
                loop.close()

            # Also fetch Ticketmaster events
            ticketmaster_events = []
            try:
                tm_api = TicketmasterAPI()
                ticketmaster_events = tm_api.get_events_for_city(city, state, limit=50)
            except Exception as tm_error:
                print(f"Ticketmaster API error (non-fatal): {tm_error}")

            # Fetch Google Custom Search volunteer opportunities
            web_events = []
            try:
                # Build mood-specific search query
                mood_keywords = {
                    "energetic": "active sports fitness",
                    "chill": "relaxing peaceful",
                    "creative": "arts crafts creative",
                    "social": "community social gathering",
                    "romantic": "couples romantic",
                    "adventurous": "adventure outdoor exciting",
                }
                keyword = mood_keywords.get(mood, "")
                web_query = f"volunteer opportunities {keyword} {city} {state}"

                # Search and convert to events
                from google_search import (
                    search_events,
                    create_events_from_search_results,
                    enrich_events_with_contact_info,
                    enrich_events_with_values,
                )

                search_results = search_events(web_query)
                if isinstance(search_results, list) and len(search_results) > 0:
                    event_dicts = create_events_from_search_results(
                        search_results,
                        web_query,
                        location={"city": city, "state": state},
                    )
                    # Enrich with values (small batch for surprise feature)
                    event_dicts = enrich_events_with_values(
                        event_dicts, max_to_enrich=3
                    )

                    # Convert to Event objects format that SurpriseEngine expects
                    for event_dict in event_dicts:
                        web_events.append(event_dict)
            except Exception as web_error:
                app.logger.info(f"Web search error (non-fatal): {web_error}")

            # Combine all three event sources
            all_events = volunteer_events + ticketmaster_events + web_events
            app.logger.info(
                f"Surprise Me: {len(volunteer_events)} volunteer + {len(ticketmaster_events)} ticketmaster + {len(web_events)} web = {len(all_events)} total"
            )

            # Generate AI-powered surprise event
            from backend.event_discovery.surprise_engine import SurpriseEngine

            surprise_engine = SurpriseEngine(db, User, Event, UserEventInteraction)

            # Use AI to generate surprise
            loop2 = asyncio.new_event_loop()
            asyncio.set_event_loop(loop2)

            try:
                ctx2 = app.app_context()
                ctx2.push()

                try:
                    surprise_event = loop2.run_until_complete(
                        surprise_engine.generate_ai_surprise(
                            user_id=uid_int,
                            location=city,
                            mood=mood,
                            budget=budget,
                            time_available=time_available
                            * 60,  # Convert hours to minutes
                            adventure_level=adventure_level,
                        )
                    )
                finally:
                    ctx2.pop()
            finally:
                loop2.close()

            if not surprise_event:
                return jsonify({"error": "No surprising events found"}), 404

            return (
                jsonify(
                    {
                        "event": surprise_event,
                        "surprise": True,
                        "mood": mood,
                        "explanation": surprise_event.get("surprise_explanation", ""),
                    }
                ),
                200,
            )

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route("/api/events/ticketmaster", methods=["POST"])
    @jwt_required()
    def get_ticketmaster_events():
        """Fetch real future events from Ticketmaster Discovery API."""
        data = request.get_json() or {}
        location = data.get("location")
        limit = data.get("limit", 50)
        classification = data.get(
            "classification"
        )  # Optional: Music, Sports, Arts & Theatre, etc.

        if not location:
            return jsonify({"error": "location required"}), 400

        parts = [p.strip() for p in location.split(",")]
        if len(parts) < 2:
            return jsonify({"error": "location must be 'City, ST' format"}), 400

        city = parts[0]
        state_code = parts[1]

        try:
            from backend.ticketmaster_api import TicketmasterAPI

            tm_api = TicketmasterAPI()

            events = tm_api.get_events_for_city(
                city=city,
                state_code=state_code,
                limit=limit,
                classification=classification,
            )

            return (
                jsonify(
                    {
                        "events": events,
                        "count": len(events),
                        "source": "Ticketmaster",
                        "city": city,
                        "state": state_code,
                    }
                ),
                200,
            )

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route("/api/achievements", methods=["GET"])
    @jwt_required()
    def get_achievements():
        """Get user's achievements and progress (role-aware)."""
        uid = get_jwt_identity()
        try:
            uid_int = int(uid)
        except Exception:
            uid_int = uid

        # Get user to check role
        user = User.query.get(uid_int)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Role-aware response
        if user.role == "organization":
            # Organizations get different metrics
            # Count events posted by this organization
            events_posted = Event.query.filter_by(
                organization=user.organization_name
            ).count()

            # Count total interactions with organization's events
            org_events = Event.query.filter_by(
                organization=user.organization_name
            ).all()
            org_event_ids = [e.id for e in org_events]

            total_views = UserEventInteraction.query.filter(
                UserEventInteraction.event_id.in_(org_event_ids),
                UserEventInteraction.interaction_type == "view",
            ).count()

            total_likes = UserEventInteraction.query.filter(
                UserEventInteraction.event_id.in_(org_event_ids),
                UserEventInteraction.interaction_type.in_(["like", "super_like"]),
            ).count()

            total_attendees = UserEventInteraction.query.filter(
                UserEventInteraction.event_id.in_(org_event_ids),
                UserEventInteraction.interaction_type == "attend",
            ).count()

            # Unique volunteers (distinct users who interacted)
            unique_volunteers = (
                db.session.query(UserEventInteraction.user_id)
                .filter(UserEventInteraction.event_id.in_(org_event_ids))
                .distinct()
                .count()
            )

            return (
                jsonify(
                    {
                        "role": "organization",
                        "organization_name": user.organization_name,
                        "metrics": {
                            "events_posted": events_posted,
                            "total_views": total_views,
                            "total_likes": total_likes,
                            "total_attendees": total_attendees,
                            "unique_volunteers": unique_volunteers,
                            "engagement_rate": (
                                round((total_likes / max(total_views, 1)) * 100, 1)
                                if total_views > 0
                                else 0
                            ),
                        },
                    }
                ),
                200,
            )

        else:
            # Volunteers get achievement system
            achievements = UserAchievement.query.filter_by(user_id=uid_int).all()

            # Calculate level and XP
            from backend.event_discovery.gamification import GamificationEngine

            gamification = GamificationEngine(
                db, User, UserAchievement, UserEventInteraction
            )
            level_info = gamification.get_user_level(uid_int)

            return (
                jsonify(
                    {
                        "role": "volunteer",
                        "achievements": [a.to_dict() for a in achievements],
                        "unlocked_count": sum(1 for a in achievements if a.unlocked),
                        "total_count": len(achievements),
                        "level_info": level_info,
                    }
                ),
                200,
            )

    admin_bp = Blueprint("admin", __name__)

    ADMIN_EMAILS = set(
        [
            "your@email.com",  # Replace with your email
            "dev1@email.com",  # Add your dev team emails
        ]
    )
    PENDING_ADMINS = set()

    @admin_bp.route("/login", methods=["POST"])
    def admin_login():
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid credentials"}), 401
        if email not in ADMIN_EMAILS:
            PENDING_ADMINS.add(email)
            # Optionally notify existing admins here
            return jsonify({"error": "Admin access pending manual approval"}), 403
        from auth import token_for

        token = token_for(user.id)
        return jsonify({"access_token": token, "user": user.to_dict()})

    @admin_bp.route("/pending", methods=["GET"])
    @jwt_required()
    def get_pending_admins():
        uid = get_jwt_identity()
        user = User.query.get(uid)
        if not user or user.email not in ADMIN_EMAILS:
            return jsonify({"error": "Not authorized"}), 403
        return jsonify({"pending_admins": list(PENDING_ADMINS)})

    @admin_bp.route("/approve", methods=["POST"])
    @jwt_required()
    def approve_admin():
        uid = get_jwt_identity()
        user = User.query.get(uid)
        if not user or user.email not in ADMIN_EMAILS:
            return jsonify({"error": "Not authorized"}), 403
        data = request.get_json() or {}
        email = data.get("email")
        if email in PENDING_ADMINS:
            ADMIN_EMAILS.add(email)
            PENDING_ADMINS.remove(email)
            return jsonify({"approved": email})
        return jsonify({"error": "Email not pending"}), 400

    app.register_blueprint(admin_bp, url_prefix="/admin")
