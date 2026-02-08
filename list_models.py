import os
from dotenv import load_dotenv
load_dotenv()
from google import genai

api_key = os.getenv("GEMINI_API_KEY", "").strip()
if not api_key:
    print("Set GEMINI_API_KEY in .env (see .env.example)")
    exit(1)
client = genai.Client(api_key=api_key)

print("Listing models...")
try:
    for m in client.models.list(config={"page_size": 10}):
        print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
