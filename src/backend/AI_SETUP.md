# AI/LLM Setup Guide

This document explains how to configure the AI providers for event discovery and personalization features.

## Overview

Tapin uses Large Language Models (LLMs) to:
- Extract volunteer event information from nonprofit websites
- Generate personalized event recommendations
- Create surprise event suggestions based on user preferences

## Supported Providers

### 1. Google Gemini (Recommended for Production)

**Best for:** Production deployment, high-quality results

**Setup:**
```bash
# In .env file
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.5-flash-lite
```

**Get API Key:**
1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Create new API key
4. Copy and paste into .env file

**Pricing:**
- Free tier: 60 requests/minute
- Cost: ~$0.075 per 1M tokens
- Estimated: $150/month for nationwide coverage

**Models:**
- `gemini-2.5-flash-lite` (fastest, cheapest)
- `gemini-1.5-flash` (balanced)
- `gemini-1.5-pro` (highest quality)

---

### 2. Perplexity AI (Alternative)

**Best for:** Real-time web data, alternative to Gemini

**Setup:**
```bash
# In .env file
LLM_PROVIDER=perplexity
PERPLEXITY_API_KEY=your-api-key-here
PERPLEXITY_MODEL=sonar
```

**Get API Key:**
1. Visit: https://www.perplexity.ai/settings/api
2. Create account
3. Generate API key
4. Copy and paste into .env file

---

### 3. Ollama (Local Development)

**Best for:** Offline development, no API costs, privacy

**Setup:**
```bash
# In .env file
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434
```

**Install Ollama:**
```bash
# Install from https://ollama.ai
# Then pull a model:
ollama pull mistral

# Or use other models:
ollama pull llama2
ollama pull codellama
ollama pull mixtral
```

**Pros:**
- Completely free
- Works offline
- No data leaves your machine
- Privacy-focused

**Cons:**
- Requires ~8GB RAM
- Slower than cloud APIs
- Lower quality results than Gemini

---

### 4. Mock Provider (Testing)

**Best for:** Testing, development without API keys

**Setup:**
```bash
# In .env file
LLM_PROVIDER=mock
```

**Behavior:**
- Returns sample volunteer events
- No actual AI processing
- Fast and reliable for tests
- Used by pytest test suite

---

## Configuration Examples

### Development (Local, No Costs)
```bash
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral
```

### Testing (No Setup Required)
```bash
LLM_PROVIDER=mock
```

### Production (Best Quality)
```bash
LLM_PROVIDER=gemini
# NOTE: do NOT commit real API keys. Replace the value in your local `.env`.
GEMINI_API_KEY=REDACTED_GOOGLE  # revoke and rotate if this was ever committed
GEMINI_MODEL=gemini-2.5-flash-lite
```

### Alternative Production
```bash
LLM_PROVIDER=perplexity
# NOTE: do NOT commit real API keys. Set this locally or in CI secrets.
PERPLEXITY_API_KEY=REDACTED_PERPLEXITY  # revoke and rotate if this was ever committed
PERPLEXITY_MODEL=sonar
```

---

## How to Switch Providers

1. **Edit .env file:**
   ```bash
   cd src/backend
   nano .env  # or your preferred editor
   ```

2. **Change LLM_PROVIDER:**
   ```bash
   LLM_PROVIDER=gemini  # or perplexity, ollama, mock
   ```

3. **Add API key (if needed):**
   ```bash
   GEMINI_API_KEY=your-actual-key-here
   ```

4. **Restart backend:**
   ```bash
   python app.py
   ```

5. **Verify in logs:**
   ```
   Using Google Gemini API with model: gemini-2.5-flash-lite
   ```

---

## Testing Your Setup

```bash
# Test event discovery endpoint
curl "http://localhost:5000/api/events/discover-tonight?location=Austin,TX&limit=5"

# Should return JSON with volunteer events
```

---

## Troubleshooting

### "No API key provided"
- Make sure .env file exists in `src/backend/`
- Check that GEMINI_API_KEY is set (no quotes needed)
- Restart backend after changing .env

### "Rate limit exceeded"
- Switch to different model: `gemini-1.5-flash`
- Use Ollama for unlimited local requests
- Add delay between requests

### "Ollama connection failed"
- Make sure Ollama is installed: https://ollama.ai
- Start Ollama: `ollama serve`
- Pull a model: `ollama pull mistral`
- Check OLLAMA_BASE_URL in .env

### Low quality results
- Upgrade to better model: `gemini-1.5-pro`
- Switch from Ollama to Gemini for cloud processing
- Check prompt engineering in code

---

## Cost Estimates

| Provider | Free Tier | Production Cost |
|----------|-----------|----------------|
| Gemini | 60 req/min | ~$150/month |
| Perplexity | 100 requests | ~$200/month |
| Ollama | Unlimited | $0 (hardware only) |
| Mock | Unlimited | $0 (no AI) |

---

## Security Notes

⚠️ **Never commit API keys to git!**

✅ API keys are stored in `.env` (gitignored)
✅ Use environment variables in production
✅ Rotate keys regularly
✅ Use restricted API keys when possible

---

## Additional Resources

- Google Gemini Docs: https://ai.google.dev/docs
- Perplexity API: https://docs.perplexity.ai/
- Ollama Models: https://ollama.ai/library
- LangChain Integration: https://python.langchain.com/docs/
