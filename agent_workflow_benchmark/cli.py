"""Package entry point for the unified campaign runner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runner import run_campaign


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a unified agent workflow manifest")
    parser.add_argument("manifest", type=Path, help="path to a YAML campaign manifest")
    parser.add_argument("--output", type=Path, default=None, help="result directory")
    parser.add_argument("--arm", action="append", dest="arms", help="run only this arm; repeatable")
    parser.add_argument(
        "--scenario", action="append", dest="scenarios", help="run only this scenario; repeatable"
    )
    parser.add_argument("--limit", type=int, help="run only the first N scenarios")
    parser.add_argument("--dry-run", action="store_true", help="validate and print the execution plan")
    args = parser.parse_args()
    result = run_campaign(
        args.manifest,
        args.output or Path("results") / args.manifest.stem,
        arm_filter=set(args.arms) if args.arms else None,
        scenario_filter=set(args.scenarios) if args.scenarios else None,
        scenario_limit=args.limit,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
