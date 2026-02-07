# PRD (Backend-First) — CheckMate

## 1) Product summary
CheckMate evaluates the legitimacy of a website (people/company/data represented by the site).

**Input:** a website URL
**Output:** an overall legitimacy score (0–100, where 100 = more legitimate) OR N/A, plus sub-scores and explainable evidence (risk flags, missing info, and why the score happened).

## 2) Hard constraints (from your answers)
*   **Priority:** backend end-to-end pipeline first (due 8:00pm).
*   **Demo:** tomorrow 9:00am.
*   **Output format:** JSON-first; JSON + HTML report if time allows.
*   **Crawl scope:** analyze homepage + key pages, because “analyze all” may not fit time.
*   **Crawl limits:** `max_pages=10`, `max_depth=2`, `timeout_per_page=10s`.
*   **Score direction:** 100 = more legitimate.
*   **Missing policy pages rule:** if missing ≥2 of {Contact, About, Privacy, Terms} → hard penalty; if missing 1 → medium penalty.
*   **Threat intel:** maintain local cache, refresh every 6 hours.
*   **Risk reporting:** significant risks must be flagged; medium risks may be flagged or marked uncertain.
*   **LLM choice:** Gemini API.

## 3) Goals (MVP)
By 8:00pm, you can run:
*   `POST /analyze` with a URL → returns a stable JSON response containing:
    *   `overall_score` (0–100) or null with `status="na"`
    *   `subscores`: formatting, relevance, sources, risk
    *   `risks[]` with severities + evidence
    *   `missing_pages[]`
    *   `pages_analyzed[]` summary
    *   `domain_info` + `security_info` + `threat_intel` results
*   Basic SSRF protection + safe fetching.
*   Basic HTTPS/cert validity signal.
*   Basic extraction + heuristics scoring.
*   Threat intel check using at least one public dataset/API (recommended: URLhaus).

If time allows (demo polish):
*   `GET /report/<analysis_id>` or `POST /analyze?format=html` → simple HTML report.

## 4) Non-goals (for hackathon scope control)
*   Full web-scale crawling
*   Perfect fact-checking against the whole internet
*   Full CSS rendering / screenshot-based UI checks
*   Training a brand-new ML model (unless you already have one ready)

## 5) User stories
1.  “I paste a link and get a clear legitimacy score + reasons.”
2.  “I can see major red flags fast (missing contact info, suspicious requests for SSN/CVV, etc.).”
3.  “I can view evidence and which pages were checked.”

## 6) System architecture (backend)
**Stack:** Python + Flask

**Core modules (aligned to 4 team members):**
*   **Member 1:** Data extraction + formatting/grammar + relevance/cohesion
*   **Member 2:** Fact extraction + source credibility checks
*   **Member 3:** Domain background + security/encryption + threat intel + typosquatting
*   **Member 4:** Compile flags + compute score + output JSON/HTML + orchestration

**Recommended repo layout**

```powershell
checkmate/
  app.py
  models.py
  pipeline.py
  safe_fetch.py
  crawl.py
  scoring.py
  render.py                # optional HTML
  modules/
    extraction.py          # Member 1
    formatting.py          # Member 1
    relevance.py           # Member 1
    fact_extract.py        # Member 2
    source_verify.py       # Member 2
    domain_info.py         # Member 3
    security_check.py      # Member 3
    threat_intel.py        # Member 3
    typosquat.py           # Member 3
    risk_compile.py        # Member 4
tests/
  ...
requirements.txt
data/
  tranco_top10k.txt
  threat_cache.json        # generated
```

## 7) Safe fetching + SSRF protection (must-have)
Because you fetch user-supplied URLs, SSRF protection is mandatory (OWASP SSRF guidance).

**Rules:**
*   Allow only `http://` and `https://`.
*   DNS resolve hostname → block if IP is:
    *   loopback, private RFC1918, link-local, multicast, reserved
    *   common cloud metadata endpoints (e.g., 169.254.169.254)
*   Limit redirects (e.g., max 3) and re-check SSRF rules after each redirect.
*   Enforce:
    *   timeout = 10 seconds per request
    *   max response size (e.g., 2MB) to prevent huge downloads
    *   allowlist content types: HTML/text (skip binaries)

