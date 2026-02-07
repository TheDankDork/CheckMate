from __future__ import annotations

import time
from typing import List, Dict, Any

from .modules.domain_info import get_domain_info
from .modules.extraction import extract_page_features, truncate_clean_text
from .modules.security_check import check_security
from .modules.threat_intel import match_url
from .safe_fetch import safe_fetch
from .schemas import AnalysisResult, PageSummary, RiskItem, EvidenceItem, Subscores

def analyze_url(url: str) -> AnalysisResult:
    start_time = time.time()
    content, status_code, content_type, final_url = safe_fetch(url, timeout=10)

    if not content or not status_code or not final_url:
        return AnalysisResult(
            status="na",
            overall_score=None,
            subscores=None,
            risks=[],
            missing_pages=[],
            pages_analyzed=[],
            domain_info={},
            security_info={},
            threat_intel={},
            limitations=["fetch_failed"],
            debug={"timings_ms": {"fetch": int((time.time() - start_time) * 1000)}},
        )

    features = extract_page_features(content, final_url)
    clean_text = truncate_clean_text(
        features.get("clean_text", ""),
        title=features.get("title"),
        headings=features.get("headings", []),
        max_chars=12000,
    )

    pages_analyzed = [
        PageSummary(
            url=final_url,
            status_code=status_code,
            title=features.get("title"),
            extracted_date=None,
        )
    ]

    domain_info = get_domain_info(final_url)
    security_info = check_security(final_url)
    threat_intel = match_url(final_url)

    # Missing policy pages detection (simple URL keyword check)
    policy_keywords = {
        "contact": ["contact", "support", "help"],
        "about": ["about", "company", "team"],
        "privacy": ["privacy", "privacy-policy"],
        "terms": ["terms", "terms-of-service", "conditions"],
    }
    found_policy = {key: False for key in policy_keywords}
    for link in features.get("links_internal", []):
        link_lower = link.lower()
        for key, tokens in policy_keywords.items():
            if any(token in link_lower for token in tokens):
                found_policy[key] = True

    missing_pages = [key for key, found in found_policy.items() if not found]

    risks: List[RiskItem] = []
    risk_penalty = 0

    if threat_intel.get("url_match"):
        risks.append(
            RiskItem(
                severity="HIGH",
                code="THREAT_INTEL_URL_MATCH",
                title="URL appears in threat intelligence feed",
                evidence=[EvidenceItem(message="URLhaus match", url=final_url)],
            )
        )
        risk_penalty += 50
    elif threat_intel.get("domain_match"):
        risks.append(
            RiskItem(
                severity="MED",
                code="THREAT_INTEL_DOMAIN_MATCH",
                title="Domain appears in threat intelligence feed",
                evidence=[EvidenceItem(message="URLhaus domain match", url=final_url)],
            )
        )
        risk_penalty += 25

    keyword_hits: Dict[str, Any] = features.get("keyword_hits", {})
    if any(keyword_hits.values()):
        risks.append(
            RiskItem(
                severity="HIGH",
                code="SENSITIVE_INFO_REQUEST",
                title="Page content suggests sensitive information requests",
                evidence=[EvidenceItem(message="Sensitive keyword hit", key="keyword_hits", value=keyword_hits)],
            )
        )
        risk_penalty += 40

    if missing_pages:
        if len(missing_pages) >= 2:
            severity = "HIGH"
            penalty = 30
        else:
            severity = "MED"
            penalty = 15
        risks.append(
            RiskItem(
                severity=severity,
                code="MISSING_POLICY_PAGES",
                title="Missing common policy pages",
                evidence=[EvidenceItem(message="Missing pages", value=missing_pages)],
            )
        )
        risk_penalty += penalty

    if not security_info.get("uses_https") or not security_info.get("cert_valid"):
        risks.append(
            RiskItem(
                severity="HIGH",
                code="TLS_SECURITY",
                title="HTTPS or certificate validation issues detected",
                evidence=[EvidenceItem(message="TLS check failed", value=security_info)],
            )
        )
        risk_penalty += 35

    risk_score = max(0, 100 - risk_penalty)
    formatting_score = 60 if clean_text else 0
    relevance_score = 50 if clean_text else 0
    sources_score = 50 if clean_text else 0

    overall_score = int(
        round(
            (risk_score * 0.40)
            + (sources_score * 0.35)
            + (formatting_score * 0.15)
            + (relevance_score * 0.10)
        )
    )

    caps_applied = []
    if threat_intel.get("url_match"):
        overall_score = min(overall_score, 20)
        caps_applied.append("CAP_APPLIED_THREAT_URL")
    if any(keyword_hits.values()):
        overall_score = min(overall_score, 20)
        caps_applied.append("CAP_APPLIED_SENSITIVE_INFO")
    if not security_info.get("uses_https") or not security_info.get("cert_valid"):
        overall_score = min(overall_score, 35)
        caps_applied.append("CAP_APPLIED_TLS")

    for cap in caps_applied:
        risks.append(
            RiskItem(
                severity="HIGH",
                code=cap,
                title="Score cap applied",
                evidence=[],
            )
        )

    subscores = Subscores(
        formatting=formatting_score,
        relevance=relevance_score,
        sources=sources_score,
        risk=risk_score,
    )

    limitations = ["gemini_not_configured"]

    return AnalysisResult(
        status="ok",
        overall_score=0,
        overall_score=overall_score,
        subscores=subscores,
        risks=risks,
        missing_pages=missing_pages,
        pages_analyzed=pages_analyzed,
        domain_info=domain_info,
        security_info=security_info,
        threat_intel=threat_intel,
        limitations=limitations,
        debug={"timings_ms": {"total": int((time.time() - start_time) * 1000)}},
    )

