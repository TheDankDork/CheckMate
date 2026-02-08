# CheckMate 🧠🔍  
**AI-assisted website credibility analysis**

CheckMate is a backend service that analyzes a website and returns a **single trust score (0–100)** with structured explanations of **risks, red flags, and limitations**. It’s designed to help answer:

> *How trustworthy does this website appear based on its content and technical signals?*

Rather than relying on one heuristic, CheckMate combines **AI analysis**, **deterministic checks**, and **threat intelligence** into a single report.

---

## What CheckMate Scans For

- **Transparency & structure**  
  Presence of key pages (About, Contact, Privacy, Terms). Missing multiple policy pages triggers strong penalties.

- **Content quality**  
  Writing clarity, formatting consistency, relevance, and signs of low-effort or manipulative text.

- **Claims & sources**  
  Detection of numerical claims and whether they appear meaningfully supported or contextualized.

- **Security signals**  
  HTTPS usage, certificate validity, and requests for sensitive information (passwords, SSNs, credit cards).

- **Domain & reputation**  
  Domain age, typosquatting patterns, and known malicious URLs via cached threat intelligence.

---

## AI Infrastructure (High Level)

CheckMate uses **Google Gemini** as its core analysis engine to interpret page content and extract structured credibility signals.

Design constraints:
- Up to **5 AI calls per analysis**
- Each call receives **≤12,000 characters** of cleaned text
- AI outputs **strict structured JSON**
- Any cited evidence must be an **exact substring** of the analyzed page

If evidence cannot be verified, the system downgrades confidence and records a limitation.

---

## Scoring & Safety

- Final scores are **deterministic**, not generated directly by AI  
- Fixed weights combine AI signals with hard technical checks  
- Serious risks apply **score caps** (e.g. malicious URLs, sensitive data requests, missing HTTPS)

The system enforces strict safety controls:
- SSRF protection
- Crawl depth and page limits
- Timeouts, size limits, and content-type allowlists

If a site cannot be safely analyzed, the system returns `"status": "na"`.

---

## Output

Each analysis returns:
- Final trust score (0–100)
- Subscores and structured risks with evidence
- Pages analyzed and missing policy pages
- Domain, security, and threat-intel summaries
- Explicit limitations

Results are **JSON-first**, with an optional lightweight HTML report.

---

## Run the website locally

**Teammates:** see **[RUN-LOCALLY.md](RUN-LOCALLY.md)** for step-by-step instructions to run the backend and frontend on your machine and open the app in your browser.

**Quick version:** Two terminals — (1) `pip install -r requirements.txt` then `python app.py`; (2) `cd frontend/checkmate && npm install && npm run dev` — then open **http://localhost:5173**. You need a `.env` with `GEMINI_API_KEY` (copy from `.env.example`).

## Host the website (Render + Vercel)

**Step-by-step:** see **[HOST-STEP-BY-STEP.md](HOST-STEP-BY-STEP.md)** to put the API on Render and the frontend on Vercel so the app is live on the internet.

---

**CheckMate surfaces signals, not verdicts — helping users and systems make better decisions about online content.**
