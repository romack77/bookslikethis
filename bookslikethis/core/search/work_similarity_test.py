from unittest import mock

from core import data_api
from core import factories
from core import test
from core.search import work_similarity


class GenreSimilarityTest(test.TestCase):

    def test_happy(self):
        genre = factories.GenreFactory.create()
        genre_two = factories.GenreFactory.create()
        work = factories.WorkFactory.create(genres=[genre, genre_two])
        work_two = factories.WorkFactory.create(genres=[genre])
        work_three = factories.WorkFactory.create(genres=[genre, genre_two])
        work_four = factories.WorkFactory.create(genres=[])
        self.assertEqual(
            work_similarity.genre_similarity(
                [work.id], [work_two.id, work_three.id, work_four.id]),
            {work_two.id: 1.5, work_three.id: 2, work_four.id: 1}
        )

    def test_multiple_sources(self):
        genre = factories.GenreFactory.create()
        genre_two = factories.GenreFactory.create()
        work = factories.WorkFactory.create(genres=[genre])
        work_two = factories.WorkFactory.create(genres=[genre_two])
        work_three = factories.WorkFactory.create(genres=[genre])
        work_four = factories.WorkFactory.create(genres=[genre_two])
        self.assertEqual(
            work_similarity.genre_similarity(
                [work.id, work_two.id], [work_three.id, work_four.id]),
            {work_three.id: 1.5, work_four.id: 1.5}
        )

    def test_no_common_genres(self):
        genre = factories.GenreFactory.create()
        genre_two = factories.GenreFactory.create()
        work = factories.WorkFactory.create(genres=[genre])
        work_two = factories.WorkFactory.create(genres=[genre_two])
        self.assertEqual(
            work_similarity.genre_similarity([work.id], [work_two.id]),
            {work_two.id: 1}
        )

    def test_same_genres(self):
        genre = factories.GenreFactory.create()
        work = factories.WorkFactory.create(genres=[genre])
        work_two = factories.WorkFactory.create(genres=[genre])
        self.assertEqual(
            work_similarity.genre_similarity([work.id], [work_two.id]),
            {work_two.id: 2}
        )

    def test_root_genres_only(self):
        parent_genre = factories.GenreFactory.create()
        sub_genre = factories.GenreFactory.create(
            parent_genre=parent_genre)
        work = factories.WorkFactory.create(genres=[sub_genre])
        work_two = factories.WorkFactory.create(genres=[sub_genre])
        self.assertEqual(
            work_similarity.genre_similarity([work.id], [work_two.id]),
            {work_two.id: 1}
        )

    def test_excluded_genres(self):
        genre = factories.GenreFactory.create(
            name=list(work_similarity.SIMILARITY_EXCLUDED_GENRES)[0])
        work = factories.WorkFactory.create(genres=[genre])
        work_two = factories.WorkFactory.create(genres=[genre])
        self.assertEqual(
            work_similarity.genre_similarity([work.id], [work_two.id]),
            {work_two.id: 1}
        )

    def test_merged_genres(self):
        merged_pair = list(
            work_similarity.SIMILARITY_MERGED_GENRE_MAP.items())[0]
        genre = factories.GenreFactory.create(name=merged_pair[0])
        genre_two = factories.GenreFactory.create(name=merged_pair[1])
        work = factories.WorkFactory.create(genres=[genre])
        work_two = factories.WorkFactory.create(genres=[genre_two])
        self.assertEqual(
            work_similarity.genre_similarity([work.id], [work_two.id]),
            {work_two.id: 2}
        )


