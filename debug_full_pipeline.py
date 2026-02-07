import os
import sys
import requests
import json
from dotenv import load_dotenv

# Force UTF-8 for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load env vars
load_dotenv()

# Import modules
from checkmate.modules.extraction import extract_page_features, truncate_clean_text
from checkmate.modules.domain_info import get_domain_info
from checkmate.modules.security_check import check_security
from checkmate.modules.threat_intel import match_url
from checkmate.modules.gemini_page import analyze_page_with_gemini

def test_full_pipeline(url):
    print(f"\n{'='*60}")
    print(f"FULL PIPELINE TEST: {url}")
    print(f"{'='*60}")

    # 1. Fetch Page (Simulating Pipeline Fetch)
    print("\n[1] Fetching Page...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 CheckMate/1.0'}
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"  Status: {resp.status_code}")
        html_content = resp.text
    except Exception as e:
        print(f"  ! Fetch failed: {e}")
        return

    # 2. Member 1: Extraction
    print("\n[2] Running Member 1 (Extraction)...")
    features = extract_page_features(html_content, url)
    print(f"  Title: {features['title']}")
    print(f"  Clean Text Length: {len(features['clean_text'])} chars")
    print(f"  Emails: {features['emails']}")
    print(f"  Phones: {features['phones']}")
    
    # Truncate for Gemini
    truncated_text = truncate_clean_text(features['clean_text'], features['title'], features['headings'])
    print(f"  Truncated Text Length: {len(truncated_text)} chars")

    # 3. Member 3: Domain/Security/Threat
    print("\n[3] Running Member 3 (Security/Domain/Threat)...")
    
    # Domain
    dom = get_domain_info(url)
    print(f"  Domain: {dom.get('registered_domain')} (Created: {dom.get('creation_date')})")
    
    # Security
    sec = check_security(url)
    print(f"  HTTPS: {sec.get('uses_https')}, Valid Cert: {sec.get('cert_valid')}")
    
    # Threat
    threat = match_url(url)
    print(f"  Threat Match: URL={threat.get('url_match')}, Domain={threat.get('domain_match')}")

    # 4. Member 2: Gemini Analysis
    print("\n[4] Running Member 2 (Gemini Analysis)...")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("  ! SKIPPING: GEMINI_API_KEY not found in environment.")
    else:
        print("  Calling Gemini (this may take a few seconds)...")
        gemini_result = analyze_page_with_gemini(
            page_url=url,
            page_title=features['title'],
            clean_text=truncated_text,
            extracted_emails=features['emails'],
            extracted_phones=features['phones'],
            extracted_date=None, # We didn't implement htmldate yet in extraction, passing None
            link_stats={"internal": len(features['links_internal']), "external": len(features['links_external'])}
        )
        
        print("\n  --- Gemini Result ---")
        print(f"  Page Type: {gemini_result.get('page_type')}")
        print(f"  Signals: {json.dumps(gemini_result.get('signals'), indent=2)}")
        print(f"  Risks ({len(gemini_result.get('risks', []))}):")
        for r in gemini_result.get('risks', []):
            print(f"    - [{r.get('severity')}] {r.get('title')}")
            print(f"      Evidence: {r.get('evidence_snippets')}")

if __name__ == "__main__":
    target_url = "https://www.cbc.ca/sports/olympics/winter/snowboard/canadian-snowboarder-meryeta-odine-to-miss-olympics-with-fractured-ankle-9.7078884"
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    
    test_full_pipeline(target_url)
