import unittest
from pathlib import Path

import pandas as pd
import pytest

from unige_data_vis_data_collector.meteoswiss import (
    load_smn_stations,
    load_precip_stations,
    get_all_stations,
)

# Use local test resources instead of downloading from the web
RESOURCES_DIR = Path(__file__).resolve().parent / "resources"
SMN_CSV = RESOURCES_DIR / "ogd-smn_meta_stations.csv"
PRECIP_CSV = RESOURCES_DIR / "ogd-smn-precip_meta_stations.csv"


class TestStationsLoading(unittest.TestCase):
    def test_load_smn_no_encoding_error(self):
        df = load_smn_stations(SMN_CSV)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(158, len(df))

    def test_load_precip_no_encoding_error(self):
        df = load_precip_stations(PRECIP_CSV)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(141, len(df))


@pytest.mark.parametrize(
    "code, loader, path",
    [
        ("GVE", load_smn_stations, SMN_CSV),
        ("BEX", load_precip_stations, PRECIP_CSV),
    ],
)
def test_known_codes_present(code, loader, path):
    df = loader(path)
    assert code in set(df["station_abbr"].astype(str))


def test_combined_union_and_flags():
    stations = get_all_stations(SMN_CSV, PRECIP_CSV)
    by_abbr = {s.abbr: s for s in stations}

    assert "GVE" in by_abbr
    assert by_abbr["GVE"].has_observations_smn is True
    assert by_abbr["GVE"].has_observations_precip is False

    assert "BEX" in by_abbr
    assert by_abbr["BEX"].has_observations_precip is True
    assert by_abbr["BEX"].has_observations_smn is False
