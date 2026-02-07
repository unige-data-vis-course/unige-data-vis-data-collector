import unittest

from unige_data_vis_data_collector.gapminder.models import GapminderConcept, CannotParseDateException


class TestConcepts(unittest.TestCase):
    _mock_concepts = {
        "id": "gini",
        "type": "measure",
        "updated_at": "October 7 2021",
        "name": "Gini",
        "description_short": "Gini coefficient",
        "description": "Gini shows income inequality.",
    }

    def test_predicted_since_year_October_7_2021(self):
        given = GapminderConcept(**self._mock_concepts)

        got = given.predicted_since_year

        self.assertEqual(got, 2021)

    def test_predicted_since_year_2023_June_6(self):
        given = GapminderConcept(**{**self._mock_concepts, "updated_at": "2023 June 6"})

        got = given.predicted_since_year

        self.assertEqual(got, 2023)

    def test_predicted_since_year_throws(self):
        given = GapminderConcept(**{**self._mock_concepts, "updated_at": "PAF"})

        with self.assertRaises(CannotParseDateException):
            given.predicted_since_year


if __name__ == "__main__":
    unittest.main()
