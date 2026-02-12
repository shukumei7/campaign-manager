"""Dev.to poster using REST API."""

import requests
from marketing.posters.base import BasePoster


class DevtoPoster(BasePoster):
    """Post articles to Dev.to via REST API."""

    API_BASE = "https://dev.to/api"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def validate(self, title: str, body: str, **kwargs) -> list[str]:
        issues = []
        check_credentials = kwargs.get("check_credentials", True)

        if check_credentials and not self.is_configured():
            issues.append("Dev.to API key not configured")
        if not title.strip():
            issues.append("Title cannot be empty")
        if not body.strip():
            issues.append("Body cannot be empty")

        tags = kwargs.get("tags", [])
        if len(tags) > 4:
            issues.append(f"Too many tags ({len(tags)}/4 max)")

        return issues

    def post(self, title: str, body: str, **kwargs) -> dict:
        tags = kwargs.get("tags", [])
        published = kwargs.get("published", False)

        headers = {"api-key": self.api_key, "Content-Type": "application/json"}
        payload = {
            "article": {
                "title": title,
                "body_markdown": body,
                "published": published,
                "tags": tags,
            }
        }

        resp = requests.post(f"{self.API_BASE}/articles", headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        return {"external_id": str(data["id"]), "external_url": data["url"]}
