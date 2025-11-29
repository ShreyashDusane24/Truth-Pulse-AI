
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, Dict

from models.claim import ClaimIn, ClaimOut
from agents.analyzer import analyze_claim
from agents.verifier import verify_sources
from agents.evaluator import evaluate_truth
from database.db import save_claim_result, get_trending_categories

app = FastAPI(
    title="TruthPulse AI Backend (Ultra Forgiving)",
    version="9.0.0",
    description=(
        "Multi-agent misinformation backend that is tolerant to different frontend payloads "
        "and leans on evidence to decide truth vs false."
    ),
)

# CORS wide open
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "app": "TruthPulse AI Backend",
        "status": "ok",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "message": "TruthPulse backend running",
        "version": "9.0.0",
    }


def _normalize_payload(raw: Dict[str, Any]) -> ClaimIn:
    """Accept many possible input shapes and convert to ClaimIn.

    Tries keys in this order for text:
    - text
    - claim
    - news
    - content
    - message
    """
    if not isinstance(raw, dict):
        raise HTTPException(status_code=400, detail="Request body must be a JSON object.")

    text = (
        raw.get("text")
        or raw.get("claim")
        or raw.get("news")
        or raw.get("content")
        or raw.get("message")
    )

    if not text or not isinstance(text, str) or len(text.strip()) < 5:
        raise HTTPException(status_code=400, detail="Provide a claim/news text with at least 5 characters.")

    severity = raw.get("severity") or raw.get("risk") or "normal"
    language = raw.get("language") or raw.get("lang") or "en"

    try:
        payload = ClaimIn(text=text, severity=severity, language=language)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")

    return payload


def _run_pipeline(payload: ClaimIn) -> ClaimOut:
    text = payload.text.strip()

    # 1) Analyzer
    analyzer_result = analyze_claim(text, language=payload.language)

    # 2) Evidence
    evidence_list = verify_sources(
        claim=text,
        category=analyzer_result["category"],
        language=payload.language,
        features=analyzer_result.get("features", {}),
    )

    # 3) Evaluator
    evaluation = evaluate_truth(
        claim=text,
        category=analyzer_result["category"],
        severity=payload.severity,
        evidence=evidence_list,
        analyzer_output=analyzer_result,
    )

    result = ClaimOut(
        claim=text,
        category=analyzer_result["category"],
        confidence=analyzer_result["confidence"],
        truth_score=evaluation["truth_score"],
        verdict=evaluation["verdict"],
        explanation=evaluation["explanation"],
        evidence=evidence_list,
        meta=evaluation["meta"],
    )

    # 4) Best-effort save
    try:
        save_claim_result(payload, result)
    except Exception:
        pass

    return result


@app.post("/api/analyze", response_model=ClaimOut)
async def analyze_endpoint(body: Dict[str, Any] = Body(...)):
    payload = _normalize_payload(body)
    return _run_pipeline(payload)


@app.post("/verify-claim", response_model=ClaimOut)
async def legacy_verify_claim(body: Dict[str, Any] = Body(...)):
    """Compatibility for older frontends hitting /verify-claim."""
    payload = _normalize_payload(body)
    return _run_pipeline(payload)


@app.get("/api/trends")
async def trends_endpoint():
    return get_trending_categories(limit=10)
