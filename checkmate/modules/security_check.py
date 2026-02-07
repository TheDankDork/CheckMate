from __future__ import annotations

import socket
import ssl
from typing import Dict, Optional
from urllib.parse import urlparse


def _format_issuer(issuer) -> Optional[str]:
    if not issuer:
        return None
    parts = []
    for rdn in issuer:
        for key, value in rdn:
            parts.append(f"{key}={value}")
    return ", ".join(parts) if parts else None


def _get_certificate_info(hostname: str, port: int = 443) -> Dict[str, Optional[str]]:
    context = ssl.create_default_context()
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    with socket.create_connection((hostname, port), timeout=10) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
    return {
        "issuer": _format_issuer(cert.get("issuer")),
        "expiry": cert.get("notAfter"),
    }


def check_security(url: str) -> Dict[str, Optional[str]]:
    parsed = urlparse(url)
    uses_https = parsed.scheme.lower() == "https"
    if not uses_https:
        return {
            "uses_https": False,
            "cert_valid": False,
            "cert_issuer": None,
            "cert_expiry": None,
            "error": "not_https",
        }

    hostname = parsed.hostname
    if not hostname:
        return {
            "uses_https": True,
            "cert_valid": False,
            "cert_issuer": None,
            "cert_expiry": None,
            "error": "missing_hostname",
        }

    try:
        cert_info = _get_certificate_info(hostname, parsed.port or 443)
        return {
            "uses_https": True,
            "cert_valid": True,
            "cert_issuer": cert_info.get("issuer"),
            "cert_expiry": cert_info.get("expiry"),
            "error": None,
        }
    except Exception as exc:
        return {
            "uses_https": True,
            "cert_valid": False,
            "cert_issuer": None,
            "cert_expiry": None,
            "error": str(exc),
        }
