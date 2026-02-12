"""Reddit metrics tracker using PRAW."""

from marketing.trackers.base import BaseTracker

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False


class RedditTracker(BaseTracker):
    """Track Reddit submission metrics via PRAW."""

    def __init__(self, credentials: dict):
        self.credentials = credentials
        if PRAW_AVAILABLE and credentials.get("client_id") and credentials.get("client_secret"):
            self.reddit = praw.Reddit(
                client_id=credentials["client_id"],
                client_secret=credentials["client_secret"],
                user_agent=credentials.get("user_agent", "campaign-manager:v0.1"),
                username=credentials.get("username", ""),
                password=credentials.get("password", ""),
            )
        else:
            self.reddit = None

    def fetch_metrics(self, external_id: str) -> dict:
        if not self.reddit:
            raise RuntimeError("Reddit client not initialized. Check credentials.")

        submission = self.reddit.submission(id=external_id)
        return {
            "upvotes": submission.score,
            "comments": submission.num_comments,
            "views": 0,
            "extra": {
                "upvote_ratio": submission.upvote_ratio,
                "is_locked": submission.locked,
            },
        }
