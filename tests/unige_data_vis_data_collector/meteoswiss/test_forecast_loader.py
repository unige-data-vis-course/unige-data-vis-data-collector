import json
from datetime import datetime, UTC
from unittest import TestCase
from unittest.mock import patch, MagicMock

import requests

from tests.unige_data_vis_data_collector.meteoswiss import RESOURCES_DIR
from unige_data_vis_data_collector.meteoswiss.forecast_loader import ForecastLoader, _parse_asset_name, _parse_timestamp, ForecastAsset  # noqa


class ForecastLoaderTest(TestCase):
    loader: ForecastLoader

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loader = ForecastLoader()
        self.given_asset = ForecastAsset(
            type="text/csv",
            href="https://data.geo.admin.ch/ch.meteoschweiz.ogd-local-forecasting/20260103-ch/vnut12.lssw.202601030000.rre150h0.csv",
            timestamp=datetime(2026, 1, 3, 22, 0, 0, tzinfo=UTC),
            feature_name="rre150h0"
        )

    def test__parse_timestamp(self):
        given = "202601032200"

        got = _parse_timestamp(given)

        self.assertEqual(datetime(2026, 1, 3, 22, 0, 0, tzinfo=UTC), got)

    def test__parse_asset_name(self):
        given = "vnut12.lssw.202601032200.tre200dx.csv"

        got_feature, got_ts = _parse_asset_name(given)

        self.assertEqual("tre200dx", got_feature)
        self.assertEqual(datetime(2026, 1, 3, 22, 0, 0, tzinfo=UTC), got_ts)

    @staticmethod
    def _mock_get_builder(mock_get):
        # returns the files from resources/mock_get, corresponding to the basename of the url
        # try to parse it as json or returns directly the content (e.g. .csv)
        def side_effect(url: str, *args, **kwargs):
            basename = url.split("/")[-1]
            path = RESOURCES_DIR / "mock_get" / basename
            if path.exists():
                response = MagicMock(spec=requests.Response)
                response.status_code = 200
                try:
                    with open(path) as f:
                        mock_data = "\n".join(f.readlines())

                    response.json.return_value = json.loads(mock_data)
                except json.JSONDecodeError:
                    response.content = mock_data.encode("utf-8")
                return response
            return MagicMock(status_code=404)

        mock_get.side_effect = side_effect

    @patch("requests.get")
    def test_load_stac_items(self, mock_get):
        self._mock_get_builder(mock_get)

        got = self.loader.load_stac_items()
        self.assertEqual(1728, len(got))

    @patch("requests.get")
    def test_filter_by_features(self, mock_get):
        self._mock_get_builder(mock_get)

        got = self.loader.load_stac_items().filter_by_features("rre150h0")
        self.assertEqual(54, len(got))

    @patch("requests.get")
    def test_load_forecast_elements(self, mock_get):

        self._mock_get_builder(mock_get)

        got = self.loader.load_forecast_elements(self.given_asset)
        self.assertEqual(999, len(got))

    @patch("requests.get")
    def test_load_forecast_elements_boundaries(self, mock_get):
        self._mock_get_builder(mock_get)

        els = self.loader.load_forecast_elements(self.given_asset)
        got_start = els.starts_at()
        got_end = els.ends_at()
        self.assertEqual(datetime(2026, 1, 3, 22, 0, tzinfo=UTC), got_start)
        self.assertEqual(datetime(2026, 1, 3, 22, 0, tzinfo=UTC), got_end)
