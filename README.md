# Campaign Manager

A Python CLI tool for managing marketing campaigns across multiple platforms (Reddit, Dev.to, and more).

Designed to be **product-agnostic** — you bring your own product details, content, and AI-assisted writing. The tool handles campaign lifecycle management, multi-platform posting, metrics tracking, and performance reporting.

---

## Features

- **Campaign lifecycle management** - Create campaigns, organize drafts, track status
- **Multi-platform posting** - Reddit (with manual fallback) and Dev.to support
- **Metrics tracking** - Fetch upvotes, comments, views from posted content
- **Manual fallback for Reddit** - Copy to clipboard when OAuth isn't available (post manually, track automatically)
- **Rich CLI output** - Tables, progress indicators, color-coded status
- **Marketing brief generation** - AI-ready summaries from your project config
- **SQLite database** - Local storage for campaigns, drafts, posts, metrics
- **Dry-run mode** - Validate before posting
- **Extensible architecture** - Add new platforms via `BasePoster` and `BaseTracker` interfaces

---

## Quick Start

### Install

```bash
cd campaign-manager
pip install -e .
```

This installs the `marketing` command globally.

### Initialize a project

```bash
cd /path/to/your-product
marketing init --name "MyApp"
```

This creates:
- `project.yaml` - Product configuration
- `.marketing/` - Database and content templates
- `.marketing/campaigns.db` - SQLite database

### Create a campaign

```bash
marketing campaign create "launch-week-1" --description "Initial launch campaign"
```

### Add a draft

Write your content in Markdown (e.g., `content/reddit_post.md`), then:

```bash
marketing draft add reddit \
  --file content/reddit_post.md \
  --title "Show HN: MyApp - AI-powered productivity tool" \
  --subreddit SideProject \
  --campaign launch-week-1
```

### Approve the draft

```bash
marketing draft list
marketing draft approve 1
```

### Post (dry-run first)

```bash
# Validate without posting
marketing post reddit --draft-id 1 --dry-run

# Post via API (requires Reddit OAuth)
marketing post reddit --draft-id 1

# Post manually (copies to clipboard)
marketing post reddit --draft-id 1 --manual
```

### Track metrics

```bash
marketing track --campaign launch-week-1
```

### Generate report

```bash
marketing report --campaign launch-week-1 --format table
```

---

## Commands Reference

### `marketing init`

Initialize a new marketing project.

```bash
marketing init --name "MyApp"
```

Creates `project.yaml` and `.marketing/` directory with database.

### `marketing analyze`

Generate a marketing brief from your `project.yaml` config.

```bash
marketing analyze
marketing analyze --live  # Fetch live subreddit stats from Reddit API
```

Outputs: `.marketing/brief.json` and `.marketing/brief.md`

Use this to feed context into AI assistants for content generation.

### `marketing campaign`

Manage campaigns.

```bash
# Create a new campaign
marketing campaign create "launch-week-1" --description "Initial launch"

# List campaigns
marketing campaign list
marketing campaign list --status active
```

### `marketing draft`

Manage content drafts.

```bash
# Add a draft
marketing draft add reddit \
  --file content/post.md \
  --title "Show HN: MyApp" \
  --subreddit SideProject

marketing draft add devto \
  --file content/article.md \
  --title "Building MyApp: Lessons Learned" \
  --tags "webdev,startup,api"

# List drafts
marketing draft list
marketing draft list --status approved --channel reddit

# Approve for posting
marketing draft approve 1
```

### `marketing post`

Post approved drafts to platforms.

```bash
# Reddit
marketing post reddit --draft-id 1 --dry-run
marketing post reddit --draft-id 1
marketing post reddit --draft-id 1 --manual  # Clipboard fallback

# Dev.to
marketing post devto --draft-id 2 --dry-run
marketing post devto --draft-id 2
```

### `marketing track`

Fetch latest metrics for posted content.

```bash
marketing track
marketing track --campaign launch-week-1
```

Updates the database with current upvotes, comments, and views.

### `marketing report`

Generate performance reports.

```bash
marketing report --campaign launch-week-1 --format table
marketing report --format json > report.json
marketing report --format markdown > report.md
```

