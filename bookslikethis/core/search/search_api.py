from django.contrib.postgres import search as pg_search

from core.search import work_similarity
from core import data_api
from core import models

# Controls which trope categories are used for work similarity
# measurement, as well as their relative weight.
TROPE_TAG_WEIGHTS = {
    'plot': 3, 'setting': 3, 'character': 3,
    'characterization': 3,
    'character_as_device': 1, 'politics': 1}
MAX_SEARCH_RESULTS = 10
MAX_AUTOCOMPLETE_RESULTS = 8

# Min trigram similarity value for an autocomplete match.
# 0-1, with 1 being identical.
MIN_AUTOCOMPLETE_SIMILARITY = 0.2


def get_similar_books(work_ids):
    """Finds books that are similar to a given set.

    Args:
        work_ids: List of integer work ids.

    Returns:
        Tuple of:
            List of work ids, most similar first. May be empty.
            Dict of trope id to distinctiveness rating. Has entries for
                every trope, obeying tag_names, in the work set.
    """
    similar_work_ids = work_similarity.find_similar_works(
        work_ids,
        limit=MAX_SEARCH_RESULTS,
        tag_names=tuple(TROPE_TAG_WEIGHTS.keys()),
        tag_weights=TROPE_TAG_WEIGHTS)
    return similar_work_ids


def get_autocomplete_suggestions(
        query,
        limit=MAX_AUTOCOMPLETE_RESULTS,
        min_similarity=MIN_AUTOCOMPLETE_SIMILARITY):
    """Gets autocomplete suggestions for a work name query.

    Args:
        query: String, search query.
        limit: Optional, integer max suggestions.
        min_similarity: Optional, float minimum trigram similarity
            of a suggestion. 0-1 where 1 is identical.

    Returns:
        List of work suggestions dicts, best first.
        May return an empty list.
        Dicts have the following keys:
            name
    """
    matching_works = models.Work.objects.annotate(
        similarity=pg_search.TrigramSimilarity('name', query)).filter(
        similarity__gte=min_similarity).order_by(
        '-similarity')[:limit]
    return [{'name': w.name} for w in matching_works]


def get_work_id_for_search_query(query):
    """Attempts to convert a work name search query to a work id.

    Args:
        query: String, search query.

    Returns:
        Integer work id, or None.
    """
    matches = get_autocomplete_suggestions(query, limit=1)
    if matches:
        work_ids = data_api.get_work_ids_by_name([matches[0]['name']])
        if work_ids:
            return work_ids[0]
    return None
