"""Event discovery module using hybrid LLM and web scraping."""

from .llm import HybridLLM
from .cache_manager import EventCacheManager

__all__ = ["HybridLLM", "EventCacheManager"]
