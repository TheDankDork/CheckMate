# Updated render.py for CheckMate
from __future__ import annotations

from typing import Any, Dict, List

from checkmate.schemas import AnalysisResult, RiskItem, EvidenceItem

def render_output(result: AnalysisResult) -> Dict[str, Any]:
    output: Dict[str, Any] = {
        "status": result.status,
        "overall_score": result.overall_score,
        "subscores": result.subscores.dict() if result.subscores else None,
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
        "limitations": result.limitations,
        "debug": result.debug,
    }
    return output
