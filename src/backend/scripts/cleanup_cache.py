"""Utility: cleanup expired cached events.

Run this daily (cron, GitHub Actions) to remove expired cache entries.
"""

from datetime import datetime, timezone
import os
import sys

# Ensure the repo src is on PYTHONPATH when invoked from project root
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_root = os.path.join(repo_root, "..")
if src_root not in sys.path:
    sys.path.insert(0, src_root)

from backend.app import db, Event  # noqa: E402


def cleanup_expired():
    now = datetime.now(timezone.utc)
    expired = Event.query.filter(
        Event.cache_expires_at.isnot(None),
        Event.cache_expires_at < now,
    )
    count = expired.count()
    if count:
        expired.delete(synchronize_session=False)
        db.session.commit()
    print(f"Cleaned up {count} expired cached events")


if __name__ == "__main__":
    cleanup_expired()
