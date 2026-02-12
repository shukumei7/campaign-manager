"""Campaign Manager CLI."""

import json
import shutil
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from marketing.config import find_project_root, get_marketing_dir, load_project_config, load_env
from marketing.db import init_db

console = Console()


@click.group()
def cli():
    """Marketing Campaign Manager - manage campaigns across Reddit, Dev.to, and more."""
    pass


# ── init ──
@cli.command()
@click.option("--name", prompt="Product name", help="Name of the product")
def init(name):
    """Initialize a new marketing project."""
    root = Path.cwd()
    project_file = root / "project.yaml"

    if project_file.exists():
        console.print("[yellow]project.yaml already exists. Skipping.[/yellow]")
    else:
        template_dir = Path(__file__).parent.parent.parent / "templates"
        if template_dir.exists():
            shutil.copy(template_dir / "project.yaml", project_file)
        else:
            import yaml

            config = {
                "product": {"name": name, "tagline": "", "url": "", "description": "", "category": ""},
                "audience": {"primary": "", "pain_points": [""], "keywords": [""]},
                "channels": {"reddit": {"subreddits": [""], "flair": ""}, "devto": {"tags": [""], "series": ""}},
                "pricing": {"model": "", "tiers": [{"name": "", "price": "", "features": [""]}]},
            }
            with open(project_file, "w") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        content = project_file.read_text()
        content = content.replace('name: ""', f'name: "{name}"', 1)
        project_file.write_text(content)
        console.print(f"[green]Created project.yaml for '{name}'[/green]")

    marketing_dir = root / ".marketing"
    marketing_dir.mkdir(exist_ok=True)

    init_db()
    console.print("[green]Initialized .marketing/ directory with database[/green]")

    template_dir = Path(__file__).parent.parent.parent / "templates"
    if template_dir.exists():
        for tmpl in ["reddit_post.md", "devto_article.md"]:
            src = template_dir / tmpl
            dst = marketing_dir / tmpl
            if src.exists() and not dst.exists():
                shutil.copy(src, dst)
        console.print("[green]Copied content templates to .marketing/[/green]")


# ── analyze ──
@cli.command()
@click.option("--live", is_flag=True, help="Fetch live data from platform APIs")
def analyze(live):
    """Generate marketing brief from project config."""
    from marketing.analyzers.brief import generate_brief, save_brief
    from marketing.analyzers.channels import analyze_channels

    config = load_project_config()
    brief = generate_brief()
    json_path, md_path = save_brief(brief)
    console.print(f"[green]Brief saved to {md_path}[/green]")

    if live:
        console.print("[cyan]Fetching live channel data...[/cyan]")
        channel_data = analyze_channels(config, live=True)
        channel_path = get_marketing_dir() / "channels.json"
        with open(channel_path, "w") as f:
            json.dump(channel_data, f, indent=2)
        console.print(f"[green]Channel analysis saved to {channel_path}[/green]")

        for sub_info in channel_data.get("reddit", {}).get("subreddits", []):
            if sub_info.get("error"):
                console.print(f"  [red]r/{sub_info['subreddit']}: {sub_info['error']}[/red]")
            elif sub_info.get("subscribers"):
                console.print(f"  [cyan]r/{sub_info['subreddit']}: {sub_info['subscribers']:,} subscribers[/cyan]")

    console.print(f"\n[bold]Product:[/bold] {brief['product_summary']['name']}")
    console.print(f"[bold]Audience:[/bold] {brief['target_audience']['primary']}")
    if brief["suggested_angles"]:
        console.print("[bold]Suggested angles:[/bold]")
        for angle in brief["suggested_angles"]:
            console.print(f"  - {angle}")


# ── campaign group ──
@cli.group()
def campaign():
    """Manage campaigns."""
    pass


@campaign.command("create")
@click.argument("name")
@click.option("--description", "-d", default="", help="Campaign description")
def campaign_create(name, description):
    """Create a new campaign."""
    from marketing.models.campaign import create_campaign, get_campaign_by_name

    init_db()

    existing = get_campaign_by_name(name)
    if existing:
        console.print(f"[red]Campaign '{name}' already exists (id={existing['id']})[/red]")
        return

    c = create_campaign(name, description)
    console.print(f"[green]Created campaign '{name}' (id={c['id']})[/green]")


