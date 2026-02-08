# Frontend Improvement PRD — CheckMate Web App

## 1) Goals (from your answers)
- **Demo day:** Judges see a polished, credible product in a short presentation.
- **Portfolio:** The app showcases strong front-end work you’d be proud to link.
- **Visual direction:** Between **A (Trust / safety)** and **B (Tech / tool)** — calm and clear that the tool helps users stay safe, with a structured, data-first dashboard feel (not purely “corporate” or purely “dev tool”).

---

## 2) Current problems (to address)

### Technical
- Inconsistent or missing error states (timeout, backend down, invalid URL).
- No loading progress or clear feedback during long analysis (~30s).
- Possible CORS or base-URL config issues when backend URL changes.
- Results layout may break with long URLs, many risks, or missing data.
- No basic accessibility (focus, labels, screen reader).
- Mobile/responsive behavior not fully considered.

### Visual
- “Rough” look: generic spacing, typography, and hierarchy.
- Header and score don’t feel like a cohesive “trust + tool” UI.
- Risk cards and subscores don’t feel scannable or professional.
- No clear visual system (scale, severity colors, empty states).
- Tagline and secondary text don’t support trust or clarity.

---

## 3) Design principles

1. **Trust & safety (A)**  
   Calm, readable, plenty of whitespace. Copy and layout should signal “this helps you stay safe.” Use restrained color (e.g. blues/grays) and clear typography.

2. **Tech / dashboard (B)**  
   Data-first: score and risks are the focus. Clear hierarchy (score → subscores → risks → details). Card-based layout, consistent spacing, and a “tool” feel without looking harsh.

3. **Demo-ready**  
   One clear flow: paste URL → see score and “why” in under 30s. No dead ends; errors and loading states are obvious and recoverable.

4. **Portfolio-ready**  
   Clean structure (components, types, API layer), consistent patterns, and a UI that looks intentional, not placeholder.

---

## 4) Technical improvements

| # | Area | What to do |
|---|------|------------|
| T1 | **Error handling** | Define explicit states: `idle | loading | success | error | na`. Handle: backend unreachable, timeout (e.g. 35s), 4xx/5xx, invalid JSON. Show a clear message and “Try again” / “Analyze another URL”. |
| T2 | **Loading UX** | Keep single spinner but add short copy: “Analyzing… This can take up to 30 seconds.” Optional: disable input and button during load. No need for real backend progress in v1. |
| T3 | **API config** | Use `VITE_API_BASE_URL` (or existing env) for backend. Document in README. In UI, show nothing sensitive; only use for `POST /analyze`. |
| T4 | **Defensive rendering** | If `subscores`, `risks`, or `missing_pages` are missing or empty, still render layout with “No data” or “—”. Never assume every field exists. |
| T5 | **Accessibility** | Ensure one focusable “Analyze” button; label URL input; use `aria-live` for result/error updates; keep contrast and focus visible. |
| T6 | **Responsive** | Header, input card, score, and risk list should stack and remain readable on small screens. Touch-friendly button and input. |

---

## 5) Visual improvements

| # | Area | What to do |
|---|------|------------|
| V1 | **Typography** | Pick a clear, readable font (e.g. system UI or one Google font). Use a simple scale: one size for score, one for section titles, one for body/evidence. Consistent font across the app. |
| V2 | **Color system** | Define a small palette: background (e.g. light gray/white), surface (cards), text (primary/secondary), and severity (e.g. red = high risk, amber = medium, blue/gray = low/neutral). Use for score label and risk badges. |
| V3 | **Header** | Compact bar: logo top-left at normal size; short tagline (trust + tool tone). Optional: subtle border or shadow to separate from content. |
| V4 | **URL input card** | Single clear card: labeled input, one primary “Analyze” button. Optional “Try example” for demo. Inline validation message only when submit fails (e.g. empty). |
| V5 | **Score block** | Large, centered score (or “N/A” + reason). Under it, one short label from score band (e.g. “Low risk” / “Mixed signals” / “High risk”) using the severity color. Feels like the “answer” of the page. |
| V6 | **Subscores** | Horizontal bars or small cards with labels (Formatting, Relevance, Sources, Risk). Same color logic (e.g. green = good, amber = okay, red = bad) so it’s scannable. |
| V7 | **Risks list** | Group by severity (HIGH first). Each risk: title, optional code, short notes, evidence snippets (plain text only). Use severity color for left border or badge. Enough spacing so it doesn’t feel cramped. |
| V8 | **Missing pages & limitations** | Badges or chips for missing pages. If `limitations` or `analysis_limited`, show a small banner (e.g. amber) so “limited analysis” is obvious. |
| V9 | **Details accordion** | Collapsed by default. Clear heading; inside: pages list, domain/security/threat summary. Keeps main view simple. |
| V10 | **Spacing & layout** | Consistent padding and gaps (e.g. 8px grid). Max width for content so lines aren’t too long. Clear vertical rhythm between sections. |

---

## 6) Copy and microcopy

- **Tagline:** Short and clear, e.g. “Check if a website is legitimate before you trust it” (trust) or “Website legitimacy check” (tool). Avoid jargon.
- **Empty state:** “Enter a URL above and click Analyze to see results.”
- **Loading:** “Analyzing… This can take up to 30 seconds.”
- **Error:** “Something went wrong. [Reason if we have it.] Try again or analyze another URL.”
- **N/A:** “We couldn’t analyze this URL. [Reason from backend.]”
- **Score labels:** e.g. 80–100 “Low risk”, 50–79 “Mixed signals”, 0–49 “High risk”.

---

## 7) Suggested implementation order

1. **Phase 1 – Technical baseline**  
   T1 (error states), T2 (loading), T4 (defensive rendering). Ensures the app never looks broken during demo.

2. **Phase 2 – Visual system**  
   V1 (typography), V2 (colors), V10 (spacing). Apply to one screen first (e.g. results), then roll out.

3. **Phase 3 – Key components**  
   V3 (header), V4 (input card), V5 (score), V6 (subscores), V7 (risks). Makes the main flow clear and portfolio-worthy.

4. **Phase 4 – Polish**  
   V8 (missing pages + limitations), V9 (accordion), T5 (a11y), T6 (responsive). Final pass for demo and portfolio.

---

## 8) Success criteria

- **Demo:** In 2 minutes, a judge can paste a URL, see a score and clear risks, and understand “why” without confusion.
- **Portfolio:** The repo has a clear front-end structure, and the UI looks intentional (typography, color, hierarchy), not like a bare prototype.
- **Trust + tool:** The app feels calm and safe (A) and clearly data-focused (B), without looking like a generic template.

---

## 9) Out of scope (for this PRD)

- Auth or user accounts.
- History of past analyses.
- Backend changes (this doc focuses on front-end and integration contract only).
- Real-time progress from backend (streaming); optional later.

---

*Summary of your choices: Goals = Demo + Portfolio. Visual = Between A (trust/safety) and B (tech/dashboard).*
