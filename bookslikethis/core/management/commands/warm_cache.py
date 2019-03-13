from django.core.management import base

from core import data_api
from core.search import search_api


class Command(base.BaseCommand):

    help = 'Warms caches.'

    def handle(self, *args, **options):
        print('Clearing cache...')
        data_api._get_tropes.cache_clear()
        data_api.get_trope_to_occurrence_count.cache_clear()
        data_api.get_genre_info.cache_clear()
        print('Warming cache...')
        data_api.get_tropes()
        data_api.get_trope_to_occurrence_count(
            tag_names=tuple(search_api.TROPE_TAG_WEIGHTS.keys()))
        data_api.get_genre_info()
        print('Finished warming cache.')
