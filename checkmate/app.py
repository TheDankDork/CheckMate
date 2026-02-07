from flask import Flask, request, jsonify
from .models import AnalyzeRequest, AnalysisResult, RiskItem, ModuleResult
from .crawl import crawl_site
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"ok": True})

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        req = AnalyzeRequest(**data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    url = req.url
    
    # 1. Crawl
    try:
        extraction_result = crawl_site(url)
    except Exception as e:
        logging.error(f"Crawl failed: {e}")
        return jsonify(AnalysisResult(
            status="error", 
            overall_score=None,
            debug={"error": str(e)}
        ).model_dump()), 500

    # Check if we got any pages
    if not extraction_result.primary_page or extraction_result.primary_page.errors:
        # If primary page failed, return NA
        return jsonify(AnalysisResult(
            status="na",
            overall_score=None,
            debug={"message": "Could not fetch primary page"}
        ).model_dump())

    # 2. Run Modules (Placeholders)
    # Member 1: Extraction + Formatting + Relevance
    # Member 2: Fact + Sources
    # Member 3: Domain + Security + Threat
    
    # 3. Compile Risks & Score (Placeholder)
    # For now, just return a stub success response
    
    result = AnalysisResult(
        status="ok",
        overall_score=0, # Placeholder
        subscores={
            "formatting": 0,
            "relevance": 0,
            "sources": 0,
            "risk": 0
        },
        risks=[],
        missing_pages=list(set(["contact", "about", "privacy", "terms"]) - set(extraction_result.key_pages.keys())),
        pages_analyzed=[
            {
                "url": p.url, 
                "status_code": p.status_code, 
                "title": p.title
            } for p in extraction_result.all_pages
        ],
        domain_info=None,
        security_info=None,
        threat_intel=None,
        debug={
            "pages_crawled": extraction_result.stats.get("pages_crawled", 0)
        }
    )

    return jsonify(result.model_dump())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
