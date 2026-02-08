import { useState } from "react";
import type { PageSummary, WebsiteType } from "../api/types";

export interface DetailsAccordionProps {
  pagesAnalyzed?: PageSummary[] | null;
  domainInfo?: Record<string, unknown> | null;
  securityInfo?: Record<string, unknown> | null;
  threatIntel?: Record<string, unknown> | null;
  websiteType?: WebsiteType | string | null;
  scoringWeights?: Record<string, number> | null;
}

function Section({
  title,
  open,
  onToggle,
  children,
}: {
  title: string;
  open: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}) {
  return (
    <div className="border-b border-slate-200 last:border-b-0">
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center justify-between py-3 text-left font-medium text-slate-800 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-inset min-h-[44px]"
        aria-expanded={open}
        id={title.replace(/\s+/g, "-").toLowerCase()}
      >
        {title}
        <span className="text-slate-400 shrink-0" aria-hidden>
          {open ? "−" : "+"}
        </span>
      </button>
      {open && <div className="pb-3 text-sm text-slate-600">{children}</div>}
    </div>
  );
}

function JsonBlock({ data }: { data: Record<string, unknown> }) {
  const str = JSON.stringify(data, null, 2);
  return (
    <pre className="overflow-x-auto rounded border border-slate-200 bg-slate-50 p-3 font-mono text-xs">
      {str}
    </pre>
  );
}

function PagesList({ pages }: { pages: PageSummary[] }) {
  return (
    <ul className="space-y-2">
      {pages.map((p, i) => (
        <li key={i} className="rounded border border-slate-200 bg-slate-50 p-2">
          <span className="font-medium text-slate-800">{p.url}</span>
          {p.title != null && (
            <span className="block text-slate-600">{p.title}</span>
          )}
          {p.status_code != null && (
            <span className="text-xs text-slate-500">HTTP {p.status_code}</span>
          )}
        </li>
      ))}
    </ul>
  );
}

function websiteTypeLabel(t: string | undefined | null): string {
  if (!t) return "—";
  switch (t) {
    case "functional": return "Functional (utility)";
    case "statistical": return "Statistical (data)";
    case "company": return "Company";
    case "news_historical": return "News / historical";
    default: return t;
  }
}

export function DetailsAccordion({
  pagesAnalyzed,
  domainInfo,
  securityInfo,
  threatIntel,
  websiteType,
  scoringWeights,
}: DetailsAccordionProps) {
  const [openSection, setOpenSection] = useState<string | null>(null);

  const hasPages = pagesAnalyzed && pagesAnalyzed.length > 0;
  const hasDomain = domainInfo && Object.keys(domainInfo).length > 0;
  const hasSecurity = securityInfo && Object.keys(securityInfo).length > 0;
  const hasThreat = threatIntel && Object.keys(threatIntel).length > 0;
  const hasScoring = (websiteType != null && websiteType !== "") || (scoringWeights && Object.keys(scoringWeights).length > 0);

  if (!hasPages && !hasDomain && !hasSecurity && !hasThreat && !hasScoring) return null;

  const toggle = (id: string) =>
    setOpenSection((s) => (s === id ? null : id));

  return (
    <div className="card">
      <div className="h-1 w-10 rounded-full bg-slate-400 mb-4" aria-hidden />
      <h3 className="section-title mb-4">
        Technical details
      </h3>
      <div className="space-y-0">
        {hasScoring && (
          <Section
            title="Website type & scoring"
            open={openSection === "scoring"}
            onToggle={() => toggle("scoring")}
          >
            <div className="space-y-2">
              <p>
                <span className="font-medium text-slate-800">Website type:</span>{" "}
                {websiteTypeLabel(websiteType ?? undefined)}
              </p>
              {scoringWeights && (
                <p>
                  <span className="font-medium text-slate-800">Weights used:</span>{" "}
                  Formatting {Math.round((scoringWeights.formatting ?? 0) * 100)}%, Relevance {Math.round((scoringWeights.relevance ?? 0) * 100)}%, Sources {Math.round((scoringWeights.sources ?? 0) * 100)}%, Safety {Math.round((scoringWeights.risk ?? 0) * 100)}%
                </p>
              )}
            </div>
          </Section>
        )}
        {hasPages && (
          <Section
            title="Pages analyzed"
            open={openSection === "pages"}
            onToggle={() => toggle("pages")}
          >
            <PagesList pages={pagesAnalyzed!} />
          </Section>
        )}
        {hasDomain && (
          <Section
            title="Domain info"
            open={openSection === "domain"}
            onToggle={() => toggle("domain")}
          >
            <JsonBlock data={domainInfo!} />
          </Section>
        )}
        {hasSecurity && (
          <Section
            title="Security info"
            open={openSection === "security"}
            onToggle={() => toggle("security")}
          >
            <JsonBlock data={securityInfo!} />
          </Section>
        )}
        {hasThreat && (
          <Section
            title="Threat intel"
            open={openSection === "threat"}
            onToggle={() => toggle("threat")}
          >
            <JsonBlock data={threatIntel!} />
          </Section>
        )}
      </div>
    </div>
  );
}
