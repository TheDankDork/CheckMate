from flask import Flask, request, jsonify
from .schemas import AnalyzeRequest, AnalysisResult
from .pipeline import analyze_url
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

    try:
        result = analyze_url(req.url)
        # If optional HTML format is requested, we would handle it here
        # format = request.args.get('format')
        # if format == 'html': return render_html(result)
        
        return jsonify(result.model_dump())
    except Exception as e:
        logging.error(f"Analysis failed: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
