from __future__ import annotations

import argparse
import glob
import json
import logging
import sqlite3
from pathlib import Path
from typing import Iterable

from unige_data_vis_data_collector.city_streets.way_segment import WaySegment
from unige_data_vis_data_collector.scripts.city_streets_db_init import (
    create_city_streets_db,
)

logging.basicConfig(level=logging.INFO)


def _connect(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(db_path))
    con.execute("PRAGMA foreign_keys = ON;")
    return con


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="city_streets_db_loader")
    p.add_argument(
        "files",
        nargs="*",
        type=Path,
        default=None,
        help="JSONL files to load (default: out/city_streets_*.jsonl)",
    )
    p.add_argument(
        "--db",
        type=Path,
        default=Path("databases") / "city_streets.db",
        help="Path to SQLite database file (default: databases/city_streets.db)",
    )
    return p.parse_args(argv)


def _default_files() -> list[Path]:
    return [Path(p) for p in glob.glob("out/city_streets_*.jsonl")]


def _iter_way_segments_from_file(path: Path) -> Iterable[WaySegment]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                logging.warning("Skipping invalid JSON line in %s", path)
                continue
            if obj.get("type") != "way":
                continue
            try:
                yield WaySegment.deserialize(obj)
            except Exception as ex:
                logging.warning("Skipping invalid way segment in %s: %s - %s", path, ex, line)


def _ensure_street(con: sqlite3.Connection, name: str) -> None:
    # We don't know people/gender here, insert a neutral default; uniqueness on name via PK
    con.execute(
        "INSERT OR IGNORE INTO streets(name, is_people_name, gender_name) VALUES (?,?,?)",
        (name, 0, None),
    )


def _segment_exists(con: sqlite3.Connection, seg_id: int) -> bool:
    cur = con.execute("SELECT 1 FROM segments WHERE id=?", (seg_id,))
    return cur.fetchone() is not None


def _insert_segment(con: sqlite3.Connection, ws: WaySegment, city: str) -> None:
    con.execute(
        "INSERT INTO segments(id, street_name, city, nb_lanes, max_speed) VALUES (?,?,?,?,?)",
        (ws.id, ws.name, city, ws.nb_lanes, ws.maxspeed),
    )


def _insert_points(con: sqlite3.Connection, ws: WaySegment) -> None:
    con.executemany(
        "INSERT INTO points(id_segment, lat, lon) VALUES (?,?,?)",
        [(ws.id, p.lat, p.lon) for p in ws.path.points],
    )


def _city_from_filename(path: Path) -> str:
    stem = path.stem  # e.g., city_streets_Genève
    prefix = "city_streets_"
    return stem[len(prefix):] if stem.startswith(prefix) else stem


def load_files_into_db(files: list[Path] | None, db_path: Path) -> int:
    files = files or _default_files()
    if not files:
        logging.info("No input files found. Nothing to do.")
        return 0

    # Ensure DB and schema exist
    create_city_streets_db(db_path)

    inserted = 0
    skipped = 0
    with _connect(db_path) as con:
        for file in files:
            logging.info("Loading file %s", file)
            city = _city_from_filename(Path(file))
            with con:  # transaction per file
                for ws in _iter_way_segments_from_file(file):
                    # must have a street name to satisfy schema
                    if not ws.name:
                        skipped += 1
                        continue
                    if _segment_exists(con, ws.id):
                        skipped += 1
                        continue
                    _ensure_street(con, ws.name)
                    _insert_segment(con, ws, city)
                    _insert_points(con, ws)
                    inserted += 1
    logging.info("Inserted %d segments, skipped %d", inserted, skipped)
    return inserted


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        load_files_into_db(args.files, args.db)
        return 0
    except Exception as ex:
        logging.exception(ex)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
