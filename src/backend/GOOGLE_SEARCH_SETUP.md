# Google Custom Search API Setup Guide

## Current Status
The Google Custom Search categorization system has been improved with:
- ✅ Comprehensive keyword mappings for all 14 volunteer categories
- ✅ Intelligent scoring system for accurate categorization
- ✅ Tested and working categorization logic

## Required: Enable Google Custom Search API

Your Google API key needs the Custom Search API enabled. Follow these steps:

### Step 1: Enable the API
Visit this link and click "Enable":
```
https://console.developers.google.com/apis/api/customsearch.googleapis.com/overview?project=400528003056
```

### Step 2: Wait for Propagation
After enabling, wait 2-5 minutes for the changes to propagate through Google's systems.

### Step 3: Test the Configuration
Run this test command from the backend directory:
```bash
PYTHONPATH=/Users/houseofobi/Documents/GitHub/Tapin_Correct/src/backend \
LLM_PROVIDER=google \
pipenv run python test_live_search.py
```

## Environment Configuration

Your `.env` file is configured with:
- **GOOGLE_API_KEY**: `AIzaSyCBioWdfsoySHMApqtODg89ARRVhkZ5B5s`
- **CUSTOM_SEARCH_ENGINE_ID**: `f1aaf5481229a485d`
- **LLM_PROVIDER**: `google`

## How the Categorization Works

### Keyword-Based Scoring System
The improved `refine_and_categorize()` function uses:

1. **Comprehensive Keyword Mappings**: Each category has 10-15 relevant keywords
   - Example: "Animal Welfare" includes: animal, pet, wildlife, shelter, rescue, zoo, etc.

2. **Weighted Scoring**:
   - Exact category name match: 3 points per occurrence
   - Related keyword match: 1 point per occurrence
   - Higher score = better category match

3. **Context Analysis**:
   - Combines both title and snippet for comprehensive matching
   - Case-insensitive matching
   - Handles multiple keyword occurrences

### Categories Supported
- Animal Welfare
- Arts & Culture
- Children & Youth
- Community Development
- Disaster Relief
- Education & Literacy
- Environment
- Health & Medicine
- Human Rights
- Seniors
- Social Services
- Sports & Recreation
- Technology
- Women's Issues

### Example Categorization
```python
# Input:
"Animal Shelter Volunteers Needed - Help care for dogs and cats"

# Process:
Keywords matched: "animal" (1), "shelter" (1), "dogs" (1), "cats" (1)
Score: 4 points for "Animal Welfare"

# Output:
Category: "Animal Welfare" ✓
```

## Quota Management

The system includes built-in quota tracking:
- Default limit: 100 requests/month (configurable via `GOOGLE_MAX_REQUESTS_PER_MONTH`)
- Automatic monthly reset
- Usage tracking in `.usage/google_usage.json`

## Testing Without API

To test categorization logic without making API calls:
```bash
PYTHONPATH=/Users/houseofobi/Documents/GitHub/Tapin_Correct/src/backend \
pipenv run python test_categorization.py
```

## Troubleshooting

### Error: "Custom Search API has not been used"
- Solution: Follow Step 1 above to enable the API
- Wait 2-5 minutes after enabling

### Error: "Quota exceeded"
- Check current usage in `.usage/google_usage.json`
- Increase `GOOGLE_MAX_REQUESTS_PER_MONTH` in `.env`
- Wait until next month for reset

### Poor Categorization Results
- Review keyword mappings in `CATEGORY_KEYWORDS` dictionary
- Add domain-specific keywords for your use case
- Consider adjusting scoring weights in `refine_and_categorize()`

## API Costs

Google Custom Search API pricing:
- First 100 queries/day: Free
- Additional queries: $5 per 1000 queries
- Recommendation: Set appropriate quota limits in `.env`
