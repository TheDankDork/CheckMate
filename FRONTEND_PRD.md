# Frontend PRD — CheckMate Web App (Hackathon MVP)

## 1) Goal
Build a fast, clean frontend that lets a judge/user:
1.  paste a website URL
2.  submit it to your backend (`POST /analyze`)
3.  see a legitimacy score (0–100 or N/A) and clear evidence-based risks
4.  optionally open an HTML report view if your backend supports it

## 2) Constraints
*   Hackathon speed > perfect design
*   Must work reliably for demo
*   Must not render untrusted HTML from scanned sites (XSS risk). Only render plain text from backend response.

## 3) Primary user flow
1.  User opens page
2.  User pastes URL
3.  Clicks Analyze
4.  Sees:
    *   overall score big and centered
    *   subscores
    *   key risks (HIGH first)
    *   missing pages (Contact/About/Privacy/Terms)
    *   limited-analysis warnings (if any)
    *   pages analyzed list (optional “expand”)
5.  User can click Analyze another URL / reset

## 4) Pages / Screens (MVP)
Single-page app with sections:

**A) Header**
*   App name: “CheckMate”
*   short tagline: “Website legitimacy check (hackathon demo)”

**B) URL Input Card**
*   URL input field (`type=url`)
*   “Analyze” button
*   Sample buttons (optional): “Try example.com”, “Try a sketchy demo site”
*   Validation:
    *   if empty → show inline error
    *   if missing scheme, auto-prepend `https://` before sending (frontend convenience)

**C) Loading State**
*   spinner + “Analyzing… (can take up to ~30s)”
*   optional progress text:
    *   “Fetching pages…”
    *   “Analyzing with Gemini…”
    *   “Computing score…”
    (Frontend can’t truly know backend stage unless you add streaming; for MVP just show spinner.)

**D) Results Dashboard**
Show these in priority order:
1.  **Overall score**
    *   If `status="ok"`: large numeric score
    *   If `status="na"`: show “N/A” + reason from limitations
    *   A short label:
        *   80–100 “Low risk”
        *   50–79 “Mixed signals”
        *   0–49 “High risk”
2.  **Subscores** (formatting / relevance / sources / risk)
    *   simple horizontal bars or small cards
3.  **Key risks / warnings**
    *   list grouped by severity: HIGH, MED, LOW, UNCERTAIN
    *   each risk card shows:
        *   title
        *   short notes
        *   evidence snippet(s) + which page URL (if provided)
        *   important: escape all text
4.  **Missing pages**
    *   display missing Contact/About/Privacy/Terms badges
5.  **Analysis limitations**
    *   if `analysis_limited=true`, show a warning banner and list `limitations[]`
6.  **Technical details** (collapsed accordion)
    *   pages analyzed list
    *   domain/security/threat intel blocks

**E) Actions**
*   “Analyze another URL” (reset)
*   Optional “View HTML report” button (only if backend supports it and you add a `GET/report` endpoint; otherwise skip)

## 5) Backend API contract (what frontend expects)
Frontend calls:
`POST /analyze`
Body: `{ "url": "https://example.com" }`

Response (key fields frontend uses):
*   `status`: "ok" | "na"
*   `overall_score`: number | null
*   `subscores`: object with formatting, relevance, sources, risk (numbers 0–100)
*   `risks`: array of:
    *   `severity`: "HIGH"|"MED"|"LOW"|"UNCERTAIN"
    *   `title`, `code`, `notes`?
    *   `evidence`: array of `{ url?, snippet?, message? }` (support both)
*   `missing_pages`: string[]
*   `analysis_limited`: boolean (optional)
*   `limitations`: string[] (optional)

Frontend should be defensive: if some fields missing, render what exists.

## 6) Error handling rules
Frontend must handle:
*   backend offline / CORS errors
*   request timeout (show “try again”)
*   `status="na"` (show “N/A” and why)
*   partial results: show warning but still display what’s available
*   invalid JSON: show “unexpected response” with raw text (developer-only panel optional)

## 7) UX quality rules (demo-friendly)
*   One clean page, no routing needed
*   Big score + clear “why”
*   Sort risks by severity
*   Make it obvious when it’s “limited analysis”

## 8) Suggested tech stack (fast)
*   React + TypeScript (or plain JS if you prefer)
*   Tailwind (optional, for fast styling)
*   Fetch via `fetch()` or `axios`
*   No auth for MVP

