#!/bin/bash
set -euo pipefail

echo "[entrypoint] Starting container entrypoint"

# Default port
PORT=${PORT:-5000}

echo "[entrypoint] Starting gunicorn on 0.0.0.0:${PORT}"
exec gunicorn -w ${GUNICORN_WORKERS:-4} -b 0.0.0.0:${PORT} wsgi:application
