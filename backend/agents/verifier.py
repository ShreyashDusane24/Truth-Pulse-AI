
"""Verifier Agent: Wikipedia-only by default (more stable).

News API is optional; if not configured, it is simply skipped.
"""

from __future__ import annotations

import os
from typing import List, Dict, Optional
from urllib.parse import quote

from utils.http_client import safe_get_json


WIKI_SEARCH_ENDPOINT = "https://en.wikipedia.org/w/api.php"
WIKI_SUMMARY_ENDPOINT = "https://en.wikipedia.org/api/rest_v1/page/summary/"


def _wiki_search(query: str, language: str = "en") -> Optional[Dict]:
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": 1,
    }
    data = safe_get_json(WIKI_SEARCH_ENDPOINT, params=params)
    if not data:
        return None
    try:
        results = data.get("query", {}).get("search", [])
        if not results:
            return None
        return results[0]
    except Exception:
        return None


def _wiki_summary(title: str) -> Optional[Dict]:
    url = WIKI_SUMMARY_ENDPOINT + quote(title)
    return safe_get_json(url)


def _news_api_search(query: str, language: str = "en") -> List[Dict]:
    """Optional news search; will be skipped if not configured."""
    endpoint = os.getenv("NEWS_API_ENDPOINT")
    api_key = os.getenv("NEWS_API_KEY")
    if not endpoint or not api_key:
        return []

    query_param = os.getenv("NEWS_API_QUERY_PARAM", "q")
    key_param = os.getenv("NEWS_API_KEY_PARAM", "apiKey")
    lang_param = os.getenv("NEWS_API_LANG_PARAM", "language")
    article_path = os.getenv("NEWS_API_ARTICLE_PATH", "articles")

    params = {
        query_param: query,
        key_param: api_key,
        lang_param: language,
    }

    data = safe_get_json(endpoint, params=params)
    if not data:
        return []

    raw_articles = data.get(article_path, [])
    articles: List[Dict] = []
    for a in raw_articles[:5]:
        src = a.get("source")
        if isinstance(src, dict):
            src_name = src.get("name")
        else:
            src_name = src
        articles.append(
            {
                "title": a.get("title"),
                "description": a.get("description") or "",
                "url": a.get("url"),
                "source": src_name or "News API",
                "published_at": a.get("publishedAt"),
            }
        )
    return articles


def _token_overlap_score(a: str, b: str) -> float:
    at = {t.lower() for t in a.split() if len(t) > 3}
    bt = {t.lower() for t in b.split() if len(t) > 3}
    if not at or not bt:
        return 0.0
    overlap = at & bt
    return max(0.0, min(len(overlap) / len(at), 1.0))


def verify_sources(
    claim: str,
    category: str,
    language: str = "en",
    features: Dict | None = None,
) -> List[Dict]:
    evidence: List[Dict] = []

    # 1) Wikipedia evidence
    wiki_hit = _wiki_search(claim, language=language)
    if wiki_hit:
        title = wiki_hit.get("title")
        snippet = wiki_hit.get("snippet", "")
        summary_data = _wiki_summary(title) if title else None

        url = None
        extract = ""
        if summary_data:
            extract = summary_data.get("extract", "") or ""
            content_urls = summary_data.get("content_urls") or {}
            url = (content_urls.get("desktop") or {}).get("page")

        text_for_overlap = extract or snippet
        match_score = _token_overlap_score(claim, text_for_overlap)
        reliability = 0.9
        confidence = 0.65 + 0.25 * match_score  # 0.65–0.9, slightly more optimistic

        evidence.append(
            {
                "source": title or "Wikipedia",
                "source_type": "encyclopedia",
                "summary": text_for_overlap or "No summary available.",
                "url": url,
                "reliability": reliability,
                "confidence": confidence,
                "match_score": match_score,
                "published_at": None,
            }
        )

    # 2) Optional news evidence
    for art in _news_api_search(claim, language=language):
        text = (art.get("title") or "") + " " + (art.get("description") or "")
        match_score = _token_overlap_score(claim, text)
        reliability = 0.75
        confidence = 0.6 + 0.25 * match_score

        evidence.append(
            {
                "source": art.get("source") or "News API",
                "source_type": "news",
                "summary": text.strip() or "No description available.",
                "url": art.get("url"),
                "reliability": reliability,
                "confidence": confidence,
                "match_score": match_score,
                "published_at": art.get("published_at"),
            }
        )

    # 3) Fallback heuristic
    if not evidence:
        risk_level = (features or {}).get("risk_level", "low")
        base_rel = 0.45 if risk_level == "high" else 0.55
        evidence.append(
            {
                "source": "Heuristic",
                "source_type": "heuristic",
                "summary": (
                    "No matching reference found in configured APIs. "
                    "This may be a new, highly local, or poorly phrased claim."
                ),
                "url": None,
                "reliability": base_rel,
                "confidence": 0.45,
                "match_score": 0.0,
                "published_at": None,
            }
        )

    return evidence
