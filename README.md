# GhostScribe

> Gateway source preview: an authenticated Cloudflare Worker for opt-in non-personal online chat, study and limited public-source research is included. See [gateway setup](GATEWAY-SETUP.md). Android source and a phone-tested APK are not part of this publication yet. The gateway stays locked until secrets and quota storage are configured. No private notes, reminders or profile are automatically attached. Online typed questions reach Google free-tier Gemini and may be used to improve products. Do not type private information. No billing or paid fallback is configured.


Your personal content engine: it researches today's top cybersecurity and AI news,
then writes a full day of social content for you - an Instagram carousel, a LinkedIn
post, and captions - all in one command.

One run = one day of content, saved as ready-to-post files.

Built with Python + Google Gemini (free tier). No paid services.

## What it does

1. **Research** - pulls fresh stories from free public RSS feeds (The Hacker News,
   BleepingComputer, SecurityWeek, Google AI, OpenAI, MIT Tech Review), scores them
   against your niche, drops duplicates, and picks the top 5.
2. **Generate** - sends public RSS excerpts to Gemini and gets back:
   - Instagram carousel slide texts (8 slides, title + recap/CTA)
   - An informative LinkedIn post with a hook and question CTA
   - A caption: hook + body + CTA + 5 hashtags
   The model is instructed to use only facts from the fetched stories - no invented claims.
3. **Output** - writes everything into `output/YYYY-MM-DD/` as markdown + JSON,
   ready to copy into Instagram and LinkedIn.

## Setup

You need **Python 3.10+** and a **free Gemini API key**.

```bash
# 1. Clone the repo and enter it
git clone https://github.com/MRNOWSHIRWAN/ghostscribe.git
cd ghostscribe

# 2. Install dependencies
pip install -r requirements.txt

# 3. Get a free Gemini key at https://aistudio.google.com -> "Get API key"
#    Then copy .env.example to .env and paste your key in it
cp .env.example .env
```

## Usage

```bash
# Full run: research + generate + write the day's content
python -m content_agent run

# Research only (no API key needed) - see today's top stories
python -m content_agent research
```

After a run, open the dated folder in `output/`:

| File | What it is |
|------|-----------|
| `1_research_digest.md` | The top 5 stories, with sources and links |
| `2_carousel.md` / `.json` | Instagram carousel slide texts |
| `3_linkedin_post.md` | LinkedIn post, ready to paste |
| `4_caption.md` | Caption: hook, body, CTA, hashtags |

## Make it yours

Everything is tuned in **`config.yaml`** - no code changes needed:

- `profile.niche` / `profile.voice` - your topics and writing style
- `research.feeds` - add or remove RSS sources
- `research.top_stories` - how many stories per run
- `content.carousel_slides`, `content.hashtags` - content shape
- `content_agent/research.py` -> `KEYWORD_WEIGHTS` - teach the scorer what matters to you

## Run it every day automatically (optional)

Linux/macOS cron example, runs daily at 7:30 AM:

```cron
30 7 * * * cd /path/to/ghostscribe && /usr/bin/python3 -m content_agent run
```

## Project structure

```
ghostscribe/
├── config.yaml            # all settings: niche, feeds, style
├── .env.example           # where your Gemini key goes
├── requirements.txt
├── content_agent/
│   ├── cli.py             # command line entry point
│   ├── config.py          # config + .env loading
│   ├── research.py        # RSS fetching, scoring, dedup
│   ├── generator.py       # Gemini prompts + parsing
│   └── writer.py          # writes the dated output files
└── output/                # generated content lands here (gitignored)
```

## Notes

- Free-tier model availability and rate limits can change. Check the provider before relying on daily runs.
- Your API key stays local in `.env` (gitignored). Never commit it.
- Always read the output before posting. The agent drafts, you approve. RSS excerpts are discovery material, not independently verified articles.

## License

MIT - see [LICENSE](LICENSE).
