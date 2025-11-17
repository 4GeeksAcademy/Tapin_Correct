# Backend Configuration & Secrets

This document lists the environment variables used by the Tapin backend, recommended defaults for local development, and guidance for storing secrets in CI (GitHub Actions).

## Required / important environment variables

- `SECRET_KEY` — Flask secret key. Defaults to a dev value in code, but _must_ be set to a strong secret in production.
- `JWT_SECRET_KEY` — Key used to sign JWTs. Defaults to `SECRET_KEY` when not provided but should be unique in production.
- `SECURITY_PASSWORD_SALT` — Salt for password reset tokens. Replace the dev value in production.

Optional but recommended:
- `SQLALCHEMY_DATABASE_URI` — Connection string for the database. Defaults to `sqlite:///backend/data.db`.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_USE_TLS` — Mail server settings for sending password reset emails.

## Event Discovery / LLM Configuration

The event discovery feature uses an LLM to extract volunteer opportunities from nonprofit websites. Configure the following:

- `LLM_PROVIDER` — Which LLM backend to use. Options:
  - `gemini` (default) — Google Gemini API (recommended for production)
  - `ollama` — Local Ollama instance (for development/testing)
  - `mock` — Returns mock data (for testing without API keys)

- `GEMINI_API_KEY` — Your Google Gemini API key. Required when `LLM_PROVIDER=gemini`.
  - Get a key at: https://aistudio.google.com/app/apikey
  - Alternative: Set `GOOGLE_API_KEY` or `GOOGLE_APPLICATION_CREDENTIALS`

- `GEMINI_MODEL` — Gemini model to use. Default: `gemini-2.5-flash-lite`
  - Options: `gemini-2.5-flash-lite` (fast, cheap), `gemini-1.5-flash`, `gemini-1.5-pro`

- `OLLAMA_MODEL` — Ollama model for local inference. Default: `mistral`
  - Requires Ollama running locally: https://ollama.ai

**Cost Considerations:**
- Gemini Flash-Lite: ~$0.075 per 1M input tokens (very cost-effective)
- Estimated cost: $150/month for nationwide coverage
- Free tier available for development (60 requests/minute)

## Local development

1. Copy `.env.sample` to `.env` in the repository root and edit values.
2. Install dev dependencies: `pip install -r backend/requirements.txt`.
3. Start the app (from repo root):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python backend/app.py
```

The app will automatically load `.env` (if `python-dotenv` is installed) and pick up values.

## GitHub Actions / CI

Store secrets in your repository or organization settings (`Settings > Secrets and variables > Actions`). Name them as follows (example):

- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `SECURITY_PASSWORD_SALT`
- `SMTP_USER`, `SMTP_PASS` (if you need SMTP in CI)

In workflow files, reference secrets via `${{ secrets.SECRET_KEY }}`. Example excerpt for `.github/workflows/backend-tests.yml`:

```yaml
env:
  SECRET_KEY: ${{ secrets.SECRET_KEY }}
  JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}
  SECURITY_PASSWORD_SALT: ${{ secrets.SECURITY_PASSWORD_SALT }}
  SQLALCHEMY_DATABASE_URI: sqlite:///backend/data.db
  LLM_PROVIDER: mock  # Use mock for CI tests
  # For production with real LLM:
  # LLM_PROVIDER: gemini
  # GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

Notes:
- Do not commit real secrets into the repository.
- For production, prefer a managed secret store (cloud provider secrets, HashiCorp Vault, etc.).

## Production Deployment Checklist

### Event Discovery Setup

1. **Get Gemini API Key:**
   ```bash
   # Visit https://aistudio.google.com/app/apikey
   # Create a new API key for your project
   ```

2. **Set Environment Variables:**
   ```bash
   export LLM_PROVIDER=gemini
   export GEMINI_API_KEY=your-api-key-here
   export GEMINI_MODEL=gemini-2.5-flash-lite
   ```

3. **Database Migration:**
   ```bash
   cd src/backend
   pipenv run alembic upgrade head
   ```

4. **Test the Setup:**
   ```bash
   curl "http://localhost:5000/events/search?city=Austin&state=TX"
   ```

5. **Monitor Usage:**
   - Check Google Cloud Console for API usage
   - Monitor cache hit rates in application logs
   - Events are cached for 30 days by default

### Scaling Considerations

- **Cache Strategy:** Events are cached by geohash (precision 6 for city-level)
- **Parallel Scraping:** Up to 10 nonprofits per state scraped concurrently
- **TTL Management:** Run `scripts/cleanup_cache.py` daily via cron to remove expired entries
- **Database:** Consider PostgreSQL for production (Supabase-compatible)
