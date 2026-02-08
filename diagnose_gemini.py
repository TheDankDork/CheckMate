#!/usr/bin/env python3
"""
Run this to see the exact Gemini error when page analysis fails.
Usage: python diagnose_gemini.py [url]
  If url is omitted, uses a minimal inline test (no fetch).
"""
from __future__ import annotations

import os
import sys
import traceback

# Load .env before importing checkmate
from dotenv import load_dotenv
load_dotenv()

def main():
    api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    model = (os.getenv("GEMINI_MODEL") or "gemini-2.0-flash").strip()
    print("Config:")
    print(f"  GEMINI_API_KEY: {'(set, len=%d)' % len(api_key) if api_key else '(NOT SET)'}")
    print(f"  GEMINI_MODEL: {model!r}")
    if not api_key:
        print("\nERROR: Set GEMINI_API_KEY in .env (see .env.example)")
        return 1

    url = (sys.argv[1:] or ["https://example.com"])[0]
    print(f"\nAnalyzing URL: {url}")

    try:
        from checkmate.pipeline import run_pipeline
        result = run_pipeline(url)
        limitations = getattr(result, "limitations", []) or []
        debug_gemini = (getattr(result, "debug", None) or {}).get("gemini") or {}
        if limitations:
            print("\nLimitations reported:")
            for lim in limitations:
                print(f"  - {lim}")
        if debug_gemini.get("limitations"):
            print("Gemini result limitations:", debug_gemini["limitations"])
        if result.status == "ok" and result.overall_score is not None:
            print(f"\nSuccess. Score: {result.overall_score}")
        else:
            print(f"\nStatus: {result.status}")
        return 0
    except Exception as e:
        print("\n" + "=" * 60)
        print("EXCEPTION (this is what we need to fix):")
        print("=" * 60)
        traceback.print_exc()
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
