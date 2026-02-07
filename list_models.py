import os
from google import genai

api_key = "AIzaSyCmV7O6nCvvQ1-7joHoHjZLeNKaAMJv8jc"
client = genai.Client(api_key=api_key)

print("Listing models...")
try:
    for m in client.models.list(config={"page_size": 10}):
        print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
