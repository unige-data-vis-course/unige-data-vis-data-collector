from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from unige_data_vis_data_collector.scripts import city_streets_db_loader as loader


def _connect(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(path))
    con.execute("PRAGMA foreign_keys = ON;")
    return con


class CityStreetsDbLoaderTest(TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.workdir = Path(self.tmp.name)
        self.db_path = self.workdir / "city_streets.db"
        self.file1 = self.workdir / "city_streets_Testville.jsonl"

        ways = [
            {
                "type": "way",
                "id": 1,
                "geometry": [
                    {"lat": 46.0, "lon": 6.0},
                    {"lat": 46.1, "lon": 6.1},
                ],
                "tags": {"name": "Rue Alpha", "lanes": "2", "maxspeed": "50"},
            },
            {
                "type": "way",
                "id": 2,
                "geometry": [
                    {"lat": 47.0, "lon": 7.0},
                    {"lat": 47.1, "lon": 7.1},
                    {"lat": 47.2, "lon": 7.2},
                ],
                "tags": {"name": "Rue Alpha", "lanes": "1"},
            },
            {
                "type": "way",
                "id": 3,
                "geometry": [
                    {"lat": 48.0, "lon": 8.0},
                ],
                "tags": {},  # missing name -> should be skipped
            },
        ]
        with open(self.file1, "w", encoding="utf-8") as f:
            for w in ways:
                f.write(json.dumps(w) + "\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_loads_jsonl_into_sqlite_and_skips_duplicates(self):
        inserted = loader.load_files_into_db([self.file1], self.db_path)
        self.assertEqual(2, inserted)  # third skipped because name missing

        with _connect(self.db_path) as con:
            cnt_streets = con.execute("SELECT COUNT(*) FROM streets").fetchone()[0]
            cnt_segments = con.execute("SELECT COUNT(*) FROM segments").fetchone()[0]
            cnt_points = con.execute("SELECT COUNT(*) FROM points").fetchone()[0]

            self.assertEqual(1, cnt_streets)  # same street only once
            self.assertEqual(2, cnt_segments)
            # points = 2 + 3 for inserted segments only
            self.assertEqual(5, cnt_points)

            # verify values
            row = con.execute(
                "SELECT id, street_name, nb_lanes, max_speed FROM segments WHERE id=1"
            ).fetchone()
            self.assertEqual((1, "Rue Alpha", 2, 50), row)

        # Load again -> should skip all existing segments by id
        inserted2 = loader.load_files_into_db([self.file1], self.db_path)
        self.assertEqual(0, inserted2)

        with _connect(self.db_path) as con:
            cnt_segments2 = con.execute("SELECT COUNT(*) FROM segments").fetchone()[0]
            cnt_points2 = con.execute("SELECT COUNT(*) FROM points").fetchone()[0]
            self.assertEqual(2, cnt_segments2)
            self.assertEqual(5, cnt_points2)
