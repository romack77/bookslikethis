"""Search related views."""
from django import http
from django import views

from core.search import search_api
from core import data_api


class SearchView(views.View):
    """Searches for works similar to a given set."""

    MAX_QUERY_WORKS = 200

    def get(self, request):
        work_info_dicts = []
        work_ids = self._extract_work_ids(request)
        if work_ids:
            similar_work_ids, trope_id_to_weight = (
                search_api.get_similar_books(
                    work_ids))
            if similar_work_ids:
                work_info_dicts = data_api.get_work_info_dicts_by_id(
                    similar_work_ids,
                    allowed_trope_id_to_weight=trope_id_to_weight)
        return http.JsonResponse(
            {'results': work_info_dicts})

    def _extract_work_ids(self, request):
        """Turns query parameter into a set of work ids."""
        work_ids = set([])
        if request.GET.getlist('works'):
            work_ids = work_ids.union(set(
                data_api.get_work_ids_by_name(
                    request.GET.getlist('works'))))
        query = request.GET.get('query')
        if query:
            work_id = search_api.get_work_id_for_search_query(query)
            if work_id is not None:
                work_ids.add(work_id)
        return set(list(work_ids)[:SearchView.MAX_QUERY_WORKS])


class AutocompleteView(views.View):
    """Autocompleter for work names."""

    def get(self, request):
        query = request.GET.get('query')
        if query:
            suggestions = search_api.get_autocomplete_suggestions(query)
        else:
            suggestions = []
        return http.JsonResponse(
            {'suggestions': suggestions})
