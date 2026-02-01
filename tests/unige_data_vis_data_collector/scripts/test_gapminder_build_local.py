import csv
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


def _expected_lines(limit: int = 5) -> list[str]:
    path = _concepts_path()
    lines: list[str] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, r in enumerate(reader):
            if i >= limit:
                break
            cid = (r.get("concept") or "").strip()
            dshort = (r.get("name") or "").strip()
            lines.append(f"{cid}:{dshort}")
    return lines


class TestGapminderBuildLocal(unittest.TestCase):
    def test_list_concepts_outputs_expected_lines(self):
        expected = _expected_lines(limit=3)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = script.main(["--source-dir", str(DATA_DIR), "--list-concepts"])
        out = buf.getvalue().strip().splitlines()
        self.assertEqual(rc, 0)
        # Ensure we produced at least as many lines as expected sample
        self.assertGreaterEqual(len(out), len(expected))
        # Compare first N lines to expected
        self.assertEqual(out[: len(expected)], expected)


if __name__ == "__main__":
    unittest.main()
