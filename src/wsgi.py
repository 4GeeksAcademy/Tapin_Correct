"""
WSGI config for the backend application.
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

from backend.app import create_app
import os

# Create the Flask app instance
try:
    application = create_app()
except Exception as e:
    print(f"Error creating Flask application in wsgi.py: {e}")
    # Optionally, create a minimal fallback app for debugging
    from flask import Flask

    application = Flask("error_app")

    @application.route("/")
    def error_page():
        return "Application failed to start. Check logs for details.", 500


if __name__ == "__main__":
    # This block is for local development and won't be executed by Gunicorn
    port = int(os.environ.get("PORT", 5000))
    application.run(host="0.0.0.0", port=port, debug=True)
