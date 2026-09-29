"""Research stage: pull fresh cybersecurity + AI news from free RSS feeds,
score each story for relevance to your niche, and pick the top ones.

No API keys needed for this stage - RSS feeds are public and free.
"""

from __future__ import annotations

import calendar
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import feedparser

# Keywords that make a story more relevant to the niche, with weights.
# Edit freely - this is how the agent learns what "matters" to you.
KEYWORD_WEIGHTS = {
    "zero-day": 5,
    "breach": 4,
    "vulnerability": 4,
    "cve": 4,
    "ransomware": 4,
    "exploit": 4,
    "malware": 3,
    "phishing": 3,
    "hack": 3,
    "data leak": 3,
    "openai": 3,
    "gemini": 3,
    "llm": 3,
    "gpt": 3,
    "agent": 2,
    "open source": 2,
    "python": 2,
    "linux": 2,
    "privacy": 2,
    "ai": 1,
    "cybersecurity": 1,
    "security": 1,
}


@dataclass
class Story:
    title: str
    link: str
    summary: str
    source: str
    category: str
    published: datetime | None
    score: float = 0.0
    matched_keywords: list[str] = field(default_factory=list)


def _parse_time(entry: dict) -> datetime | None:
    """Extract a timezone-aware publish time from a feed entry."""
    struct = entry.get("published_parsed") or entry.get("updated_parsed")
    if not struct:
        return None
    return datetime.fromtimestamp(calendar.timegm(struct), tz=timezone.utc)


def score_story(story: Story) -> None:
    """Score a story by keyword hits plus a recency bonus."""
    text = f"{story.title} {story.summary}".lower()
    score = 0.0
    matched = []
    for keyword, weight in KEYWORD_WEIGHTS.items():
        if keyword in text:
            score += weight
            matched.append(keyword)
    # Newer stories win ties: up to +3 points, decaying over 48 hours.
    if story.published:
        age_hours = (datetime.now(timezone.utc) - story.published).total_seconds() / 3600
        score += max(0.0, 3.0 - age_hours / 16)
    story.score = score
    story.matched_keywords = matched


def fetch_feed(name: str, url: str, category: str, max_age_hours: int) -> list[Story]:
    """Fetch one RSS feed and return fresh stories from it."""
    parsed = feedparser.parse(url)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    stories = []
    for entry in parsed.entries:
        published = _parse_time(entry)
        if published and published < cutoff:
            continue  # too old
        summary = entry.get("summary", "") or ""
        # Strip rough HTML remnants and cap the summary length.
        summary = " ".join(summary.replace("<", " <").split())[:500]
        stories.append(
            Story(
                title=entry.get("title", "(untitled)").strip(),
                link=entry.get("link", ""),
                summary=summary,
                source=name,
                category=category,
                published=published,
            )
        )
    return stories


def collect_stories(config: dict, verbose: bool = True) -> list[Story]:
    """Fetch every configured feed, score all stories, return them sorted."""
    research_cfg = config["research"]
    max_age = int(research_cfg.get("max_age_hours", 48))
    all_stories: list[Story] = []
    for feed in research_cfg["feeds"]:
        try:
            stories = fetch_feed(feed["name"], feed["url"], feed["category"], max_age)
        except Exception as exc:  # a dead feed should never kill the run
            if verbose:
                print(f"  ! {feed['name']}: failed ({exc})")
            continue
        if verbose:
            print(f"  - {feed['name']}: {len(stories)} fresh stories")
        all_stories.extend(stories)
    for story in all_stories:
        score_story(story)
    all_stories.sort(key=lambda s: s.score, reverse=True)
    return all_stories


def _title_tokens(title: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", title.lower()) if len(t) > 2}


def _too_similar(a: set[str], b: set[str]) -> bool:
    """Jaccard similarity > 0.5 means two titles cover the same story."""
    if not a or not b:
        return False
    return len(a & b) / len(a | b) > 0.5


def pick_top(stories: list[Story], n: int, per_source_cap: int = 2) -> list[Story]:
    """Pick the top N stories.

    Caps per source so one feed can't dominate, and drops near-duplicate
    titles so the same breaking story doesn't take three slots.
    """
    picked: list[Story] = []
    picked_tokens: list[set[str]] = []
    per_source: dict[str, int] = {}
    for story in stories:
        if len(picked) >= n:
            break
        if per_source.get(story.source, 0) >= per_source_cap:
            continue
        tokens = _title_tokens(story.title)
        if any(_too_similar(tokens, t) for t in picked_tokens):
            continue
        per_source[story.source] = per_source.get(story.source, 0) + 1
        picked.append(story)
        picked_tokens.append(tokens)
    return picked
