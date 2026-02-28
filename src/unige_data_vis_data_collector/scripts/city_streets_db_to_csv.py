from __future__ import annotations

import argparse
import csv
import logging
import sqlite3
from pathlib import Path
from typing import Iterable

from unige_data_vis_data_collector.scripts import setup_logging

setup_logging()


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="city_streets_db_to_csv")
    p.add_argument(
        "--db",
        type=Path,
        default=Path("databases") / "city_streets.db",
        help="Path to SQLite database file (default: databases/city_streets.db)",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("out") / "city_streets_csv",
        help="Output directory for CSV files (default: out/city_streets_csv)",
    )
    return p.parse_args(argv)


def _connect(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(db_path))
    con.execute("PRAGMA foreign_keys = ON;")
    return con


def _ensure_out_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _column_names(cursor: sqlite3.Cursor) -> list[str]:
    return [d[0] for d in cursor.description or []]


def _iter_rows(cursor: sqlite3.Cursor) -> Iterable[tuple]:
    while True:
        rows = cursor.fetchmany(1000)
        if not rows:
            break
        for r in rows:
            yield r


def _export_table(con: sqlite3.Connection, table: str, out_file: Path) -> int:
    cur = con.execute(f"SELECT * FROM {table}")
    headers = _column_names(cur)
    count = 0
    with open(out_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in _iter_rows(cur):
            writer.writerow(row)
            count += 1
    return count


def export_db_to_csv(db_path: Path, out_dir: Path) -> dict[str, int]:
    _ensure_out_dir(out_dir)
    with _connect(db_path) as con:
        results = {}
        for table in ("points", "segments", "streets"):
            out_file = out_dir / f"{table}.csv"
            logging.info("Exporting %s -> %s", table, out_file)
            results[table] = _export_table(con, table, out_file)
        return results


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        counts = export_db_to_csv(args.db, args.out)
        logging.info("Export completed: %s", counts)
        return 0
    except Exception as ex:
        logging.exception(ex)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
