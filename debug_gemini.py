import os
import sys
import json
from checkmate.modules.gemini_page import analyze_page_with_gemini

# Force UTF-8 for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_gemini_module():
    print(f"\n{'='*60}")
    print("Testing Member 2 (Gemini Module)")
    print(f"{'='*60}")

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("Set GEMINI_API_KEY in .env (see .env.example)")
        sys.exit(1)

    # Mock Data (simulating what Extraction module would provide)
    page_url = "https://example.com/fake-scam"
    page_title = "URGENT: Verify Your Account Now!"
    clean_text = (
        "URGENT: Verify Your Account Now! "
        "Dear Customer, we have detected unusual activity on your account. "
        "Please click the link below to verify your identity immediately or your account will be suspended. "
        "We require your Social Security Number and Credit Card details for verification. "
        "This is a limited time notice. Act now! "
        "Copyright 2023 Secure Bank."
    )
    extracted_emails = ["support@secure-bank-verify.com"]
    extracted_phones = []
    extracted_date = "2023-10-27"
    link_stats = {"internal": 2, "external": 5}

    print("\n[Input Data]")
    print(f"  URL: {page_url}")
    print(f"  Title: {page_title}")
    print(f"  Text Snippet: {clean_text[:100]}...")

    print("\n[Calling Gemini]...")
    try:
        result = analyze_page_with_gemini(
            page_url=page_url,
            page_title=page_title,
            clean_text=clean_text,
            extracted_emails=extracted_emails,
            extracted_phones=extracted_phones,
            extracted_date=extracted_date,
            link_stats=link_stats
        )

        print("\n[Result]")
        print(json.dumps(result, indent=2))
        
        # Validation Checks
        print("\n[Validation]")
        if result.get("page_type") == "unknown":
             print("  [WARN] Page type is unknown (might be expected for this fake text)")
        
        signals = result.get("signals", {})
        if signals.get("asks_sensitive_info"):
            print("  [PASS] Correctly detected sensitive info request.")
        else:
            print("  [FAIL] Failed to detect sensitive info request.")

        if signals.get("payment_pressure"):
            print("  [PASS] Correctly detected pressure.")
        else:
            print("  [FAIL] Failed to detect pressure.")
            
        risks = result.get("risks", [])
        if risks:
            print(f"  [PASS] Generated {len(risks)} risks.")
        else:
            print("  [WARN] No risks generated.")

    except Exception as e:
        print(f"\n[ERROR] Gemini call failed: {e}")

if __name__ == "__main__":
    test_gemini_module()
