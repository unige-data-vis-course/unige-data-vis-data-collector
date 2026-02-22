from __future__ import annotations

import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from unige_data_vis_data_collector.scripts import city_streets_db_init as script


def _connect(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(path))
    con.execute("PRAGMA foreign_keys = ON;")
    return con


class CityStreetsDbInitTest(TestCase):
    def setUp(self):
        self.tmpdir = TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "city_streets.sqlite"

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_create_db_and_tables(self):
        created = script.create_city_streets_db(self.db_path)
        self.assertTrue(created.exists())

        with _connect(created) as con:
            # verify tables exist
            tables = {
                row[0]
                for row in con.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            self.assertTrue({"streets", "segments", "points"}.issubset(tables))

            # verify streets columns
            streets_cols = {
                row[1]: (row[2], row[3])  # type, notnull
                for row in con.execute("PRAGMA table_info('streets')").fetchall()
            }
            self.assertEqual(("TEXT", 0), streets_cols["gender_name"])  # nullable
            self.assertEqual(("TEXT", 1), streets_cols["name"])  # PK is notnull
            self.assertEqual(("BOOL", 0), streets_cols["is_people_name"])  # notnull

            # verify foreign keys
            fk_segments = con.execute("PRAGMA foreign_key_list('segments')").fetchall()
            # columns: (id, seq, table, from, to, on_update, on_delete, match)
            self.assertTrue(any(r[2] == "streets" and r[3] == "street_name" and r[4] == "name" for r in fk_segments))

            fk_points = con.execute("PRAGMA foreign_key_list('points')").fetchall()
            self.assertTrue(any(r[2] == "segments" and r[3] == "id_segment" and r[4] == "id" for r in fk_points))

            # verify segments columns include city NOT NULL
            segments_cols = {
                row[1]: (row[2], row[3])  # type, notnull
                for row in con.execute("PRAGMA table_info('segments')").fetchall()
            }
            self.assertEqual(("TEXT", 1), segments_cols["city"])  # notnull

    def test_gender_check_constraint(self):
        script.create_city_streets_db(self.db_path)
        with _connect(self.db_path) as con:
            # valid inserts
            con.execute(
                "INSERT INTO streets(name, is_people_name, gender_name) VALUES (?,?,?)",
                ("Rue Alpha", True, "MALE"),
            )
            con.execute(
                "INSERT INTO streets(name, is_people_name, gender_name) VALUES (?,?,?)",
                ("Rue Beta", True, None),
            )

            # invalid gender must fail
            with self.assertRaises(sqlite3.IntegrityError):
                con.execute(
                    "INSERT INTO streets(name, is_people_name, gender_name) VALUES (?,?,?)",
                    ("Rue Gamma", True, "paf"),
                )

    def test_foreign_keys_and_cascade(self):
        script.create_city_streets_db(self.db_path)
        with _connect(self.db_path) as con:
            con.execute(
                "INSERT INTO streets(name, is_people_name, gender_name) VALUES (?,?,?)",
                ("Rue Delta", None, None),
            )
            con.execute(
                "INSERT INTO segments(id, street_name, city, nb_lanes, max_speed) VALUES (?,?,?,?,?)",
                (101, "Rue Delta", "TestCity", None, 50),
            )
            con.execute(
                "INSERT INTO points(id_segment, lat, lon) VALUES (?,?,?)",
                (101, 46.0, 6.0),
            )

            # Deleting segment should cascade delete points
            con.execute("DELETE FROM segments WHERE id = 101")
            cnt = con.execute("SELECT COUNT(*) FROM points WHERE id_segment=101").fetchone()[0]
            self.assertEqual(0, cnt)
