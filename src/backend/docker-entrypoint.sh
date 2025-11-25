#!/bin/sh
set -e

echo "[entrypoint] Starting container entrypoint"

# Default port
PORT=${PORT:-5000}

echo "[entrypoint] Ensuring DB tables exist (calling SQLAlchemy create_all)"
python - <<'PY'
from app import app, db
with app.app_context():
    try:
        db.create_all()
        print("[entrypoint] db.create_all() completed")
    except Exception as e:
        print(f"[entrypoint] db.create_all() error: {e}")
PY

if [ "${SEED_DB}" = "1" ]; then
  echo "[entrypoint] SEED_DB=1, seeding database"
  if [ -f seed_sample_data.py ]; then
    python seed_sample_data.py || true
  elif [ -f seed_data.py ]; then
    python seed_data.py || true
  else
    echo "[entrypoint] No seed script found, skipping"
  fi
else
  echo "[entrypoint] SEED_DB not set or !=1; skipping seeding"
fi

echo "[entrypoint] Starting gunicorn on 0.0.0.0:${PORT}"
exec gunicorn -w ${GUNICORN_WORKERS:-4} -b 0.0.0.0:${PORT} wsgi:application
