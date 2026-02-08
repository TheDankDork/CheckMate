import type { RiskItem, RiskSeverity, EvidenceItem } from "../api/types";

export interface RisksPanelProps {
  risks?: RiskItem[] | null;
}

const SEVERITY_ORDER: RiskSeverity[] = ["HIGH", "MED", "LOW", "UNCERTAIN"];

const SEVERITY_STYLES: Record<RiskSeverity, { bg: string; text: string; border: string; left: string }> = {
  HIGH: { bg: "bg-red-50", text: "text-red-800", border: "border-red-200", left: "border-l-red-500" },
  MED: { bg: "bg-amber-50", text: "text-amber-800", border: "border-amber-200", left: "border-l-amber-500" },
  LOW: { bg: "bg-slate-100", text: "text-slate-800", border: "border-slate-200", left: "border-l-slate-400" },
  UNCERTAIN: { bg: "bg-slate-50", text: "text-slate-600", border: "border-slate-200", left: "border-l-slate-300" },
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
      className={`rounded-xl border-l-4 border ${style.bg} ${style.border} ${style.left} p-4`}
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
      {risk.notes && (
        <p className="mt-1 text-sm text-slate-600">{risk.notes}</p>
      )}
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

export function RisksPanel({ risks = [] }: RisksPanelProps) {
  const safeRisks = risks ?? [];
  const bySeverity =
    safeRisks.length > 0
    ? SEVERITY_ORDER.map((sev) => ({
          severity: sev,
          items: safeRisks.filter((r) => r.severity === sev),
        })).filter((g) => g.items.length > 0)
      : [];

  return (
    <div className="card">
      <div className="h-1 w-10 rounded-full bg-amber-500 mb-4" aria-hidden />
      <h3 className="section-title mb-5">Risks &amp; warnings</h3>
      {bySeverity.length > 0 ? (
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
      ) : (
        <p className="text-slate-500" aria-live="polite">No risks reported.</p>
      )}
    </div>
  );
}
