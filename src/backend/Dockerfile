# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app

# Copy frontend package files and install dependencies
COPY src/front/package.json src/front/package-lock.json ./
WORKDIR /app
RUN mkdir -p src/front
WORKDIR /app/src/front
RUN npm ci --silent

# Copy frontend source and build
COPY src/front/ /app/src/front/
RUN npm run build

# Stage 2: Backend
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y gcc postgresql-client curl && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY src/backend/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    pip install gunicorn

# Copy backend source and wsgi
COPY src/backend /app/backend
COPY src/wsgi.py /app/wsgi.py
COPY src/app.py /app/src/app.py

# Copy built frontend from the frontend-build stage
COPY --from=frontend-build /app/src/front/dist /app/dist

# Copy entrypoint and make executable
COPY src/backend/docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Set PYTHONPATH so 'backend' module is importable
ENV PYTHONPATH=/app:/app/backend
ENV PORT=8080

# Create data directory for SQLite or local storage
RUN mkdir -p /app/data && chmod 777 /app/data

EXPOSE 8080

# Use entrypoint script to start gunicorn
ENTRYPOINT ["/app/docker-entrypoint.sh"]
