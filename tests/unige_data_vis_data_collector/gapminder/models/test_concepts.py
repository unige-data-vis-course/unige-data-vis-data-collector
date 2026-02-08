import unittest

from unige_data_vis_data_collector.gapminder.models import GapminderConcept, GapminderConcepts, CannotParseDateException, CannotFindConceptByIdException, \
    MultipleFindConceptByIdException

_mock_concept = {
    "id": "gini",
    "type": "measure",
    "updated_at": "October 7 2021",
    "name": "Gini",
    "description_short": "Gini coefficient",
    "description": "Gini shows income inequality.",
}


class TestGapminderConcept(unittest.TestCase):

    def test_predicted_since_year_October_7_2021(self):
        given = GapminderConcept(**_mock_concept)

        got = given.predicted_since_year

        self.assertEqual(got, 2021)

    def test_predicted_since_year_2023_June_6(self):
        given = GapminderConcept(**{**_mock_concept, "updated_at": "2023 June 6"})

        got = given.predicted_since_year

        self.assertEqual(got, 2023)

    def test_predicted_since_year_throws(self):
        given = GapminderConcept(**{**_mock_concept, "updated_at": "PAF"})

        with self.assertRaises(CannotParseDateException):
            given.predicted_since_year


class TestGapminderConcepts(unittest.TestCase):
    _mock_concepts: GapminderConcepts

    def setUp(self):
        self._mock_concepts = GapminderConcepts([
            GapminderConcept(**_mock_concept),
            GapminderConcept(**{**_mock_concept, "id": 'duo'}),
            GapminderConcept(**{**_mock_concept, "id": 'duo'}),

        ])

    def test_by_id(self):
        got = self._mock_concepts.by_id("gini")
        self.assertEqual(got.id, "gini")

    def test_by_id_cannot_find(self):
        with self.assertRaises(CannotFindConceptByIdException):
            self._mock_concepts.by_id("paf")

    def test_by_id_duplicate(self):
        with self.assertRaises(MultipleFindConceptByIdException):
            self._mock_concepts.by_id("duo")


if __name__ == "__main__":
    unittest.main()
