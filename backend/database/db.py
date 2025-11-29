
"""MongoDB + in-memory trends."""

from __future__ import annotations

import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.claim import ClaimIn, ClaimOut

try:
    from pymongo import MongoClient, errors  # type: ignore
except Exception:  # pragma: no cover
    MongoClient = None  # type: ignore
    errors = None  # type: ignore


_MONGO_CLIENT: Optional["MongoClient"] = None
_IN_MEMORY_LOG: List[Dict[str, Any]] = []


def _get_client() -> Optional["MongoClient"]:
    global _MONGO_CLIENT
    if MongoClient is None:
        return None
    if _MONGO_CLIENT is not None:
        return _MONGO_CLIENT

    uri = os.getenv(
        "MONGODB_URI",
        "mongodb+srv://shreyashdusane605_db_user:shreyash@misinformation.ltyzx17.mongodb.net/",
    )
    try:
        _MONGO_CLIENT = MongoClient(uri, serverSelectionTimeoutMS=1000)
        _MONGO_CLIENT.admin.command("ping")
        return _MONGO_CLIENT
    except Exception:
        _MONGO_CLIENT = None
        return None


def _get_collection():
    client = _get_client()
    if not client:
        return None
    db = client["truthpulse"]
    return db["claims"]


def save_claim_result(payload: ClaimIn, result: ClaimOut) -> None:
    doc: Dict[str, Any] = {
        "claim": result.claim,
        "category": result.category,
        "confidence": result.confidence,
        "truth_score": result.truth_score,
        "verdict": result.verdict,
        "severity": payload.severity,
        "language": payload.language,
        "meta": result.meta,
        "created_at": datetime.utcnow(),
    }

    _IN_MEMORY_LOG.append(doc)
    if len(_IN_MEMORY_LOG) > 500:
        del _IN_MEMORY_LOG[: len(_IN_MEMORY_LOG) - 500]

    col = _get_collection()
    if not col:
        return
    try:
        col.insert_one(doc)
    except Exception:
        return


def _aggregate_from_memory(limit: int) -> List[Dict[str, Any]]:
    counts: Dict[str, int] = {}
    for doc in _IN_MEMORY_LOG:
        cat = doc.get("category", "other")
        counts[cat] = counts.get(cat, 0) + 1
    items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    return [{"category": k, "count": v} for k, v in items]


def get_trending_categories(limit: int = 10) -> List[Dict[str, Any]]:
    col = _get_collection()
    if not col:
        return _aggregate_from_memory(limit)

    try:
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]
        docs = list(col.aggregate(pipeline))
        if not docs:
            return _aggregate_from_memory(limit)
        return [
            {"category": d.get("_id", "other"), "count": d.get("count", 0)} for d in docs
        ]
    except Exception:
        return _aggregate_from_memory(limit)
