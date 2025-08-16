from typing import List, Dict
import itertools

# Define compatibility rules (expandable)
FIT_COMPATIBILITY = {
    "slim": ["relaxed", "structured", "slim"],
    "relaxed": ["slim", "oversized", "relaxed"],
    "oversized": ["relaxed", "oversized"],
}

SILHOUETTE_COMPATIBILITY = {
    "structured": ["structured", "flowy", "boxy"],
    "flowy": ["structured", "flowy"],
    "boxy": ["structured", "boxy"],
}

TEXTURE_COMPATIBILITY = {
    "smooth": ["smooth", "silky"],
    "rough": ["rough", "textured"],
    "sheer": ["smooth", "silky"],
}

def score_pair(item1: Dict, item2: Dict) -> float:
    """
    Scores pairwise compatibility between two clothing items.
    Each dimension (fit, silhouette, textureStyle) contributes equally (1/3).
    """
    metadata1 = item1.get("metadata", {})
    metadata2 = item2.get("metadata", {})

    fit1, fit2 = metadata1.get("fit"), metadata2.get("fit")
    silhouette1, silhouette2 = metadata1.get("silhouette"), metadata2.get("silhouette")
    texture1, texture2 = metadata1.get("textureStyle"), metadata2.get("textureStyle")

    score = 0
    total = 0

    if fit1 and fit2:
        total += 1
        if fit2 in FIT_COMPATIBILITY.get(fit1, []):
            score += 1

    if silhouette1 and silhouette2:
        total += 1
        if silhouette2 in SILHOUETTE_COMPATIBILITY.get(silhouette1, []):
            score += 1

    if texture1 and texture2:
        total += 1
        if texture2 in TEXTURE_COMPATIBILITY.get(texture1, []):
            score += 1

    return score / total if total > 0 else 0.5  # default neutral if unknown

def average_pairability(items: List[Dict]) -> float:
    """
    Averages all pairwise scores in the outfit.
    """
    if len(items) < 2:
        return 1.0  # trivially perfect

    pairs = list(itertools.combinations(items, 2))
    total_score = sum(score_pair(i1, i2) for i1, i2 in pairs)
    return total_score / len(pairs) 