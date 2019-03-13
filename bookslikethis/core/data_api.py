from core import models
from core import cache
from django.db import models as dj_models


def get_tropes(tag_names=None):
    """Fetches all tropes.

    Args:
        tag_names: Iterable of tag names to limit tropes to.

    Returns:
        List of models.Trope objects, with tags prefetched.
    """
    tropes = _get_tropes()
    if tag_names is None:
        return tropes

    filtered_tropes = []
    tag_names = set(tag_names)
    for trope in tropes:
        if trope.get_tag_set().intersection(tag_names):
            filtered_tropes.append(trope)
    return filtered_tropes


@cache.lru_cache(maxsize=1)
def _get_tropes():
    """Fetches all tropes.

    Returns:
        List of models.Trope objects, with tag names prefetched.
    """
    tropes = list(models.Trope.objects.all())
    trope_id_to_tags = get_tags_for_tropes([t.id for t in tropes])
    for trope in tropes:
        trope.set_tag_set(trope_id_to_tags[trope.id])
    return tropes


@cache.lru_cache(maxsize=32)
def get_trope_to_occurrence_count(tag_names=None):
    """Gets number of works per trope.

    Args:
        tag_names: Optional, tuple of string trope tag names.
            If supplied, only tropes with at least one of those
            tags will be counted.

    Returns:
        Dict of integer trope id to integer count of works.
        Tropes with zero works are omitted.
    """
    tropes = get_tropes(tag_names=tag_names)
    trope_works = models.TropeWork.objects.filter(
        trope_id__in=[t.id for t in tropes])
    return {
        tw['trope']: tw['num_works']
        for tw in trope_works.values('trope').annotate(
            num_works=dj_models.Count('work', distinct=True))}


@cache.lru_cache(maxsize=1)
def get_genre_info():
    """Fetches genre information.

    Returns:
        Dict of genre id to (name, depth) tuple.
    """
    genre_id_to_name = {}
    genre_map = {}
    for genre_id, genre_name, parent_id in (
            models.Genre.objects.all().values_list(
                'id', 'name', 'parent_genre')):
        genre_id_to_name[genre_id] = genre_name
        genre_map[genre_id] = parent_id

    def get_depth(gid):
        depth = 0
        gid = genre_map.get(gid)
        while gid is not None:
            depth += 1
            gid = genre_map.get(gid)
        return depth

    # Calculate the depth of each genre.
    genre_id_to_name_and_depth = {
        gid: (name, get_depth(gid))
        for (gid, name) in genre_id_to_name.items()}
    return genre_id_to_name_and_depth


def get_genres_with_depth_for_works(work_ids):
    """Fetch genres for a list of works.

    Args:
        work_ids: List of work ids.

    Returns:
        Dict of work id to set of (genre name, genre depth) tuples.
        Depth indicates the genre's depth in the genre hierarchy -
        genres may have parents, and depth 0 indicates a root genre.
    """
    genre_id_to_name_and_depth = get_genre_info()

    work_id_to_genre_name_and_depth = {wid: set([]) for wid in work_ids}
    for work_id, genre_id in models.GenreMap.objects.filter(
            work_id__in=work_ids).values_list('work_id', 'genre_id'):
        work_id_to_genre_name_and_depth[work_id].add(
            genre_id_to_name_and_depth[genre_id])

    return work_id_to_genre_name_and_depth


def get_work_ids_with_tropes(trope_ids):
    """Fetches works with at least one of the given tropes.

    Args:
        trope_ids: List of trope ids.

    Returns:
        Set of work ids.
    """
    if not trope_ids:
        return set([])
    return set(models.TropeWork.objects.filter(
        trope_id__in=trope_ids).values_list(
        'work_id', flat=True))


