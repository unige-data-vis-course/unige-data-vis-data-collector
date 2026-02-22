from __future__ import annotations

import logging
import sqlite3
from pathlib import Path


def _ensure_parent_dir(path: Path) -> None:
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def _connect(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(db_path))
    con.execute("PRAGMA foreign_keys = ON;")
    return con


def _create_tables(con: sqlite3.Connection) -> None:
    # streets table
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS streets (
            name TEXT NOT NULL PRIMARY KEY,
            is_people_name BOOL NULL CHECK ((is_people_name IN (TRUE, FALSE)) OR (is_people_name IS NULL)),
            gender_name TEXT NULL CHECK (
                (gender_name IN ('MALE','FEMALE','NEUTRAL')) OR (gender_name IS NULL)
            )
        );
        """
    )

    # segments table
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS segments (
            id INTEGER PRIMARY KEY,
            street_name TEXT NOT NULL,
            city TEXT NOT NULL,
            nb_lanes INTEGER NULL,
            max_speed INTEGER NULL,
            CONSTRAINT fk_segments_street
                FOREIGN KEY (street_name)
                REFERENCES streets(name)
                ON DELETE RESTRICT
                ON UPDATE CASCADE
        );
        """
    )

    # points table
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_segment INTEGER NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            CONSTRAINT fk_points_segment
                FOREIGN KEY (id_segment)
                REFERENCES segments(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );
        """
    )


def create_city_streets_db(db_path: str | Path) -> Path:
    """Create the city streets SQLite database with required schema.

    Returns the path to the created database file.
    """
    logging.info(f"Creating SQLite database in {db_path}")
    p = Path(db_path)
    _ensure_parent_dir(p)
    with _connect(p) as con:
        _create_tables(con)
        con.commit()
        logging.info(f"SQLite database created successfully: {p}")
    return p
