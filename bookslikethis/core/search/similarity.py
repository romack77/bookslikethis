import math


def dunning_log_likelihood(f1, s1, f2, s2):
    """Calculates Dunning log likelihood of an observation in two groups.

    This determines if an observation is more strongly associated with
    one of two groups, and the strength of that association.

    Args:
        f1: Integer, observation frequency in group one.
        s1: Integer, total data points in group one.
        f2: Integer, observation frequency in group two.
        s2: Integer, total data points in group two.

    Returns:
        Float log likelihood. This will be positive if the
        observation is more likely in group one. More extreme
        values indicate a stronger association.
    """
    if f1 + f2 == 0:
        return 0.0
    if s1 == 0 or s2 == 0:
        return 0.0
    f1, s1, f2, s2 = float(f1), float(s1), float(f2), float(s2)
    # Expected values
    e1 = s1 * (f1 + f2) / (s1 + s2)
    e2 = s2 * (f1 + f2) / (s1 + s2)
    l1, l2 = 0, 0
    if e1 != 0 and f1 != 0:
        l1 = f1 * math.log(f1 / e1)
    if e2 != 0 and f2 != 0:
        l2 = f2 * math.log(f2 / e2)

    likelihood = 2 * (l1 + l2)
    if f2 / s2 > f1 / s1:
        likelihood = -likelihood
    return likelihood


def jaccard_similarity(
        set_a, set_b, element_to_weight=None, max_intersections=None):
    """Calculates Jaccard similarity, a measure of set overlap.

    Args:
        set_a: First set.
        set_b: Second set.
        element_to_weight: Optional, a dict of set elements to
            numeric weights. This results in a weighted Jaccard
            similarity. Default weight is 1.
        max_intersections: Optional integer, ignore intersections
            beyond this threshold. If elements are weighted, the
            strongest intersections are the ones counted.

    Returns:
        Float, 0 (no overlap) - 1 (complete overlap). Two empty sets
        return 0.
    """
    if element_to_weight is None:
        element_to_weight = {}
    intersection_weights = sorted([
        max(element_to_weight.get(e, 1), 1)
        for e in set_a.intersection(set_b)], reverse=True)
    if max_intersections is not None:
        intersection_weights = intersection_weights[:max_intersections]

    intersection = sum(intersection_weights)
    union = intersection + len(set_a.union(set_b)) - len(intersection_weights)
    if not union:
        return 0.0
    return intersection / float(union)
