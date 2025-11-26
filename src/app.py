"""
Entry point for Tapin_Correct.

Rather than using the default 4Geeks blueprint scaffold, we boot the Tapin_
backend (now copied under src/backend) and only add the static file serving
needed for the Vite front-end build in dist/.
"""

import os
from flask import send_from_directory
from backend.app import create_app

app = create_app()

ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dist/")


@app.route("/")
def sitemap():
    """
    Serve Vite's index.html.
    """
    return send_from_directory(static_file_dir, "index.html")


@app.route("/<path:path>", methods=["GET"])
def serve_any_other_file(path):
    """
    Serve static assets built by Vite. Unknown paths fall back to index.html
    so the SPA router can handle them.
    """
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = "index.html"
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0  # avoid cache memory
    return response


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3001))
    app.run(host="0.0.0.0", port=PORT, debug=True)
