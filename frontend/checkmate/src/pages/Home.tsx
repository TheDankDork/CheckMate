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
  website_type: "news_historical",
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

export type HomeState = "idle" | "loading" | "success" | "error" | "na";

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
    <div className="min-h-screen">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded focus:bg-white focus:px-4 focus:py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
      >
        Skip to main content
      </a>
      <header className="relative flex items-center bg-slate-900 px-4 py-4 sm:px-8 shadow-lg">
        <div className="absolute inset-x-0 bottom-0 h-[3px] bg-gradient-to-r from-emerald-400 via-emerald-500 to-teal-500" aria-hidden />
        <img
          src="/logo.png"
          alt="CheckMate"
          className="h-11 w-auto object-contain relative z-10"
        />
        <p className="ml-4 text-sm text-slate-300 font-medium relative z-10">
          Check if a website is legitimate before you trust it
        </p>
      </header>

      <main id="main-content" className="mx-auto max-w-3xl px-4 py-8 sm:px-8 sm:py-12" tabIndex={-1}>
        <div className="space-y-8">
          <UrlInputCard
            onAnalyze={onAnalyze}
            disabled={state === "loading"}
            initialUrl=""
          />

          {state === "loading" && (
            <div
              className="card flex flex-col items-center justify-center py-16 bg-gradient-to-b from-white to-emerald-50/20"
              role="status"
              aria-live="polite"
              aria-busy="true"
            >
              <div
                className="h-12 w-12 animate-spin rounded-full border-2 border-emerald-500 border-t-transparent"
                aria-hidden
              />
              <p className="mt-5 text-lg font-semibold text-slate-800">Analyzing…</p>
              <p className="mt-1.5 text-sm text-slate-500">
                This can take up to 35 seconds. Please wait.
              </p>
            </div>
          )}

          {state === "error" && error && (
            <div
              className="rounded-2xl border-2 border-red-200 bg-red-50/95 shadow-lg p-5 text-red-800"
              role="alert"
              aria-live="assertive"
            >
              <p className="font-medium">Something went wrong.</p>
              <p className="mt-1 text-sm">{error}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {lastRequestUrl && (
                  <button
                    type="button"
                    onClick={() => onAnalyze(lastRequestUrl!)}
                    className="rounded-lg border border-red-300 bg-white px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 min-h-[44px] min-w-[44px]"
                  >
                    Try again
                  </button>
                )}
                <button
                  type="button"
                  onClick={handleReset}
                  className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 min-h-[44px] min-w-[44px]"
                >
                  Analyze another URL
                </button>
              </div>
            </div>
          )}

          {state === "na" && data && (
            <div
              className="rounded-2xl border-2 border-amber-200 bg-amber-50/95 shadow-lg p-5 text-amber-900"
              role="status"
              aria-live="polite"
            >
              <p className="font-medium">We couldn’t analyze this URL.</p>
              <p className="mt-1 text-sm">
                {data.limitations?.length
                  ? data.limitations.join(" ")
                  : "The site could not be fetched or is not supported."}
              </p>
              <button
                type="button"
                onClick={handleReset}
                className="mt-4 rounded-lg border border-amber-300 bg-white px-4 py-2 text-sm font-medium text-amber-800 hover:bg-amber-50 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2"
              >
                Analyze another URL
              </button>
            </div>
          )}

          {displayData && (
            <section aria-live="polite" aria-label="Analysis results" className="space-y-6">
              {(() => {
                const websiteType = displayData.website_type ?? displayData.debug?.website_type ?? displayData.debug?.scoring?.website_type ?? (displayData.overall_score != null ? "news_historical" : null);
                const websiteTypeLabel = websiteType === "functional" ? "Functional (utility)" : websiteType === "statistical" ? "Statistical (data)" : websiteType === "company" ? "Company" : websiteType === "news_historical" ? "News / historical" : (displayData.overall_score != null ? "News / historical" : null);
                return (
              <>
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <div className="h-1 w-10 rounded-full bg-emerald-500 mb-2" aria-hidden />
                  <h2 className="text-2xl font-bold tracking-tight text-slate-900">Results</h2>
                  {lastRequestUrl && (
                    <p className="mt-1 text-sm text-slate-500">Analyzed: {lastRequestUrl}</p>
                  )}
                  <p className="mt-0.5 text-sm text-slate-600">
                    Website type:{" "}
                    <span className="font-medium text-slate-800">
                      {websiteTypeLabel ?? "—"}
                    </span>
                  </p>
                  {displayData.debug?.scoring?.weights && (
                    <p className="mt-0.5 text-xs text-slate-500">
                      Score weights: Formatting {Math.round((displayData.debug.scoring.weights as Record<string, number>).formatting * 100)}%, Relevance {Math.round((displayData.debug.scoring.weights as Record<string, number>).relevance * 100)}%, Sources {Math.round((displayData.debug.scoring.weights as Record<string, number>).sources * 100)}%, Safety {Math.round((displayData.debug.scoring.weights as Record<string, number>).risk * 100)}%
                    </p>
                  )}
                </div>
                <button
                  type="button"
                  onClick={handleReset}
                  className="rounded-xl border-2 border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 hover:border-emerald-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 min-h-[44px] transition-colors"
                >
                  Analyze another URL
                </button>
              </div>

              <div className="space-y-6">
                <ScoreHero
                  overallScore={displayData.overall_score}
                  status={displayData.status}
                />
                <div className="rounded-xl border border-slate-200 bg-slate-50/80 px-4 py-3">
                  <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Website type</p>
                  <p className="mt-1 font-medium text-slate-800">
                    {websiteTypeLabel ?? "Not classified"}
                  </p>
                </div>
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
                  websiteType={websiteType ?? displayData.website_type}
                  scoringWeights={displayData.debug?.scoring?.weights as Record<string, number> | undefined}
                />
              </div>
              </>
                );
              })()}
            </section>
          )}

          {state === "idle" && !displayData && (
            <div className="card p-10 text-center overflow-hidden relative">
              <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-bl from-emerald-100/60 to-transparent rounded-full -translate-y-1/2 translate-x-1/2" aria-hidden />
              <div className="relative">
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-emerald-100 text-emerald-600 mb-4" aria-hidden>
                  <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9a9 9 0 009 9m-9-9a9 9 0 009-9" /></svg>
                </div>
                <p className="text-slate-600 font-medium">Enter a URL above and click Analyze to see results.</p>
                <p className="mt-3 text-sm text-slate-500">
                  Or use mock data:{" "}
                  <button
                    type="button"
                    onClick={() => setUseMock(true)}
                    className="font-semibold text-emerald-600 hover:text-emerald-700 hover:underline focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 rounded min-h-[44px] min-w-[44px] inline-flex items-center justify-center transition-colors"
                  >
                    Load mock result
                  </button>
                </p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
