import json
import asyncio
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from backend.event_discovery.cache_manager import EventCacheManager


def fake_loader_factory(html_content):
    class FakeDoc:
        def __init__(self, page_content):
            self.page_content = page_content

    class FakeLoader:
        def __init__(self, urls=None):
            self._urls = urls

        async def aload(self):
            return [FakeDoc(html_content)]

    return FakeLoader


def make_fake_llm_response(events):
    class Resp:
        def __init__(self, content):
            self.content = content

    class FakeLLM:
        async def ainvoke(self, prompt):
            return Resp(json.dumps(events))

    return FakeLLM


def test_scrape_and_persist_images(tmp_path):
    # Prepare one fake event with images
    events_payload = [
        {
            "title": "Community Cleanup",
            "organization": "Local Org",
            "description": "Clean up the park",
            "city": "SampleCity",
            "state": "ST",
            "lat": 1.0,
            "lon": 2.0,
            "images": ["http://example.com/i1.jpg", "http://example.com/i2.jpg"],
            "url": "http://example.org/event/1",
            "date": "2025-12-01",
        }
    ]

    # Patch AsyncHtmlLoader and HybridLLM used inside cache_manager
    from app import app as flask_app, db, Event, EventImage

    with flask_app.app_context():
        db.create_all()
        with patch(
            "event_discovery.cache_manager.AsyncHtmlLoader",
            new=fake_loader_factory("<html></html>"),
        ):
            with patch(
                "event_discovery.cache_manager.HybridLLM",
                new=make_fake_llm_response(events_payload),
            ):
                mgr = EventCacheManager()

                # override geocoder to return a predictable lat/lon
                mgr.geocoder = SimpleNamespace(
                    geocode=lambda q: SimpleNamespace(latitude=1.0, longitude=2.0)
                )

                # Run search_by_location which triggers scrape -> upsert
                persisted = asyncio.run(mgr.search_by_location("SampleCity", "ST"))

                # ensure persisted list was returned
                assert isinstance(persisted, list) and len(persisted) >= 1

                # verify Event and EventImage rows exist in DB
                ev = Event.query.filter_by(url="http://example.org/event/1").first()
                assert ev is not None
                imgs = (
                    EventImage.query.filter_by(event_id=ev.id)
                    .order_by(EventImage.position.asc())
                    .all()
                )
                assert len(imgs) == 2
                assert imgs[0].url == "http://example.com/i1.jpg"
                assert imgs[1].url == "http://example.com/i2.jpg"

        # cleanup DB
        db.session.remove()
        db.drop_all()
