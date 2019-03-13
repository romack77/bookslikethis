from core import data_api
from core.search import similarity

# When works are compared based on tropes, only the strongest
# this-many tropes are counted. Use None for no limit.
# A threshold helps prioritize distinctiveness over works with
# lots of bland tropes.
WORK_SIMILARITY_MAX_INTERSECTIONS = 20

# Genres to exclude when considering work similarity by genre.
SIMILARITY_EXCLUDED_GENRES = {
    'Picaresque', 'Dime Novel', 'Sea Stories'}

# Genres to merge when considering work similarity by genre.
SIMILARITY_MERGED_GENRE_MAP = {
    'Mystery Lit': 'Mystery Fiction',
    'Superhero Literature': 'Speculative Fiction',
    'Legend': 'Fables, Fairy Tales, and Folklore',
    'Mythology': 'Fables, Fairy Tales, and Folklore',
    'Mythopoeia': 'Fables, Fairy Tales, and Folklore',
    'Chivalric Romance': 'Romance'}


def genre_similarity(reference_work_ids, target_work_ids):
    """Calculates a multiplier factor based on genre similarity.

    This looks at all genre tags and calculates a jaccard
    set similarity score. This is done separately for each
    work in work_ids.

    Args:
        reference_work_ids: List of work ids for the reference set.
        target_work_ids: List of work ids for which to calculate similarity
            to the reference set.

    Returns:
        Dict of each target work id to float genre similarity score, 1-2.
        1 indicates no overlap; 2 is complete overlap.
    """
    reference_work_ids = set(reference_work_ids)
    target_work_ids = set(target_work_ids)

    def filter_genres(genres):
        filtered_genres = set([])
        for genre_name, genre_depth in genres:
            if genre_depth != 0:
                continue  # root genres only
            if genre_name in SIMILARITY_EXCLUDED_GENRES:
                continue
            if genre_name in SIMILARITY_MERGED_GENRE_MAP:
                genre_name = SIMILARITY_MERGED_GENRE_MAP[genre_name]
            filtered_genres.add((genre_name, genre_depth))
        return filtered_genres

    work_id_to_genres = data_api.get_genres_with_depth_for_works(
        reference_work_ids.union(target_work_ids))
    work_id_to_genres = {
        wid: filter_genres(genres)
        for (wid, genres) in work_id_to_genres.items()}

    work_id_to_genre_similarity = {}
    for target_wid in target_work_ids:
        target_genres = work_id_to_genres[target_wid]
        jaccard_scores = []
        for wid in reference_work_ids:
            if wid == target_wid:
                continue
            source_genres = work_id_to_genres[wid]
            jaccard_scores.append(
                similarity.jaccard_similarity(source_genres, target_genres))
        average_score = sum(jaccard_scores) / len(jaccard_scores)
        work_id_to_genre_similarity[target_wid] = average_score + 1

    return work_id_to_genre_similarity


def calc_trope_distinctiveness_for_works(
        work_id_to_tropes, tag_names=None, tag_weights=None):
    """Scores the distinctiveness of tropes in a set of works.

    This compares trope frequency in the given set of works with the
    rest of the works in the database.

    Args:
        work_id_to_tropes: Dict of work ids to set of tropes.
        tag_names: Optional, tuple of trope tag names to limit results to.
        tag_weights: Optional, dict of trope tag name to float weight.

    Returns:
        Dict of trope id to float distinctiveness score.
    """
    # Get trope frequencies within the work set.
    subset_trope_to_count = _get_trope_counts(
        work_id_to_tropes, tag_names=tag_names)
    subset_occurrences = sum(subset_trope_to_count.values())
    # Get trope frequencies db-wide.
    all_trope_to_count = data_api.get_trope_to_occurrence_count(
        tag_names=tag_names)
    all_occurrences = sum(all_trope_to_count.values())

    # Use frequencies to calculate log likelihood for each trope.
    trope_to_likelihood = {}
    for trope, works_count in subset_trope_to_count.items():
        trope_to_likelihood[trope] = similarity.dunning_log_likelihood(
            subset_trope_to_count[trope],
            subset_occurrences,
            (all_trope_to_count[trope.id] -
                subset_trope_to_count.get(trope, 0)),
            all_occurrences - subset_occurrences)

    if not tag_weights:
        return {t.id: s for (t, s) in trope_to_likelihood.items()}

    # Apply any trope tag_name weighting.
    trope_id_to_weighted_likelihood = {}
    for trope, original_weight in trope_to_likelihood.items():
        trope_id_to_weighted_likelihood[trope.id] = original_weight
        for cat_name in trope.get_tag_set():
            if cat_name in tag_weights:
                trope_id_to_weighted_likelihood[trope.id] = max(
                    trope_id_to_weighted_likelihood[trope.id],
                    original_weight * tag_weights[cat_name])
    return trope_id_to_weighted_likelihood


