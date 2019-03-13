from core import test
from core.search import similarity


class DunningLogLikelihoodTest(test.TestCase):

    def test_happy(self):
        self.assertEqual(
            round(similarity.dunning_log_likelihood(2, 10, 1, 10), 2),
            0.34)
        self.assertEqual(
            round(similarity.dunning_log_likelihood(5, 10, 1, 10), 2),
            2.91)
        self.assertEqual(
            round(similarity.dunning_log_likelihood(1, 10, 5, 10), 2),
            -2.91)

    def test_equal_likelihood(self):
        self.assertEqual(
            similarity.dunning_log_likelihood(1, 10, 1, 10),
            0)
        self.assertEqual(
            similarity.dunning_log_likelihood(1, 10, 10, 100),
            0)

    def test_zero_args(self):
        self.assertEqual(
            round(similarity.dunning_log_likelihood(10, 10, 0, 10), 2),
            13.86)
        self.assertEqual(
            similarity.dunning_log_likelihood(0, 10, 0, 10),
            0)
        self.assertEqual(
            similarity.dunning_log_likelihood(0, 10, 0, 0),
            0)
        self.assertEqual(
            similarity.dunning_log_likelihood(0, 0, 0, 0),
            0)


class JaccardSimilarityTest(test.TestCase):

    def setUp(self):
        self.set_a = {'a', 'b', 'c'}
        self.set_b = {'c', 'd'}

    def test_happy(self):
        self.assertEqual(
            similarity.jaccard_similarity({'a', 'b', 'c'}, {'c', 'd'}),
            .25)
        self.assertEqual(
            similarity.jaccard_similarity({'a', 'b', 'c'}, {'b', 'c', 'd'}),
            .50)
        self.assertEqual(
            similarity.jaccard_similarity({'a', 'b', 'c', 'd'}, {'c', 'd'}),
            .50)

    def test_full_overlap(self):
        self.assertEqual(
            similarity.jaccard_similarity({'a', 'b'}, {'a', 'b'}),
            1.0)

    def test_no_overlap(self):
        self.assertEqual(
            similarity.jaccard_similarity({'a', 'b'}, {'x', 'y'}),
            0.0)
        self.assertEqual(
            similarity.jaccard_similarity({'a', 'b'}, set([])),
            0.0)

    def test_empty(self):
        self.assertEqual(
            similarity.jaccard_similarity(set([]), set([])),
            0.0)

    def test_weighted_jaccard(self):
        self.assertEqual(
            similarity.jaccard_similarity(
                {'a', 'b', 'c'}, {'c', 'd'},
                element_to_weight={'a': 1, 'b': 1, 'c': 1, 'd': 1}),
            .25)

        self.assertEqual(
            similarity.jaccard_similarity(
                {'a', 'b', 'c'}, {'c', 'd'},
                element_to_weight={'c': 5}),
            .625)

    def test_max_num_weighted(self):
        set_a = {'a', 'b', 'c'}
        set_b = {'a', 'b', 'c', 'd'}
        weight_dict = {'a': 5, 'b': 5, 'c': 5, 'd': 1}
        self.assertEqual(
            similarity.jaccard_similarity(
                set_a,
                set_b,
                element_to_weight=weight_dict,
                max_intersections=4),
            .9375)

        self.assertEqual(
            similarity.jaccard_similarity(
                set_a,
                set_b,
                element_to_weight=weight_dict,
                max_intersections=3),
            .9375)

        self.assertEqual(
            similarity.jaccard_similarity(
                set_a,
                set_b,
                element_to_weight=weight_dict,
                max_intersections=1),
            .625)

        self.assertEqual(
            similarity.jaccard_similarity(
                set_a,
                set_b,
                element_to_weight=weight_dict,
                max_intersections=0),
            0)