def get_tags_for_tropes(trope_ids):
    """Fetches tags associated with each trope.

    Args:
        trope_ids: Iterable of trope ids.

    Returns:
        Dict of trope id to frozenset of string tag names.
    """
    trope_id_to_tags = {tid: set() for tid in trope_ids}
    for trope_id, tag_name in models.TropeTagMap.objects.filter(
            trope_id__in=trope_ids).select_related(
            'trope_tag').values_list(
            'trope_id', 'trope_tag__name'):
        trope_id_to_tags[trope_id].add(tag_name)
    return {
        tid: frozenset(tags)
        for (tid, tags) in trope_id_to_tags.items()}


def get_tropes_by_work_id(work_ids, tag_names=None):
    """Fetches tropes associated with each work.

    Args:
        work_ids: List of work ids.
        tag_names: Optional, list of tag names to
            limit tropes to.

    Returns:
        Dict of work id to set of models.Trope objects.
    """
    if not work_ids:
        return {}
    tropes = {t.id: t for t in get_tropes(tag_names=tag_names)}
    trope_works = models.TropeWork.objects.filter(
        work_id__in=work_ids).values_list('work_id', 'trope_id')

    work_to_tropes = {wid: set([]) for wid in work_ids}
    for work_id, trope_id in trope_works:
        if trope_id in tropes:
            work_to_tropes[work_id].add(tropes[trope_id])
    return work_to_tropes


def get_work_ids_by_name(work_names):
    """Fetches work ids based on URLs.

    Args:
        work_names: Iterable of string work names.

    Returns:
        List of work ids in no particular order.
    """
    return list(models.Work.objects.filter(
        name__in=work_names).values_list('id', flat=True))


def get_work_info_dicts_by_id(
        work_ids, allowed_trope_id_to_weight=None, max_tropes_per_work=10):
    """Fetches work info by id.

    Args:
        work_ids: List of work ids.
        allowed_trope_id_to_weight: Optional, dict of trope id to float
            weight. Limits the tropes returned with each work to ones in
            this dict. The returned tropes are also ordered according to
            their associated weight value, highest first. Pass None to return
            all tropes in no specific order.
        max_tropes_per_work: Optional, integer max trope dicts to return
            with any work. Pass None for unlimited.

    Returns:
        List of dicts with these fields:
            -id
            -name
            -url
            -creator: dict with name and url fields
            -genre: list of unique genre names.
            -tropes:  list of trope info dicts for shared tropes, ordered by
                allowed_trope_id_to_weights. Has these keys:
                -id
                -name
                -url
                -laconic_description
            -total_shared_tropes: Integer, total shared allowed tropes.
                Ignores max_tropes_per_work.
        Results follow the same order as the work_ids argument.

    Raises:
        DoesNotExist if any work_id is not found in the DB.
    """
    id_to_work = {
        w.id: w for w in models.Work.objects.filter(
            id__in=work_ids).select_related(
            'creator').prefetch_related('genres', 'tropes')}
    info_dicts = []
    for work_id in work_ids:
        if work_id not in id_to_work:
            raise models.Work.DoesNotExist
        work = id_to_work[work_id]
        info_dict = {
            'id': work.id, 'name': work.name, 'url': work.url,
            'creator': ({'id': work.creator.id,
                         'name': work.creator.name,
                         'url': work.creator.url}
                        if work.creator else None),
            'genres': list({g.name for g in work.genres.all()}),
        }
        # Add trope data, filtered and sorted by weight if applicable.
        tropes = [{
            'id': t.id,
            'name': t.name,
            'url': t.url,
            'laconic_description': t.laconic_description}
            for t in work.tropes.all()
            if (allowed_trope_id_to_weight is None or
                t.id in allowed_trope_id_to_weight)]
        if allowed_trope_id_to_weight is not None:
            tropes = sorted(
                tropes,
                key=lambda td: allowed_trope_id_to_weight[td['id']],
                reverse=True)
        info_dict['total_shared_tropes'] = len(tropes)
        if max_tropes_per_work is not None:
            tropes = tropes[:max_tropes_per_work]
        info_dict['tropes'] = tropes
        info_dicts.append(info_dict)
    return info_dicts
