#!/bin/bash
set -euo pipefail

echo "[entrypoint] Starting container entrypoint"

# Default port (align with fly.toml)
PORT=${PORT:-8080}

echo "[entrypoint] Starting gunicorn on 0.0.0.0:${PORT}"
exec gunicorn -w ${GUNICORN_WORKERS:-2} -b 0.0.0.0:${PORT} wsgi:application
