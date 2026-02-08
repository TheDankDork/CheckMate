import type { RiskItem, RiskSeverity, EvidenceItem } from "../api/types";

export interface RisksPanelProps {
  risks: RiskItem[] | null | undefined;
}

const SEVERITY_ORDER: RiskSeverity[] = ["HIGH", "MED", "LOW", "UNCERTAIN"];

const SEVERITY_STYLES: Record<RiskSeverity, { bg: string; text: string; border: string }> = {
  HIGH: { bg: "bg-red-50", text: "text-red-800", border: "border-red-200" },
  MED: { bg: "bg-amber-50", text: "text-amber-800", border: "border-amber-200" },
  LOW: { bg: "bg-slate-50", text: "text-slate-800", border: "border-slate-200" },
  UNCERTAIN: { bg: "bg-slate-50", text: "text-slate-600", border: "border-slate-200" },
};

function EvidenceSnippet({ item }: { item: EvidenceItem }) {
  const text = item.snippet ?? item.message ?? "";
  if (!text) return null;
  return (
    <div className="mt-2 rounded border border-slate-200 bg-white px-3 py-2 font-mono text-xs text-slate-700">
      {text}
    </div>
  );
}

function RiskCard({ risk }: { risk: RiskItem }) {
  const style = SEVERITY_STYLES[risk.severity];
  const evidence = risk.evidence ?? [];

  return (
    <div
      className={`rounded-lg border p-4 ${style.bg} ${style.border}`}
      role="article"
      aria-label={`Risk: ${risk.title}, severity ${risk.severity}`}
    >
      <div className="flex items-start justify-between gap-2">
        <span
          className={`inline-block rounded px-2 py-0.5 text-xs font-semibold uppercase ${style.text}`}
        >
          {risk.severity}
        </span>
        {risk.code && (
          <span className="text-xs text-slate-500">{risk.code}</span>
        )}
      </div>
      <h4 className="mt-2 font-semibold text-slate-800">{risk.title}</h4>
      {evidence.length > 0 && (
        <div className="mt-2 space-y-2">
          {evidence.map((item, i) => (
            <EvidenceSnippet key={i} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}

export function RisksPanel({ risks }: RisksPanelProps) {
  if (!risks?.length) return null;

  const bySeverity = SEVERITY_ORDER.map((sev) => ({
    severity: sev,
    items: risks.filter((r) => r.severity === sev),
  })).filter((g) => g.items.length > 0);

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold text-slate-800">Risks &amp; warnings</h3>
      <div className="space-y-4">
        {bySeverity.map(({ severity, items }) => (
          <div key={severity}>
            <h4 className="mb-2 text-sm font-medium text-slate-600">
              {severity} ({items.length})
            </h4>
            <div className="space-y-2">
              {items.map((risk, i) => (
                <RiskCard key={`${risk.title}-${i}`} risk={risk} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
