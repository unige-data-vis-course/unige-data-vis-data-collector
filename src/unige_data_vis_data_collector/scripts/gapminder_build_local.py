from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from unige_data_vis_data_collector.gapminder import GapminderImporter
from unige_data_vis_data_collector.scripts import setup_logging

DEFAULT_SOURCE = Path("data/ddf--gapminder--fasttrack/")
setup_logging()


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
        help="take a list of measure ids to collated in a .csv file, in the --output directory",
    )

    p.add_argument(
        "--output",
        type=str,
        default="out",
        help="output path for the collated dataframe",
    )

    p.add_argument(
        "--countries",
        default=False,
        action="store_true",
        help="copy countries information in the --output directory"
    )

    return p.parse_args(argv)


def _get_importer(source_dir: Path) -> GapminderImporter:
    return GapminderImporter(source_dir=source_dir)


def _cmd_list_concepts(imp: GapminderImporter) -> int:
    for c in imp.concepts:
        print(c)


def _cmd_collate_measures(imp: GapminderImporter, concept_ids: str, output: str) -> str:
    df = None
    for concept_id in concept_ids.split(','):
        df_c = imp.by_country_data(concept_id)
        prediction_since = imp.concepts.by_id(concept_id).predicted_since_year
        df_c[f"{concept_id}_is_forecast"] = df_c["time"].apply(lambda x: x >= prediction_since)
        df = df_c if df is None else df.merge(df_c, on=['country', 'time'], how='outer')

    Path(output).mkdir(exist_ok=True, parents=True)

    out_file = Path(output) / "gapminder-collated.csv"
    df.to_csv(out_file, index=False, sep=";", encoding="utf-8-sig")
    return str(out_file)


def _cmd_copy_countries(imp: GapminderImporter, output: str) -> str:
    Path(output).mkdir(exist_ok=True, parents=True)
    out_file = Path(output) / "gapminder-countries.csv"
    shutil.copyfile(imp.country_def_file(), out_file)
    return str(out_file)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    imp = _get_importer(args.source_dir)

    action = False
    if args.list_concepts:
        _cmd_list_concepts(imp)
        action = True

    if args.collate_measures:
        o = _cmd_collate_measures(imp, args.collate_measures, args.output)
        print(f"Measures copied into {o}")
        action = True

    if args.countries:
        _cmd_copy_countries(imp, args.output)
        print(f"Countries copied into {o}")
        action = True

    if not action:
        args.print_help()

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit as e:
        # allow argparse to control exit codes and messages
        sys.exit(e.code)