class CalcTropeDistinctivenessForWorksTest(test.TestCase):

    def test_happy(self):
        trope_one = factories.TropeFactory.create()
        work = factories.WorkFactory.create(tropes=[trope_one])
        trope_two = factories.TropeFactory.create()
        work_two = factories.WorkFactory.create(tropes=[trope_one])
        factories.WorkFactory.create(tropes=[trope_two])
        work_to_tropes = data_api.get_tropes_by_work_id([work.id])
        trope_id_to_score = (
            work_similarity.calc_trope_distinctiveness_for_works(
                work_to_tropes))
        self.assertEqual(trope_id_to_score, {trope_one.id: mock.ANY})
        self.assertEqual(round(trope_id_to_score[trope_one.id], 2), 0.24)
        # Adding works to the DB without the trope makes it more distinct.
        factories.WorkFactory.create(tropes=[trope_two])
        trope_id_to_score = (
            work_similarity.calc_trope_distinctiveness_for_works(
                work_to_tropes))
        self.assertEqual(trope_id_to_score, {trope_one.id: mock.ANY})
        self.assertEqual(round(trope_id_to_score[trope_one.id], 2), 0.58)
        # Including both works with the trope in the work set makes
        # it more distinct.
        work_to_tropes = data_api.get_tropes_by_work_id([work.id, work_two.id])
        trope_id_to_score = (
            work_similarity.calc_trope_distinctiveness_for_works(
                work_to_tropes))
        self.assertEqual(trope_id_to_score, {trope_one.id: mock.ANY})
        self.assertEqual(round(trope_id_to_score[trope_one.id], 2), 2.77)

    def test_no_tropes(self):
        work = factories.WorkFactory.create()
        work_to_tropes = data_api.get_tropes_by_work_id([work.id])
        self.assertEqual(
            work_similarity.calc_trope_distinctiveness_for_works(
                work_to_tropes),
            {})

    def test_tag_names(self):
        in_tag = factories.TropeTagFactory.create(name='included')
        out_tag = factories.TropeTagFactory.create(name='excluded')
        in_trope = factories.TropeFactory.create(tags=[in_tag])
        out_trope = factories.TropeFactory.create(tags=[out_tag])
        work = factories.WorkFactory.create(tropes=[in_trope, out_trope])
        work_to_tropes = data_api.get_tropes_by_work_id([work.id])
        self.assertEqual(
            work_similarity.calc_trope_distinctiveness_for_works(
                work_to_tropes, tag_names=[in_tag.name]),
            {in_trope.id: 0.0})

    def test_tag_weights(self):
        tag_one = factories.TropeTagFactory.create(name='one')
        tag_two = factories.TropeTagFactory.create(name='two')
        trope_one = factories.TropeFactory.create(tags=[tag_one])
        trope_two = factories.TropeFactory.create(tags=[tag_two])
        trope_both = factories.TropeFactory.create(tags=[tag_one, tag_two])
        other_trope = factories.TropeFactory.create()
        work = factories.WorkFactory.create(
            tropes=[trope_one, trope_two, trope_both])
        factories.WorkFactory.create(tropes=[other_trope])
        work_to_tropes = data_api.get_tropes_by_work_id([work.id])
        trope_id_to_score = (
            work_similarity.calc_trope_distinctiveness_for_works(
                work_to_tropes,
                tag_weights={tag_one.name: 1, tag_two.name: 10}))
        self.assertEqual(len(trope_id_to_score), 3)
        self.assertEqual(round(trope_id_to_score[trope_one.id], 2), .58)
        self.assertEqual(round(trope_id_to_score[trope_two.id], 2), 5.75)
        self.assertEqual(round(trope_id_to_score[trope_both.id], 2), 5.75)


class FindSimilarWorksTest(test.TestCase):

    def test_happy(self):
        trope_one = factories.TropeFactory.create()
        trope_two = factories.TropeFactory.create()
        trope_three = factories.TropeFactory.create()
        work = factories.WorkFactory.create(tropes=[trope_one, trope_two])
        work_one_match = factories.WorkFactory.create(tropes=[trope_one])
        work_two_match = factories.WorkFactory.create(
            tropes=[trope_one, trope_two])
        factories.WorkFactory.create(tropes=[trope_three])  # No match
        ranked_works, trope_id_to_score = work_similarity.find_similar_works(
            [work.id])
        self.assertEqual(ranked_works, [work_two_match.id, work_one_match.id])
        self.assertEqual(
            trope_id_to_score,
            {trope_one.id: mock.ANY, trope_two.id: mock.ANY})
