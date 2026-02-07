from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import tldextract
import whois


def _normalize_registered_domain(value: str) -> Optional[str]:
    if not value:
        return None
    parsed = urlparse(value)
    host = parsed.netloc or parsed.path
    extracted = tldextract.extract(host)
    if not extracted.suffix:
        return None
    return f"{extracted.domain}.{extracted.suffix}".lower()


def _coerce_date(value: Any) -> Optional[str]:
    if isinstance(value, list):
        for item in value:
            parsed = _coerce_date(item)
            if parsed:
                return parsed
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return None


def get_domain_info(url_or_domain: str) -> Dict[str, Optional[str]]:
    registered_domain = _normalize_registered_domain(url_or_domain)
    creation_date = None
    registrar = None
    whois_error = None

    if not registered_domain:
        return {
            "registered_domain": None,
            "creation_date": None,
            "registrar": None,
            "whois_error": "unable_to_parse_domain",
        }

    try:
        result = whois.whois(registered_domain)
        creation_date = _coerce_date(getattr(result, "creation_date", None))
        registrar = getattr(result, "registrar", None)
    except Exception as exc:
        whois_error = str(exc)

    return {
        "registered_domain": registered_domain,
        "creation_date": creation_date,
        "registrar": registrar,
        "whois_error": whois_error,
    }
