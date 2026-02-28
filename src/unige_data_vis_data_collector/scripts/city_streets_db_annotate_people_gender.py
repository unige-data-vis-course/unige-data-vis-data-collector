from __future__ import annotations

import argparse
import logging
import sqlite3
from pathlib import Path
from typing import Iterable, List, Protocol

from dotenv import load_dotenv

from unige_data_vis_data_collector.scripts import setup_logging

try:
    from tqdm import tqdm  # type: ignore
except Exception:  # pragma: no cover
    tqdm = None  # fallback defined below

from unige_data_vis_data_collector.city_streets.people_gender_inference_service import (
    StreetPeopleGenderInferenceItem,
    PeopleGenderInferenceService,
)

setup_logging()


class _InferenceService(Protocol):
    def infer(self, street_names: Iterable[str]) -> List[StreetPeopleGenderInferenceItem]:
        ...


def _connect(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(db_path))
    con.execute("PRAGMA foreign_keys = ON;")
    return con


def _fetch_all_street_names(con: sqlite3.Connection) -> list[str]:
    cur = con.execute("SELECT name FROM streets WHERE is_people_name IS NULL")
    return [r[0] for r in cur.fetchall()]


def _chunk(seq: list[str], size: int) -> Iterable[list[str]]:
    for i in range(0, len(seq), size):
        yield seq[i: i + size]


def _update_batch(
        con: sqlite3.Connection, items: List[StreetPeopleGenderInferenceItem]
) -> None:
    data = []
    for it in items:
        is_people_int = 1 if it.is_people else 0
        if it.is_people and it.gender is not None:
            g = it.gender
            gender_value = getattr(g, "value", g)
        else:
            gender_value = None
        data.append((is_people_int, gender_value, it.street_name))
    con.executemany(
        "UPDATE streets SET is_people_name=?, gender_name=? WHERE name=?",
        data,
    )


def annotate_db(
        db_path: Path,
        batch_size: int,
        service: _InferenceService | None = None,
) -> int:
    """Annotate all streets with inferred people/gender.

    Returns number of streets processed.
    """
    if service is None:
        service = PeopleGenderInferenceService.from_azure_env()

    with _connect(db_path) as con:
        names = _fetch_all_street_names(con)
        total = len(names)
        if total == 0:
            logging.info("No streets found in database %s", db_path)
            return 0

        progress = tqdm(total=total, desc="Annotating streets")
        with progress as pbar:
            for group in _chunk(names, batch_size):
                items = service.infer(group)
                with con:  # batch transaction
                    _update_batch(con, items)
                pbar.update(len(group))
        return total


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="city_streets_db_annotate_people_gender")
    p.add_argument(
        "--db",
        type=Path,
        default=Path("databases") / "city_streets.db",
        help="Path to SQLite database file (default: databases/city_streets.db)",
    )
    p.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for inference calls (default: 100)",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        annotate_db(args.db, args.batch_size)
        return 0
    except Exception as ex:
        logging.exception(ex)
        return 1


if __name__ == "__main__":
    load_dotenv()
    raise SystemExit(main())
