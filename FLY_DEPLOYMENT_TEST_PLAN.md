# Fly.io Deployment Test and Debugging Plan

This document outlines the steps to test and debug the Fly.io deployment for the Tapin_Correct application.

## 1. Local Verification

Before deploying to Fly.io, we need to ensure the application can run correctly in a local containerized environment that mimics the Fly.io setup.

### 1.1. Build the Docker Image

Build the Docker image using the same Dockerfile that Fly.io uses.

```bash
docker build -t tapin-correct-local -f src/backend/Dockerfile .
```

### 1.2. Run the Docker Container Locally

Run the container, providing the necessary environment variables. You will need a `.env` file with your local or a test database URL.

```bash
docker run -it --rm -p 5000:5000 --env-file .env tapin-correct-local
```

**Expected Outcome:** The container should start without errors, and you should see Gunicorn startup logs. You should be able to access the application at `http://localhost:5000`.

## 2. Fly.io Deployment and Debugging

Once the application runs locally, we can proceed with deploying to Fly.io and debugging any issues that arise.

### 2.1. Deploy to Fly.io

Deploy the `experiment` branch to Fly.io.

```bash
fly deploy
```

### 2.2. Monitor Logs

Immediately after starting the deployment, monitor the logs for any errors.

```bash
fly logs
```

Look for:

- Python stack traces
- Database connection errors
- `gunicorn` errors
- Health check failures

### 2.3. Check Machine Status

Check the status of the machines to see if they are starting, running, or stuck in a restart loop.

```bash
fly status
```

### 2.4. Interactive Debugging (if necessary)

If the application fails to start, connect to the running machine for interactive debugging.

```bash
fly ssh console
```

Once inside the machine, you can:

- Check environment variables: `printenv`
- Manually run the entrypoint script: `/app/src/backend/docker-entrypoint.sh`
- Check network connectivity
- Run `ps aux` to see running processes.

## 3. Common Issues and Solutions

- **Database Connection Errors:**
  - **`invalid dsn: invalid connection option "pool_mode"`:** This was addressed by sanitizing the database URL. Verify the fix is working.
  - **Connection refused:** Ensure the database is accessible from the Fly.io app and that the `DATABASE_URL` is correct.
- **`Bad substitution` in `docker-entrypoint.sh`:** This was addressed by changing the shebang to `#!/bin/bash`. Verify the fix.
- **Health Check Failures:** This is usually a symptom of the application not starting correctly. Address the root cause found in the logs.
- **Application Errors:** If the application starts but is not behaving correctly, check the application logs for Python errors.

By following this plan, we can systematically debug the deployment and get the application running on Fly.io.
