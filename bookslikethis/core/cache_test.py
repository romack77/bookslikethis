from core import cache
from core import test


class LRUCacheTest(test.TestCase):

    MOCK_CACHE = False

    @cache.lru_cache(maxsize=2, typed=False)
    def add(self, x, y):
        return x + y

    def setUp(self):
        self.add.cache_clear()

    def test_happy(self):
        self.assertEqual(self.add(1, 1), 2)
        cache_info = self.add.cache_info()
        self.assertEqual(cache_info.hits, 0)
        self.assertEqual(cache_info.misses, 1)

        self.assertEqual(self.add(1, 1), 2)
        cache_info = self.add.cache_info()
        self.assertEqual(cache_info.hits, 1)
        self.assertEqual(cache_info.misses, 1)

        self.assertEqual(self.add(2, 2), 4)
        cache_info = self.add.cache_info()
        self.assertEqual(cache_info.hits, 1)
        self.assertEqual(cache_info.misses, 2)

        self.assertEqual(self.add(2, 2), 4)
        cache_info = self.add.cache_info()
        self.assertEqual(cache_info.hits, 2)
        self.assertEqual(cache_info.misses, 2)

    def test_eviction(self):
        self.assertEqual(self.add(1, 1), 2)
        self.assertEqual(self.add(2, 2), 4)
        self.assertEqual(self.add(3, 3), 6)

        self.assertEqual(self.add(3, 3), 6)
        self.assertEqual(self.add(1, 1), 2)
        cache_info = self.add.cache_info()
        self.assertEqual(cache_info.hits, 1)
        self.assertEqual(cache_info.misses, 4)

    def test_empty(self):
        cache_info = self.add.cache_info()
        self.assertEqual(cache_info.hits, 0)
        self.assertEqual(cache_info.misses, 0)

    def test_clear(self):
        self.assertEqual(self.add(1, 1), 2)
        self.assertEqual(self.add(1, 1), 2)
        cache_info = self.add.cache_info()
        self.assertEqual(cache_info.hits, 1)
        self.assertEqual(cache_info.misses, 1)

        self.add.cache_clear()
        self.assertEqual(self.add(1, 1), 2)
        cache_info = self.add.cache_info()
        self.assertEqual(cache_info.hits, 0)
        self.assertEqual(cache_info.misses, 1)
