
"""Truth Evaluation Agent (truth-leaning, evidence-driven)."""

from __future__ import annotations

from typing import Dict, List


def _aggregate_evidence(evidence: List[Dict]) -> float:
    if not evidence:
        return 0.5

    total = 0.0
    weight_sum = 0.0
    for item in evidence:
        reliability = float(item.get("reliability", 0.5))
        confidence = float(item.get("confidence", 0.5))
        match_score = float(item.get("match_score", 0.0))

        support = confidence * (0.5 + 0.5 * match_score)
        weight = 0.4 + reliability
        total += support * weight
        weight_sum += weight

    return total / weight_sum if weight_sum else 0.5


def _has_strong_evidence(evidence: List[Dict]) -> bool:
    for item in evidence:
        reliability = float(item.get("reliability", 0.5))
        confidence = float(item.get("confidence", 0.5))
        match_score = float(item.get("match_score", 0.0))
        if reliability >= 0.8 and confidence >= 0.7 and match_score >= 0.3:
            return True
    return False


def _severity_penalty(severity: str, risk_level: str, subjectivity: float) -> float:
    severity = (severity or "normal").lower()
    risk_level = (risk_level or "low").lower()

    penalty = 0.0

    if severity == "high":
        penalty -= 0.06
    elif severity == "normal":
        penalty -= 0.03

    if risk_level == "high":
        penalty -= 0.04
    elif risk_level == "medium":
        penalty -= 0.02

    if subjectivity > 0.3:
        penalty -= 0.02
    elif subjectivity > 0.15:
        penalty -= 0.01

    return penalty


def _to_verdict(score: int) -> str:
    if score >= 80:
        return "Likely True"
    if score >= 60:
        return "Partially True / Needs Context"
    if score >= 40:
        return "Unclear / Unverified"
    return "Likely False or Misleading"


def evaluate_truth(
    claim: str,
    category: str,
    severity: str,
    evidence: List[Dict],
    analyzer_output: Dict,
) -> Dict:
    support_score = _aggregate_evidence(evidence)
    analyzer_conf = float(analyzer_output.get("confidence", 0.6))
    features = analyzer_output.get("features", {}) or {}
    risk_level = features.get("risk_level", "low")
    subjectivity = float(features.get("subjectivity", 0.0))

    strong_evidence = _has_strong_evidence(evidence)
    penalty = _severity_penalty(severity, risk_level, subjectivity)

    # Base from analyzer confidence (0.4–0.92) mapped to 55–92
    base_from_analyzer = 55 + (analyzer_conf - 0.4) * (37 / 0.52)

    # Evidence delta -18 .. +18
    evidence_delta = (support_score - 0.5) * 36

    raw = base_from_analyzer + evidence_delta + 100 * penalty

    # If strong evidence, don't let score be too low
    if strong_evidence and raw < 75:
        raw = 75 + (raw - 75) * 0.2

    truth_score = int(max(0, min(100, round(raw))))
    verdict = _to_verdict(truth_score)

    explanation = (
        f"Category: {category or 'other'}. "
        f"Analyzer confidence: {analyzer_conf:.2f}. "
        f"Evidence support: {support_score:.2f} "
        f"({'strong' if strong_evidence else 'weak/medium'} evidence). "
        f"Risk: {risk_level}, subjectivity: {subjectivity:.2f}. "
        f"Severity: {severity or 'normal'}."
    )

    return {
        "truth_score": truth_score,
        "verdict": verdict,
        "explanation": explanation,
        "meta": {
            "support_score": support_score,
            "analyzer_confidence": analyzer_conf,
            "severity_penalty": penalty,
            "risk_level": risk_level,
            "subjectivity": subjectivity,
            "strong_evidence": strong_evidence,
            "category": category,
        },
    }
