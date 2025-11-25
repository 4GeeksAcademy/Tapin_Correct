**Deployment / Production run notes**

- Use a real database in production by setting `SQLALCHEMY_DATABASE_URI` (e.g. a Postgres URL) in the environment.
- Supply secrets as environment variables: `SECRET_KEY`, `JWT_SECRET_KEY`, `SECURITY_PASSWORD_SALT`.

Docker build and run (example):

```bash
# build image from repo root
docker build -t tapin-backend -f src/backend/Dockerfile .

# Run with a real DB (example using a Postgres connection string)
docker run -e SQLALCHEMY_DATABASE_URI="postgresql://user:pass@db:5432/tapin" \  # pragma: allowlist secret
  -e JWT_SECRET_KEY="your-jwt-secret" \  # pragma: allowlist secret
  -e SECRET_KEY="your-secret" \  # pragma: allowlist secret
  -e SEED_DB=1 \
  -p 5000:5000 \
  tapin-backend
```

Notes:

- The container will run `update_schema.py` at startup to ensure tables exist.
- If `SEED_DB=1` the container will try `seed_sample_data.py` then `seed_data.py` to populate demo records (useful for staging).
- For production do NOT set `SEED_DB=1` unless you intentionally want to populate/reset sample data.

CI / Playwright:

- Playwright in `src/front/playwright.config.js` will use a real backend by default.
- To run Playwright with the lightweight mock API set `USE_MOCK_API=1` in the environment.

Perplexity integration:

- To enable Perplexity-powered event search set the following env vars:
  - `PERPLEXITY_API_KEY` — your API key
  - `PERPLEXITY_API_URL` — the full Perplexity-compatible endpoint URL

When configured the backend will call Perplexity for `/api/search/events`.
