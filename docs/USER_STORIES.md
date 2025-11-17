# PM Stories: Nationwide Event Discovery & Caching

These user stories capture the work necessary to implement on-demand nationwide volunteer event discovery, geolocation caching, and LLM-powered scraping. They are derived directly from `new-features.md` and include concrete implementation notes (geohash precision, DB schema recommend, LLM strategy).

## Epic: On-demand Nationwide Event Discovery

As a user, I want to search for volunteer opportunities by city/state and get fresh, relevant results quickly, so that I can find opportunities near me without stale data.

Acceptance criteria:

- Search endpoint returns results within 2-5s for a first-time cache miss and <1s for cache hits.
- Results include title, organization, date (or null), location (city/state), lat/lon, url, and source.
- Results are cached with a TTL and returned from the DB when present.

Stories:

1. Story: Install scraping & LLM runtime (high priority)
   - Add Python deps to `src/backend/Pipfile`: `playwright`, `langchain`, `langchain-google-genai`, `langchain-community`, `geopy`, `geohash2`.
   - Run `pipenv install` and `pipenv run python -m playwright install chromium` (or `playwright install chromium` in the venv).
   - Smoke test: import `PlaywrightURLLoader` and call a minimal loader on a static page; ensure no import errors.
   - Acceptance: Playwright and LangChain connectors import and a minimal LLM invocation or stub returns successfully.

2. Story: Persist scraped events (high priority)
   - Add an `Event` SQLAlchemy model and DB migrations (Postgres preferred). For local dev, SQLite-compatible model is acceptable.
   - Recommended columns: `id (uuid)`, `title`, `organization`, `description`, `date_start`, `location_city`, `location_state`, `latitude`, `longitude`, `geohash_4`, `geohash_6`, `url`, `source`, `scraped_at`, `cache_expires_at`.
   - Wire `EventCacheManager` to upsert scraped events using URL or title+org+date as dedupe keys; set `cache_expires_at` (suggested default: 30 days).
   - Acceptance: After running a search, new rows appear in the `events` table and subsequent searches for the same geohash return `cached: true`.

   Implementation notes (from `new-features.md`):
   - Use geohash precision 6 for city-level caching, and precision 4 for broader regional grouping.
   - Index `geohash_6` and `cache_expires_at` for efficient lookups and cleanup.

3. Story: Geohash-based lookup & cache semantics
   - Use geohash precision 6 for city-level cache and precision 4 for regional grouping.
   - Implement cache hit lookup and return cached events when fresh.
   - Acceptance: Cache hit returns DB rows and sets `cached: true` in API response.

4. Story: Cache invalidation & housekeeping
   - Add a scheduled job to delete expired cache entries daily.
   - Acceptance: Expired rows removed after job runs.

5. Story: LLM hybrid (Gemini dev / Ollama prod)
   - Implement an LLM wrapper that prefers `ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")` during development and falls back to a local Ollama model in production if available.
   - Provide environment variable toggles (e.g., `LLM_PROVIDER=gemini|ollama|mock`) for testing.
   - Acceptance: Wrapper returns valid JSON for a test HTML payload when using the Gemini connector (or returns stubbed JSON in offline dev).

Priority: Stories 1 and 2 are highest priority for enabling functionality and testing. Stories 3-5 follow once persistence and runtime are stable.

--
PM: create tasks from these stories and assign to engineering as needed.
