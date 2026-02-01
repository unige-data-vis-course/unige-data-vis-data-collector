from __future__ import annotations

import argparse
import sys
from pathlib import Path

from unige_data_vis_data_collector.gapminder import GapminderImporter


DEFAULT_SOURCE = Path("data/ddf--gapminder--fasttrack/")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="gapminder_build_local")
    p.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Path to local Gapminder dataset (default: %(default)s)",
    )
    p.add_argument(
        "--list-concepts",
        action="store_true",
        help="List concepts as 'id:description_short'",
    )
    return p.parse_args(argv)


def _get_importer(source_dir: Path) -> GapminderImporter:
    return GapminderImporter(source_dir=source_dir)


def _format_concept_line(c) -> str:
    return f"{c.id}:{c.description_short}"


def _cmd_list_concepts(imp: GapminderImporter) -> int:
    for c in imp.load_concepts():
        print(_format_concept_line(c))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    imp = _get_importer(args.source_dir)
    if args.list_concepts:
        return _cmd_list_concepts(imp)
    # If no action provided, show help
    parse_args(["-h"])  # will print help and exit via SystemExit
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit as e:
        # allow argparse to control exit codes and messages
        sys.exit(e.code)
