#!/bin/bash
# Run the test suite with Perplexity AI

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/src/backend"

echo "🧪 Running Tapin Correct Test Suite with Perplexity AI"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

PYTHONPATH="$SCRIPT_DIR/src/backend" \
LLM_PROVIDER=perplexity \
PERPLEXITY_API_KEY="REDACTED_PERPLEXITY" \
pipenv run pytest tests/test_event_discovery_api.py tests/test_api.py tests/test_auth.py tests/test_listings.py -v --tb=short

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Test suite completed!"
