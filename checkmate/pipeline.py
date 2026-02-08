# Updated pipeline.py based on full CheckMate project context
from __future__ import annotations

import logging
from typing import List
from urllib.parse import urlparse

from checkmate.schemas import AnalysisResult, RiskItem, PageSummary
from checkmate.safe_fetch import safe_fetch
from checkmate.modules.extraction import extract_page_features, truncate_clean_text
from checkmate.modules.domain_info import get_domain_info
from checkmate.modules.security_check import check_security
from checkmate.modules.threat_intel import match_url
from checkmate.modules.gemini_page import analyze_page_with_gemini, classify_website_type_with_gemini

logger = logging.getLogger(__name__)


SAFE_PAGE_LIMIT = 5


def run_pipeline(url: str) -> AnalysisResult:
    result = AnalysisResult(status="ok", url=url)

    # Safe Fetch
    content, status_code, content_type, final_url = safe_fetch(url)
    if not content:
        result.status = "na"
        result.missing_pages.append(url)
        return result

    result.status = "ok"
    result.pages_analyzed.append(
        PageSummary(
            url=final_url or url,
            status_code=status_code,
            title=None,
            extracted_date=None
        )
    )

    # Feature Extraction
    page_features = extract_page_features(content, base_url=url)
    truncated_text = truncate_clean_text(
        page_features.get("clean_text", ""),
        page_features.get("title"),
        page_features.get("headings", [])
    )

    # Classify website type first (for score weighting)
    text_snippet = (page_features.get("clean_text", "") or "")[:4000]
    website_type = classify_website_type_with_gemini(
        page_url=url,
        page_title=page_features.get("title"),
        text_snippet=text_snippet,
    )
    # Normalize to a known type (classifier can return unexpected value on parse failure)
    if website_type not in ("functional", "statistical", "news_historical", "company"):
        website_type = "news_historical"
    result.website_type = website_type
    result.debug["website_type"] = website_type

    # Gemini Analysis
    gemini_result = analyze_page_with_gemini(
        page_url=url,
        page_title=page_features.get("title"),
        clean_text=truncated_text,
        extracted_emails=page_features.get("emails", []),
        extracted_phones=page_features.get("phones", []),
        extracted_date=None,
        link_stats={
            "internal_links": len(page_features.get("links_internal", [])),
            "external_links": len(page_features.get("links_external", []))
        },
    )

    result.debug["gemini"] = gemini_result
    result.limitations.extend(gemini_result.get("limitations", []))

    # Attach Gemini page type and risks
    result.risks.extend([
    RiskItem(
        severity=r["severity"],
        code=r["code"],
        title=r["title"],
        evidence=[
            {
                "message": snippet,
                "snippet": snippet,
            } for snippet in r.get("evidence_snippets", [])
        ],
    )
    for r in gemini_result.get("risks", [])
    ])

    # Domain Info
    domain_info = get_domain_info(url)
    result.domain_info = domain_info

    # Security
    security_info = check_security(url)
    result.security_info = security_info

    # Threat Intel
    result.threat_intel = match_url(url)

    return result
