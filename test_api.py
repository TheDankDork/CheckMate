import requests
import json
import sys

def test_analyze(url):
    api_url = "http://127.0.0.1:5000/analyze"
    headers = {"Content-Type": "application/json"}
    payload = {"url": url}

    print(f"\nSending request to {api_url}...")
    print(f"Payload: {json.dumps(payload)}")

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            print("\nResponse JSON:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")

    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the server. Make sure 'python -m checkmate.app' is running.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = input("Enter URL to analyze (default: https://example.com): ").strip() or "https://example.com"
    
    test_analyze(target_url)
