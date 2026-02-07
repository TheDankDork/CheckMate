import requests
import sys

# Force UTF-8 encoding for stdout to handle special characters on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from checkmate.modules.extraction import extract_page_features

def test_url(url):
    print(f"\n{'='*50}")
    print(f"Testing URL: {url}")
    print(f"{'='*50}")
    
    try:
        # User-Agent header to avoid being blocked by some sites
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print("Warning: Non-200 status code")
        
        features = extract_page_features(response.text, url)

        print("\n--- Extracted Features ---")
        print(f"Title: {features['title']}")
        print(f"Headings ({len(features['headings'])} found):")
        for h in features['headings'][:5]:
            print(f"  - {h}")
        if len(features['headings']) > 5: print("  ... (more)")
            
        print(f"\nEmails: {features['emails']}")
        print(f"Phones: {features['phones']}")
        
        print(f"\nInternal Links ({len(features['links_internal'])}):")
        for l in features['links_internal'][:3]:
            print(f"  - {l}")
            
        print(f"\nExternal Links ({len(features['links_external'])}):")
        for l in features['links_external'][:3]:
            print(f"  - {l}")
            
        print(f"\nKeyword Hits: {features['keyword_hits']}")
        print(f"\nClean Text Snippet (first 500 chars):\n{'-'*20}\n{features['clean_text'][:500]}\n{'-'*20}")
        
    except Exception as e:
        print(f"Error fetching/processing {url}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter a URL to test (e.g., https://www.wikipedia.org): ").strip()
        if not url:
            url = "https://www.wikipedia.org"
            
    test_url(url)