def _get_trope_counts(work_id_to_tropes, tag_names=None):
    """Totals occurrences of each trope across works.

    Args:
        work_id_to_tropes: Dict of work id to set of models.Trope objects.
        tag_names: Optional, iterable of string trope tag names to limit
            similarity scoring to.

    Returns:
        Dict of models.Trope to integer count.
    """
    if tag_names is None:
        tag_names = []
    tag_names = set(tag_names)
    trope_to_count = {}
    for tropes in work_id_to_tropes.values():
        for trope in tropes:
            if not tag_names or tag_names.intersection(trope.get_tag_set()):
                trope_to_count.setdefault(trope, 0)
                trope_to_count[trope] += 1
    return trope_to_count


def find_similar_works(
        work_ids, limit=10,
        tag_names=None, tag_weights=None, use_genre_weights=True):
    """Finds works similar to an given set of works.

    Similarity is based on tropes in common. A genre similarity weighting is
    also applied by default.

    Args:
        work_ids: List of work ids.
        limit: Integer, max number of results to return. None means unlimited.
        tag_names: Optional, tuple of string trope tag names to limit
            similarity scoring to.
        tag_weights: Optional, dict of trope tag name to float
            weight. Any omitted entry will default to a weight of 1.
        use_genre_weights: Boolean, whether to apply a genre similarity
            scoring factor.

    Returns:
        Tuple of:
            List of work ids, most similar first.
            Dict of trope id to distinctiveness rating. Has entries for
                every trope, obeying tag_names, in the work set.
    """
    # Look up the tropes in the reference set.
    ref_work_id_to_tropes = data_api.get_tropes_by_work_id(
        work_ids, tag_names=tag_names)
    ref_tropes = set.union(*ref_work_id_to_tropes.values())

    # Find works which share any relevant tropes with the reference
    # set, and fetch their tropes for analysis.
    match_work_ids = {
        wid for wid in data_api.get_work_ids_with_tropes(
            ref_tropes) if wid not in work_ids}
    match_work_to_ranking = {wid: 0 for wid in match_work_ids}
    match_work_id_to_tropes = data_api.get_tropes_by_work_id(
        match_work_ids, tag_names=tag_names)

    # Score similarity of each matching work, and rank them.
    if use_genre_weights:
        work_id_to_genre_similarity = genre_similarity(
            work_ids, match_work_ids)
    else:
        work_id_to_genre_similarity = {wid: 1 for wid in match_work_ids}

    tropes_by_distinctiveness = calc_trope_distinctiveness_for_works(
        ref_work_id_to_tropes, tag_names=tag_names, tag_weights=tag_weights)

    for work_id in match_work_ids:
        genre_weight = work_id_to_genre_similarity[work_id]
        match_work_to_ranking[work_id] = similarity.jaccard_similarity(
            ref_tropes,
            match_work_id_to_tropes[work_id],
            element_to_weight=tropes_by_distinctiveness,
            max_intersections=WORK_SIMILARITY_MAX_INTERSECTIONS) * genre_weight
    ranked_works = sorted(
        match_work_to_ranking.items(),
        key=lambda t: t[1],
        reverse=True)
    if limit is not None:
        ranked_works = ranked_works[:limit]
    return [rw[0] for rw in ranked_works], tropes_by_distinctiveness


