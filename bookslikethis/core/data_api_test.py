from unittest import mock

from core import data_api
from core import factories
from core import models
from core import test


class GetTropesTest(test.TestCase):

    def test_empty_db(self):
        self.assertEqual(data_api.get_tropes(), [])
        self.assertEqual(data_api.get_tropes(tag_names=('tag', )), [])

    def test_happy(self):
        trope = factories.TropeFactory.create()
        trope_two = factories.TropeFactory.create()
        self.assertEqual(
            set(data_api.get_tropes()), {trope, trope_two})
        trope_three = factories.TropeFactory.create()
        self.assertEqual(
            set(data_api.get_tropes()), {trope, trope_two, trope_three})

    def test_tag_filter(self):
        trope_tag = factories.TropeTagFactory.create(name='it')
        trope_tag_two = factories.TropeTagFactory.create(name='it 2')
        trope = factories.TropeFactory.create(tags=[trope_tag])
        trope_two = factories.TropeFactory.create(tags=[trope_tag_two])
        self.assertEqual(
            data_api.get_tropes(tag_names=('not it', )),
            [])
        self.assertEqual(
            data_api.get_tropes(tag_names=(trope_tag.name, )),
            [trope])
        self.assertEqual(
            set(data_api.get_tropes(
                tag_names=(trope_tag.name, trope_tag_two.name))),
            {trope, trope_two})


class GetTropesCacheTest(test.TestCase):

    MOCK_CACHE = False

    def setUp(self):
        data_api._get_tropes.cache_clear()

    def test_caching(self):
        data_api.get_tropes()
        cache_info = data_api._get_tropes.cache_info()
        self.assertEqual(cache_info.misses, 1)
        self.assertEqual(cache_info.hits, 0)

        data_api.get_tropes()
        cache_info = data_api._get_tropes.cache_info()
        self.assertEqual(cache_info.misses, 1)
        self.assertEqual(cache_info.hits, 1)


class GetTropeToOccurrenceCountTest(test.TestCase):

    def test_empty_db(self):
        trope_to_count = data_api.get_trope_to_occurrence_count()
        self.assertEqual(trope_to_count, {})
        trope_to_count = data_api.get_trope_to_occurrence_count(
            tag_names=('tag', ))
        self.assertEqual(trope_to_count, {})

    def test_happy(self):
        trope = factories.TropeFactory.create()
        trope_two = factories.TropeFactory.create()
        factories.TropeFactory.create()
        factories.WorkFactory.create(tropes=[trope, trope_two])
        factories.WorkFactory.create(tropes=[trope])
        factories.WorkFactory.create()

        trope_to_count = data_api.get_trope_to_occurrence_count()
        self.assertEqual(
            trope_to_count, {trope.id: 2, trope_two.id: 1})

        factories.WorkFactory.create(tropes=[trope])
        trope_to_count = data_api.get_trope_to_occurrence_count()
        self.assertEqual(
            trope_to_count, {trope.id: 3, trope_two.id: 1})

    def test_tag_filter(self):
        trope_tag = factories.TropeTagFactory.create(name='it')
        trope_tag_two = factories.TropeTagFactory.create(name='it 2')
        trope = factories.TropeFactory.create(tags=[trope_tag])
        trope_two = factories.TropeFactory.create(tags=[trope_tag_two])
        factories.WorkFactory.create(tropes=[trope, trope_two])

        trope_to_count = data_api.get_trope_to_occurrence_count(
            tag_names=('not it', ))
        self.assertEqual(trope_to_count, {})

        trope_to_count = data_api.get_trope_to_occurrence_count(
            tag_names=(trope_tag.name, ))
        self.assertEqual(trope_to_count, {trope.id: 1})

        trope_to_count = data_api.get_trope_to_occurrence_count(
            tag_names=(trope_tag.name, trope_tag_two.name))
        self.assertEqual(trope_to_count, {trope.id: 1, trope_two.id: 1})


class GetTropeToOccurrenceCountCacheTest(test.TestCase):

    MOCK_CACHE = False

    def setUp(self):
        data_api.get_trope_to_occurrence_count.cache_clear()

    def test_caching(self):
        data_api.get_trope_to_occurrence_count()
        cache_info = data_api.get_trope_to_occurrence_count.cache_info()
        self.assertEqual(cache_info.misses, 1)
        self.assertEqual(cache_info.hits, 0)

        data_api.get_trope_to_occurrence_count()
        cache_info = data_api.get_trope_to_occurrence_count.cache_info()
        self.assertEqual(cache_info.misses, 1)
        self.assertEqual(cache_info.hits, 1)


