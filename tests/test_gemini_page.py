import json
from unittest.mock import patch

from checkmate.modules.gemini_page import analyze_page_with_gemini


class DummyResp:
    def __init__(self, text):
        self.text = text


def test_analyze_page_parses_json_and_validates_evidence(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake")
    monkeypatch.setenv("GEMINI_MODEL", "fake-model")

    clean_text = "Hello world. Contact us at support@example.com. We are #1."

    # Gemini returns evidence snippet that is NOT in text -> should be downgraded to UNCERTAIN and removed
    fake_output = {
        "page_url": "https://x.com",
        "page_type": "home",
        "signals": {
            "writing_quality_0_1": 0.7,
            "cohesion_0_1": 0.8,
            "title_body_alignment_0_1": 0.6,
            "marketing_heaviness_0_1": 0.7,
            "source_traceability_0_1": 0.2,
            "asks_sensitive_info": False,
            "payment_pressure": False,
        },
        "numeric_claims": [
            {
                "claim_text": "We are #1",
                "value": "#1",
                "has_citation_in_text": False,
                "citation_snippet": "",
                "evidence_snippet": "We are #1.",
            }
        ],
        "risks": [
            {
                "severity": "HIGH",
                "code": "TEST_RISK",
                "title": "Some risk",
                "evidence_snippets": ["THIS DOES NOT EXIST"],
                "notes": "short",
            }
        ],
    }

    def fake_call(prompt, schema, api_key, model):
        return json.dumps(fake_output)

    with patch("checkmate.modules.gemini_page._call_gemini_json", side_effect=fake_call):
        res = analyze_page_with_gemini(
            page_url="https://x.com",
            page_title="X",
            clean_text=clean_text,
            extracted_emails=[],
            extracted_phones=[],
            extracted_date=None,
            link_stats={"internal": 1, "external": 2},
        )

    # numeric claim evidence is in clean_text -> remains
    assert res["numeric_claims"][0]["evidence_snippet"] == "We are #1."

    # risk evidence NOT in clean_text -> severity downgraded + evidence removed
    assert res["risks"][0]["severity"] == "UNCERTAIN"
    assert res["risks"][0]["evidence_snippets"] == []
