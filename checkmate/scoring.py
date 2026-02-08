# Updated scoring.py to match CheckMate pipeline structure
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from checkmate.schemas import AnalysisResult, Subscores

# (formatting, relevance, sources, risk) — must sum to 1.0
# Spec: Functional = no sources, equal weight to other 3. Statistical = relevance+sources doubled.
# News = regular. Company = formatting +15%, 5% taken from each of other 3.
WEIGHT_BY_TYPE: Dict[str, Tuple[float, float, float, float]] = {
    # 1. Functional: do not consider sources; distribute weighting equally to the other three
    "functional": (1.0 / 3, 1.0 / 3, 0.0, 1.0 / 3),
    # 2. Statistical: relevance and sources doubled, other two reduced; relevance also uses recency (in _score_relevance)
    "statistical": (0.1, 0.4, 0.4, 0.1),
    # 3. News / historical: regular weighting
    "news_historical": (0.3, 0.3, 0.2, 0.2),
    # 4. Company: sources not weighted much; formatting +15%, 5% taken from each of the other 3
    "company": (0.45, 0.30, 0.10, 0.15),
}
DEFAULT_WEIGHTS = WEIGHT_BY_TYPE["news_historical"]


def _weights_for_type(website_type: Optional[str]) -> Tuple[float, float, float, float]:
    if website_type and website_type in WEIGHT_BY_TYPE:
        return WEIGHT_BY_TYPE[website_type]
    return DEFAULT_WEIGHTS


def compute_score(result: AnalysisResult) -> AnalysisResult:
    if result.status != "ok":
        result.status = "na"
        result.overall_score = None
        return result

    debug: Dict[str, Any] = {}

    # Format Score
    formatting = _score_formatting(result, debug)

    # Relevance Score (for statistical type, blend in information_recency)
    relevance = _score_relevance(result, debug)

    # Source Score
    sources = _score_sources(result, debug)

    # Risk Score (higher risk = lower score)
    risk_score = _score_risk(result, debug)

    # Type-specific weights
    w_f, w_r, w_s, w_risk = _weights_for_type(result.website_type)
    debug["website_type"] = result.website_type or "news_historical"
    debug["weights"] = {"formatting": w_f, "relevance": w_r, "sources": w_s, "risk": w_risk}

    score = int(w_f * formatting + w_r * relevance + w_s * sources + w_risk * risk_score)
    score = max(0, min(100, score))

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
    # For statistical sites, factor in how up-to-date the information is
    if result.website_type == "statistical":
        recency = gemini.get("information_recency_0_1", 0.5)
        relevance = 0.6 * relevance + 0.4 * recency
    relevance_score = int(relevance * 100)
    relevance_score = max(0, min(100, relevance_score))
    debug["relevance"] = {
        "marketing": marketing,
        "score": relevance_score,
    }
    if result.website_type == "statistical":
        debug["relevance"]["information_recency_0_1"] = gemini.get("information_recency_0_1", 0.5)
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

def _is_content_safety_risk(result: AnalysisResult, risk: Any) -> bool:
    if result.website_type != "news_historical":
        return False
    code = (getattr(risk, "code", "") or "").strip().upper()
    title = (getattr(risk, "title", "") or "").strip().lower()
    if code == "CONTENT_SAFETY":
        return True
    topic_keywords = (
        "content safety",
        "topic safety",
        "dangerous topic",
        "dangerous content",
        "unsafe content",
        "extreme weather",
        "extreme cold",
        "extreme heat",
        "storm",
        "hurricane",
        "tornado",
        "earthquake",
        "wildfire",
        "flood",
        "disaster",
    )
    return any(keyword in title for keyword in topic_keywords)

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
