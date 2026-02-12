"""Generate marketing brief from project.yaml config."""

import json
from pathlib import Path
from marketing.config import load_project_config, get_marketing_dir


def generate_brief() -> dict:
    """Generate a marketing brief from project config."""
    config = load_project_config()
    product = config.get("product", {})
    audience = config.get("audience", {})
    channels = config.get("channels", {})
    pricing = config.get("pricing", {})

    pain_points = audience.get("pain_points", [])
    angles = []
    for pain in pain_points:
        if pain:
            angles.append(f"How {product.get('name', 'our product')} solves: {pain}")

    return {
        "product_summary": {
            "name": product.get("name", ""),
            "tagline": product.get("tagline", ""),
            "url": product.get("url", ""),
            "description": product.get("description", ""),
            "category": product.get("category", ""),
        },
        "target_audience": {
            "primary": audience.get("primary", ""),
            "pain_points": [p for p in pain_points if p],
            "keywords": [k for k in audience.get("keywords", []) if k],
        },
        "channel_strategy": {
            "reddit": {
                "subreddits": [s for s in channels.get("reddit", {}).get("subreddits", []) if s],
                "flair": channels.get("reddit", {}).get("flair", ""),
            },
            "devto": {
                "tags": [t for t in channels.get("devto", {}).get("tags", []) if t],
                "series": channels.get("devto", {}).get("series", ""),
            },
        },
        "pricing_summary": {
            "model": pricing.get("model", ""),
            "tiers": pricing.get("tiers", []),
        },
        "suggested_angles": angles,
    }


def save_brief(brief: dict) -> tuple[Path, Path]:
    """Save brief as both JSON and Markdown. Returns (json_path, md_path)."""
    marketing_dir = get_marketing_dir()

    json_path = marketing_dir / "brief.json"
    with open(json_path, "w") as f:
        json.dump(brief, f, indent=2)

    md_path = marketing_dir / "brief.md"
    with open(md_path, "w") as f:
        f.write(format_brief_markdown(brief))

    return json_path, md_path


def format_brief_markdown(brief: dict) -> str:
    """Format brief as readable markdown."""
    lines = ["# Marketing Brief\n"]

    ps = brief["product_summary"]
    lines.append(f"## Product: {ps['name']}")
    if ps["tagline"]:
        lines.append(f"*{ps['tagline']}*\n")
    if ps["url"]:
        lines.append(f"**URL:** {ps['url']}")
    if ps["description"]:
        lines.append(f"\n{ps['description']}\n")
    if ps["category"]:
        lines.append(f"**Category:** {ps['category']}\n")

    ta = brief["target_audience"]
    lines.append("## Target Audience")
    if ta["primary"]:
        lines.append(f"**Primary:** {ta['primary']}\n")
    if ta["pain_points"]:
        lines.append("**Pain Points:**")
        for p in ta["pain_points"]:
            lines.append(f"- {p}")
        lines.append("")
    if ta["keywords"]:
        lines.append(f"**Keywords:** {', '.join(ta['keywords'])}\n")

    cs = brief["channel_strategy"]
    lines.append("## Channel Strategy")
    if cs["reddit"]["subreddits"]:
        lines.append(f"**Reddit:** {', '.join('r/' + s for s in cs['reddit']['subreddits'])}")
    if cs["devto"]["tags"]:
        lines.append(f"**Dev.to tags:** {', '.join(cs['devto']['tags'])}")
    lines.append("")

    if brief["suggested_angles"]:
        lines.append("## Suggested Content Angles")
        for angle in brief["suggested_angles"]:
            lines.append(f"- {angle}")
        lines.append("")

    pr = brief["pricing_summary"]
    if pr["model"]:
        lines.append("## Pricing")
        lines.append(f"**Model:** {pr['model']}\n")
        for tier in pr.get("tiers", []):
            if tier.get("name"):
                features = ", ".join(tier.get("features", []))
                lines.append(f"- **{tier['name']}** ({tier.get('price', 'N/A')}): {features}")

    return "\n".join(lines) + "\n"
