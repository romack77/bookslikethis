from core import data_api
from core import test
from core.management.commands import warm_cache


class WarmCacheTest(test.TestCase):

    MOCK_CACHE = False

    def test_happy(self):
        data_api.get_trope_to_occurrence_count.cache_clear()

        command = warm_cache.Command()
        command.handle()

        cache_info = data_api.get_trope_to_occurrence_count.cache_info()
        self.assertEqual(cache_info.misses, 1)
