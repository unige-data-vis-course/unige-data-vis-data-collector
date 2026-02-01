import unittest
from pathlib import Path

from unige_data_vis_data_collector.gapminder import GapminderImporter


class TestGapminderImporter(unittest.TestCase):
    def test_construct_with_string_path(self):
        gi = GapminderImporter(source_dir="/tmp/gapminder-src")
        self.assertIsInstance(gi.source_dir, Path)
        self.assertEqual(gi.source_dir, Path("/tmp/gapminder-src"))

    def test_construct_with_path_object(self):
        p = Path("/var/data/gm")
        gi = GapminderImporter(source_dir=p)
        self.assertIs(gi.source_dir, p)


if __name__ == "__main__":
    unittest.main()
