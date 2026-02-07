from __future__ import annotations

from typing import Dict, Optional

import tldextract


def _normalize_domain(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    extracted = tldextract.extract(value)
    if not extracted.suffix:
        return None
    return f"{extracted.domain}.{extracted.suffix}".lower()


def _levenshtein_distance(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    if len(a) < len(b):
        a, b = b, a

    previous_row = list(range(len(b) + 1))
    for i, char_a in enumerate(a, start=1):
        current_row = [i]
        for j, char_b in enumerate(b, start=1):
            insert_cost = current_row[j - 1] + 1
            delete_cost = previous_row[j] + 1
            replace_cost = previous_row[j - 1] + (char_a != char_b)
            current_row.append(min(insert_cost, delete_cost, replace_cost))
        previous_row = current_row
    return previous_row[-1]


def check_typosquat(registered_domain: Optional[str], claimed_brand_domain: Optional[str]) -> Dict[str, Optional[object]]:
    normalized_registered = _normalize_domain(registered_domain)
    normalized_claimed = _normalize_domain(claimed_brand_domain)

    if not normalized_registered or not normalized_claimed:
        return {
            "is_suspicious": False,
            "closest_match": None,
            "distance": None,
            "similarity": None,
        }

    distance = _levenshtein_distance(normalized_registered, normalized_claimed)
    max_len = max(len(normalized_registered), len(normalized_claimed))
    similarity = 1.0 - (distance / max_len) if max_len else 1.0

    is_suspicious = (
        normalized_registered != normalized_claimed
        and distance <= 2
        and similarity >= 0.8
    )

    return {
        "is_suspicious": is_suspicious,
        "closest_match": normalized_claimed,
        "distance": distance,
        "similarity": round(similarity, 4),
    }
