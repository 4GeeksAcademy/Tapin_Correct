# AI-Powered Features Setup Guide

This guide explains how to set up and use the AI-powered personalization and surprise features with the HybridLLM system.

## Overview

The cutting-edge features now use **AI (LLM)** to provide:
- **AI-Powered Personalization**: Intelligent event recommendations with natural language explanations
- **Surprise Me AI**: Creative, unexpected event suggestions based on mood and context

## Supported LLM Providers

The system supports multiple LLM providers through the **HybridLLM** system:

1. **Perplexity** (Recommended for production)
2. **Ollama** (Local, free, good for development)
3. **Google Gemini** (Cloud, requires API key)

## Quick Setup - Perplexity API

### Step 1: Get Perplexity API Key

1. Visit https://www.perplexity.ai/
2. Sign up or log in
3. Navigate to API settings
4. Generate an API key

### Step 2: Configure Environment Variables

Add to your `.env` file:

```bash
# AI Configuration
LLM_PROVIDER=perplexity
PERPLEXITY_API_KEY=your-perplexity-api-key-here
PERPLEXITY_MODEL=sonar  # Or: sonar-pro, sonar-reasoning
```

### Step 3: Restart Backend

```bash
cd src/backend
python app.py
```

The system will automatically use Perplexity for AI features!

## Alternative Setup - Ollama (Local, Free)

### Step 1: Install Ollama

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Or download from https://ollama.com/download
```

### Step 2: Pull a Model

```bash
# Recommended: Mistral (fast, good quality)
ollama pull mistral

# Or try other models:
ollama pull llama3
ollama pull qwen2.5
```

### Step 3: Configure Environment

Add to your `.env` file:

```bash
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral
OLLAMA_API_URL=http://localhost:11434  # Default
```

### Step 4: Start Ollama

```bash
ollama serve
```

The system will automatically connect to your local Ollama instance!

## Alternative Setup - Google Gemini

### Step 1: Get Gemini API Key

1. Visit https://makersuite.google.com/app/apikey
2. Create an API key

### Step 2: Configure Environment

Add to your `.env` file:

```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.5-flash-lite  # Or: gemini-2.0-flash
```

## Testing AI Features

### Test AI Personalization

```bash
curl -X POST http://localhost:5000/api/events/personalized \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Dallas, TX",
    "limit": 10
  }'
```

Expected response:
```json
{
  "events": [
    {
      "title": "Jazz Night at The Majestic",
      "category": "Music & Concerts",
      "ai_match_score": 95,
      "ai_explanation": "Perfect match because you love jazz and frequently attend music events at similar venues"
    }
  ],
  "personalized": true
}
```

### Test Surprise Me AI

```bash
curl -X POST http://localhost:5000/api/events/surprise-me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Dallas, TX",
    "mood": "adventurous",
    "budget": 50,
    "time_available": 3,
    "adventure_level": "high"
  }'
```

Expected response:
```json
{
  "event": {
    "title": "Underground Comedy Night",
    "category": "Comedy",
    "surprise_score": 92,
    "surprise_explanation": "This hidden gem comedy show is completely different from your usual tech meetups, but matches your adventurous mood perfectly. The intimate venue and experimental format will surprise and delight you!"
  },
  "surprise": true
}
```

## How It Works

### AI Personalization Flow

1. User requests personalized events
2. System fetches available events from database
3. User's interaction history is analyzed (likes, dislikes, attendance)
4. Top 50 candidates are pre-scored using collaborative filtering
5. **AI analyzes** user profile, past preferences, and candidates
6. **AI generates** personalized rankings with natural language explanations
7. Results returned to user with match scores and reasons

### AI Surprise Flow

1. User selects mood (energetic, chill, creative, social, romantic, adventurous)
2. User sets constraints (budget, time available, adventure level)
3. System fetches events matching location
4. User's past interactions are analyzed
5. **AI considers** mood, constraints, and user history
6. **AI picks** ONE surprising event that's unexpected but delightful
7. **AI generates** creative explanation of why it's a perfect surprise
8. Result returned with surprise score

## Fallback Behavior

If the LLM is unavailable or returns errors, the system automatically falls back to:
- **Personalization**: Basic collaborative filtering + content-based scoring
- **Surprise**: Rule-based mood matching with random selection

This ensures the features always work, even without AI!

## Performance Considerations

### Perplexity
- **Latency**: ~1-3 seconds per request
- **Cost**: Pay per request (check Perplexity pricing)
- **Quality**: Excellent, uses latest AI models
- **Best for**: Production deployments

### Ollama
- **Latency**: ~2-10 seconds depending on model and hardware
- **Cost**: Free (runs locally)
- **Quality**: Good to excellent (depends on model)
- **Best for**: Development, self-hosted deployments

### Gemini
- **Latency**: ~1-2 seconds per request
- **Cost**: Free tier available, then pay-per-use
- **Quality**: Excellent
- **Best for**: Google Cloud users

## Caching Recommendations

To improve performance, consider caching AI responses:

```python
# Example: Cache user taste profiles for 1 hour
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_profile(user_id):
    return engine.calculate_user_taste_profile(user_id)
```

## Debugging

Enable debug logging to see AI prompts and responses:

```python
# In app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check logs for:
- `Using Perplexity HTTP API` - Confirms Perplexity connection
- `Using Ollama HTTP API` - Confirms Ollama connection
- `AI personalization error` - LLM call failed
- `AI surprise error` - LLM call failed

## Environment Variables Reference

```bash
# LLM Provider Selection
LLM_PROVIDER=perplexity          # Options: perplexity, ollama, gemini

# Perplexity Configuration
PERPLEXITY_API_KEY=pplx-xxx
PERPLEXITY_MODEL=sonar           # Options: sonar, sonar-pro, sonar-reasoning

# Ollama Configuration
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=mistral             # Options: mistral, llama3, qwen2.5, etc.

# Gemini Configuration
GEMINI_API_KEY=AIza-xxx
GEMINI_MODEL=gemini-2.5-flash-lite  # Options: gemini-2.0-flash, gemini-pro
```

## Troubleshooting

### "AI personalization error" in logs

**Check:**
1. Is the API key correct?
2. Is the LLM service running (for Ollama)?
3. Do you have internet connection (for Perplexity/Gemini)?
4. Check rate limits on your API key

**Solution:**
- Verify environment variables are set correctly
- Test API key with curl:
  ```bash
  curl https://api.perplexity.ai/chat/completions \
    -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model":"sonar","messages":[{"role":"user","content":"test"}]}'
  ```

### Slow responses

**Solutions:**
- Use faster models (sonar instead of sonar-pro)
- Reduce candidate event count in prompts
- Implement caching
- Use Perplexity instead of local Ollama

### No AI explanations in responses

**Cause:** LLM failed, system fell back to basic algorithm

**Check:**
- Look for error messages in logs
- Verify LLM configuration
- Test LLM independently

## Next Steps

1. **Set up monitoring**: Track AI response times and error rates
2. **A/B test**: Compare AI vs non-AI personalization
3. **Tune prompts**: Customize prompts for your specific use case
4. **Add caching**: Improve performance for repeat users
5. **Collect feedback**: Let users rate AI recommendations

## Support

For issues with:
- **Perplexity**: https://docs.perplexity.ai/
- **Ollama**: https://ollama.com/
- **Gemini**: https://ai.google.dev/docs

For issues with this integration, check the HybridLLM implementation in:
- `src/backend/event_discovery/llm_impl.py`
- `src/backend/event_discovery/personalization.py`
- `src/backend/event_discovery/surprise_engine.py`
