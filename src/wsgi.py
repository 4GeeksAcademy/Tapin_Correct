# This file was created to run the application on heroku using gunicorn.
# Read more about it here: https://devcenter.heroku.com/articles/python-gunicorn

try:
    # Try backend module import first (Docker/production)
    from backend.app import app as application
except ModuleNotFoundError:
    # Fallback to direct import (local development)
    from app import app as application

if __name__ == "__main__":
    application.run()
