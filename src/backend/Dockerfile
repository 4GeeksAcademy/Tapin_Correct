# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Working directory
WORKDIR /app

# Copy backend requirements and install
COPY src/backend/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel && \
	pip install -r requirements.txt && \
	pip install gunicorn

# Copy backend source as 'backend' directory to match import structure
COPY src/backend /app/backend
# Copy wsgi entrypoint from repo root `src/wsgi.py` so gunicorn can import it
COPY src/wsgi.py /app/wsgi.py

# Copy entrypoint script
COPY src/backend/docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Set PYTHONPATH so 'backend' module is importable
ENV PYTHONPATH=/app:/app/backend

# Expose port
EXPOSE 5000

# Entrypoint to run migrations/seed and start gunicorn
ENTRYPOINT ["/app/docker-entrypoint.sh"]
