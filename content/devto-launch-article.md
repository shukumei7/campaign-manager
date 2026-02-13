---
title: I stopped prompt-engineering the same text features and turned them into 9 API endpoints
published: false
tags: api, webdev, ai, productivity
series: Building TextKit API
---

Here's a pattern I kept repeating across projects:

```javascript
const response = await openai.chat.completions.create({
  model: "gpt-4o-mini",
  messages: [
    { role: "system", content: "You are a text summarizer. Summarize the following text concisely..." },
    { role: "user", content: userText }
  ],
  max_tokens: 500,
  temperature: 0.3
});
// Then parse the response, handle errors, validate output format...
```

Multiply that by nine different text operations — summarize, rewrite, repurpose for different platforms, generate headlines, extract keywords, analyze tone — and you've got weeks of prompt-engineering that you'll copy-paste into every new project.

After the fifth time, I asked: **why isn't `POST /summarize` just... a thing?**

## The problem nobody talks about

OpenAI's API is a canvas. You can build anything. But most developers don't need a canvas — they need a tool. They need "rewrite this for a Twitter audience" or "generate 5 email subject lines from these bullet points," not "design a system prompt with the right temperature and token limit for cross-platform content adaptation."

The gap isn't capability. It's **abstraction level**. We have raw LLM access. We don't have purpose-built text endpoints.

## What I built

[TextKit API](https://www.textkitapi.com) — 9 endpoints, each doing one text task:

| Endpoint | What it does |
|----------|-------------|
| `/repurpose` | Transform content across platforms (blog → tweet, email → LinkedIn) |
| `/summarize` | Extract key points with adjustable length |
| `/rewrite` | Adapt text for different audiences or reading levels |
| `/seo` | Generate meta descriptions and optimized titles |
| `/email` | Draft professional emails from bullet points |
| `/headlines` | Generate engagement-optimized subject lines |
| `/keywords` | Extract relevant phrases for SEO |
| `/tone` | Analyze emotional sentiment and tone |
| `/compare` | Evaluate differences between text versions |

```bash
# Summarize an article
curl -X POST https://www.textkitapi.com/api/v1/summarize \
  -H "Content-Type: application/json" \
  -H "x-api-key: your_key" \
  -d '{"text": "Your long article text here...", "length": "short"}'

# Generate headlines from content
curl -X POST https://www.textkitapi.com/api/v1/headlines \
  -H "Content-Type: application/json" \
  -H "x-api-key: your_key" \
  -d '{"text": "Product launch announcement details..."}'

# Repurpose a blog post for Twitter
curl -X POST https://www.textkitapi.com/api/v1/repurpose \
  -H "Content-Type: application/json" \
  -H "x-api-key: your_key" \
  -d '{"text": "Full blog post...", "platform": "twitter"}'
```

No prompt engineering. No model selection. No token math. Each endpoint has sensible defaults, validates input, handles retries, and returns structured JSON.

## Why not just use [competitor]?

I looked at what exists:

- **Google Cloud NLP** — enterprise pricing, requires GCP setup, overkill for indie projects
- **NLP Cloud** — fine-tuning focus, targets ML teams, up to $499/mo
- **SMMRY** — summarization only, doesn't cover the other 8 operations
- **Raw OpenAI** — maximum flexibility, maximum boilerplate

Nothing covers the "I need 9 common text operations behind clean REST endpoints" use case at indie-developer prices. The closest competitor on RapidAPI (WebKnox) covers some of this but with less transparency on pricing and fewer content-creation endpoints.

## The stack (for the curious)

Node.js + Express, GPT-4o under the hood, SQLite for usage tracking, Swagger docs at `/docs`. Hosted on Railway. Available on the site and through RapidAPI.

There's a **free tier** — 10 requests/day, all 9 endpoints, no credit card required. Paid plans start at $9/mo for higher limits. There's also a live demo on the landing page where you can test endpoints without signing up.

## What I'd love feedback on

- Which of these 9 endpoints would you actually use in your projects?
- Is the current pricing model right (daily limits), or would monthly quotas make more sense?
- Any text operations I'm missing that you keep rebuilding?

**Try it:** [textkitapi.com](https://www.textkitapi.com) — you can test endpoints live from the homepage demo before creating an account.

---

*Solo dev building in public. This is post 1 in the "Building TextKit API" series — next up: why simple REST endpoints are accidentally perfect for AI agents.*