class GetGenreInfoTest(test.TestCase):

    def test_happy(self):
        genre_one = factories.GenreFactory.create()
        genre_two = factories.GenreFactory.create()
        sub_genre = factories.GenreFactory.create(parent_genre=genre_one)
        sub_sub_genre = factories.GenreFactory.create(parent_genre=sub_genre)
        self.assertEqual(
            data_api.get_genre_info(),
            {genre_one.id: (genre_one.name, 0),
             genre_two.id: (genre_two.name, 0),
             sub_genre.id: (sub_genre.name, 1),
             sub_sub_genre.id: (sub_sub_genre.name, 2)})

    def test_no_genres(self):
        self.assertEqual(
            data_api.get_genre_info(),
            {})


class GetGenreInfoCacheTest(test.TestCase):

    MOCK_CACHE = False

    def setUp(self):
        data_api.get_genre_info.cache_clear()

    def test_caching(self):
        data_api.get_genre_info()
        cache_info = data_api.get_genre_info.cache_info()
        self.assertEqual(cache_info.misses, 1)
        self.assertEqual(cache_info.hits, 0)

        data_api.get_genre_info()
        cache_info = data_api.get_genre_info.cache_info()
        self.assertEqual(cache_info.misses, 1)
        self.assertEqual(cache_info.hits, 1)


class GetGenresWithDepthForWorksTest(test.TestCase):

    def test_happy(self):
        genre = factories.GenreFactory.create()
        work = factories.WorkFactory.create(genres=[genre])
        self.assertEqual(
            data_api.get_genres_with_depth_for_works([work.id]),
            {work.id: {(genre.name, 0)}})

    def test_sub_genre(self):
        genre = factories.GenreFactory.create()
        sub_genre = factories.GenreFactory.create(parent_genre=genre)
        work = factories.WorkFactory.create(genres=[genre, sub_genre])
        self.assertEqual(
            data_api.get_genres_with_depth_for_works([work.id]),
            {work.id: {(genre.name, 0), (sub_genre.name, 1)}})

    def test_no_genres(self):
        work = factories.WorkFactory.create()
        self.assertEqual(
            data_api.get_genres_with_depth_for_works([work.id]),
            {work.id: set([])})
        factories.GenreFactory.create()
        self.assertEqual(
            data_api.get_genres_with_depth_for_works([work.id]),
            {work.id: set([])})


class GetWorkIdsWithTropesTest(test.TestCase):

    def setUp(self):
        self.trope = factories.TropeFactory()
        self.other_trope = factories.TropeFactory()
        self.orphan_trope = factories.TropeFactory()
        self.work = factories.WorkFactory.create(tropes=[self.trope])
        self.other_work = factories.WorkFactory.create(
            tropes=[self.other_trope])

    def test_match(self):
        self.assertEqual(
            data_api.get_work_ids_with_tropes([self.trope.id]),
            {self.work.id})
        self.assertEqual(
            data_api.get_work_ids_with_tropes([self.other_trope.id]),
            {self.other_work.id})
        self.assertEqual(
            data_api.get_work_ids_with_tropes([
                self.trope.id, self.orphan_trope.id]),
            {self.work.id})
        self.assertEqual(
            data_api.get_work_ids_with_tropes([
                self.trope.id, self.other_trope.id, self.orphan_trope.id]),
            {self.work.id, self.other_work.id})

    def test_no_match(self):
        # Empty trope ids list.
        self.assertEqual(data_api.get_work_ids_with_tropes([]), set([]))
        # Trope id not found.
        self.assertEqual(
            data_api.get_work_ids_with_tropes([1]), set([]))
        # Trope has no works.
        self.assertEqual(data_api.get_work_ids_with_tropes(
            [self.orphan_trope.id]), set([]))


