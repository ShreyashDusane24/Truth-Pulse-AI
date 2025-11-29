
"""NLP-ish analyzer (unchanged from previous tuned version)."""

from __future__ import annotations

import re
from typing import Dict, List, Tuple


BASIC_STOPWORDS = {
    "the", "is", "are", "am", "a", "an", "of", "and", "or", "to", "in",
    "on", "for", "with", "from", "by", "about", "as", "that", "this",
    "was", "were", "be", "been", "at", "it", "its", "into", "than",
}

CATEGORY_PATTERNS = {
    "politics": [
        "prime minister", "president", "election", "government", "parliament",
        "minister", "mla", "mp", "lok sabha", "rajya sabha", "policy", "bill",
    ],
    "health": [
        "covid", "coronavirus", "vaccine", "vaccination", "virus", "infection",
        "cancer", "hospital", "doctor", "symptom", "fever", "pandemic",
    ],
    "finance": [
        "stock market", "share market", "bitcoin", "crypto", "rupee",
        "dollar", "interest rate", "inflation", "budget", "loan", "gst",
    ],
    "technology": [
        "artificial intelligence", "ai", "machine learning", "robot",
        "iphone", "android", "laptop", "server", "data breach", "hacked",
    ],
}

SUBJECTIVE_WORDS = [
    "amazing", "shocking", "unbelievable", "fake", "real", "miracle",
    "worst", "best", "crazy", "insane", "exposed", "secret", "hidden",
]

RISKY_TERMS = [
    "kill", "dies", "dead", "cancer", "toxic", "ban", "explosion",
    "outbreak", "terrorist", "unsafe", "emergency",
]


def _normalize(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _basic_tokens(text: str) -> List[str]:
    return re.findall(r"[\w$%]+", text.lower())


def _remove_stopwords(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in BASIC_STOPWORDS]


def _bigrams(tokens: List[str]) -> List[Tuple[str, str]]:
    return list(zip(tokens, tokens[1:])) if len(tokens) > 1 else []


def _detect_category(tokens: List[str], bigrams_list: List[Tuple[str, str]]) -> str:
    joined_bigrams = {" ".join(bg) for bg in bigrams_list}
    joined_tokens = set(tokens)

    scores: Dict[str, int] = {}
    for cat, patterns in CATEGORY_PATTERNS.items():
        score = 0
        for p in patterns:
            if " " in p:
                if p in joined_bigrams:
                    score += 3
            else:
                if p in joined_tokens:
                    score += 1
        if score:
            scores[cat] = score

    if not scores:
        return "other"
    return max(scores.items(), key=lambda kv: kv[1])[0]


def analyze_claim(text: str, language: str = "en") -> Dict:
    norm = _normalize(text)
    raw_tokens = _basic_tokens(norm)
    tokens = _remove_stopwords(raw_tokens)
    bigrams_list = _bigrams(tokens)

    length_tokens = len(tokens)
    avg_token_len = sum(len(t) for t in tokens) / max(length_tokens, 1)
    exclamations = text.count("!")
    question_marks = text.count("?")
    has_numbers = any(re.search(r"\d", t) for t in tokens)

    subjective_hits = sum(1 for t in tokens if t in SUBJECTIVE_WORDS)
    subjectivity = subjective_hits / max(length_tokens, 1)

    risky_hits = sum(1 for t in tokens if t in RISKY_TERMS)
    if risky_hits >= 2:
        risk_level = "high"
    elif risky_hits == 1:
        risk_level = "medium"
    else:
        risk_level = "low"

    category = _detect_category(tokens, bigrams_list)

    base_conf = min(0.4 + 0.025 * min(length_tokens, 40), 0.92)
    noise_penalty = min(0.03 * exclamations + 0.02 * question_marks, 0.25)
    confidence = max(0.4, base_conf - noise_penalty)

    features: Dict = {
        "language": language,
        "length_tokens": length_tokens,
        "avg_token_len": round(avg_token_len, 2),
        "has_numbers": has_numbers,
        "exclamation_count": exclamations,
        "question_count": question_marks,
        "subjectivity": round(subjectivity, 3),
        "risk_level": risk_level,
    }

    return {
        "claim": text,
        "normalized": norm,
        "tokens": tokens,
        "bigrams": [" ".join(bg) for bg in bigrams_list],
        "category": category,
        "confidence": confidence,
        "features": features,
    }
