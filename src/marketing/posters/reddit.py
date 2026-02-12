"""Reddit poster using PRAW."""

import subprocess
import sys
from marketing.posters.base import BasePoster

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False


class RedditPoster(BasePoster):
    """Post content to Reddit via PRAW."""

    def __init__(self, credentials: dict):
        self.credentials = credentials
        self.client_id = credentials.get("client_id", "")
        self.client_secret = credentials.get("client_secret", "")
        self.user_agent = credentials.get("user_agent", "campaign-manager:v0.1")
        self.username = credentials.get("username", "")
        self.password = credentials.get("password", "")

        if PRAW_AVAILABLE and self.is_configured():
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
                username=self.username,
                password=self.password,
            )
        else:
            self.reddit = None

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def validate(self, title: str, body: str, **kwargs) -> list[str]:
        """Validate content. Pass check_credentials=False to skip credential checks."""
        issues = []
        check_credentials = kwargs.get("check_credentials", True)

        if check_credentials:
            if not PRAW_AVAILABLE:
                issues.append("PRAW library not installed (pip install praw)")
            if not self.is_configured():
                issues.append("Reddit credentials not configured")

        if len(title) > 300:
            issues.append(f"Title too long ({len(title)}/300 chars)")
        if not title.strip():
            issues.append("Title cannot be empty")
        if not body.strip():
            issues.append("Body cannot be empty")
        if not kwargs.get("subreddit"):
            issues.append("Subreddit must be specified")

        return issues

    def post(self, title: str, body: str, **kwargs) -> dict:
        manual = kwargs.get("manual", False)
        subreddit_name = kwargs.get("subreddit", "")

        # Auto-fallback to manual mode if PRAW not available
        if not manual and not self.reddit:
            print("[yellow]Reddit API not configured. Falling back to manual mode.[/yellow]")
            manual = True

        if manual:
            if sys.platform == "win32":
                try:
                    subprocess.run(["clip"], input=body.encode(), check=True)
                    print(f"Body copied to clipboard. Please manually post to r/{subreddit_name}")
                except Exception as e:
                    print(f"Could not copy to clipboard: {e}")
                    print(f"Please manually post the following to r/{subreddit_name}:")
                    print(body)
            else:
                print(f"Please manually post the following to r/{subreddit_name}:")
                print(body)
            return {"external_id": "manual", "external_url": ""}

        subreddit = self.reddit.subreddit(subreddit_name)
        submission = subreddit.submit(title, selftext=body)
        return {"external_id": submission.id, "external_url": submission.url}
