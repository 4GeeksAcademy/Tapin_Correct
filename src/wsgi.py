"""
WSGI config for the Tapin application.
It exposes the WSGI callable as a module-level variable named ``application``.
This imports the full app wrapper that serves both backend API and frontend.
"""

import os
import sys

# Add src directory to path so we can import src.app
sys.path.insert(0, "/app")

try:
    # Import the full app that includes both backend API and frontend serving
    from src.app import app as application
except Exception as e:
    print(f"Error importing Tapin application in wsgi.py: {e}")
    # Fallback to backend-only if the full app fails
    try:
        from backend.app import create_app

        application = create_app()
        print("Loaded backend-only app as fallback")
    except Exception as fallback_error:
        print(f"Error creating fallback Flask application: {fallback_error}")
        from flask import Flask

        application = Flask("error_app")

        @application.route("/")
        def error_page():
            return "Application failed to start. Check logs for details.", 500


if __name__ == "__main__":
    # This block is for local development and won't be executed by Gunicorn
    port = int(os.environ.get("PORT", 5000))
    application.run(host="0.0.0.0", port=port, debug=True)
