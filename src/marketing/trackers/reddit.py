"""Reddit metrics tracker using public JSON API (no auth required)."""

import requests
from marketing.trackers.base import BaseTracker


class RedditTracker(BaseTracker):
    """Track Reddit submission metrics via public JSON endpoint."""

    def __init__(self, user_agent: str = "campaign-manager:v0.1"):
        self.user_agent = user_agent

    def fetch_metrics(self, external_id: str) -> dict:
        """Fetch metrics for a Reddit submission by ID."""
        headers = {"User-Agent": self.user_agent}
        resp = requests.get(
            f"https://www.reddit.com/comments/{external_id}.json",
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        post_data = data[0]["data"]["children"][0]["data"]
        return {
            "upvotes": post_data.get("score", 0),
            "comments": post_data.get("num_comments", 0),
            "views": 0,
            "extra": {
                "upvote_ratio": post_data.get("upvote_ratio", 0),
                "permalink": f"https://www.reddit.com{post_data.get('permalink', '')}",
            },
        }
