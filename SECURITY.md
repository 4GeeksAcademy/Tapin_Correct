# Security Guide

## 🚨 CRITICAL: API Key Security

### API Keys Found and Removed

The following API keys were **exposed in public documentation** and have been sanitized:

1. ~~`AIzaSyCBioWdfsoySHMApqtODg89ARRVhkZ5B5s`~~ - **REVOKED** (found in GOOGLE_SEARCH_SETUP.md)
2. `AIzaSyDtOC0LYVBmxPyvK9MkN2mHMPfgzOFULzw` - Currently in use (should be rotated)
3. `AIzaSyBXfPZLg3p_CIQv2xmEAHjVjF2MfktXqXo` - GEMINI_API_KEY (should be rotated)

### IMMEDIATE ACTION REQUIRED

**You MUST rotate these keys immediately:**

1. Go to [Google Cloud Console - API Credentials](https://console.cloud.google.com/apis/credentials?project=tapin-application)
2. **Delete** the exposed keys listed above
3. **Generate new keys** for:
   - GOOGLE_API_KEY (for Custom Search)
   - GEMINI_API_KEY (for Gemini LLM)
4. Update your local `.env` file with new keys
5. **Never commit `.env` to git**

## Security Best Practices

### Environment Variables

**✅ DO:**
- Store all secrets in `.env` files
- Add `.env` to `.gitignore`
- Use `.env.sample` as template (without real values)
- Use environment variables in code: `os.getenv('API_KEY')`
- Rotate keys regularly (every 90 days)

**❌ DON'T:**
- Commit real API keys to git
- Share keys in documentation
- Hard-code keys in source code
- Use the same key across environments
- Share keys in Slack, email, or messages

### .env File Template

Create `.env` in project root:

```bash
# Google API Keys (Get from console.cloud.google.com)
GOOGLE_API_KEY=your_google_api_key_here
CUSTOM_SEARCH_ENGINE_ID=your_search_engine_id_here
GEMINI_API_KEY=your_gemini_api_key_here

# LLM Provider
LLM_PROVIDER=gemini

# Database
DATABASE_URL=your_database_url_here

# Application
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here

# Email (Optional)
MAIL_USERNAME=your_email_username
MAIL_PASSWORD=your_email_password

# Ticketmaster (Optional)
TICKETMASTER_API_KEY=your_ticketmaster_key

# Perplexity (Optional)
PERPLEXITY_API_KEY=your_perplexity_key
```

### Git Security

Verify `.gitignore` includes:

```gitignore
# Environment variables
.env
.env.local
.env.*.local

# API Keys and secrets
*.pem
*.key
credentials.json
secrets.json

# Usage tracking (may contain sensitive data)
.usage/

# IDE settings (may contain local paths/keys)
.vscode/settings.json
.idea/
```

### Checking for Exposed Secrets

Run this command regularly:

```bash
# Search for potential API keys
grep -r "AIzaSy" . --include="*.py" --include="*.js" --include="*.md"

# Search for other secrets
grep -r "sk-" . --include="*.py" --include="*.js"  # OpenAI keys
grep -r "pplx-" . --include="*.py" --include="*.js"  # Perplexity keys
```

### If a Key is Exposed

1. **Immediately revoke** the key in the provider's console
2. **Generate a new key**
3. **Update** all environments with the new key
4. **Remove** the exposed key from git history:
   ```bash
   # WARNING: This rewrites history
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/file" \
     --prune-empty --tag-name-filter cat -- --all
   ```
5. **Force push** to remote (if needed):
   ```bash
   git push origin --force --all
   ```
6. **Notify team members** to pull fresh copy

### Google Cloud Security

**Enable API restrictions:**

1. Go to API Credentials page
2. Click on your API key
3. Under "API restrictions":
   - ✅ Restrict key to specific APIs
   - Select only: Custom Search API, Gemini API
4. Under "Application restrictions":
   - ✅ HTTP referrers (for web)
   - ✅ IP addresses (for backend)

**Set quota limits:**

1. Go to API Quotas page
2. Set daily limits:
   - Custom Search: 100 queries/day (free tier)
   - Gemini API: Appropriate for your usage
3. Set up budget alerts

### Monitoring

**Enable alerting:**
- Set up billing alerts in Google Cloud
- Monitor API usage daily
- Enable Cloud Logging for API access
- Review access logs weekly

**Watch for suspicious activity:**
- Unexpected API usage spikes
- Requests from unknown IPs
- Failed authentication attempts
- Quota exceeded alerts

## Security Checklist

- [ ] All API keys rotated after exposure
- [ ] `.env` file created locally (not committed)
- [ ] `.gitignore` updated and verified
- [ ] All documentation sanitized (no real keys)
- [ ] API restrictions enabled in Google Cloud
- [ ] Quota limits set
- [ ] Billing alerts configured
- [ ] Team notified of security incident
- [ ] Git history cleaned (if needed)
- [ ] All environments updated with new keys

## Incident Response

If you discover a security issue:

1. **Assess impact**: What was exposed? For how long?
2. **Contain**: Revoke compromised credentials immediately
3. **Investigate**: Check logs for unauthorized usage
4. **Remediate**: Rotate all potentially compromised secrets
5. **Document**: Record what happened and lessons learned
6. **Prevent**: Implement safeguards to prevent recurrence

## Contact

For security issues, contact:
- **Project Owner**: houseofobi
- **Report vulnerabilities**: Open a private GitHub security advisory

## Resources

- [Google Cloud Security Best Practices](https://cloud.google.com/security/best-practices)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Git Secrets Tool](https://github.com/awslabs/git-secrets)

---

**Last Updated:** November 24, 2025
**Incident Date:** November 24, 2025 - API keys found in public docs
**Status:** ⚠️ KEYS NEED ROTATION