---

## Supported Channels

### Reddit (PRAW)

Uses the [PRAW](https://praw.readthedocs.io/) library for Reddit OAuth2.

**Important:** As of November 2025, Reddit requires pre-approval for new OAuth applications. If you don't have an approved app, use `--manual` mode.

**Manual mode (`--manual`):**
- Copies title + body to clipboard
- You paste manually into Reddit
- Database tracks the post as "manual" (no API ID)
- Metrics can still be tracked if you add the external URL later

**API mode:**
- Requires Reddit OAuth2 credentials (see Credentials Setup below)
- Posts directly via API
- Returns post ID and URL for tracking

### Dev.to

Uses the [Dev.to REST API](https://developers.forem.com/api).

- Requires API key (generated in Dev.to settings)
- Posts as drafts by default (`published=False`)
- Supports tags and series

---

## Project Configuration

The `project.yaml` file defines your product details for AI-assisted content generation.

**Template structure:**

```yaml
product:
  name: "MyApp"
  tagline: "Your productivity copilot"
  url: "https://myapp.com"
  description: "AI-powered task management and automation"
  category: "developer-tools"

audience:
  primary: "indie developers and small teams"
  pain_points:
    - "Scattered tools and context switching"
    - "Manual repetitive tasks"
  keywords:
    - "automation"
    - "productivity"
    - "developer-tools"

channels:
  reddit:
    subreddits:
      - "SideProject"
      - "webdev"
      - "programming"
    flair: "Show & Tell"
  devto:
    tags:
      - "api"
      - "webdev"
      - "productivity"
    series: "Building MyApp"

pricing:
  model: "freemium"
  tiers:
    - name: "Free"
      price: "$0"
      features:
        - "100 API calls/month"
        - "Community support"
    - name: "Pro"
      price: "$29/mo"
      features:
        - "10,000 API calls/month"
        - "Priority support"
```

Fill this in once, then run `marketing analyze` to generate AI-ready briefs.

---

## Credentials Setup

Create a `.env` file in your project root (next to `project.yaml`):

```bash
# Reddit OAuth2
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
REDDIT_USER_AGENT=campaign-manager:v0.1 (by u/your_username)

# Dev.to API
DEVTO_API_KEY=your_devto_api_key
```

### Getting Reddit credentials

1. Go to https://www.reddit.com/prefs/apps
2. Create a new "script" app
3. Note your `client_id` and `client_secret`
4. **Note:** New apps require Reddit approval (as of Nov 2025). Use `--manual` mode if pending.

### Getting Dev.to API key

1. Go to https://dev.to/settings/extensions
2. Generate an API key under "DEV Community API Keys"
3. Copy to `.env` as `DEVTO_API_KEY`

---

## Workflow

### 1. Setup

```bash
cd your-product/
marketing init --name "MyApp"
```

Edit `project.yaml` with your product details.

### 2. Generate marketing brief

```bash
marketing analyze
```

This creates `.marketing/brief.md` — use it as context for AI content generation.

### 3. Create campaign

```bash
marketing campaign create "launch-week-1" --description "Initial launch"
```

### 4. Write content (with Claude/GPT)

In your Claude Code session:

> "Generate a Reddit post for r/SideProject announcing MyApp. Use the brief in .marketing/brief.md as context."

Save output to `content/reddit_post_1.md`.

### 5. Register draft

```bash
marketing draft add reddit \
  --file content/reddit_post_1.md \
  --title "Show HN: MyApp - AI-powered productivity tool" \
  --subreddit SideProject
```

### 6. Approve and post

```bash
marketing draft approve 1
marketing post reddit --draft-id 1 --dry-run  # Validate
marketing post reddit --draft-id 1            # Post
```

### 7. Track and report

Wait a few hours/days, then:

```bash
marketing track
marketing report --campaign launch-week-1
```

---

## Adding New Channels

The tool is designed for easy extension to new platforms (Hacker News, Twitter, LinkedIn, etc.).

### 1. Implement `BasePoster`

Create `src/marketing/posters/yourplatform.py`:

```python
from marketing.posters.base import BasePoster

class YourPlatformPoster(BasePoster):
    def __init__(self, config: dict):
        self.config = config

    def validate(self, title: str, body: str, **kwargs) -> list[str]:
        """Return list of validation issues (empty = valid)."""
        issues = []
        if len(title) > 100:
            issues.append("Title too long (max 100 chars)")
        return issues

    def post(self, title: str, body: str, **kwargs) -> dict:
        """Post content. Return dict with external_id and external_url."""
        # Call your platform's API
        response = your_platform_api.create_post(title, body)
        return {
            "external_id": response["id"],
            "external_url": response["url"]
        }

    def is_configured(self) -> bool:
        """Check if credentials are set."""
        return bool(self.config.get("api_key"))
```

### 2. Implement `BaseTracker`

Create `src/marketing/trackers/yourplatform.py`:

```python
from marketing.trackers.base import BaseTracker

class YourPlatformTracker(BaseTracker):
    def __init__(self, config: dict):
        self.config = config

    def fetch_metrics(self, external_id: str) -> dict:
        """Fetch current metrics."""
        response = your_platform_api.get_post(external_id)
        return {
            "upvotes": response["likes"],
            "comments": response["comment_count"],
            "views": response["views"],
            "extra": {"shares": response["shares"]}
        }
```

### 3. Wire into CLI

In `src/marketing/cli.py`, add your platform to the `post` and `track` commands:

```python
@click.argument("channel", type=click.Choice(["reddit", "devto", "yourplatform"]))
```

Follow the pattern from `reddit` or `devto` handlers.

### 4. Update config

Add credentials to `.env`:

```bash
YOURPLATFORM_API_KEY=your_key
```

And optionally add platform-specific config to `project.yaml`.

---

## File Structure

```
src/marketing/
├── __init__.py
├── __main__.py
├── cli.py                  # Main CLI entry point
├── config.py               # Project config loader
├── db.py                   # SQLite initialization
├── models/
│   ├── campaign.py         # Campaign CRUD
│   ├── draft.py            # Draft CRUD
│   ├── post.py             # Post CRUD
│   └── metric.py           # Metric CRUD
├── posters/
│   ├── base.py             # BasePoster interface
│   ├── reddit.py           # Reddit poster (PRAW)
│   └── devto.py            # Dev.to poster (REST API)
├── trackers/
│   ├── base.py             # BaseTracker interface
│   ├── reddit.py           # Reddit metrics tracker
│   └── devto.py            # Dev.to metrics tracker
├── analyzers/
│   ├── brief.py            # Marketing brief generator
│   └── channels.py         # Live channel analysis
└── reports/
    ├── summary.py          # Campaign summary logic
    └── formatters.py       # Table/JSON/Markdown output
```

---

## License

MIT

---

## Contributing

This tool is designed for personal use and rapid iteration. If you add support for new platforms or features, feel free to share back!

**Common extensions:**
- Hacker News (manual posting + tracking via Algolia API)
- Twitter/X (requires OAuth2 for posting)
- LinkedIn (REST API for articles)
- Product Hunt (API for launches)

---

## FAQ

**Q: Why SQLite instead of a SaaS analytics platform?**
A: Simplicity and cost. You own your data, no API rate limits, works offline.

**Q: Why manual mode for Reddit?**
A: Reddit's November 2025 policy change requires pre-approval for new OAuth apps. Manual mode lets you post immediately while approval is pending.

**Q: Can I use this for multiple products?**
A: Yes. Each product should have its own `project.yaml`. Run `marketing init` in separate directories.

**Q: How do I update metrics over time?**
A: Run `marketing track` periodically (cron job, manual, etc.). Each run adds a new metrics snapshot.

**Q: Can I edit content after posting?**
A: Not through this tool. Edit directly on the platform (Reddit/Dev.to). The tool tracks external IDs, not content sync.

---

## Acknowledgments

Built to scratch the itch of "I have Claude writing great marketing content, now where do I put it all?"

The tool manages the boring parts (campaign tracking, metrics, posting) so you can focus on the creative parts (content, strategy, timing).
