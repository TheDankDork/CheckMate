from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from google import genai  # type: ignore


def _get_client(api_key: str):
    return genai.Client(api_key=api_key)


def _verify_schema() -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "verifications": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "claim_text": {"type": "string"},
                        "verdict": {"type": "string", "enum": ["supported", "contradicted", "unclear"]},
                        "rationale": {"type": "string"},
                        "citations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "url": {"type": "string"},
                                },
                                "required": ["title", "url"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["claim_text", "verdict", "rationale", "citations"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["verifications"],
        "additionalProperties": False,
    }


def verify_claims(
    claims: List[Dict[str, Any]],
    domain: str,
    org_name: Optional[str] = None,
    mode: str = "external_snippets",
    snippets: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """
    Spec:
    - mode="grounding" if google_search tool usable, else "external_snippets"
    - grounding: call Gemini with google_search tool enabled and request JSON
    - external_snippets: accept snippets from backend, ask Gemini to label supported/contradicted/unclear

    MVP implementation:
    - grounding mode returns fail-soft empty unless your team confirms tool support.
    - external_snippets mode works if snippets are provided.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

    if not api_key or not claims:
        return {"verifications": []}

    schema = _verify_schema()

    # Keep request small: only verify top 3 claims
    claim_texts = [c.get("claim_text") or c.get("raw") or "" for c in claims][:3]
    claim_texts = [c for c in claim_texts if c.strip()]

    if not claim_texts:
        return {"verifications": []}

    org = org_name or ""
    client = _get_client(api_key)

    if mode == "grounding":
        # Many hackathon accounts may not have this enabled. Fail-soft.
        # If your team confirms support, we can implement tools config here.
        return {"verifications": []}

    # external_snippets mode
    snippets = snippets or []
    # Example snippet dict: {"title":"...", "url":"...", "text":"..."}
    snippet_payload = [{"title": s.get("title", ""), "url": s.get("url", ""), "text": s.get("text", "")} for s in snippets][:8]

    prompt = (
        "You are verifying claims using ONLY the provided snippets. Do not use prior knowledge.\n"
        "Return ONLY JSON matching the schema.\n"
        f"Domain: {domain}\n"
        f"Org name (if any): {org}\n"
        "Claims:\n"
        + json.dumps(claim_texts, ensure_ascii=False)
        + "\nSnippets:\n"
        + json.dumps(snippet_payload, ensure_ascii=False)
        + "\nTask: For each claim, output verdict supported/contradicted/unclear. "
          "Citations must be URLs from snippets (title+url)."
    )

    try:
        resp = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "temperature": 0.0,
                "response_mime_type": "application/json",
                "response_json_schema": schema,
            },
        )
        raw = getattr(resp, "text", "") or ""
        if not raw:
            return {"verifications": []}

        try:
            return json.loads(raw)
        except Exception:
            # retry once
            resp2 = client.models.generate_content(
                model=model,
                contents=prompt + "\nReturn strict JSON only.",
                config={
                    "temperature": 0.0,
                    "response_mime_type": "application/json",
                    "response_json_schema": schema,
                },
            )
            raw2 = getattr(resp2, "text", "") or ""
            return json.loads(raw2) if raw2 else {"verifications": []}

    except Exception:
        return {"verifications": []}

pass
