#!/bin/sh
set -e

echo "[entrypoint] Starting container entrypoint"

# Default port
PORT=${PORT:-5000}

echo "[entrypoint] Checking whether to create DB tables"
# Only create tables on startup when explicitly allowed or when using sqlite
if [ "${RUN_MIGRATIONS_ON_START}" = "1" ] || [ "${RUN_MIGRATIONS_ON_START,,}" = "true" ]; then
  echo "[entrypoint] RUN_MIGRATIONS_ON_START set -> creating DB tables"
  python - <<'PY'
from backend.app import app, db
with app.app_context():
    try:
        db.create_all()
        print("[entrypoint] db.create_all() completed")
    except Exception as e:
        print(f"[entrypoint] db.create_all() error: {e}")
PY
else
  DB_URL=${SQLALCHEMY_DATABASE_URI:-${DATABASE_URL:-}}
  case "${DB_URL}" in
    sqlite:*)
      echo "[entrypoint] Detected sqlite DB URL -> creating DB tables (dev)"
      python - <<'PY'
from backend.app import app, db
with app.app_context():
    try:
        db.create_all()
        print("[entrypoint] db.create_all() completed")
    except Exception as e:
        print(f"[entrypoint] db.create_all() error: {e}")
PY
      ;;
    *)
      echo "[entrypoint] Skipping create_all() (RUN_MIGRATIONS_ON_START not set and DB is not sqlite)"
      ;;
  esac
fi

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
