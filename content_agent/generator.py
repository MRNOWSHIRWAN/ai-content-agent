"""Generation stage: turn the day's top stories into ready-to-post content
using Google's Gemini API (free tier - get a key at aistudio.google.com).

Produces, in one run:
  1. Instagram carousel slide texts
  2. A LinkedIn post
  3. A caption (hook + CTA + hashtags)
"""

from __future__ import annotations

import json
import re

from .config import get_gemini_key
from .research import Story


class MissingApiKey(RuntimeError):
    pass


def _stories_block(stories: list[Story]) -> str:
    """Render the research digest as prompt context for the model."""
    lines = []
    for i, s in enumerate(stories, 1):
        lines.append(
            f"{i}. [{s.source}] {s.title}\n   {s.summary}\n   Link: {s.link}"
        )
    return "\n".join(lines)


def _extract_json(text: str) -> dict:
    """Pull a JSON object out of a model response, tolerating code fences."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Model response did not contain JSON")
    return json.loads(text[start : end + 1])


def build_prompt(stories: list[Story], config: dict) -> str:
    profile = config["profile"]
    content = config["content"]
    slides = int(content.get("carousel_slides", 8))
    hashtags = int(content.get("hashtags", 5))
    niche = ", ".join(profile.get("niche", []))
    return f"""You are the content engine behind a tech creator's page ({profile.get('name', 'creator')}).
Niche: {niche}.
Voice: {profile.get('voice', 'direct and educational')}

Here are today's top verified stories from real news feeds:

{_stories_block(stories)}

Create one full day of content from these stories. Rules:
- Only use facts from the stories above. Never invent numbers, names or claims.
- Pick the single strongest story for the Instagram carousel.
- Write in {content.get('language', 'English')}.

Return ONLY a JSON object with this exact shape:
{{
  "carousel": {{
    "topic": "short topic title",
    "slides": [
      {{"heading": "slide heading", "body": "2-4 short lines of slide text"}}
    ]
  }},
  "linkedin_post": "a full informative LinkedIn post (150-250 words) about one story, with a strong first-line hook and a question CTA at the end",
  "caption": {{
    "hook": "one short hook line",
    "body": "2-3 lines expanding on the hook",
    "cta": "one call to action (save/comment/share)",
    "hashtags": ["tag1", "tag2"]
  }},
  "why_these_stories": "2-3 sentences on why these stories matter to the niche"
}}

Constraints:
- carousel.slides must have exactly {slides} items: slide 1 is a bold title slide, the last slide is a recap + follow CTA.
- caption.hashtags must have exactly {hashtags} items, without the '#' symbol.
- Keep slide text short enough to read on a phone."""


def generate_content(stories: list[Story], config: dict) -> dict:
    """Call Gemini and return the parsed content dict.

    Raises MissingApiKey with setup instructions when no key is configured.
    """
    key = get_gemini_key()
    if not key:
        raise MissingApiKey(
            "No Gemini API key found.\n"
            "  1. Get a free key at https://aistudio.google.com\n"
            "  2. Copy .env.example to .env and paste it there\n"
            "     (or: export GEMINI_API_KEY=your-key)"
        )
    try:
        import google.generativeai as genai
    except ImportError as exc:
        raise RuntimeError(
            "google-generativeai is not installed. Run: pip install -r requirements.txt"
        ) from exc

    genai.configure(api_key=key)
    model = genai.GenerativeModel(
        config.get("gemini_model", "gemini-2.0-flash"),
        generation_config={"temperature": 0.7, "response_mime_type": "application/json"},
    )
    response = model.generate_content(build_prompt(stories, config))
    return _extract_json(response.text)