class GetTagsForTropes(test.TestCase):

    def test_happy(self):
        tag = factories.TropeTagFactory.create()
        tag_two = factories.TropeTagFactory.create()
        trope = factories.TropeFactory.create(tags=[tag, tag_two])
        trope_two = factories.TropeFactory.create(tags=[tag_two])
        self.assertEqual(
            data_api.get_tags_for_tropes([trope.id, trope_two.id]),
            {trope.id: {tag.name, tag_two.name},
             trope_two.id: {tag_two.name}})

    def test_no_tags(self):
        trope = factories.TropeFactory.create()
        self.assertEqual(
            data_api.get_tags_for_tropes([trope.id]),
            {trope.id: set()})


class GetTropesByWorkId(test.TestCase):

    def setUp(self):
        self.tag = factories.TropeTagFactory()
        self.trope = factories.TropeFactory.create(tags=[self.tag])
        self.work = factories.WorkFactory.create(tropes=[self.trope])
        self.other_tag = factories.TropeTagFactory(name='tag 2')
        self.other_trope = factories.TropeFactory.create(
            tags=[self.other_tag])
        self.other_work = factories.WorkFactory.create(
            tropes=[self.other_trope])
        self.both_tags_work = factories.WorkFactory.create(
            tropes=[self.trope, self.other_trope])
        self.no_tropes_work = factories.WorkFactory.create()

    def test_happy(self):
        self.assertEqual(
            data_api.get_tropes_by_work_id([
                self.work.id, self.both_tags_work.id, self.no_tropes_work.id]),
            {self.work.id: {self.trope},
             self.both_tags_work.id: {self.trope, self.other_trope},
             self.no_tropes_work.id: set([])})

    def test_work_id_not_found(self):
        self.assertEqual(data_api.get_tropes_by_work_id([]), {})
        fake_id = 1
        self.assertEqual(
            data_api.get_tropes_by_work_id([fake_id]),
            {fake_id: set([])})

    def test_tag_filter(self):
        # No tag filter.
        self.assertEqual(data_api.get_tropes_by_work_id(
            [self.work.id], tag_names=None), {self.work.id: {self.trope}})
        # No tags.
        self.assertEqual(data_api.get_tropes_by_work_id(
            [self.work.id], tag_names=()), {self.work.id: set([])})
        # First tag.
        self.assertEqual(
            data_api.get_tropes_by_work_id(
                [self.work.id, self.other_work.id, self.both_tags_work.id],
                tag_names=(self.tag.name, )),
            {self.work.id: {self.trope},
             self.other_work.id: set([]),
             self.both_tags_work.id: {self.trope}})
        # Other tag.
        self.assertEqual(
            data_api.get_tropes_by_work_id(
                [self.work.id, self.other_work.id, self.both_tags_work.id],
                tag_names=(self.other_tag.name, )),
            {self.work.id: set([]),
             self.other_work.id: {self.other_trope},
             self.both_tags_work.id: {self.other_trope}})
        # Both tags.
        self.assertEqual(
            data_api.get_tropes_by_work_id(
                [self.work.id, self.other_work.id, self.both_tags_work.id],
                tag_names=(self.tag.name, self.other_tag.name)),
            {self.work.id: {self.trope},
             self.other_work.id: {self.other_trope},
             self.both_tags_work.id: {self.trope, self.other_trope}})


class GetWorkIdsByName(test.TestCase):

    def test_happy(self):
        work_one = factories.WorkFactory.create()
        work_two = factories.WorkFactory.create()
        self.assertEqual(
            data_api.get_work_ids_by_name([work_one.name]),
            [work_one.id])
        self.assertEqual(
            set(data_api.get_work_ids_by_name([
                work_one.name, work_two.name])),
            {work_one.id, work_two.id})

    def test_empty(self):
        self.assertEqual(data_api.get_work_ids_by_name([]), [])


