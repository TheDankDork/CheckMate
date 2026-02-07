from unittest.mock import patch

from checkmate.modules.gemini_page import analyze_page_with_gemini


def test_retry_once_on_invalid_json(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake")
    monkeypatch.setenv("GEMINI_MODEL", "fake-model")

    clean_text = "Hello world."

    calls = {"n": 0}

    def fake_call(prompt, schema, api_key, model):
        calls["n"] += 1
        if calls["n"] == 1:
            return "NOT JSON"
        # second call valid
        return """
        {
          "page_url":"https://a.com",
          "page_type":"home",
          "signals":{
            "writing_quality_0_1":0.5,
            "cohesion_0_1":0.5,
            "title_body_alignment_0_1":0.5,
            "marketing_heaviness_0_1":0.5,
            "source_traceability_0_1":0.5,
            "asks_sensitive_info":false,
            "payment_pressure":false
          },
          "numeric_claims":[],
          "risks":[]
        }
        """

    with patch("checkmate.modules.gemini_page._call_gemini_json", side_effect=fake_call):
        res = analyze_page_with_gemini(
            page_url="https://a.com",
            page_title=None,
            clean_text=clean_text,
            extracted_emails=[],
            extracted_phones=[],
            extracted_date=None,
            link_stats={},
        )

    assert res["page_url"] == "https://a.com"
    assert calls["n"] == 2
