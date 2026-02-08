# Updated app.py for CheckMate to match full pipeline and schema integration
from __future__ import annotations

import os
from flask import Flask, request, jsonify
from checkmate.pipeline import run_pipeline
from checkmate.scoring import compute_scores
from checkmate.render import render_result
from checkmate.schemas import AnalyzeRequest

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        parsed = AnalyzeRequest(**data)
        result = run_pipeline(parsed.url)

        if result.status == "ok":
            result = compute_scores(result)

        rendered = render_result(result)
        return jsonify(rendered)

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
