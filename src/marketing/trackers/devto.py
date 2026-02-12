"""Dev.to metrics tracker using REST API."""

import requests
from marketing.trackers.base import BaseTracker


class DevtoTracker(BaseTracker):
    """Track Dev.to article metrics via REST API."""

    API_BASE = "https://dev.to/api"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_metrics(self, external_id: str) -> dict:
        headers = {"api-key": self.api_key} if self.api_key else {}
        resp = requests.get(f"{self.API_BASE}/articles/{external_id}", headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        return {
            "upvotes": data.get("positive_reactions_count", 0),
            "comments": data.get("comments_count", 0),
            "views": data.get("page_views_count", 0),
            "extra": {
                "reading_time": data.get("reading_time_minutes", 0),
            },
        }
