import unittest
from pathlib import Path

import pandas as pd
import pytest

from unige_data_vis_data_collector.meteoswiss import (
    load_smn_stations,
    load_precip_stations,
    get_all_stations,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestStationsLoading(unittest.TestCase):
    def test_load_smn_no_encoding_error(self):
        df = load_smn_stations()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)

    def test_load_precip_no_encoding_error(self):
        df = load_precip_stations()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)
        print(df)


@pytest.mark.parametrize(
    "code, loader",
    [
        ("GVE", load_smn_stations),
        ("BEX", load_precip_stations),
    ],
)
def test_known_codes_present(code, loader):
    df = loader()
    assert code in set(df["station_abbr"].astype(str))


def test_combined_union_and_flags():
    stations = get_all_stations()
    by_abbr = {s.abbr: s for s in stations}

    assert "GVE" in by_abbr
    assert by_abbr["GVE"].has_observations_smn is True
    assert by_abbr["GVE"].has_observations_precip is False

    assert "BEX" in by_abbr
    assert by_abbr["BEX"].has_observations_precip is True
    assert by_abbr["BEX"].has_observations_smn is False
