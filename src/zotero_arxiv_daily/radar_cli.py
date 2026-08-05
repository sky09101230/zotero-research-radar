"""Command-line interface for local research radar runs."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
from typing import Sequence

from hydra import compose, initialize_config_dir
from hydra.core.global_hydra import GlobalHydra
from omegaconf.errors import InterpolationResolutionError

from .outputs import report_document, write_report
from .radar import RadarPipeline
from .state import StateStore


def load_config(config_dir: str, config_name: str, overrides: list[str]):
    GlobalHydra.instance().clear()
    with initialize_config_dir(config_dir=str(Path(config_dir).resolve()), version_base=None):
        return compose(config_name=config_name, overrides=overrides)


def add_config_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config-dir", default="config", help="Hydra configuration directory.")
    parser.add_argument("--config-name", default="default", help="Hydra configuration name.")
    parser.add_argument("--set", dest="overrides", action="append", default=[], help="Hydra override, e.g. executor.source=[arxiv].")


def recommend(args: argparse.Namespace) -> int:
    config = load_config(args.config_dir, args.config_name, args.overrides)
    pipeline = RadarPipeline(config, args.state)
    papers = pipeline.recommend(
        include_seen=args.include_seen,
        summarize=args.summarize,
        max_papers=args.top_k,
    )
    document = report_document(
        papers,
        {
            "mode": "recommend",
            "sources": list(config.executor.source),
            "include_seen": args.include_seen,
            "summarize": args.summarize,
        },
    )
    write_report(document, args.output, args.format)
    return 0


def doctor(args: argparse.Namespace) -> int:
    config = load_config(args.config_dir, args.config_name, args.overrides)
    errors = []
    try:
        if str(config.zotero.user_id) in {"", "???"}:
            errors.append("zotero.user_id is not configured")
        if str(config.zotero.api_key) in {"", "???"}:
            errors.append("zotero.api_key is not configured")
        if not config.executor.source:
            errors.append("executor.source must contain at least one source")
    except InterpolationResolutionError as error:
        match = re.search(r"Environment variable '([^']+)' not found", str(error))
        variable = match.group(1) if match else "required environment variable"
        errors.append(f"required environment variable is not set: {variable}")
    output_parent = Path(args.output).parent
    try:
        output_parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        errors.append(f"output directory is not writable: {error}")
    if errors:
        print("Radar configuration is not ready:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Radar configuration is ready for a recommendation run.")
    return 0


def feedback(args: argparse.Namespace) -> int:
    StateStore(args.state).record_feedback(args.paper_id, args.action)
    print(f"Recorded {args.action} feedback for {args.paper_id}.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="radar", description="Local-first Zotero research radar.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    recommend_parser = subparsers.add_parser("recommend", help="Generate a ranked paper report.")
    add_config_options(recommend_parser)
    recommend_parser.add_argument("--format", choices=("json", "markdown"), default="json")
    recommend_parser.add_argument("--output", default="reports/radar.json")
    recommend_parser.add_argument("--state", default=".radar/history.sqlite")
    recommend_parser.add_argument("--top-k", type=int, default=None)
    recommend_parser.add_argument("--include-seen", action="store_true")
    recommend_parser.add_argument("--summarize", action="store_true")
    recommend_parser.set_defaults(handler=recommend)

    doctor_parser = subparsers.add_parser("doctor", help="Validate local configuration without making network requests.")
    add_config_options(doctor_parser)
    doctor_parser.add_argument("--output", default="reports/radar.json")
    doctor_parser.set_defaults(handler=doctor)

    feedback_parser = subparsers.add_parser("feedback", help="Record feedback for a paper identifier.")
    feedback_parser.add_argument("action", choices=("accept", "reject", "later", "seen"))
    feedback_parser.add_argument("paper_id")
    feedback_parser.add_argument("--state", default=".radar/history.sqlite")
    feedback_parser.set_defaults(handler=feedback)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
