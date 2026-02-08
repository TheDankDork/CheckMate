# Updated app.py for CheckMate to match full pipeline and schema integration
from __future__ import annotations

import os
from flask import Flask, request, jsonify, send_from_directory
from checkmate.pipeline import run_pipeline
from checkmate.scoring import compute_score
from checkmate.render import render_output
from checkmate.schemas import AnalyzeRequest

app = Flask(__name__)

ALLOWED_ORIGINS = {
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
}


@app.after_request
def add_cors_headers(response):
    """Allow frontend (different port) to call this API."""
    origin = getattr(request, "origin", None)
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
    else:
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
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
        parsed = AnalyzeRequest(**data)
        result = run_pipeline(parsed.url)

        if result.status == "ok":
            result = compute_score(result)

        rendered = render_output(result)
        return jsonify(rendered)

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
