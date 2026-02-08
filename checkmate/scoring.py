# Updated scoring.py to match CheckMate pipeline structure
from __future__ import annotations

from typing import Any, Dict, Optional

from checkmate.schemas import AnalysisResult, Subscores

def compute_score(result: AnalysisResult) -> AnalysisResult:
    if result.status != "ok":
        result.status = "na"
        result.overall_score = None
        return result

    debug: Dict[str, Any] = {}

    # Format Score
    formatting = _score_formatting(result, debug)

    # Relevance Score
    relevance = _score_relevance(result, debug)

    # Source Score
    sources = _score_sources(result, debug)

    # Risk Score (higher risk = lower score)
    risk_score = _score_risk(result, debug)

    # Weighted total (max 100)
    # You can change weights later as needed
    score = int(0.3 * formatting + 0.3 * relevance + 0.2 * sources + 0.2 * risk_score)

    result.subscores = Subscores(
        formatting=formatting,
        relevance=relevance,
        sources=sources,
        risk=risk_score,
    )
    result.overall_score = score
    result.debug["scoring"] = debug
    return result

def _score_formatting(result: AnalysisResult, debug: Dict[str, Any]) -> int:
    gemini = result.debug.get("gemini", {}).get("signals", {})
    writing = gemini.get("writing_quality_0_1", 0.5)
    cohesion = gemini.get("cohesion_0_1", 0.5)
    title_align = gemini.get("title_body_alignment_0_1", 0.5)
    
    avg = (writing + cohesion + title_align) / 3
    formatting_score = int(avg * 100)
    debug["formatting"] = {
        "writing": writing,
        "cohesion": cohesion,
        "title_align": title_align,
        "score": formatting_score,
    }
    return formatting_score

def _score_relevance(result: AnalysisResult, debug: Dict[str, Any]) -> int:
    gemini = result.debug.get("gemini", {}).get("signals", {})
    marketing = gemini.get("marketing_heaviness_0_1", 0.5)
    relevance = 1.0 - marketing
    relevance_score = int(relevance * 100)
    debug["relevance"] = {
        "marketing": marketing,
        "score": relevance_score,
    }
    return relevance_score

def _score_sources(result: AnalysisResult, debug: Dict[str, Any]) -> int:
    gemini = result.debug.get("gemini", {}).get("signals", {})
    traceability = gemini.get("source_traceability_0_1", 0.5)
    score = int(traceability * 100)
    debug["sources"] = {
        "traceability": traceability,
        "score": score,
    }
    return score

def _score_risk(result: AnalysisResult, debug: Dict[str, Any]) -> int:
    # Risk score goes down with HIGH/MED risks and presence of payment/sensitive info
    gemini = result.debug.get("gemini", {}).get("signals", {})
    asks_sensitive = gemini.get("asks_sensitive_info", False)
    payment_pressure = gemini.get("payment_pressure", False)

    score = 100
    deductions = []
    for risk in result.risks:
        if risk.severity == "HIGH":
            score -= 30
            deductions.append("HIGH")
        elif risk.severity == "MED":
            score -= 15
            deductions.append("MED")

    if asks_sensitive:
        score -= 10
        deductions.append("asks_sensitive_info")
    if payment_pressure:
        score -= 10
        deductions.append("payment_pressure")

    score = max(0, min(100, score))
    debug["risk"] = {
        "deductions": deductions,
        "score": score,
    }
    return score
