import { useState } from "react";
import type { PageSummary } from "../api/types";

export interface DetailsAccordionProps {
  pagesAnalyzed?: PageSummary[] | null;
  domainInfo?: Record<string, unknown> | null;
  securityInfo?: Record<string, unknown> | null;
  threatIntel?: Record<string, unknown> | null;
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
        className="flex w-full items-center justify-between py-3 text-left font-medium text-slate-800 hover:text-slate-900"
        aria-expanded={open}
      >
        {title}
        <span className="text-slate-400" aria-hidden>
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

export function DetailsAccordion({
  pagesAnalyzed,
  domainInfo,
  securityInfo,
  threatIntel,
}: DetailsAccordionProps) {
  const [openSection, setOpenSection] = useState<string | null>(null);

  const hasPages = pagesAnalyzed && pagesAnalyzed.length > 0;
  const hasDomain = domainInfo && Object.keys(domainInfo).length > 0;
  const hasSecurity = securityInfo && Object.keys(securityInfo).length > 0;
  const hasThreat = threatIntel && Object.keys(threatIntel).length > 0;

  if (!hasPages && !hasDomain && !hasSecurity && !hasThreat) return null;

  const toggle = (id: string) =>
    setOpenSection((s) => (s === id ? null : id));

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold text-slate-800">
        Technical details
      </h3>
      <div className="space-y-0">
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
