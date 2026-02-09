import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from unige_data_vis_data_collector.scripts import gapminder_build_local as script

DATA_DIR = Path("data/ddf--gapminder--fasttrack/")
CONCEPTS_FILE_CANDIDATES = [
    DATA_DIR / "ddf-concepts.csv",
    DATA_DIR / "ddf--concepts.csv",
]


def _concepts_path() -> Path:
    for p in CONCEPTS_FILE_CANDIDATES:
        if p.exists():
            return p
    raise FileNotFoundError("No concepts CSV found in data directory for tests")


class TestGapminderBuildLocal(unittest.TestCase):
    def test_list_concepts_outputs_expected_lines(self):
        expected = [
            'gini ([forecast>=2021]): Gini',
            'journakilled ([forecast>=2024]): Journalists killed',
            'journaprison ([forecast>=2024]): Journalists imprisoned'
        ]
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = script.main(["--source-dir", str(DATA_DIR), "--list-concepts"])
        out = buf.getvalue().strip().splitlines()
        self.assertEqual(0, rc)
        # Ensure we produced at least as many lines as expected sample
        self.assertGreaterEqual(len(out), len(expected))
        # Compare first N lines to expected
        self.assertEqual(out[: len(expected)], expected)


if __name__ == "__main__":
    unittest.main()
