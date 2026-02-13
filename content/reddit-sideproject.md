I kept writing the same OpenAI wrapper code in every project. Summarize this text, rewrite that for a different audience, generate headlines from bullet points, repurpose a blog post into a tweet thread — each one needs a system prompt, token limits, error handling, response parsing. After the fifth time copy-pasting the same boilerplate, I productized it.

**TextKit API** — 9 text processing endpoints that just work:

- `/repurpose` — transform content across platforms (blog → tweet, email → LinkedIn)
- `/summarize` — extract key points with adjustable length
- `/rewrite` — adapt text for different audiences/reading levels
- `/seo` — generate meta descriptions and titles
- `/email` — draft professional emails from bullet points
- `/headlines` — generate engagement-optimized subject lines
- `/keywords` — extract relevant phrases for SEO
- `/tone` — analyze emotional sentiment and tone
- `/compare` — evaluate differences between text versions

The pitch is simple: instead of prompt-engineering each text feature from scratch, call a purpose-built endpoint. No model selection, no token math — just `POST /api/v1/summarize` with your text.

I looked at what exists — Google NLP is enterprise-priced and requires GCP setup, NLP Cloud targets ML teams at $499/mo, SMMRY only does summarization. The closest thing on RapidAPI (WebKnox) covers some text processing but with less transparency and no content-creation endpoints like repurpose/email/headlines.

**Stack:** Node.js, Express, GPT-4o under the hood, Swagger docs at `/docs`.

**Pricing:** Free tier (10 requests/day, no credit card). Paid plans from $9/mo for 100 requests/day. All 9 endpoints on every plan.

The site has a live demo where you can test endpoints without signing up: [textkitapi.com](https://www.textkitapi.com)

Two questions for this community:
1. Which of these 9 endpoints would you actually use in your projects?
2. Daily request limits vs monthly quotas — which makes more sense for a developer API?