@campaign.command("list")
@click.option("--status", type=click.Choice(["active", "paused", "completed"]), default=None)
def campaign_list(status):
    """List campaigns."""
    from marketing.models.campaign import list_campaigns

    init_db()

    campaigns = list_campaigns(status)
    if not campaigns:
        console.print("[yellow]No campaigns found.[/yellow]")
        return

    table = Table(title="Campaigns")
    table.add_column("ID", justify="right")
    table.add_column("Name", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Description")
    table.add_column("Created")

    for c in campaigns:
        table.add_row(str(c["id"]), c["name"], c["status"], c.get("description", ""), c["created_at"])

    console.print(table)


# ── draft group ──
@cli.group()
def draft():
    """Manage content drafts."""
    pass


@draft.command("add")
@click.argument("channel", type=click.Choice(["reddit", "devto"]))
@click.option("--file", "-f", required=True, type=click.Path(exists=True), help="Path to content file")
@click.option("--title", "-t", required=True, help="Draft title")
@click.option("--campaign", "-c", default=None, help="Campaign name (uses first active if not specified)")
@click.option("--subreddit", "-s", default=None, help="Target subreddit (reddit only)")
@click.option("--tags", default=None, help="Comma-separated tags (devto only)")
def draft_add(channel, file, title, campaign, subreddit, tags):
    """Register a content draft for a channel."""
    from marketing.models.draft import add_draft
    from marketing.models.campaign import list_campaigns, get_campaign_by_name, create_campaign

    init_db()

    if campaign:
        camp = get_campaign_by_name(campaign)
        if not camp:
            console.print(f"[red]Campaign '{campaign}' not found. Create it first.[/red]")
            return
    else:
        active = list_campaigns("active")
        if active:
            camp = active[0]
            console.print(f"[dim]Using campaign: {camp['name']}[/dim]")
        else:
            camp = create_campaign("default", "Auto-created default campaign")
            console.print("[dim]Created default campaign[/dim]")

    metadata = {}
    if subreddit:
        metadata["subreddit"] = subreddit
    if tags:
        metadata["tags"] = [t.strip() for t in tags.split(",")]

    file_path = str(Path(file).resolve())
    d = add_draft(camp["id"], channel, title, file_path, metadata)
    console.print(f"[green]Added draft #{d['id']}: '{title}' for {channel}[/green]")


@draft.command("list")
@click.option("--status", type=click.Choice(["draft", "approved", "posted", "failed"]), default=None)
@click.option("--channel", type=click.Choice(["reddit", "devto"]), default=None)
@click.option("--campaign", "-c", default=None, help="Campaign name filter")
def draft_list(status, channel, campaign):
    """List content drafts."""
    from marketing.models.draft import list_drafts
    from marketing.models.campaign import get_campaign_by_name

    init_db()

    campaign_id = None
    if campaign:
        camp = get_campaign_by_name(campaign)
        if camp:
            campaign_id = camp["id"]

    drafts = list_drafts(campaign_id=campaign_id, channel=channel, status=status)
    if not drafts:
        console.print("[yellow]No drafts found.[/yellow]")
        return

    table = Table(title="Drafts")
    table.add_column("ID", justify="right")
    table.add_column("Title", style="cyan")
    table.add_column("Channel", style="green")
    table.add_column("Status")
    table.add_column("Rev", justify="right")
    table.add_column("File", style="dim")

    for d in drafts:
        status_style = {"draft": "yellow", "approved": "green", "posted": "blue", "failed": "red"}.get(d["status"], "")
        table.add_row(
            str(d["id"]),
            d["title"],
            d["channel"],
            f"[{status_style}]{d['status']}[/{status_style}]",
            str(d["revision"]),
            d["file_path"],
        )

    console.print(table)


@draft.command("approve")
@click.argument("draft_id", type=int)
def draft_approve(draft_id):
    """Approve a draft for posting."""
    from marketing.models.draft import approve_draft, get_draft

    init_db()

    d = get_draft(draft_id)
    if not d:
        console.print(f"[red]Draft #{draft_id} not found.[/red]")
        return
    if d["status"] != "draft":
        console.print(f"[yellow]Draft #{draft_id} is already '{d['status']}'[/yellow]")
        return

    approve_draft(draft_id)
    console.print(f"[green]Draft #{draft_id} approved: '{d['title']}'[/green]")


# ── post ──
@cli.command()
@click.argument("channel", type=click.Choice(["reddit", "devto"]))
@click.option("--draft-id", "-d", required=True, type=int, help="Draft ID to post")
@click.option("--dry-run", is_flag=True, help="Validate without posting")
@click.option("--manual", is_flag=True, help="Copy to clipboard instead of API posting")
def post(channel, draft_id, dry_run, manual):
    """Post a draft to a platform."""
    from marketing.models.draft import get_draft, mark_posted, mark_failed
    from marketing.models.post import create_post

    init_db()

    d = get_draft(draft_id)
    if not d:
        console.print(f"[red]Draft #{draft_id} not found.[/red]")
        return

    if d["status"] not in ("approved", "draft"):
        console.print(f"[yellow]Draft #{draft_id} has status '{d['status']}' - expected 'approved'[/yellow]")
        return

    file_path = Path(d["file_path"])
    if not file_path.exists():
        console.print(f"[red]Content file not found: {file_path}[/red]")
        return
    body = file_path.read_text(encoding="utf-8")
    title = d["title"]
    metadata = json.loads(d["metadata_json"]) if d["metadata_json"] else {}

    env = load_env()

    if channel == "reddit":
        from marketing.posters.reddit import RedditPoster

        poster = RedditPoster(env["reddit"])
        subreddit = metadata.get("subreddit", "")
        issues = poster.validate(title, body, subreddit=subreddit, check_credentials=not (dry_run or manual))

        if issues:
            console.print("[red]Validation issues:[/red]")
            for issue in issues:
                console.print(f"  - {issue}")
            return

        if dry_run:
            console.print(f"[green]Dry run OK: '{title}' -> r/{subreddit}[/green]")
            return

        if not poster.is_configured() and not manual:
            console.print("[yellow]Reddit API not configured. Use --manual or set credentials in .env[/yellow]")
            manual = True

        try:
            result = poster.post(title, body, subreddit=subreddit, manual=manual)
            create_post(draft_id, channel, result.get("external_id"), result.get("external_url"))
            mark_posted(draft_id)
            if manual:
                console.print("[green]Content copied. Post manually and update external URL later.[/green]")
            else:
                console.print(f"[green]Posted to r/{subreddit}: {result.get('external_url', '')}[/green]")
        except Exception as e:
            mark_failed(draft_id)
            console.print(f"[red]Failed to post: {e}[/red]")

    elif channel == "devto":
        from marketing.posters.devto import DevtoPoster

        poster = DevtoPoster(env["devto"]["api_key"])
        tags = metadata.get("tags", [])
        issues = poster.validate(title, body, tags=tags, check_credentials=not dry_run)

        if issues:
            console.print("[red]Validation issues:[/red]")
            for issue in issues:
                console.print(f"  - {issue}")
            return

        if dry_run:
            console.print(f"[green]Dry run OK: '{title}' -> Dev.to (tags: {', '.join(tags)})[/green]")
            return

        if not poster.is_configured():
            console.print("[red]Dev.to API key not configured. Set DEVTO_API_KEY in .env[/red]")
            return

        try:
            result = poster.post(title, body, tags=tags, published=False)
            create_post(draft_id, channel, result.get("external_id"), result.get("external_url"))
            mark_posted(draft_id)
            console.print(f"[green]Posted as draft to Dev.to: {result.get('external_url', '')}[/green]")
        except Exception as e:
            mark_failed(draft_id)
            console.print(f"[red]Failed to post: {e}[/red]")


# ── track ──
@cli.command()
@click.option("--campaign", "-c", default=None, help="Campaign name to track")
def track(campaign):
    """Fetch latest metrics for posted content."""
    from marketing.models.post import list_posts
    from marketing.models.draft import get_draft
    from marketing.models.metric import add_metric
    from marketing.models.campaign import get_campaign_by_name

    init_db()

    env = load_env()
    posts = list_posts()

    if campaign:
        camp = get_campaign_by_name(campaign)
        if not camp:
            console.print(f"[red]Campaign '{campaign}' not found.[/red]")
            return

    tracked = 0
    for p in posts:
        p = dict(p) if not isinstance(p, dict) else p
        if not p.get("external_id") or p["external_id"] == "manual":
            continue

        ch = p["channel"]
        try:
            if ch == "reddit":
                from marketing.trackers.reddit import RedditTracker

                tracker = RedditTracker(env["reddit"])
                metrics = tracker.fetch_metrics(p["external_id"])
            elif ch == "devto":
                from marketing.trackers.devto import DevtoTracker

                tracker = DevtoTracker(env["devto"]["api_key"])
                metrics = tracker.fetch_metrics(p["external_id"])
            else:
                continue

            add_metric(p["id"], metrics["upvotes"], metrics["comments"], metrics["views"], metrics.get("extra"))

            d = get_draft(p["draft_id"])
            title = d["title"] if d else f"Post #{p['id']}"
            console.print(
                f"  [cyan]{title}[/cyan] ({ch}): "
                f"{metrics['upvotes']}up / {metrics['comments']}comments / {metrics['views']}views"
            )
            tracked += 1
        except Exception as e:
            console.print(f"  [red]Error tracking {ch} post {p['external_id']}: {e}[/red]")

    if tracked == 0:
        console.print("[yellow]No posts with trackable external IDs found.[/yellow]")
    else:
        console.print(f"\n[green]Tracked {tracked} post(s)[/green]")


# ── report ──
@cli.command()
@click.option("--campaign", "-c", default=None, help="Campaign name")
@click.option("--format", "fmt", type=click.Choice(["table", "json", "markdown"]), default="table")
def report(campaign, fmt):
    """Generate campaign performance report."""
    from marketing.reports.summary import campaign_summary
    from marketing.reports.formatters import format_json, format_markdown, format_table

    init_db()

    data = campaign_summary(campaign)

    if data["total_posts"] == 0:
        console.print("[yellow]No posted content found. Post some drafts first.[/yellow]")
        return

    if fmt == "json":
        console.print(format_json(data))
    elif fmt == "markdown":
        console.print(format_markdown(data))
    else:
        format_table(data)


if __name__ == "__main__":
    cli()
