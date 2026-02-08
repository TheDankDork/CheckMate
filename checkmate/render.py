# Updated render.py for CheckMate
from __future__ import annotations

from typing import Any, Dict, List

from checkmate.schemas import AnalysisResult, RiskItem, EvidenceItem

def render_output(result: AnalysisResult) -> Dict[str, Any]:
    # Always send a website_type (backend may be old and not set it; fall back to debug or default)
    website_type = result.website_type or result.debug.get("website_type") or "news_historical"
    if website_type not in ("functional", "statistical", "news_historical", "company"):
        website_type = "news_historical"
    output: Dict[str, Any] = {
        "status": result.status,
        "overall_score": result.overall_score,
        "website_type": website_type,
        "subscores": result.subscores.model_dump() if result.subscores else None,
        "risks": [
            {
                "severity": r.severity,
                "code": r.code,
                "title": r.title,
                "evidence": [
                    {
                        "message": e.message,
                        "url": e.url,
                        "snippet": e.snippet,
                        "key": e.key,
                        "value": e.value,
                    }
                    for e in r.evidence
                ],
            }
            for r in result.risks
            if "gemini page analysis failed" not in (r.title or "").lower()
            and (r.code or "").upper() != "GEMINI_FAILED"
        ],
        "missing_pages": result.missing_pages,
        "pages_analyzed": [
            {
                "url": page.url,
                "status_code": page.status_code,
                "title": page.title,
                "extracted_date": page.extracted_date,
            }
            for page in result.pages_analyzed
        ],
        "domain_info": result.domain_info,
        "security_info": result.security_info,
        "threat_intel": result.threat_intel,
        "limitations": [
            "Page analysis could not be completed (API error)." if (lim and "Gemini page analysis failed" in lim) else lim
            for lim in (result.limitations or [])
        ],
        "debug": result.debug,
    }
    return output
