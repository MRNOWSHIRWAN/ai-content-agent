"""Command line interface.

  python -m content_agent run        # research + generate + write files
  python -m content_agent research   # research only, no API key needed
"""

from __future__ import annotations

import argparse

from .config import load_config
from .generator import MissingApiKey, generate_content
from .research import collect_stories, pick_top
from .writer import write_day


def _cmd_run(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    print("Researching today's stories...")
    stories = collect_stories(config)
    if not stories:
        print("No fresh stories found. Try increasing max_age_hours in config.yaml.")
        return
    top = pick_top(stories, int(config["research"].get("top_stories", 5)))
    print(f"\nTop {len(top)} stories:")
    for i, s in enumerate(top, 1):
        print(f"  {i}. [{s.source}] {s.title} (score {s.score:.1f})")

    content = None
    if args.research_only:
        print("\nResearch-only mode: skipping generation.")
    else:
        print("\nGenerating content with Gemini...")
        try:
            content = generate_content(top, config)
        except MissingApiKey as exc:
            print(f"\n{exc}")
        except Exception as exc:
            print(f"\nGeneration failed: {exc}\nWriting the research digest anyway.")
    write_day(config, top, content)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="content_agent",
        description="GhostScribe: research-to-posting, one run = one day of content.",
    )
    parser.add_argument("--config", help="Path to config.yaml (default: project config)")
    sub = parser.add_subparsers(dest="command")
    run = sub.add_parser("run", help="Research + generate + write a day of content")
    run.add_argument("--research-only", action="store_true",
                     help="Skip Gemini generation (no API key needed)")
    sub.add_parser("research", help="Research only, print the digest")
    args = parser.parse_args()

    if args.command == "research":
        args.research_only = True
        _cmd_run(args)
    elif args.command == "run":
        _cmd_run(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
