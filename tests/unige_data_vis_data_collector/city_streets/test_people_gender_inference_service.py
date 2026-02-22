import json
import unittest
from typing import Any

from unige_data_vis_data_collector.city_streets.people_gender_inference_service import (
    PeopleGenderInferenceService,
    StreetPeopleGenderInferenceItem,
    Gender,
)


class _Msg:
    def __init__(self, content: str):
        self.content = content


class _FakeLLM:
    def __init__(self, payload: Any):
        self._payload = payload

    def invoke(self, prompt: str) -> Any:  # noqa: ARG002
        return self._payload


class PeopleGenderInferenceServiceTest(unittest.TestCase):
    def test_infer_with_json_string(self):
        payload = json.dumps(
            [
                {"street_name": "Avenue Marie Curie", "is_people": True, "gender": "FEMALE"},
                {"street_name": "Rue du Lac", "is_people": False, "gender": None},
            ]
        )
        svc = PeopleGenderInferenceService(_FakeLLM(payload))
        items = svc.infer(["Avenue Marie Curie", "Rue du Lac"])

        self.assertIsInstance(items, list)
        self.assertEqual(2, len(items))
        self.assertIsInstance(items[0], StreetPeopleGenderInferenceItem)
        self.assertEqual("Avenue Marie Curie", items[0].street_name)
        self.assertTrue(items[0].is_people)
        self.assertEqual(Gender.FEMALE, items[0].gender)

        self.assertEqual("Rue du Lac", items[1].street_name)
        self.assertFalse(items[1].is_people)
        self.assertIsNone(items[1].gender)

    def test_infer_with_message_content(self):
        array = [
            {"street_name": "Boulevard Victor Hugo", "is_people": True, "gender": "MALE"},
        ]
        msg = _Msg(json.dumps(array))
        svc = PeopleGenderInferenceService(_FakeLLM(msg))
        items = svc.infer(["Boulevard Victor Hugo"])
        self.assertEqual(1, len(items))
        self.assertEqual(Gender.MALE, items[0].gender)

    def test_normalize_gender_variants(self):
        array = [
            {"street_name": "Allée Rosa Parks", "is_people": True, "gender": "feminine"},
            {"street_name": "Impasse Non-Binary Hero", "is_people": True, "gender": "non-binary"},
        ]
        svc = PeopleGenderInferenceService(_FakeLLM(json.dumps(array)))
        items = svc.infer(["Allée Rosa Parks", "Impasse Non-Binary Hero"])
        self.assertEqual(Gender.FEMALE, items[0].gender)
        self.assertEqual(Gender.NEUTRAL, items[1].gender)


if __name__ == "__main__":
    unittest.main()
