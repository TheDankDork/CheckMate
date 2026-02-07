from __future__ import annotations

import csv
import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlsplit, urlunsplit

import requests
import tldextract

URLHAUS_CSV_URL = "https://urlhaus.abuse.ch/downloads/csv_online/"
CACHE_FILENAME = "threat_intel_cache.json"
REFRESH_INTERVAL_SECONDS = 6 * 60 * 60

logger = logging.getLogger(__name__)


@dataclass
class ThreatIntelCache:
    url_set: Set[str] = field(default_factory=set)
    domain_set: Set[str] = field(default_factory=set)
    last_updated: Optional[str] = None


def _normalize_url(url: str) -> Optional[str]:
    if not url:
        return None
    parts = urlsplit(url.strip())
    if not parts.scheme or not parts.netloc:
        return None
    normalized = urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            parts.path or "/",
            parts.query,
            "",
        )
    )
    return normalized


def _extract_registered_domain(url: str) -> Optional[str]:
    parts = urlsplit(url)
    if not parts.netloc:
        return None
    extracted = tldextract.extract(parts.netloc)
    if not extracted.suffix:
        return None
    return f"{extracted.domain}.{extracted.suffix}".lower()


def parse_urlhaus_csv(csv_text: str) -> Tuple[Set[str], Set[str]]:
    url_set: Set[str] = set()
    domain_set: Set[str] = set()
    reader = csv.reader(line for line in csv_text.splitlines() if line and not line.startswith("#"))
    for row in reader:
        if len(row) < 3:
            continue
        url = row[2].strip()
        normalized = _normalize_url(url)
        if not normalized:
            continue
        url_set.add(normalized)
        domain = _extract_registered_domain(normalized)
        if domain:
            domain_set.add(domain)
    return url_set, domain_set


def _cache_path() -> Path:
    return Path(__file__).resolve().parent / CACHE_FILENAME


def _load_cache_from_disk() -> ThreatIntelCache:
    path = _cache_path()
    if not path.exists():
        return ThreatIntelCache()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return ThreatIntelCache(
            url_set=set(data.get("url_set", [])),
            domain_set=set(data.get("domain_set", [])),
            last_updated=data.get("last_updated"),
        )
    except Exception as exc:
        logger.warning("Failed to load threat intel cache: %s", exc)
        return ThreatIntelCache()


def _save_cache_to_disk(cache: ThreatIntelCache) -> None:
    path = _cache_path()
    tmp_path = path.with_suffix(".tmp")
    payload = {
        "url_set": sorted(cache.url_set),
        "domain_set": sorted(cache.domain_set),
        "last_updated": cache.last_updated,
    }
    tmp_path.write_text(json.dumps(payload), encoding="utf-8")
    tmp_path.replace(path)


_cache_lock = threading.Lock()
_cache = _load_cache_from_disk()
_background_started = False


def refresh_cache() -> bool:
    try:
        response = requests.get(URLHAUS_CSV_URL, timeout=10)
        response.raise_for_status()
        url_set, domain_set = parse_urlhaus_csv(response.text)
        if not url_set:
            raise ValueError("URLhaus returned empty feed")
        new_cache = ThreatIntelCache(
            url_set=url_set,
            domain_set=domain_set,
            last_updated=datetime.now(timezone.utc).isoformat(),
        )
        with _cache_lock:
            global _cache
            _cache = new_cache
            _save_cache_to_disk(new_cache)
        return True
    except Exception as exc:
        logger.warning("Threat intel refresh failed: %s", exc)
        return False


def _background_refresh_loop() -> None:
    while True:
        time.sleep(REFRESH_INTERVAL_SECONDS)
        refresh_cache()


def start_background_refresh() -> None:
    global _background_started
    if _background_started:
        return
    if os.environ.get("CHECKMATE_DISABLE_THREAT_INTEL_BG") == "1":
        return
    thread = threading.Thread(target=_background_refresh_loop, daemon=True)
    thread.start()
    _background_started = True


start_background_refresh()


def match_url(url: str, cache: Optional[ThreatIntelCache] = None) -> Dict[str, object]:
    normalized = _normalize_url(url)
    if not normalized:
        return {
            "url_match": False,
            "domain_match": False,
            "provider_hits": [],
            "last_updated": None,
        }
    domain = _extract_registered_domain(normalized)
    with _cache_lock:
        active_cache = cache or _cache
        url_match = normalized in active_cache.url_set
        domain_match = bool(domain and domain in active_cache.domain_set)
        last_updated = active_cache.last_updated

    provider_hits: List[Dict[str, str]] = []
    if url_match:
        provider_hits.append(
            {
                "provider": "urlhaus",
                "match": "url",
                "risk": "HIGH",
                "value": normalized,
            }
        )
    if domain_match:
        provider_hits.append(
            {
                "provider": "urlhaus",
                "match": "domain",
                "risk": "MED",
                "value": domain or "",
            }
        )

    return {
        "url_match": url_match,
        "domain_match": domain_match,
        "provider_hits": provider_hits,
        "last_updated": last_updated,
    }
