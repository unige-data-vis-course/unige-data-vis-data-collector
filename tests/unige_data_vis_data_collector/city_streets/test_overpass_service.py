from unittest import TestCase
from unittest.mock import patch, Mock

from unige_data_vis_data_collector.city_streets.way_segment import WaySegment


def _make_element(idx: int):
    return WaySegment.deserialize(
        {
            "type": "way",
            "id": idx,
            "nodes": [idx, idx + 1, idx + 2],
            "tags": {"highway": "residential", "name": f"Street {idx}"},
            "geometry": [
                {"lat": 46.2 + idx * 1e-6, "lon": 6.1 + idx * 1e-6},
                {"lat": 46.2 + (idx + 1) * 1e-6, "lon": 6.1 + (idx + 1) * 1e-6},
            ],
        }
    )


class OverpassCityStreetsServiceTest(TestCase):
    @patch("requests.post")
    def test_load_city_segments_paginates_and_concats(self, mock_post: Mock):
        # Arrange: first all ids, first batch 100, second batch 3, then 0
        post_batches = [
            {"elements": [{"id": i} for i in range(103)]},
            {"elements": [_make_element(i) for i in range(100)]},
            {"elements": [_make_element(i) for i in range(100, 103)]},
            {"elements": []}
        ]

        def side_effect(*args, **kwargs):
            resp = Mock()  # spec=Response is optional if you want stricter checks
            resp.raise_for_status = Mock()  # does nothing (no HTTP error)
            resp.json = Mock(side_effect=lambda: post_batches.pop(0))
            return resp

        mock_post.side_effect = side_effect

        from unige_data_vis_data_collector.city_streets.overpass_service import (
            OverpassCityStreetsService,
        )

        service = OverpassCityStreetsService()

        # Act
        got = list(service.load_city_segments(city_name="Geneva", batch_size=100))

        # Assert
        self.assertEqual(103, len(got))
        self.assertIsInstance(got[0], WaySegment)
        self.assertEqual({"highway": "residential", "name": "Street 0"}, got[0].tags)
        self.assertEqual(2, len(got[0].path))

    @patch("unige_data_vis_data_collector.city_streets.overpass_service.requests.post")
    def test_empty_city_returns_empty_list(self, mock_post: Mock):
        m = Mock()
        m.json.return_value = {"elements": []}
        m.raise_for_status.return_value = None
        mock_post.return_value = m

        from unige_data_vis_data_collector.city_streets.overpass_service import OverpassCityStreetsService

        service = OverpassCityStreetsService()
        got = list(service.load_city_segments(city_name="Nowhere", batch_size=100))
        self.assertEqual([], got)
