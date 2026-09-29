"""Output stage: write the day's content into a dated folder of
markdown/JSON files, ready to copy into Instagram and LinkedIn.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .research import Story


def _fmt_time(story: Story) -> str:
    return story.published.strftime("%Y-%m-%d %H:%M UTC") if story.published else "unknown time"


def write_research_digest(out_dir: Path, stories: list[Story]) -> Path:
    lines = ["# Research digest\n"]
    for i, s in enumerate(stories, 1):
        lines.append(f"## {i}. {s.title}")
        lines.append(f"- Source: {s.source} ({s.category}) - {_fmt_time(s)}")
        lines.append(f"- Link: {s.link}")
        if s.matched_keywords:
            lines.append(f"- Matched: {', '.join(s.matched_keywords)} (score {s.score:.1f})")
        if s.summary:
            lines.append(f"\n{s.summary}\n")
        lines.append("")
    path = out_dir / "1_research_digest.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_carousel(out_dir: Path, carousel: dict) -> tuple[Path, Path]:
    slides = carousel.get("slides", [])
    md = [f"# Instagram carousel: {carousel.get('topic', '')}\n"]
    for i, slide in enumerate(slides, 1):
        md.append(f"## Slide {i:02d}")
        md.append(f"**{slide.get('heading', '')}**\n")
        md.append(slide.get("body", ""))
        md.append("")
    md_path = out_dir / "2_carousel.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    json_path = out_dir / "2_carousel.json"
    json_path.write_text(json.dumps(carousel, indent=2, ensure_ascii=False), encoding="utf-8")
    return md_path, json_path


def write_linkedin(out_dir: Path, post: str) -> Path:
    path = out_dir / "3_linkedin_post.md"
    path.write_text(f"# LinkedIn post\n\n{post}\n", encoding="utf-8")
    return path


def write_caption(out_dir: Path, caption: dict) -> Path:
    tags = " ".join(f"#{t.lstrip('#')}" for t in caption.get("hashtags", []))
    text = (
        "# Instagram caption\n\n"
        f"{caption.get('hook', '')}\n\n"
        f"{caption.get('body', '')}\n\n"
        f"{caption.get('cta', '')}\n\n"
        f"{tags}\n"
    )
    path = out_dir / "4_caption.md"
    path.write_text(text, encoding="utf-8")
    return path


def write_day(config: dict, stories: list[Story], content: dict | None,
              date: datetime | None = None) -> Path:
    """Write everything for one run. Returns the output folder."""
    date = date or datetime.now()
    out_dir = Path(config.get("output_dir", "output")) / date.strftime("%Y-%m-%d")
    out_dir.mkdir(parents=True, exist_ok=True)

    written = [write_research_digest(out_dir, stories)]
    if content:
        written.extend(write_carousel(out_dir, content.get("carousel", {})))
        written.append(write_linkedin(out_dir, content.get("linkedin_post", "")))
        written.append(write_caption(out_dir, content.get("caption", {})))
        if content.get("why_these_stories"):
            (out_dir / "0_why_these_stories.md").write_text(
                f"# Why these stories\n\n{content['why_these_stories']}\n", encoding="utf-8"
            )
    else:
        (out_dir / "GENERATION_SKIPPED.md").write_text(
            "Content generation was skipped (no Gemini API key configured).\n"
            "Add your key to .env and re-run to get carousel, LinkedIn post and captions.\n",
            encoding="utf-8",
        )
    print(f"\nDone. Your day of content is in: {out_dir}/")
    for path in written:
        print(f"  - {path.name}")
    return out_dir
