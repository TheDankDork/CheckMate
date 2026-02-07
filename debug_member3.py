import sys
import logging
from checkmate.modules.domain_info import get_domain_info
from checkmate.modules.security_check import check_security
from checkmate.modules.threat_intel import ThreatIntelCache
from checkmate.modules.typosquat import check_typosquat

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_member3_modules(url: str):
    print(f"\n{'='*60}")
    print(f"Testing Member 3 Modules for URL: {url}")
    print(f"{'='*60}")

    # 1. Domain Info
    print("\n[1] Testing Domain Info...")
    try:
        domain_data = get_domain_info(url)
        print(f"  - Registered Domain: {domain_data.get('registered_domain')}")
        print(f"  - Creation Date: {domain_data.get('creation_date')}")
        print(f"  - Registrar: {domain_data.get('registrar')}")
        if domain_data.get('whois_error'):
            print(f"  - WHOIS Error: {domain_data.get('whois_error')}")
    except Exception as e:
        print(f"  ! Error: {e}")

    # 2. Security Check
    print("\n[2] Testing Security Check...")
    try:
        sec_data = check_security(url)
        print(f"  - Uses HTTPS: {sec_data.get('uses_https')}")
        print(f"  - Cert Valid: {sec_data.get('cert_valid')}")
        print(f"  - Issuer: {sec_data.get('cert_issuer')}")
        print(f"  - Expiry: {sec_data.get('cert_expiry')}")
        if sec_data.get('error'):
            print(f"  ! Error: {sec_data.get('error')}")
    except Exception as e:
        print(f"  ! Error: {e}")

    # 3. Threat Intel
    print("\n[3] Testing Threat Intel (URLhaus)...")
    try:
        # Initialize cache (might take a moment to load/download on first run)
        ti_cache = ThreatIntelCache()
        ti_result = ti_cache.match_url(url)
        print(f"  - URL Match: {ti_result.get('url_match')}")
        print(f"  - Domain Match: {ti_result.get('domain_match')}")
        print(f"  - Provider Hits: {ti_result.get('provider_hits')}")
        print(f"  - Last Updated: {ti_result.get('last_updated')}")
    except Exception as e:
        print(f"  ! Error: {e}")

    # 4. Typosquatting
    print("\n[4] Testing Typosquatting...")
    try:
        # For this test, we need to extract the domain first
        import tldextract
        ext = tldextract.extract(url)
        domain = f"{ext.domain}.{ext.suffix}"
        
        # We need a "claimed brand" to compare against. 
        # In the real pipeline, Gemini extracts this. 
        # For the testbench, we'll ask the user or guess.
        claimed_brand = input(f"  Enter a brand name to check typosquatting against (default: {ext.domain}): ").strip()
        if not claimed_brand:
            claimed_brand = ext.domain
            
        # We assume the module takes (registered_domain, claimed_brand_domain)
        # We construct a fake "claimed domain" just for testing logic
        claimed_domain = f"{claimed_brand}.com" 
        
        print(f"  Checking '{domain}' against claimed '{claimed_domain}'...")
        
        ts_result = check_typosquat(domain, claimed_domain)
        print(f"  - Suspicious: {ts_result.get('is_suspicious')}")
        print(f"  - Closest Match: {ts_result.get('closest_match')}")
        print(f"  - Distance: {ts_result.get('distance')}")
        print(f"  - Similarity: {ts_result.get('similarity')}")
        
    except Exception as e:
        print(f"  ! Error: {e}")

if __name__ == "__main__":
    target_url = "https://google.com"
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        user_input = input("Enter URL to test (default: https://google.com): ").strip()
        if user_input:
            target_url = user_input
            
    test_member3_modules(target_url)