**N/A policy (recommended “best” approach):**
Return `status="na"` (`overall_score = null`) when:
*   URL is invalid / unsupported scheme
*   blocked by SSRF rules
*   cannot fetch ANY HTML/text page (timeouts, DNS failure, SSL failures, etc.)
*   content is non-text (e.g., PDF/image only) and you chose not to parse it

Otherwise, return `status="ok"` even if some pages fail—include warnings in evidence.

(References: OWASP SSRF Top 10 & prevention cheat sheet:
[https://owasp.org/Top10/2021/A10_2021-Server-Side_Request_Forgery_(SSRF)/](https://owasp.org/Top10/2021/A10_2021-Server-Side_Request_Forgery_(SSRF)/)
[https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html))

## 8) Crawl policy (MVP)
**Target pages**
Always attempt:
*   Homepage (input URL)
*   Key pages discovered via internal links:
    *   Contact, About, Privacy Policy, Terms & Conditions

**Limits (your chosen values)**
*   `max_pages = 10`
*   `max_depth = 2`
*   `timeout_per_page = 10s`

**Link-check policy**
Because of time: only “light” link validation:
*   sample up to 20 extracted links; do HEAD/GET with timeout

## 9) Signals to extract (shared)
From each fetched page:
*   text, title, headings, meta tags
*   internal/external links
*   emails and phone numbers (regex + phonenumbers)
*   keywords for sensitive info / payment:
    *   credit card, CVV, SSN, social security, password, etc.
*   grammar errors count (LanguageTool)
*   date signals (htmldate)

## 10) Scoring model (MVP)
You output:
*   `formatting_score` (0–100)
*   `relevance_score` (0–100)
*   `sources_score` (0–100)
*   `risk_score` (0–100) (higher = safer/less risk)

**Weights (recommended default)**
*   risk: 40%
*   sources/credibility: 35%
*   formatting: 15%
*   relevance: 10%

**Caps / hard rules (safety overrides)**
Apply after weighted average:
*   Threat intel exact URL match → cap overall at 20
*   Non-HTTPS or invalid cert → cap overall at 35
*   Sensitive info request detected (SSN/CVV/password patterns) → cap overall at 20
*   Missing policy pages:
    *   missing ≥2 of (Contact/About/Privacy/Terms) → strong penalty (and risk HIGH)
    *   missing 1 → medium penalty (risk MED)

**Evidence requirement**
Every major deduction must provide:
*   what signal triggered it
*   where it was found (URL, snippet)
*   impact on score (or cap reason)

## 11) Gemini API usage (where it helps most)
Because you chose Gemini, use it where heuristics are weakest:
*   Scam-likeness reasoning from extracted text snippets (NOT full crawl)
*   Summarize “Key Risks / Warnings” in plain English
*   Detect “strong similarity to known scam patterns” based on:
    *   red-flag phrases
    *   missing identity info
    *   request for sensitive details
    *   unnatural claims

**Important:** Gemini should not be required for core pipeline to run. If Gemini fails/timeouts, return results using heuristics + evidence.

## 12) Threat intel dataset (existing datasets)
You asked if there’s an existing dataset—yes:
*   **URLhaus (abuse.ch)** — malware URL dataset + community API
    *   [https://urlhaus.abuse.ch/api/](https://urlhaus.abuse.ch/api/)
    *   [https://urlhaus.abuse.ch/feeds/](https://urlhaus.abuse.ch/feeds/)
*   **PhishTank** — phishing URL clearinghouse
    *   [https://www.phishtank.com/](https://www.phishtank.com/)

**MVP:** implement URLhaus first (easiest), keep architecture pluggable to add PhishTank if time.

## 13) API contract (Flask)
**POST /analyze**
Request JSON:
```json
{ "url": "https://example.com" }
```

Response JSON (shape example):
```json
{
  "status": "ok",
  "overall_score": 72,
  "subscores": {
    "formatting": 80,
    "relevance": 70,
    "sources": 65,
    "risk": 75
  },
  "risks": [
    {
      "severity": "MED",
      "code": "MISSING_PRIVACY",
      "title": "Privacy Policy missing",
      "score_impact": -8,
      "evidence": [{ "message": "No privacy policy page found after checking key links." }]
    }
  ],
  "missing_pages": ["privacy"],
  "pages_analyzed": [
    { "url": "https://example.com", "status_code": 200, "title": "Home" }
  ],
  "domain_info": { "registered_domain": "example.com", "creation_date": "2001-01-01" },
  "security_info": { "uses_https": true, "cert_valid": true },
  "threat_intel": { "url_match": false, "domain_match": false, "provider": "urlhaus", "last_updated": "..." },
  "debug": { "timings_ms": { "fetch": 1200, "llm": 900 } }
}
```

**GET /health**
Returns `{ "ok": true }`

**Optional: HTML**
*   `POST /analyze?format=html` returns HTML report (same underlying JSON).

## 14) Team ownership (your mapping)
*   **Member #1:** data extraction + formatting/grammar + relevance/cohesion
*   **Member #2:** fact extraction + verification of facts/sources
*   **Member #3:** domain background + security/encryption
*   **Member #4:** compile flags + calculate score + display output

## 15) Acceptance checklist (MVP)
*   ✅ SSRF blocks localhost/private IPs
*   ✅ Works on at least 2 real websites and 1 local “sketchy” fixture HTML
*   ✅ Returns JSON in < ~30s total worst case (10 pages * 10s is theoretical max; implement early exits)
*   ✅ Evidence included for key penalties/caps
*   ✅ Threat intel cache exists + refresh interval is 6h (can be “refresh on demand” for hackathon, but must store last_updated)

---

## COPY/PASTE AI PROMPTS (Gemini) — more detailed

### Prompt 0 (Leader / Member 4 first): Generate shared skeleton + models + safe_fetch
**Use this FIRST so everyone codes against the same contract.**

```text
You are a senior backend engineer. Build the backend skeleton for a hackathon project called CheckMate.

Goal: Input a website URL, output JSON that scores legitimacy (0–100, 100=more legit) plus evidence. JSON-first. Optional HTML later.

HARD CONSTRAINTS:
- Python 3.11+
- Flask
- Crawl policy: analyze homepage + key pages (Contact/About/Privacy/Terms)
- Limits: max_pages=10, max_depth=2, timeout_per_page=10s
- Must include SSRF protection (block localhost/private/link-local/multicast/reserved; re-check after redirects)
- requests MUST use timeout=10 and verify=True
- Return N/A as: {status:"na", overall_score:null} when URL invalid/blocked/zero pages fetched.
- Must produce evidence items everywhere.

DELIVERABLES (code files):
1) checkmate/models.py
   - Use Pydantic v2 (preferred) OR dataclasses. Define stable schemas:
     - AnalyzeRequest(url: str)
     - EvidenceItem(key: str|None, message: str, url: str|None, snippet: str|None, value: any|None, severity: "HIGH"|"MED"|"LOW"|None)
     - PageArtifact(url, final_url, status_code, content_type, html, text, title, headings[], meta{}, links_internal[], links_external[], fetched_at, errors[])
     - ExtractionResult(primary_page, key_pages{contact/about/privacy/terms}, all_pages[], stats{})
     - ModuleResult(score: int 0-100, signals[], evidence[])
     - RiskItem(severity, code, title, score_impact:int, evidence[])
     - AnalysisResult(status:"ok"|"na"|"error", overall_score:int|None, subscores{}, risks[], missing_pages[], pages_analyzed[], domain_info{}, security_info{}, threat_intel{}, debug{})
   - Provide .model_dump() usage and helper functions to produce JSON.

2) checkmate/safe_fetch.py
   - Implement safe_fetch(url)->PageArtifact
   - SSRF guard:
     - allow only http/https
     - resolve DNS; block private/loopback/link-local/etc.
     - block 169.254.169.254 explicitly
     - limit redirects to 3, re-check IP after redirect
   - Enforce timeout=10, verify=True, max bytes 2MB, allow only text/html or text/*.
   - Return errors in PageArtifact.errors rather than crashing.

3) checkmate/crawl.py
   - BFS crawl with max_depth=2 and max_pages=10
   - Start at input URL
   - Discover internal links only for crawling
   - Specifically try to find key pages by anchor text or URL contains:
     contact, about, privacy, terms, conditions
   - Output ExtractionResult with primary_page + key_pages + all_pages + stats.

4) checkmate/app.py
   - Flask app with:
     - GET /health
     - POST /analyze (JSON)
     - optional ?format=html pass-through (can return JSON for now)

5) tests/
   - Unit tests for SSRF block (localhost, 127.0.0.1, 10.0.0.0/8, 169.254.169.254)
   - Unit test for safe_fetch timeout handling (mock requests)
   - Unit test for crawl respecting max_pages/max_depth

Also output requirements.txt.

Do NOT implement the scoring modules yet beyond placeholders; just return empty ModuleResults and a stub AnalysisResult so the pipeline can run end-to-end.
```

### Prompt 1 (Member #1): Extraction + Formatting/Grammar + Relevance/Cohesion
```text
You are Member #1 implementing:
- Data extraction
- Formatting/Grammar scoring
- Relevance/Cohesion scoring

You MUST follow the existing Pydantic models in checkmate/models.py exactly.

Implement files:
- checkmate/modules/extraction.py
  - Function: enrich_page_artifact(page: PageArtifact) -> PageArtifact
  - Use BeautifulSoup4 to populate:
    - text (visible text; remove scripts/styles/nav if easy)
    - title
    - headings list (h1-h3)
    - meta dict (description, og:title, etc. if present)
    - links_internal and links_external (absolute URLs)
  - Keep it robust to broken HTML and empty pages.

- checkmate/modules/formatting.py
  - Use language_tool_python to compute grammar/spelling error count on the page text.
  - Compute a formatting score 0-100:
    - Start at 100
    - Subtract points based on errors per 100 words (normalize).
    - Add small penalties for structural weirdness:
      - missing title
      - heading hierarchy jump (h1 -> h4 etc.)
      - excessive inline styles / <font> tags count heuristic
  - Output ModuleResult(score, signals, evidence). Evidence MUST include:
    - word_count
    - grammar_errors
    - errors_per_100_words
    - title_present boolean

- checkmate/modules/relevance.py
  - Compute relevance/cohesion score 0-100 using heuristics (no ML):
    - title/headings keyword overlap with body text (simple token overlap)
    - detect clickbait mismatch if overlap very low
    - marketing-vs-factual heuristic: ratio of factual/contact keywords (address/phone/email/privacy/terms/team) vs heavy marketing keywords (best, #1, amazing, buy now, limited time, etc.)
    - use htmldate to extract publication/update date if available and record evidence; do not heavily penalize unless obviously stale or contradictory
  - Output ModuleResult with evidence:
    - title_heading_overlap_ratio
    - marketing_ratio
    - extracted_date (if any)

Add tests:
- 3 HTML fixtures:
  1) normal legit-looking
  2) empty/minimal
  3) clickbait title but unrelated text
- Verify scores are in 0-100 and evidence keys exist.

Update requirements.txt with needed libs.

Keep runtime fast and avoid extra network calls.
```

### Prompt 2 (Member #2): Fact Extraction + Source Credibility
```text
You are Member #2 implementing:
- Fact extraction (numeric claims)
- Verification of facts and sources (MVP: traceability & source accessibility)

Follow checkmate/models.py exactly. Implement:

- checkmate/modules/fact_extract.py
  - From PageArtifact.text, extract numeric claims using regex:
    - years (19xx/20xx)
    - percentages (e.g., 12%, 12.5 percent)
    - money ($1,234, €99, "USD 100M")
    - large counts (1,000; 2 million)
  - For each claim, store:
    - type, value, unit, context_sentence (or 200-char window), confidence
  - Detect "according to" / "source:" / "reported by" patterns in nearby text and attach a source hint (domain or nearby link if available).

- checkmate/modules/source_verify.py
  - For claims with a URL source hint:
    - use checkmate/safe_fetch.py (do NOT call requests directly)
    - attempt HEAD/GET quickly (timeout already enforced)
    - mark source accessible/unreachable and record status code
  - If claim says "according to" but no source link/org name found: mark as unsupported (negative signal)

- Output a ModuleResult for sources_score:
  - 0-100 where higher means more verifiable
  - Evidence must include:
    - claims_total
    - claims_with_sources
    - sources_accessible
    - unsupported_claims
    - accessible_ratio

Testing:
- Provide text fixture with multiple numeric claims:
  - some with links
  - some "according to" with no link
- Mock safe_fetch to simulate accessible/unreachable sources and verify scoring changes.

Do NOT require external search APIs in MVP.
If you want a future search provider, create an interface but keep default as no-op.
```

### Prompt 3 (Member #3): Domain Background + Security + Threat Intel + Typosquatting
```text
You are Member #3 implementing:
- Domain background checks (WHOIS)
- Security/encryption checks (HTTPS + cert validity)
- Threat intel (local cache, refresh every 6 hours)
- Typosquatting check using Top 10k baseline

Follow checkmate/models.py exactly.

Implement:
- checkmate/modules/domain_info.py
  - Use tldextract to parse registered_domain, subdomain, suffix
  - Use python-whois to fetch domain creation_date and registrar (robust to None/list)
  - Do not crash if WHOIS fails; record evidence.

- checkmate/modules/security_check.py
  - uses_https = (url scheme == https)
  - cert_valid:
     - attempt safe_fetch on https; if SSL error happens, cert_valid=false and record error evidence
  - Note: HTTPS should not give big positive points; only penalize if missing/invalid.

- checkmate/modules/threat_intel.py
  - Implement ThreatIntelCache that stores:
    - url_set
    - domain_set
    - last_updated timestamp
  - Refresh every 6 hours (can be on startup + background thread, or refresh-on-demand if older than 6h)
  - Use URLhaus as MVP:
    - download from URLhaus feeds or API dataset
    - parse into URL and domain sets
  - Matching rules:
    - exact URL match => HIGH severity + score cap to 20 (Member #4 will cap, you just provide the signal)
    - domain match => MED severity
  - Return threat_intel result fields + evidence (provider, last_updated, hit_type)

- checkmate/modules/typosquat.py
  - Load local file data/tranco_top10k.txt
  - Compute Levenshtein distance (use python-Levenshtein if available or rapidfuzz)
  - If close match found (distance <= 1 or similarity threshold), produce MED/HIGH risk signal with evidence showing the closest domain.

Tests:
- typosquat test with "paypaI.com" vs "paypal.com" style cases (or similar)
- threat intel cache parsing test (use small fixture feed file)
- WHOIS failure test (mock whois call)
- SSL error test (mock safe_fetch raising SSLError)
```

### Prompt 4 (Member #4): Compile Flags + Score + Output (JSON + optional HTML)
```text
You are Member #4 implementing:
- Orchestration pipeline
- Risk compilation
- Final scoring + caps
- Output JSON and optional HTML report

Follow checkmate/models.py exactly.

Implement:
- checkmate/pipeline.py
  - Orchestrate:
    1) crawl (checkmate/crawl.py)
    2) run Member1 modules on pages (extraction+formatting+relevance)
    3) run Member2 modules (fact+sources)
    4) run Member3 modules (domain/security/threat/typosquat)
    5) compile risks + compute subscores + overall_score
  - Fail-soft: if a module errors, continue and record evidence.

- checkmate/modules/risk_compile.py
  - Merge signals into RiskItem list with severity and score_impact
  - Enforce missing policy pages rule:
    - missing >=2 of {contact, about, privacy, terms} => HIGH + hard penalty
    - missing ==1 => MED + medium penalty
  - Include “significant risks” as flagged; medium risks can be flagged or set as uncertain in title/message.

- checkmate/scoring.py
  - Weighted average:
    risk 40, sources 35, formatting 15, relevance 10
  - Apply caps:
    - threat exact url hit => cap 20
    - sensitive info request => cap 20
    - non-https or cert invalid => cap 35
  - Include score_breakdown evidence:
    - weights used
    - raw weighted score
    - which caps applied and why

- checkmate/render.py (optional)
  - Minimal Jinja2 HTML report:
    - big overall score
    - subscores
    - sorted risks (HIGH->LOW)
    - key evidence (top 1–2 per risk)
    - pages analyzed

- Update checkmate/app.py to support ?format=html if render.py exists.

Integration tests:
- 1 “good” real URL (or fixture)
- 1 “missing policies” fixture to trigger penalties
- 1 SSRF-block input must return status="na" and overall_score=null
```

### Quick note on your earlier question (JSON-only vs HTML report)
*   **JSON-only:** fastest, easiest to debug, best for backend-first.
*   **Simple HTML report:** makes the demo dramatically clearer. Since you chose “if time allows, do both”, your plan is perfect: ship JSON first, add a thin Jinja2 template later that renders the JSON.
