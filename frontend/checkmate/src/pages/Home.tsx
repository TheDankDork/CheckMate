import { useState, useCallback } from "react";
import type { AnalyzeResponse } from "../api/types";
import { UrlInputCard } from "../components/UrlInputCard";
import { ScoreHero } from "../components/ScoreHero";
import { SubscoresPanel } from "../components/SubscoresPanel";
import { RisksPanel } from "../components/RisksPanel";
import { MissingPagesBadges } from "../components/MissingPagesBadges";
import { LimitationsBanner } from "../components/LimitationsBanner";
import { DetailsAccordion } from "../components/DetailsAccordion";

/** Mock result for testing UI without backend */
export const MOCK_RESULT: AnalyzeResponse = {
  status: "ok",
  overall_score: 72,
  subscores: {
    formatting: 85,
    relevance: 70,
    sources: 65,
    risk: 68,
  },
  risks: [
    {
      severity: "HIGH",
      code: "NO_HTTPS",
      title: "Site does not enforce HTTPS on all pages",
      evidence: [
        { message: "HTTP used on login page", url: "http://example.com/login", snippet: "Redirect chain did not end at HTTPS" },
      ],
    },
    {
      severity: "MED",
      code: "WEAK_CONTACT",
      title: "Contact page lacks physical address",
      evidence: [
        { snippet: "Only email found; no street address or phone." },
      ],
    },
    {
      severity: "LOW",
      code: "OLD_COPYRIGHT",
      title: "Copyright year may be outdated",
      evidence: [{ message: "Footer shows 2022" }],
    },
  ],
  missing_pages: ["Privacy", "Terms of Service"],
  pages_analyzed: [
    { url: "https://example.com/", status_code: 200, title: "Example Domain" },
    { url: "https://example.com/about", status_code: 200, title: "About Us" },
    { url: "https://example.com/contact", status_code: 200, title: "Contact" },
  ],
  domain_info: { registrar: "Example Registrar", created: "2020-01-15" },
  security_info: { ssl_grade: "B", hsts: false },
  threat_intel: { blacklists: [], reputation: "neutral" },
  limitations: ["Only 3 pages could be fetched within time limit."],
  analysis_limited: true,
};

export type HomeState = "idle" | "loading" | "success" | "error";

export interface HomeProps {
  onAnalyze: (url: string) => void;
  onReset: () => void;
  state: HomeState;
  data: AnalyzeResponse | null;
  error: string | null;
  /** Last URL sent to the API (normalized) */
  lastRequestUrl?: string | null;
  /** When true, use mock result for dashboard instead of real data (for demo without backend) */
  useMockForDemo?: boolean;
}

export function Home({
  onAnalyze,
  onReset,
  state,
  data,
  error,
  lastRequestUrl = null,
  useMockForDemo = false,
}: HomeProps) {
  const [useMock, setUseMock] = useState(useMockForDemo);
  const displayData =
    state === "success" && data
      ? data
      : useMock
        ? MOCK_RESULT
        : null;

  const handleReset = useCallback(() => {
    setUseMock(false);
    onReset();
  }, [onReset]);

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white shadow-sm">
        <div className="mx-auto max-w-3xl px-4 py-6 sm:px-6">
          <h1 className="text-2xl font-bold text-slate-900">CheckMate</h1>
          <p className="mt-1 text-sm text-slate-600">
            Website legitimacy check (hackathon demo)
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
        <div className="space-y-8">
          <UrlInputCard
            onAnalyze={onAnalyze}
            disabled={state === "loading"}
            initialUrl=""
          />

          {state === "loading" && (
            <div
              className="flex flex-col items-center justify-center rounded-xl border border-slate-200 bg-white py-12 shadow-sm"
              role="status"
              aria-live="polite"
            >
              <div
                className="h-10 w-10 animate-spin rounded-full border-2 border-emerald-500 border-t-transparent"
                aria-hidden
              />
              <p className="mt-4 font-medium text-slate-700">Analyzing…</p>
              <p className="mt-1 text-sm text-slate-500">
                This can take up to ~30 seconds.
              </p>
            </div>
          )}

          {state === "error" && error && (
            <div
              className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-800"
              role="alert"
            >
              <p className="font-medium">Analysis failed</p>
              <p className="mt-1 text-sm">{error}</p>
            </div>
          )}

          {displayData && (
            <>
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-slate-800">Results</h2>
                  {lastRequestUrl && (
                    <p className="mt-0.5 text-sm text-slate-500">Analyzed: {lastRequestUrl}</p>
                  )}
                </div>
                <button
                  type="button"
                  onClick={handleReset}
                  className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
                >
                  Analyze another URL
                </button>
              </div>

              <div className="space-y-6">
                <ScoreHero
                  overallScore={displayData.overall_score}
                  status={displayData.status}
                />
                <SubscoresPanel subscores={displayData.subscores} />
                <RisksPanel risks={displayData.risks} />
                <MissingPagesBadges missingPages={displayData.missing_pages} />
                <LimitationsBanner
                  analysisLimited={displayData.analysis_limited}
                  limitations={displayData.limitations}
                />
                <DetailsAccordion
                  pagesAnalyzed={displayData.pages_analyzed}
                  domainInfo={displayData.domain_info}
                  securityInfo={displayData.security_info}
                  threatIntel={displayData.threat_intel}
                />
              </div>
            </>
          )}

          {state === "idle" && !displayData && (
            <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-slate-500 shadow-sm">
              <p>Enter a URL above and click Analyze to see results.</p>
              <p className="mt-2 text-sm">
                Or use mock data:{" "}
                <button
                  type="button"
                  onClick={() => setUseMock(true)}
                  className="font-medium text-emerald-600 hover:underline"
                >
                  Load mock result
                </button>
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
