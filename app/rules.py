from __future__ import annotations

import re
from typing import List, Dict, Any, Optional, Tuple

SUPPORTED_FEATURES_BY_VERSION = {
    "1.0": {"collections", "basic queries", "indexes"},
    "1.1": {"collections", "basic queries", "indexes", "feature x"},
}

UNSUPPORTED_FEATURES = {"sharding"}  # demo


def extract_requested_version(query: str) -> Optional[str]:
    m = re.search(r"v(\d+\.\d+)", query.lower())
    if m:
        return m.group(1)
    return None


def mentions_feature_x(query: str) -> bool:
    return "feature x" in query.lower()


def is_unsupported_feature_question(query: str, requested_version: Optional[str]) -> bool:
    q = query.lower()
    # In this demo, Feature X is unsupported in v1.0 but supported in v1.1.
    if "feature x" in q and requested_version == "1.0":
        return True
    for feat in UNSUPPORTED_FEATURES:
        if feat in q:
            return True
    return False


def has_version_conflict(citations: List[Dict[str, Any]], requested_version: Optional[str]) -> bool:
    if not citations:
        return False
    versions = {c.get("version") for c in citations if c.get("version")}
    if requested_version:
        versions.add(requested_version)
    versions.discard(None)
    return len(versions) >= 2