## 9) Frontend repo layout (example)
```css
frontend/
  src/
    api/
      client.ts
      types.ts
    components/
      UrlInputCard.tsx
      ScoreHero.tsx
      SubscoresPanel.tsx
      RisksPanel.tsx
      MissingPagesBadges.tsx
      LimitationsBanner.tsx
      DetailsAccordion.tsx
    pages/
      Home.tsx
    App.tsx
    main.tsx
  .env
  vite.config.ts
```

## Task split (2 people)

**Person 1: UI/Components + Layout**
Owns:
*   URL input card
*   loading state
*   results layout and styling
*   risk cards, severity grouping
*   missing pages badges
*   limitations banner
*   responsive layout
Deliverable: app renders correctly with a mock JSON response.

**Person 2: API Integration + Types + State**
Owns:
*   `api/types.ts` for backend response types
*   `api/client.ts` for `POST /analyze`
*   global state handling:
    *   idle → loading → results/error
    *   URL normalization + validation
    *   error handling + defensive rendering helpers
    *   optional: simple config for backend base URL (`VITE_API_BASE_URL`)
Deliverable: app works end-to-end against real backend.

---

## AI Module Prompt 1 (Person 1) — UI + Components
Copy/paste this into your coding AI:

```text
You are building the frontend UI for “CheckMate” (hackathon MVP).
Tech: React + TypeScript (Vite). Styling: Tailwind preferred but optional if time.

Implement these files:
• “src/components/UrlInputCard.tsx”
• “src/components/ScoreHero.tsx”
• “src/components/SubscoresPanel.tsx”
• “src/components/RisksPanel.tsx”
• “src/components/MissingPagesBadges.tsx”
• “src/components/LimitationsBanner.tsx”
• “src/components/DetailsAccordion.tsx”
• “src/pages/Home.tsx”

Requirements:
1. “Home page has: header, URL input card, loading state, results dashboard, reset button.”
2. “Results dashboard shows:”
• “overall_score big (or “N/A” if null)”
• “subscores as bars/cards”
• “risks grouped by severity (HIGH first)”
• “missing pages badges”
• “limitations banner if analysis_limited or limitations exist”
• “details accordion with pages/security/threat intel (if present)”
3. “All text must be rendered safely (no dangerouslySetInnerHTML). Evidence snippets must be plain text.”
4. “Components accept props typed with interfaces (use types from src/api/types.ts).”
5. “Provide a “mock result” object inside Home.tsx so UI can be tested without backend.”
6. “Keep UI clean and demo-friendly.”

Output complete code for all files.
```

## AI Module Prompt 2 (Person 2) — API + Types + State
Copy/paste this into your coding AI:

```text
You are building API integration and state management for the “CheckMate” frontend (React + TypeScript + Vite).

Implement these files:
• “src/api/types.ts”
• “src/api/client.ts”
• “src/App.tsx”
• “src/main.tsx”

Requirements:
1. “Define TypeScript types for backend response:”
• “AnalyzeRequest { url: string }”
• “AnalyzeResponse with fields:
status: "ok" | "na"
overall_score: number | null
subscores?: { formatting:number; relevance:number; sources:number; risk:number }
risks?: Array<{ severity:"HIGH"|"MED"|"LOW"|"UNCERTAIN"; code?:string; title:string; notes?:string; evidence?: Array<{ url?:string; snippet?:string; message?:string }> }>
missing_pages?: string[]
analysis_limited?: boolean
limitations?: string[]
pages_analyzed?: Array<{ url:string; status_code?:number; title?:string }>
domain_info?: any; security_info?: any; threat_intel?: any; debug?: any”

2. “Implement postAnalyze(url: string): Promise<AnalyzeResponse> in client.ts:”
• “base URL from import.meta.env.VITE_API_BASE_URL defaulting to http://localhost:5000”
• “POST /analyze JSON body”
• “handle non-2xx by throwing an Error with message”

3. “In App.tsx, wire state:”
• “idle | loading | success | error”
• “store last request URL, response, error text”

4. “Add URL normalization:”
• “trim”
• “if missing scheme, prepend https://”

5. “Make it easy for Person 1:”
• “Home component receives props: onAnalyze(url), onReset(), state, data, error”

6. “No UI styling needed here, just clean wiring.”

7. “Add a simple README comment at top of client.ts explaining env var usage.”

Output complete code for all files.
```
