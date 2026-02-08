from typing import List, Dict, Any, Optional
import os
import json
from google import genai  # type: ignore

def verify_claims(
    claims: List[Dict[str, Any]], 
    domain: str, 
    org_name: str, 
    mode: str = "external_snippets"
) -> Dict[str, Any]:
    """
    Verifies claims using Gemini with either Google Search Grounding or external snippets.
    
    Args:
        claims: List of claim dicts (e.g. {"claim_text": "..."})
        domain: The domain being analyzed
        org_name: The organization name
        mode: "grounding" (uses google_search tool) or "external_snippets" (uses provided context)
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    
    if not api_key:
        return {"verifications": []}

    client = genai.Client(api_key=api_key)
    
    # Prepare the claims for the prompt
    claims_text = "\n".join([f"- {c.get('claim_text', '')}" for c in claims if c.get('claim_text')])
    if not claims_text:
        return {"verifications": []}

    prompt = (
        f"Verify the following claims made by {org_name} ({domain}):\n\n"
        f"{claims_text}\n\n"
        "For each claim, determine if it is SUPPORTED, CONTRADICTED, or UNCLEAR based on public information.\n"
        "Return a JSON object with a 'verifications' list."
    )

    # Schema for verification result
    schema = {
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
                                    "url": {"type": "string"}
                                }
                            }
                        }
                    },
                    "required": ["claim_text", "verdict", "rationale"]
                }
            }
        }
    }

    config = {
        "temperature": 0.0,
        "response_mime_type": "application/json",
        "response_json_schema": schema,
    }

    # Enable grounding if requested
    if mode == "grounding":
        config["tools"] = [{"google_search": {}}]

    try:
        resp = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config
        )
        
        if resp.text:
            return json.loads(resp.text)
            
    except Exception as e:
        # Fail soft
        pass

    return {"verifications": []}
