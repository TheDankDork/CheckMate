# Updated app.py for CheckMate to match full pipeline and schema integration
from __future__ import annotations

import logging
import os
from pathlib import Path

# Load .env from project root (where app.py lives) so the key is found no matter where you run from
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

from flask import Flask, request, jsonify, send_from_directory
from pydantic import ValidationError
from checkmate.pipeline import run_pipeline
from checkmate.scoring import compute_score
from checkmate.render import render_output
from checkmate.schemas import AnalyzeRequest

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)
app = Flask(__name__)

# CORS: local dev + production frontend (set FRONTEND_URL on Render to your Vercel URL)
_ALLOWED = os.environ.get("FRONTEND_URL", "").strip().split(",") if os.environ.get("FRONTEND_URL") else []
ALLOWED_ORIGINS = {
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    *(_ALLOWED if _ALLOWED else []),
}


def _cors_origin(request_origin: str | None) -> str:
    if request_origin and request_origin in ALLOWED_ORIGINS:
        return request_origin
    if request_origin and request_origin.rstrip("/").endswith(".vercel.app"):
        return request_origin
    return "http://localhost:5173"


@app.after_request
def add_cors_headers(response):
    """Allow frontend (different port or Vercel) to call this API."""
    origin = getattr(request, "origin", None)
    response.headers["Access-Control-Allow-Origin"] = _cors_origin(origin)
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/", methods=["GET"])
def home():
    return send_from_directory(".", "index.html")


@app.route("/analyze", methods=["POST", "OPTIONS"])
def analyze():
    if request.method == "OPTIONS":
        return "", 204
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"status": "error", "error": "Request body must be JSON with a 'url' field."}), 400
        parsed = AnalyzeRequest(**data)
        result = run_pipeline(parsed.url)

        if result.status == "ok":
            result = compute_score(result)

        rendered = render_output(result)
        return jsonify(rendered)

    except ValidationError:
        return jsonify({"status": "error", "error": "Invalid request: send JSON with a 'url' field."}), 400
    except Exception as e:
        logger.exception("Analyze failed: %s", e)
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        logger.warning("GEMINI_API_KEY is not set. Create .env from .env.example and add your key.")
    else:
        logger.info("GEMINI_API_KEY is set (len=%d).", len(key))
    app.run(host="0.0.0.0", port=port)
