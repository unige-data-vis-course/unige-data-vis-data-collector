import csv
import tempfile
import unittest
from pathlib import Path

from unige_data_vis_data_collector.gapminder import GapminderImporter
from unige_data_vis_data_collector.gapminder.models import GapminderConcept


def _write_concepts_csv(path: Path, rows: list[dict[str, str]]):
    headers = [
        "concept",
        "concept_type",
        "source_url",
        "version",
        "updated",
        "name_short",
        "name",
        "name_catalog",
        "description",
        "unit",
        "tags",
        "color",
        "format",
        "scales",
        "domain",
        "indicator_url",
        "drill_up",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


class TestLoadConcepts(unittest.TestCase):
    def _sample_rows(self):
        return [
            {
                "concept": "gini",
                "concept_type": "measure",
                "source_url": "",
                "version": "v4",
                "updated": "October 7 2021",
                "name_short": "Gini",
                "name": "Gini coefficient",
                "name_catalog": "",
                "description": "Gini shows income inequality.",
                "unit": "",
                "tags": "",
                "color": "",
                "format": "",
                "scales": "",
                "domain": "",
                "indicator_url": "",
                "drill_up": "",
            },
            {
                "concept": "journakilled",
                "concept_type": "measure",
                "source_url": "",
                "version": "v5",
                "updated": "October 8 2024",
                "name_short": "Journalists killed",
                "name": "Number of journalists killed",
                "name_catalog": "",
                "description": "Number of journalists killed in given year.",
                "unit": "",
                "tags": "",
                "color": "",
                "format": "",
                "scales": "",
                "domain": "",
                "indicator_url": "",
                "drill_up": "",
            },
        ]

    def _assert_gini(self, first: GapminderConcept):
        self.assertIsInstance(first, GapminderConcept)
        self.assertEqual(first.id, "gini")
        self.assertEqual(first.type, "measure")
        self.assertEqual(first.updated_at, "October 7 2021")
        self.assertEqual(first.name, "Gini")
        self.assertEqual(first.description_short, "Gini coefficient")
        self.assertTrue(first.description.startswith("Gini shows income"))

    def test_load_concepts_primary_filename(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            _write_concepts_csv(d / "ddf-concepts.csv", self._sample_rows())
            gi = GapminderImporter(source_dir=d)
            concepts = gi.load_concepts()
            self.assertEqual(len(concepts), 2)
            self._assert_gini(concepts[0])

    def test_load_concepts_double_dash_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            _write_concepts_csv(d / "ddf--concepts.csv", self._sample_rows())
            gi = GapminderImporter(source_dir=d)
            concepts = gi.load_concepts()
            self.assertEqual(len(concepts), 2)
            self._assert_gini(concepts[0])


if __name__ == "__main__":
    unittest.main()
