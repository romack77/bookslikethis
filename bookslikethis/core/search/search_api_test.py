from unittest import mock

from core import factories
from core import test
from core.search import search_api
from core.search import work_similarity


class GetSimilarBooksTest(test.TestCase):

    def test_happy(self):
        work = factories.WorkFactory.create()
        with mock.patch.object(
                work_similarity, 'find_similar_works') as find_similar_mock:
            search_api.get_similar_books([work.id])
            find_similar_mock.assert_called_with(
                [work.id],
                limit=search_api.MAX_SEARCH_RESULTS,
                tag_names=tuple(search_api.TROPE_TAG_WEIGHTS.keys()),
                tag_weights=search_api.TROPE_TAG_WEIGHTS)


class GetAutocompleteSuggestionsTest(test.TestCase):

    def setUp(self):
        self.work = factories.WorkFactory.create(name='Taken')
        self.work_two = factories.WorkFactory.create(name='Taken Too')
        self.work_three = factories.WorkFactory.create(
            name='Taken Three Times: Shame On Me')
        self.work_four = factories.WorkFactory.create(
            name='zzz')

    def test_happy(self):
        self.assertEqual(
            search_api.get_autocomplete_suggestions(self.work.name),
            [{'name': self.work.name},
             {'name': self.work_two.name},
             {'name': self.work_three.name},
             ])

    def test_no_matches(self):
        self.assertEqual(search_api.get_autocomplete_suggestions('yyy'), [])

    def test_empty_query(self):
        self.assertEqual(search_api.get_autocomplete_suggestions(''), [])

    def test_results_limit(self):
        self.assertEqual(
            len(search_api.get_autocomplete_suggestions(
                self.work.name, limit=10)),
            3)
        self.assertEqual(
            search_api.get_autocomplete_suggestions(
                self.work.name, limit=1),
            [{'name': self.work.name}])

    def test_similarity_threshold(self):
        self.assertEqual(
            len(search_api.get_autocomplete_suggestions(
                self.work.name, min_similarity=0.0)),
            4)
        self.assertEqual(
            len(search_api.get_autocomplete_suggestions(
                self.work.name, min_similarity=0.3)),
            2)
        self.assertEqual(
            len(search_api.get_autocomplete_suggestions(
                self.work.name, min_similarity=1.0)),
            1)
        self.assertEqual(
            len(search_api.get_autocomplete_suggestions(
                self.work.name + 'z', min_similarity=1.0)),
            0)


class GetWorkIdForSearchQueryTest(test.TestCase):

    def test_happy(self):
        work = factories.WorkFactory.create(name='Book')
        work_two = factories.WorkFactory.create(name='Different Book')
        self.assertEqual(
            search_api.get_work_id_for_search_query(work.name),
            work.id)
        self.assertEqual(
            search_api.get_work_id_for_search_query(work_two.name),
            work_two.id)
        self.assertEqual(
            search_api.get_work_id_for_search_query(work.name + 'z'),
            work.id)
