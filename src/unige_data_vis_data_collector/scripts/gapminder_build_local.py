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

    p.add_argument(
        "--collate-measures",
        type=str,
        help="a list of measure names to collate in a dataframe, separated by commas",
    )

    return p.parse_args(argv)


def _get_importer(source_dir: Path) -> GapminderImporter:
    return GapminderImporter(source_dir=source_dir)


def _cmd_list_concepts(imp: GapminderImporter) -> int:
    for c in imp.concepts:
        print(c)


def _cmd_collate_measures(imp: GapminderImporter, concept_ids: str):
    df = None
    for concept_id in concept_ids.split(','):
        df_c = imp.country_data(concept_id)
        df = df_c if df is None else df.merge(df_c, on=['country', 'time'])
    print(df)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    imp = _get_importer(args.source_dir)
    if args.list_concepts:
        _cmd_list_concepts(imp)

    if args.collate_measures:
        _cmd_collate_measures(imp, args.collate_measures)

    # If no action provided, show help
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit as e:
        # allow argparse to control exit codes and messages
        sys.exit(e.code)