class GetWorkInfoDictsById(test.TestCase):

    def test_happy(self):
        work = factories.WorkFactory.create()
        self.assertEqual(
            data_api.get_work_info_dicts_by_id([work.id]),
            [{
                'id': work.id, 'name': work.name, 'url': work.url,
                'creator': {
                    'id': work.creator.id,
                    'name': work.creator.name,
                    'url': work.creator.url},
                'genres': [],
                'total_shared_tropes': 0,
                'tropes': []
            }])

    def test_genres(self):
        genre_one = factories.GenreFactory.create()
        genre_two = factories.GenreFactory.create()
        work = factories.WorkFactory.create(genres=[genre_one, genre_two])
        info_dicts = data_api.get_work_info_dicts_by_id([work.id])
        self.assertEqual(
            info_dicts,
            [{
                'id': work.id, 'name': work.name, 'url': work.url,
                'creator': {
                    'id': work.creator.id,
                    'name': work.creator.name,
                    'url': work.creator.url},
                'genres': mock.ANY,
                'total_shared_tropes': 0,
                'tropes': []
            }])
        self.assertCountEqual(
            set(info_dicts[0]['genres']), [genre_one.name, genre_two.name])

    def test_tropes(self):
        trope = factories.TropeFactory.create()
        trope_two = factories.TropeFactory.create()
        work = factories.WorkFactory.create(tropes=[trope, trope_two])
        info_dicts = data_api.get_work_info_dicts_by_id([work.id])
        self.assertEqual(
            info_dicts,
            [{
                'id': work.id, 'name': work.name, 'url': work.url,
                'creator': {
                    'id': work.creator.id,
                    'name': work.creator.name,
                    'url': work.creator.url},
                'genres': [],
                'total_shared_tropes': 2,
                'tropes': mock.ANY
            }])
        self.assertCountEqual(
            info_dicts[0]['tropes'],
            [{'id': trope.id,
              'name': trope.name,
              'url': trope.url,
              'laconic_description': trope.laconic_description},
             {'id': trope_two.id,
              'name': trope_two.name,
              'url': trope_two.url,
              'laconic_description': trope_two.laconic_description}])

    def test_filtered_tropes(self):
        trope = factories.TropeFactory.create()
        trope_two = factories.TropeFactory.create()
        trope_three = factories.TropeFactory.create()
        excluded_trope = factories.TropeFactory.create()
        excluded_trope_two = factories.TropeFactory.create()
        work = factories.WorkFactory.create(
            tropes=[trope, trope_two, trope_three,
                    excluded_trope, excluded_trope_two])
        info_dicts = data_api.get_work_info_dicts_by_id(
            [work.id], allowed_trope_id_to_weight={
                trope.id: 1, trope_two.id: 3, trope_three.id: 2})
        self.assertEqual(
            info_dicts,
            [{
                'id': work.id, 'name': work.name, 'url': work.url,
                'creator': {
                    'id': work.creator.id,
                    'name': work.creator.name,
                    'url': work.creator.url},
                'genres': [],
                'total_shared_tropes': 3,
                'tropes': [
                    {
                       'id': trope_two.id,
                       'name': trope_two.name,
                       'url': trope_two.url,
                       'laconic_description': trope_two.laconic_description
                    },
                    {
                        'id': trope_three.id,
                        'name': trope_three.name,
                        'url': trope_three.url,
                        'laconic_description': trope_three.laconic_description
                    },
                    {
                        'id': trope.id,
                        'name': trope.name,
                        'url': trope.url,
                        'laconic_description': trope.laconic_description
                    },
                ]
            }])

    def test_max_tropes_per_work(self):
        trope = factories.TropeFactory.create()
        trope_two = factories.TropeFactory.create()
        work = factories.WorkFactory.create(tropes=[trope, trope_two])
        info_dicts = data_api.get_work_info_dicts_by_id(
            [work.id], max_tropes_per_work=2)
        self.assertEqual(len(info_dicts[0]['tropes']), 2)
        self.assertEqual(info_dicts[0]['total_shared_tropes'], 2)

        info_dicts = data_api.get_work_info_dicts_by_id(
            [work.id], max_tropes_per_work=1)
        self.assertEqual(len(info_dicts[0]['tropes']), 1)
        self.assertEqual(info_dicts[0]['total_shared_tropes'], 2)

        info_dicts = data_api.get_work_info_dicts_by_id(
            [work.id], max_tropes_per_work=0)
        self.assertEqual(len(info_dicts[0]['tropes']), 0)
        self.assertEqual(info_dicts[0]['total_shared_tropes'], 2)

    def test_no_creator(self):
        work = factories.WorkFactory.create(creator=None)
        self.assertEqual(
            data_api.get_work_info_dicts_by_id([work.id]),
            [{
                'id': work.id, 'name': work.name, 'url': work.url,
                'creator': None,
                'genres': [],
                'total_shared_tropes': 0,
                'tropes': []
            }])

    def test_not_found(self):
        with self.assertRaises(models.Work.DoesNotExist):
            data_api.get_work_info_dicts_by_id([1])
