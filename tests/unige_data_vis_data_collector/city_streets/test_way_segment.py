from unittest import TestCase

from tests.unige_data_vis_data_collector.city_streets.resources import mock_segments_json
from unige_data_vis_data_collector.city_streets.way_segment import WaySegment


def _ws(id: int = 0, geometry: list[dict] = None, extra_tags: dict[str, str] = None) -> WaySegment:
    if geometry is None:
        geometry = []
    if extra_tags is None:
        extra_tags = {}
    args = {
        "type": "way",
        "id": id or 1,
        "geometry": geometry or [
            {"lat": 46.206506, "lon": 6.140445},
            {"lat": 46.206528, "lon": 6.140406},
        ],
        "tags": {
            "highway": "secondary",
            "lanes": "3",
            "lanes:backward": "2",
            "lanes:forward": "1",
            "name": "Place Isaac-Mercier",
            "surface": "asphalt",
            "trolley_wire": "yes",
            **extra_tags,
        },

    }
    return WaySegment.deserialize(args)


class WaySegmentTest(TestCase):
    def test_deserialize_way_segment(self):
        given = mock_segments_json(0)

        got = WaySegment.deserialize(given)
        self.assertIsInstance(got, WaySegment)

        self.assertEqual("Rue du 31-Décembre", got.name)
        self.assertEqual(3, got.nb_lanes)

    def test_maxspeed_none(self):
        given = _ws()

        self.assertEqual(None, given.maxspeed)

    def test_maxspeed_yes(self):
        given = _ws(extra_tags={"maxspeed": "42"})

        self.assertEqual(42, given.maxspeed)
