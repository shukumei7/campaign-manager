"""Format reports as markdown, JSON, or rich table."""

import json
from rich.console import Console
from rich.table import Table


def format_json(data: dict) -> str:
    return json.dumps(data, indent=2)


def format_markdown(data: dict) -> str:
    lines = ["# Campaign Report\n"]
    lines.append(f"**Total Posts:** {data['total_posts']}")
    t = data["totals"]
    lines.append(f"**Totals:** {t['upvotes']} upvotes, {t['comments']} comments, {t['views']} views\n")

    if data["channels"]:
        lines.append("## By Channel")
        for ch, stats in data["channels"].items():
            lines.append(f"### {ch.title()}")
            lines.append(f"- Posts: {stats['posts']}")
            lines.append(f"- Upvotes: {stats['upvotes']}")
            lines.append(f"- Comments: {stats['comments']}")
            lines.append(f"- Views: {stats['views']}")
        lines.append("")

    if data["posts"]:
        lines.append("## Posts")
        for p in data["posts"]:
            m = p["metrics"]
            lines.append(f"- **{p['title']}** ({p['channel']}) - {m['upvotes']}up/{m['comments']}comments/{m['views']}views")
            if p["url"]:
                lines.append(f"  {p['url']}")

    return "\n".join(lines) + "\n"


def format_table(data: dict):
    """Print a rich table to console."""
    console = Console()

    table = Table(title="Campaign Report")
    table.add_column("Title", style="cyan")
    table.add_column("Channel", style="green")
    table.add_column("Campaign", style="yellow")
    table.add_column("Upvotes", justify="right")
    table.add_column("Comments", justify="right")
    table.add_column("Views", justify="right")
    table.add_column("URL", style="dim")

    for p in data.get("posts", []):
        m = p["metrics"]
        table.add_row(
            p["title"], p["channel"], p.get("campaign", ""),
            str(m["upvotes"]), str(m["comments"]), str(m["views"]),
            p.get("url", "")
        )

    t = data["totals"]
    table.add_row(
        f"TOTAL ({data['total_posts']} posts)", "", "",
        str(t["upvotes"]), str(t["comments"]), str(t["views"]), "",
        style="bold"
    )

    console.print(table)
