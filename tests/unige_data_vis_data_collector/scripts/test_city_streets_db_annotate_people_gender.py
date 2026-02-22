import sqlite3
import tempfile
import unittest
from pathlib import Path

from unige_data_vis_data_collector.city_streets.people_gender_inference_service import (
    Gender,
    StreetPeopleGenderInferenceItem,
)
from unige_data_vis_data_collector.scripts.city_streets_db_annotate_people_gender import (
    annotate_db,
)
from unige_data_vis_data_collector.scripts.city_streets_db_init import (
    create_city_streets_db,
)


class FakeService:
    def __init__(self, mapping: dict[str, tuple[bool, Gender | None]]):
        self._map = mapping
        self.calls: list[list[str]] = []

    def infer(self, street_names):
        names = list(street_names)
        self.calls.append(names)
        items: list[StreetPeopleGenderInferenceItem] = []
        for n in names:
            is_people, gender = self._map.get(n, (False, None))
            items.append(
                StreetPeopleGenderInferenceItem(street_name=n, is_people=is_people, gender=gender)
            )
        return items


def _connect(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(db_path))
    con.execute("PRAGMA foreign_keys = ON;")
    return con


class TestAnnotatePeopleGender(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "city_streets.db"
        create_city_streets_db(self.db_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def _insert_streets(self, names: list[str]):
        with _connect(self.db_path) as con:
            con.executemany(
                "INSERT INTO streets(name, is_people_name, gender_name) VALUES (?,?,?)",
                [(n, None, None) for n in names],
            )

    def _fetch_all(self) -> dict[str, tuple[int, str | None]]:
        with _connect(self.db_path) as con:
            cur = con.execute("SELECT name, is_people_name, gender_name FROM streets")
            return {row[0]: (row[1], row[2]) for row in cur.fetchall()}

    def test_annotate_updates_fields(self):
        names = [
            "Avenue Marie Curie",
            "Rue du Lac",
            "Place Victor Hugo",
            "Allée des Lilas",
        ]
        self._insert_streets(names)
        mapping = {
            "Avenue Marie Curie": (True, Gender.FEMALE),
            "Rue du Lac": (False, None),
            "Place Victor Hugo": (True, Gender.MALE),
            "Allée des Lilas": (False, None),
        }
        service = FakeService(mapping)

        processed = annotate_db(self.db_path, batch_size=2, service=service)

        self.assertEqual(processed, len(names))
        rows = self._fetch_all()
        self.assertEqual(rows["Avenue Marie Curie"], (True, "FEMALE"))
        self.assertEqual(rows["Rue du Lac"], (False, None))
        self.assertEqual(rows["Place Victor Hugo"], (True, "MALE"))
        self.assertEqual(rows["Allée des Lilas"], (False, None))

    def test_batches_are_respected(self):
        names = [f"Street {i}" for i in range(5)]
        self._insert_streets(names)
        mapping = {n: (False, None) for n in names}
        service = FakeService(mapping)

        annotate_db(self.db_path, batch_size=2, service=service)

        # Expect ceil(5/2) = 3 calls
        self.assertEqual(len(service.calls), 3)
        # Each call should be size 2,2,1
        sizes = list(map(len, service.calls))
        self.assertEqual(sizes, [2, 2, 1])
