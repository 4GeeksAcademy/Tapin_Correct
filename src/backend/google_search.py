import os
import json
from pathlib import Path
from datetime import datetime
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

try:
    import google.generativeai as genai
except Exception:
    genai = None
from dotenv import load_dotenv

load_dotenv()


def _quota_file_path():
    d = Path(__file__).resolve().parent / ".usage"
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return d / "google_usage.json"


def _load_google_usage():
    p = _quota_file_path()
    if not p.exists():
        return {"month": datetime.utcnow().strftime("%Y-%m"), "count": 0}
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"month": datetime.utcnow().strftime("%Y-%m"), "count": 0}


def _save_google_usage(data):
    p = _quota_file_path()
    try:
        with p.open("w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


def _allowed_google_request():
    max_req = int(os.getenv("GOOGLE_MAX_REQUESTS_PER_MONTH", "100"))
    usage = _load_google_usage()
    current = datetime.utcnow().strftime("%Y-%m")
    if usage.get("month") != current:
        usage = {"month": current, "count": 0}
        _save_google_usage(usage)
    return usage.get("count", 0) < max_req


def _increment_google_usage():
    usage = _load_google_usage()
    current = datetime.utcnow().strftime("%Y-%m")
    if usage.get("month") != current:
        usage = {"month": current, "count": 0}
    usage["count"] = usage.get("count", 0) + 1
    _save_google_usage(usage)


def search_events_perplexity(query):
    """
    Query a Perplexity-like API endpoint for events.

    Configuration:
      - PERPLEXITY_API_KEY: API key
      - PERPLEXITY_API_URL: Full URL to the Perplexity-compatible endpoint

    The exact Perplexity API contract may vary; this function tries a
    reasonable POST with JSON {query: ...} and will attempt to normalize
    returned items into a list of {title, snippet, link} objects.
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    api_url = os.getenv("PERPLEXITY_API_URL")

    if not api_key or not api_url:
        return {
            "error": (
                "Perplexity API not configured "
                "(PERPLEXITY_API_KEY/PERPLEXITY_API_URL)."
            )
        }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # If the Perplexity chat completions endpoint is used, send a chat-style
    # payload; otherwise send a simple {query, limit} body to support older
    # or mock endpoints.
    is_chat_endpoint = "/chat" in api_url or "chat/completions" in api_url
    if is_chat_endpoint:
        payload = {
            "messages": [{"role": "user", "content": query}],
            "temperature": 0.2,
            "max_tokens": 512,
        }
    else:
        payload = {"query": query, "limit": 10}

    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        # If this is a chat-style response, try to extract the assistant's
        # textual reply from common fields (choices/message, outputs, answer).
        text = None
        if isinstance(data, dict):
            # OpenAI-like shape: {choices:[{message:{content:...}}]}
            choices = data.get("choices")
            if isinstance(choices, list) and len(choices) > 0:
                first = choices[0]
                if isinstance(first, dict):
                    msg = first.get("message") or first
                    if isinstance(msg, dict):
                        text = msg.get("content") or msg.get("text")
                    else:
                        text = first.get("text")

            # Perplexity/other shape: {outputs:[{content:[{text:...}]}, ...]}
            if not text and "outputs" in data and isinstance(data["outputs"], list):
                out = data["outputs"][0]
                content = out.get("content") if isinstance(out, dict) else None
                if isinstance(content, list):
                    parts = []
                    for c in content:
                        if isinstance(c, dict):
                            parts.append(c.get("text") or c.get("content") or "")
                        else:
                            parts.append(str(c))
                    text = "\n".join([p for p in parts if p])
                else:
                    text = out.get("text") if isinstance(out, dict) else None

            # Fallback fields
            if not text and "answer" in data:
                ans = data.get("answer")
                text = ans if isinstance(ans, str) else json.dumps(ans)

            # If there's a 'results' list, normalize that as items
            results = data.get("results") or data.get("items") or data.get("answers")
            if isinstance(results, list) and len(results) > 0:
                normalized = []
                for it in results:
                    if not isinstance(it, dict):
                        normalized.append(
                            {"title": None, "snippet": str(it), "link": None}
                        )
                        continue
                    title = it.get("title") or it.get("heading") or it.get("name")
                    snippet = (
                        it.get("snippet")
                        or it.get("summary")
                        or it.get("text")
                        or it.get("answer")
                    )
                    link = it.get("link") or it.get("url") or it.get("source")
                    normalized.append(
                        {"title": title, "snippet": snippet, "link": link}
                    )
                return refine_and_categorize(normalized)

        elif isinstance(data, list):
            # A list of items: normalize directly
            normalized = []
            for it in data:
                if not isinstance(it, dict):
                    normalized.append({"title": None, "snippet": str(it), "link": None})
                    continue
                title = it.get("title") or it.get("heading") or it.get("name")
                snippet = (
                    it.get("snippet")
                    or it.get("summary")
                    or it.get("text")
                    or it.get("answer")
                )
                link = it.get("link") or it.get("url") or it.get("source")
                normalized.append({"title": title, "snippet": snippet, "link": link})
            return refine_and_categorize(normalized)

        # If we didn't get a structured list, use the extracted text as a single item
        if not text:
            text = json.dumps(data)

        item = {"title": query, "snippet": text, "link": None}
        return refine_and_categorize([item])
    except Exception as e:
        return {"error": f"Perplexity request failed: {e}"}


def search_events(query):
    """
    Unified search entrypoint. Prefer Perplexity when configured, then
    fall back to Google Custom Search if available. Enforces a monthly
    Google request quota defined by `GOOGLE_MAX_REQUESTS_PER_MONTH`.
    """
    provider = os.getenv("LLM_PROVIDER", "").lower()

    # If explicitly asked for Google, use it (fail if not configured)
    if provider == "google":
        api_key = os.getenv("GOOGLE_API_KEY")
        search_engine_id = os.getenv("CUSTOM_SEARCH_ENGINE_ID")
        if not api_key or not search_engine_id:
            return {
                "error": (
                    "LLM_PROVIDER=google but "
                    "GOOGLE_API_KEY/CUSTOM_SEARCH_ENGINE_ID missing."
                )
            }
        try:
            if not _allowed_google_request():
                return {
                    "error": (
                        "Google monthly quota reached "
                        "(set GOOGLE_MAX_REQUESTS_PER_MONTH)"
                    )
                }
            service = build("customsearch", "v1", developerKey=api_key)
            result = service.cse().list(q=query, cx=search_engine_id, num=10).execute()
            # Normalize and categorize the Google items first
            refined = refine_and_categorize(result.get("items", []))

            # If the Google Generative AI client is available and a key is set,
            # try to generate a short summary of the top results and prepend
            # it as an "AI Summary" item for the frontend to display.
            try:
                google_api_key = os.getenv("GOOGLE_API_KEY")
                if genai is not None and google_api_key:
                    genai.configure(api_key=google_api_key)
                    # Build a short prompt using the top results
                    snippet_lines = []
                    for i, it in enumerate(refined[:5], start=1):
                        title = it.get("title") or "(no title)"
                        snip = it.get("snippet") or ""
                        snippet_lines.append(f"{i}. {title} - {snip}")

                    prompt = (
                        "Summarize these search results briefly (2-3 sentences) and "
                        "give 3 short suggested next steps for someone looking to "
                        f"find volunteer opportunities for: '{query}'.\n\n"
                        "Results:\n" + "\n".join(snippet_lines)
                    )

                    resp = genai.chat.create(
                        model=os.getenv("LLM_MODEL", "gemini-1.5"),
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are a concise assistant that summarizes search results "
                                    "and suggests next steps for finding volunteer opportunities."
                                ),
                            },
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.2,
                        max_output_tokens=256,
                    )

                    # Defensive extraction of the assistant text
                    summary_text = None
                    try:
                        if hasattr(resp, "last") and resp.last:
                            # some clients expose `last` with content
                            last = resp.last
                            if isinstance(last, dict):
                                summary_text = last.get("content") or last.get("output")
                        if not summary_text:
                            # newer shape: resp.output[0].content[0].text
                            summary_text = (
                                resp.output[0]["content"][0].get("text")
                                if resp.output
                                else None
                            )
                    except Exception:
                        summary_text = None

                    if not summary_text:
                        try:
                            summary_text = str(resp)
                        except Exception:
                            summary_text = None

                    if summary_text:
                        ai_item = {
                            "title": "AI Summary",
                            "snippet": summary_text,
                            "link": None,
                            "category": "Summary",
                        }
                        # Prepend summary so frontend (which expects a list)
                        # will display it first.
                        refined.insert(0, ai_item)
            except Exception:
                # Don't fail the search if summarization errors out.
                pass

            try:
                _increment_google_usage()
            except Exception:
                pass

            return refined
        except HttpError as e:
            # If Google returns a 403 (accessNotConfigured / disabled),
            # attempt Perplexity if it is configured.
            try_perplexity = (
                getattr(e, "resp", None) is not None
                and getattr(e.resp, "status", None) == 403
            )
            if (
                try_perplexity
                and os.getenv("PERPLEXITY_API_KEY")
                and os.getenv("PERPLEXITY_API_URL")
            ):
                p = search_events_perplexity(query)
                if not (isinstance(p, dict) and p.get("error")):
                    return p
            return {"error": str(e)}
        except Exception as e:
            # Other errors: try Perplexity as a fallback if available
            if os.getenv("PERPLEXITY_API_KEY") and os.getenv("PERPLEXITY_API_URL"):
                return search_events_perplexity(query)
            return {"error": str(e)}

    # If explicitly asked for Perplexity, try it first and fall back to Google
    if provider == "perplexity":
        if os.getenv("PERPLEXITY_API_KEY") and os.getenv("PERPLEXITY_API_URL"):
            p = search_events_perplexity(query)
            if not (isinstance(p, dict) and p.get("error")):
                return p
        # If Perplexity not configured or failed, fall through to Google

    # Default: prefer Google if configured, otherwise try Perplexity
    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("CUSTOM_SEARCH_ENGINE_ID")
    if api_key and search_engine_id:
        try:
            if not _allowed_google_request():
                return {
                    "error": (
                        "Google monthly quota reached "
                        "(set GOOGLE_MAX_REQUESTS_PER_MONTH)"
                    )
                }
            service = build("customsearch", "v1", developerKey=api_key)
            result = service.cse().list(q=query, cx=search_engine_id, num=10).execute()
            items = result.get("items", [])
            try:
                _increment_google_usage()
            except Exception:
                pass
            return refine_and_categorize(items)
        except HttpError as e:
            try_perplexity = (
                getattr(e, "resp", None) is not None
                and getattr(e.resp, "status", None) == 403
            )
            if (
                try_perplexity
                and os.getenv("PERPLEXITY_API_KEY")
                and os.getenv("PERPLEXITY_API_URL")
            ):
                p = search_events_perplexity(query)
                if not (isinstance(p, dict) and p.get("error")):
                    return p
            if os.getenv("PERPLEXITY_API_KEY") and os.getenv("PERPLEXITY_API_URL"):
                return search_events_perplexity(query)
            return {"error": str(e)}
        except Exception as e:
            if os.getenv("PERPLEXITY_API_KEY") and os.getenv("PERPLEXITY_API_URL"):
                return search_events_perplexity(query)
            return {"error": str(e)}

    # Try Perplexity if Google not available
    if os.getenv("PERPLEXITY_API_KEY") and os.getenv("PERPLEXITY_API_URL"):
        return search_events_perplexity(query)

    return {"error": "No search provider configured (Google or Perplexity)."}


CATEGORY_KEYWORDS = {
    "Animal Welfare": [
        "animal",
        "pet",
        "wildlife",
        "shelter",
        "rescue",
        "zoo",
        "aquarium",
        "veterinary",
        "spca",
        "humane society",
        "dog",
        "cat",
        "horse",
        "conservation",
        "endangered species",
        "marine life",
    ],
    "Arts & Culture": [
        "art",
        "museum",
        "gallery",
        "theater",
        "theatre",
        "music",
        "dance",
        "cultural",
        "heritage",
        "festival",
        "concert",
        "exhibition",
        "performance",
        "creative",
        "artist",
        "painting",
        "sculpture",
    ],
    "Children & Youth": [
        "children",
        "youth",
        "kids",
        "teen",
        "adolescent",
        "child care",
        "daycare",
        "mentoring",
        "tutoring",
        "after school",
        "camp",
        "playground",
        "pediatric",
        "young people",
        "student",
    ],
    "Community Development": [
        "community",
        "neighborhood",
        "housing",
        "urban",
        "development",
        "infrastructure",
        "revitalization",
        "affordable housing",
        "homeless",
        "poverty",
        "economic development",
        "job training",
    ],
    "Disaster Relief": [
        "disaster",
        "emergency",
        "relief",
        "hurricane",
        "flood",
        "earthquake",
        "fire",
        "tornado",
        "crisis",
        "rescue",
        "evacuation",
        "red cross",
        "fema",
        "recovery",
    ],
    "Education & Literacy": [
        "education",
        "literacy",
        "school",
        "teaching",
        "learning",
        "tutor",
        "library",
        "reading",
        "writing",
        "adult education",
        "esl",
        "homework",
        "academic",
        "scholarship",
        "books",
    ],
    "Environment": [
        "environment",
        "climate",
        "sustainability",
        "recycling",
        "conservation",
        "green",
        "eco",
        "nature",
        "pollution",
        "cleanup",
        "renewable energy",
        "organic",
        "carbon",
        "ecology",
        "forest",
        "ocean",
    ],
    "Health & Medicine": [
        "health",
        "medical",
        "hospital",
        "clinic",
        "healthcare",
        "nursing",
        "patient",
        "disease",
        "mental health",
        "wellness",
        "fitness",
        "nutrition",
        "therapy",
        "counseling",
        "public health",
        "vaccine",
    ],
    "Human Rights": [
        "human rights",
        "civil rights",
        "justice",
        "equality",
        "discrimination",
        "advocacy",
        "refugee",
        "immigrant",
        "asylum",
        "freedom",
        "lgbtq",
        "minority",
        "inclusion",
        "equity",
        "social justice",
    ],
    "Seniors": [
        "senior",
        "elderly",
        "aging",
        "retirement",
        "elder care",
        "nursing home",
        "assisted living",
        "geriatric",
        "older adult",
        "medicare",
        "pension",
    ],
    "Social Services": [
        "social service",
        "welfare",
        "assistance",
        "support",
        "counseling",
        "family services",
        "food bank",
        "soup kitchen",
        "charity",
        "nonprofit",
        "outreach",
        "aid",
        "donation",
        "volunteer",
    ],
    "Sports & Recreation": [
        "sport",
        "recreation",
        "athletic",
        "fitness",
        "gym",
        "coach",
        "team",
        "league",
        "tournament",
        "outdoor",
        "hiking",
        "camping",
        "park",
        "playground",
        "youth sports",
    ],
    "Technology": [
        "technology",
        "tech",
        "computer",
        "coding",
        "programming",
        "software",
        "digital",
        "internet",
        "web",
        "app",
        "cyber",
        "it",
        "stem",
        "robotics",
        "ai",
        "data",
    ],
    "Women's Issues": [
        "women",
        "female",
        "girl",
        "maternal",
        "pregnancy",
        "reproductive",
        "domestic violence",
        "gender equality",
        "women's health",
        "feminism",
        "empowerment",
        "single mother",
    ],
}


def refine_and_categorize(items):
    """
    Normalizes and categorizes items, expecting dicts with at least
    'title' or 'snippet' keys. Uses keyword matching with scoring to
    determine the best category fit.
    """
    refined_results = []
    for item in items:
        title = item.get("title") if isinstance(item, dict) else None
        snippet = item.get("snippet") if isinstance(item, dict) else str(item)

        # Combine title and snippet for better matching
        text = f"{title or ''} {snippet or ''}".lower()

        # Score each category based on keyword matches
        category_scores = {}
        for category, keywords in CATEGORY_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                # Count occurrences of each keyword
                count = text.count(keyword.lower())
                if count > 0:
                    # Weight exact category name matches higher
                    if keyword.lower() == category.lower():
                        score += count * 3
                    else:
                        score += count

            if score > 0:
                category_scores[category] = score

        # Assign the category with the highest score, or "Other" if no matches
        if category_scores:
            assigned = max(category_scores, key=category_scores.get)
        else:
            assigned = "Other"

        refined_results.append(
            {
                "title": title,
                "snippet": snippet,
                "link": item.get("link") if isinstance(item, dict) else None,
                "category": assigned,
            }
        )

    return refined_results


def create_events_from_search_results(results, query, location=None):
    """
    Convert Google Custom Search results into Event records for the database.

    Args:
        results: List of search result dictionaries from search_events()
        query: The original search query
        location: Optional location dict with 'city' and 'state' keys

    Returns:
        List of Event dictionaries ready to be saved to the database
    """
    import uuid
    from datetime import datetime, timezone, timedelta

    events = []

    for result in results:
        if not isinstance(result, dict):
            continue

        # Skip if no title or link
        title = result.get("title")
        url = result.get("link")
        if not title or not url:
            continue

        # Extract organization name from title or use title
        organization = title.split(" - ")[0] if " - " in title else title
        organization = (
            organization.split(" | ")[0] if " | " in organization else organization
        )

        # Create a unique ID based on URL and title
        event_id = str(uuid.uuid5(uuid.NAMESPACE_URL, url))

        # Build the event dictionary
        event = {
            "id": event_id,
            "title": title,
            "organization": organization[:200],  # Limit to 200 chars
            "description": result.get("snippet", ""),
            "category": result.get("category", "Other"),
            "url": url[:1000],  # Limit to 1000 chars
            "source": "google_custom_search",
            "scraped_at": datetime.now(timezone.utc),
            "cache_expires_at": datetime.now(timezone.utc) + timedelta(days=30),
            # Set location from search query if provided
            "location_city": location.get("city") if location else None,
            "location_state": location.get("state") if location else None,
            # Contact info - these will be None initially
            # Could be enhanced with web scraping or LLM extraction
            "contact_email": None,
            "contact_phone": None,
            "contact_person": None,
            # Optional fields
            "date_start": None,
            "location_address": None,
            "location_zip": None,
            "latitude": None,
            "longitude": None,
            "venue": None,
            "price": "Free",  # Assume volunteer opportunities are free
            "image_url": None,
            "image_urls": None,
        }

        events.append(event)

    return events


def extract_contact_info_from_url(url):
    """
    Attempt to extract contact information from a URL by scraping and analyzing the page.

    Args:
        url: The URL to scrape for contact information

    Returns:
        Dict with contact_email, contact_phone, and contact_person (or None for each)
    """
    import re

    contact_info = {
        "contact_email": None,
        "contact_phone": None,
        "contact_person": None,
    }

    try:
        # Try to fetch the page content
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )
        response.raise_for_status()
        content = response.text

        # Extract email addresses using regex
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, content)
        if emails:
            # Filter out common non-contact emails
            filtered_emails = [
                e
                for e in emails
                if not any(
                    x in e.lower()
                    for x in ["noreply", "privacy", "support@", "info@example"]
                )
            ]
            if filtered_emails:
                contact_info["contact_email"] = filtered_emails[0]

        # Extract phone numbers using regex (US format)
        phone_pattern = (
            r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b"
        )
        phones = re.findall(phone_pattern, content)
        if phones:
            # Format the phone number
            contact_info["contact_phone"] = (
                f"({phones[0][0]}) {phones[0][1]}-{phones[0][2]}"
            )

    except Exception as e:
        # If scraping fails, just return None values
        pass

    return contact_info


def enrich_events_with_contact_info(events, max_to_enrich=3):
    """
    Enrich event records with contact information scraped from their URLs.

    Args:
        events: List of event dictionaries
        max_to_enrich: Maximum number of events to enrich (to avoid too many requests)

    Returns:
        List of enriched event dictionaries
    """
    enriched_count = 0

    for event in events:
        if enriched_count >= max_to_enrich:
            break

        url = event.get("url")
        if not url:
            continue

        # Skip if contact info already exists
        if event.get("contact_email") or event.get("contact_phone"):
            continue

        # Extract contact info from the URL
        contact_info = extract_contact_info_from_url(url)

        # Update the event with extracted contact info
        if contact_info["contact_email"]:
            event["contact_email"] = contact_info["contact_email"]
        if contact_info["contact_phone"]:
            event["contact_phone"] = contact_info["contact_phone"]
        if contact_info["contact_person"]:
            event["contact_person"] = contact_info["contact_person"]

        enriched_count += 1

    return events


def extract_values_from_event(event):
    """
    Extract organization values from event information using LLM.
    Returns a JSON string containing an array of value IDs.

    Available values:
    - community: Community Building
    - environment: Environmental Sustainability
    - education: Education & Learning
    - health: Health & Wellness
    - equality: Equality & Justice
    - poverty: Poverty Alleviation
    - youth: Youth Empowerment
    - seniors: Elder Care
    - animals: Animal Welfare
    - arts: Arts & Culture
    - innovation: Innovation & Technology
    - disaster: Disaster Relief
    - hunger: Hunger Relief
    - women: Women Empowerment
    - inclusion: Diversity & Inclusion
    """
    try:
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "event_discovery"))
        from llm_impl import HybridLLM
        import asyncio

        # Build the prompt
        prompt = f"""Analyze this volunteer opportunity/organization and identify which core values align with their work.

Return ONLY value IDs as a comma-separated list (no other text).

Available Values:
- community: Community Building
- environment: Environmental Sustainability
- education: Education & Learning
- health: Health & Wellness
- equality: Equality & Justice
- poverty: Poverty Alleviation
- youth: Youth Empowerment
- seniors: Elder Care
- animals: Animal Welfare
- arts: Arts & Culture
- innovation: Innovation & Technology
- disaster: Disaster Relief
- hunger: Hunger Relief
- women: Women Empowerment
- inclusion: Diversity & Inclusion

Organization: {event.get('organization', 'Unknown')}
Title: {event.get('title', '')}
Description: {event.get('description', '')}
Category: {event.get('category', '')}

Return format: value1,value2,value3 (e.g., community,youth,education)"""

        # Call LLM - explicitly use Google Gemini
        llm = HybridLLM(provider="gemini")

        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(llm.ainvoke(prompt))
            result_text = response.content.strip()

            # Parse comma-separated values
            value_ids = [v.strip() for v in result_text.split(",") if v.strip()]

            # Validate value IDs against known values
            valid_values = {
                "community",
                "environment",
                "education",
                "health",
                "equality",
                "poverty",
                "youth",
                "seniors",
                "animals",
                "arts",
                "innovation",
                "disaster",
                "hunger",
                "women",
                "inclusion",
            }
            filtered_values = [v for v in value_ids if v in valid_values]

            return json.dumps(filtered_values) if filtered_values else None
        finally:
            loop.close()

    except Exception as e:
        print(f"Error extracting values: {e}")
        # Fallback: map category to default values
        category = event.get("category", "")
        category_to_values = {
            "Community": ["community"],
            "Environment": ["environment"],
            "Education": ["education"],
            "Health": ["health"],
            "Animals": ["animals"],
            "Children & Youth": ["youth"],
            "Seniors": ["seniors"],
            "Arts & Culture": ["arts"],
            "Disaster Relief": ["disaster"],
            "Human Rights": ["equality"],
            "Social Services": ["poverty"],
            "Technology": ["innovation"],
            "Women's Issues": ["women"],
        }
        values = category_to_values.get(category, [])
        return json.dumps(values) if values else None


def enrich_events_with_values(events, max_to_enrich=5):
    """
    Enrich events with values using LLM extraction.
    Only enriches up to max_to_enrich events to avoid excessive LLM calls.
    """
    enriched_count = 0

    for event in events:
        if enriched_count >= max_to_enrich:
            break

        # Skip if values already exist
        if event.get("values"):
            continue

        # Extract values
        values_json = extract_values_from_event(event)
        if values_json:
            event["values"] = values_json
            enriched_count += 1

    return events
