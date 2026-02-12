"""Live channel analysis - subreddit rules, Dev.to tag stats."""

import requests


def get_subreddit_info(subreddit: str, user_agent: str = "campaign-manager:v0.1") -> dict:
    """Fetch subreddit info from Reddit's public JSON API (no auth needed)."""
    headers = {"User-Agent": user_agent}
    info = {"subreddit": subreddit, "error": None}

    try:
        resp = requests.get(
            f"https://www.reddit.com/r/{subreddit}/about.json",
            headers=headers,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            info["subscribers"] = data.get("subscribers", 0)
            info["description"] = data.get("public_description", "")
            info["submission_type"] = data.get("submission_type", "any")
            info["allow_images"] = data.get("allow_images", True)
            info["selftext_only"] = data.get("submission_type") == "self"
        else:
            info["error"] = f"HTTP {resp.status_code}"
    except requests.RequestException as e:
        info["error"] = str(e)

    return info


def get_devto_tag_info(tag: str) -> dict:
    """Fetch Dev.to tag info from public API."""
    info = {"tag": tag, "error": None}

    try:
        resp = requests.get("https://dev.to/api/tags?per_page=100", timeout=10)
        if resp.status_code == 200:
            tags = resp.json()
            match = next((t for t in tags if t.get("name", "").lower() == tag.lower()), None)
            if match:
                info["name"] = match.get("name", tag)
            else:
                info["name"] = tag
                info["note"] = "Tag not found in top 100, may still be valid"
        else:
            info["error"] = f"HTTP {resp.status_code}"
    except requests.RequestException as e:
        info["error"] = str(e)

    return info


def analyze_channels(config: dict, live: bool = False) -> dict:
    """Analyze configured channels. If live=True, fetch real data."""
    channels = config.get("channels", {})
    result = {}

    reddit_config = channels.get("reddit", {})
    subreddits = [s for s in reddit_config.get("subreddits", []) if s]
    result["reddit"] = {"subreddits": []}
    for sub in subreddits:
        if live:
            info = get_subreddit_info(sub)
        else:
            info = {"subreddit": sub, "note": "Use --live to fetch real data"}
        result["reddit"]["subreddits"].append(info)

    devto_config = channels.get("devto", {})
    tags = [t for t in devto_config.get("tags", []) if t]
    result["devto"] = {"tags": []}
    for tag in tags:
        if live:
            info = get_devto_tag_info(tag)
        else:
            info = {"tag": tag, "note": "Use --live to fetch real data"}
        result["devto"]["tags"].append(info)

    return result
