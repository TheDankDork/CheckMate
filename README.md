# CheckMate 
**AI-assisted website credibility analysis**

CheckMate is a Flask-based backend (plus a React/Vite frontend) that analyzes a single webpage URL and returns a **trust score (0–100)** with structured explanations of **risks, signals, and limitations**. It answers:

> *How trustworthy does this website appear based on its content and technical signals?*

Rather than relying on one heuristic, CheckMate combines **Gemini analysis**, **deterministic checks**, and **threat intelligence** into one report.

---

## What CheckMate Scans For

- **Transparency & structure**  
  Core site signals derived from the main page content, headings, and metadata.

- **Content quality**  
  Writing clarity, cohesion, and title/body alignment from Gemini’s structured analysis.

- **Claims & sources**  
  Numeric claims plus whether evidence appears in the text, with strict substring checks.

- **Security signals**  
  HTTPS usage, certificate validity, and sensitive-info pressure from content analysis.

- **Domain & reputation**  
  WHOIS-based domain metadata and URLhaus threat-intel matches (URL or registered domain).

---

## AI Infrastructure (High Level)

CheckMate uses **Google Gemini** (via the `google-genai` SDK) as its core analysis engine to interpret page content and extract structured credibility signals.

Design constraints:
- **1–2 AI calls per analysis** (website type classification + page analysis)
- Each call receives **≤12,000 characters** of cleaned text
- AI outputs **strict structured JSON**
- Any cited evidence must be an **exact substring** of the analyzed page

If evidence cannot be verified, the system downgrades confidence and records a limitation.

---

## Scoring & Safety

- Final scores are **deterministic**, not generated directly by AI
- Weighted subscores combine writing quality, relevance, source traceability, and risk
- Weighting adjusts by **website type** (functional, statistical, news/historical, company)

The system enforces strict safety controls:
- SSRF protection and blocked IP ranges
- Redirect and size limits (HTML/text only, capped responses)
- TLS validation for HTTPS certificate checks

If a site cannot be safely analyzed, the system returns `"status": "na"`.

---

## Output

Each analysis returns:
- Final trust score (0–100)
- Website type and subscores
- Structured risks with evidence snippets
- Pages analyzed (currently the single page URL)
- Domain, security, and threat-intel summaries
- Explicit limitations and debug details

Results are **JSON-first** via the API response.

## API

**`POST /analyze`** expects JSON: `{ "url": "https://example.com" }`.

Possible statuses:
- `ok`: analysis completed (scores + subscores included)
- `na`: analysis could not be completed safely
- `error`: server error (check logs)

The backend also serves `/` for a static `index.html` (if present) and uses CORS to allow local dev and Vercel frontends (`FRONTEND_URL`).

## Environment Variables

- `GEMINI_API_KEY` (required for Gemini analysis)
- `GEMINI_MODEL` (optional, default `gemini-2.5-flash`)
- `FRONTEND_URL` (optional, comma-separated allowed origins)
- `CHECKMATE_DISABLE_THREAT_INTEL_BG=1` (disable background URLhaus refresh)
- `CHECKMATE_DEBUG_CLASSIFY=1` (log website-type classification)

## Run the website locally

**Teammates:** see **[RUN-LOCALLY.md](RUN-LOCALLY.md)** for step-by-step instructions to run the backend and frontend on your machine and open the app in your browser.

**Quick version:** Two terminals — (1) `pip install -r requirements.txt` then `python app.py`; (2) `cd frontend/checkmate && npm install && npm run dev` — then open **http://localhost:5173**. You need a `.env` with `GEMINI_API_KEY` (copy from `.env.example`).
