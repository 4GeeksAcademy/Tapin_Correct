import os
import asyncio
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception:
    ChatGoogleGenerativeAI = None

try:
    from langchain_community.llms import Ollama
except Exception:
    Ollama = None

try:
    from langchain_openai import ChatOpenAI
except Exception:
    ChatOpenAI = None

import urllib.request


class HybridLLM:
    """Hybrid LLM wrapper with an HTTP Ollama fallback.

    This implementation mirrors the intended behavior: prefer LangChain
    connectors, fall back to the local Ollama HTTP API, otherwise
    return a deterministic mock string for tests.
    """

    def __init__(self, provider: Optional[str] = None):
        env_provider = os.environ.get("LLM_PROVIDER")
        pytest_hint = "PYTEST_CURRENT_TEST" in os.environ
        default = "ollama" if pytest_hint else "gemini"
        self.provider = provider or env_provider or default

        self._llm = None
        self._init_attempted = False
        self._ollama_http_available = False

    def _check_ollama_http(self) -> bool:
        url = os.environ.get("OLLAMA_API_URL", "http://localhost:11434")
        # Use /api/tags endpoint to check Ollama availability
        tags_url = f"{url}/api/tags"
        try:
            with urllib.request.urlopen(tags_url, timeout=2) as resp:
                return getattr(resp, "status", 200) == 200
        except Exception:
            return False

    def _init_llm(self):
        if self._init_attempted:
            return
        self._init_attempted = True
        try:
            if self.provider == "ollama":
                # Prefer HTTP fallback for Ollama to avoid asyncio event loop issues
                if self._check_ollama_http():
                    self._ollama_http_available = True
                    logger.info(
                        f"Using Ollama HTTP API with model: {os.environ.get('OLLAMA_MODEL', 'mistral')}"
                    )
                    return
                # Fallback to LangChain wrapper if HTTP not available
                if Ollama is not None:
                    model_name = os.environ.get("OLLAMA_MODEL", "mistral")
                    self._llm = Ollama(model=model_name)
                    return

            if self.provider == "perplexity":
                api_key = os.environ.get("PERPLEXITY_API_KEY")
                if api_key:
                    # Use direct HTTP API for Perplexity
                    logger.info(
                        f"Using Perplexity HTTP API with model: {os.environ.get('PERPLEXITY_MODEL', 'sonar')}"
                    )
                    return

            if self.provider == "gemini" and ChatGoogleGenerativeAI is not None:
                if (
                    os.environ.get("GEMINI_API_KEY")
                    or os.environ.get("GOOGLE_API_KEY")
                    or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
                ):
                    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")
                    self._llm = ChatGoogleGenerativeAI(model=model)
                    return
        except Exception:
            self._llm = None

    async def _ollama_http_generate(self, prompt: str) -> Optional[str]:
        def _sync_call():
            url = os.environ.get("OLLAMA_API_URL", "http://localhost:11434")
            endpoint = f"{url}/api/generate"
            model = os.environ.get("OLLAMA_MODEL", "mistral")
            payload = json.dumps({"model": model, "prompt": prompt}).encode("utf-8")
            req = urllib.request.Request(
                endpoint,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                # Increased timeout for large models like gpt-oss:120b-cloud
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = resp.read().decode("utf-8")
                    # Ollama streams JSONL: each line is a JSON object with "response" field
                    # Concatenate all "response" fields to get full text
                    if "\n" in data and data.strip().startswith("{"):
                        # JSONL streaming response
                        full_response = ""
                        for line in data.strip().split("\n"):
                            if line.strip():
                                try:
                                    obj = json.loads(line)
                                    if isinstance(obj, dict):
                                        full_response += obj.get("response", "")
                                except Exception:
                                    pass
                        if full_response:
                            return full_response
                    try:
                        parsed = json.loads(data)
                        if isinstance(parsed, dict):
                            # Check common response fields
                            for key in ("response", "output", "text", "content"):
                                val = parsed.get(key)
                                if isinstance(val, str):
                                    return val
                            if "choices" in parsed and parsed["choices"]:
                                first = parsed["choices"][0]
                                if isinstance(first, dict) and "text" in first:
                                    return first["text"]
                            if "outputs" in parsed and parsed["outputs"]:
                                out0 = parsed["outputs"][0]
                                if isinstance(out0, dict):
                                    if "content" in out0:
                                        return out0["content"]
                        return json.dumps(parsed)
                    except Exception:
                        return data
            except Exception as e:
                logger.info(f"Ollama HTTP error: {e}")
                return None

        return await asyncio.to_thread(_sync_call)

    async def _perplexity_http_generate(self, prompt: str) -> Optional[str]:
        """Direct HTTP API call to Perplexity (OpenAI-compatible)."""

        def _sync_call():
            api_key = os.environ.get("PERPLEXITY_API_KEY")
            if not api_key:
                return None

            # Default to sonar model (latest Perplexity model)
            model = os.environ.get("PERPLEXITY_MODEL", "sonar")
            payload = json.dumps(
                {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                }
            ).encode("utf-8")

            req = urllib.request.Request(
                "https://api.perplexity.ai/chat/completions",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = resp.read().decode("utf-8")
                    parsed = json.loads(data)
                    # OpenAI-compatible response format
                    if "choices" in parsed and parsed["choices"]:
                        first = parsed["choices"][0]
                        if isinstance(first, dict):
                            # Check message.content (chat completion format)
                            if "message" in first and "content" in first["message"]:
                                return first["message"]["content"]
                            # Check text (completion format)
                            if "text" in first:
                                return first["text"]
                    return json.dumps(parsed)
            except Exception as e:
                logger.info(f"Perplexity HTTP error: {e}")
                return None

        return await asyncio.to_thread(_sync_call)

    async def ainvoke(self, prompt: str):
        class Resp:
            def __init__(self, content: str):
                self.content = content

        if not self._init_attempted:
            await asyncio.to_thread(self._init_llm)

        if self._llm is not None:
            try:
                if hasattr(self._llm, "ainvoke"):
                    result = await self._llm.ainvoke(prompt)
                elif hasattr(self._llm, "invoke"):
                    result = await asyncio.to_thread(self._llm.invoke, prompt)
                elif hasattr(self._llm, "predict"):
                    result = await asyncio.to_thread(self._llm.predict, prompt)
                else:
                    result = None

                if result is None:
                    raise RuntimeError("LLM returned no result")

                if isinstance(result, str):
                    return Resp(result)

                content = getattr(result, "content", None)
                if content is not None:
                    return Resp(content)

                return Resp(json.dumps(result))

            except Exception as exc:  # noqa: S110 - logging only
                logger.info(f"LLM invocation error: {exc}")

        if self._ollama_http_available or (self.provider == "ollama"):
            if not self._ollama_http_available:
                self._ollama_http_available = await asyncio.to_thread(
                    self._check_ollama_http
                )
            if self._ollama_http_available:
                text = await self._ollama_http_generate(prompt)
                if text is not None:
                    return Resp(text)

        # Try Perplexity HTTP API if provider is perplexity
        if self.provider == "perplexity" and os.environ.get("PERPLEXITY_API_KEY"):
            text = await self._perplexity_http_generate(prompt)
            if text is not None:
                return Resp(text)

        mock = json.dumps(
            [
                {
                    "title": "Community Cleanup",
                    "organization": "Local Org",
                    "description": "Help clean up the park",
                    "city": "Sample",
                    "state": "ST",
                    "lat": 0.0,
                    "lon": 0.0,
                }
            ]
        )
        return Resp(mock)
