import type { Subscores as SubscoresType } from "../api/types";

export interface SubscoresPanelProps {
  subscores: SubscoresType | null | undefined;
}

const LABELS: Record<keyof SubscoresType, string> = {
  formatting: "Formatting",
  relevance: "Relevance",
  sources: "Sources",
  risk: "Risk",
};

function Bar({ value, label }: { value: number; label: string }) {
  const pct = Math.max(0, Math.min(100, value));
  const color =
    pct >= 80 ? "bg-emerald-500" : pct >= 50 ? "bg-amber-500" : "bg-red-500";

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="font-medium text-slate-700">{label}</span>
        <span className="tabular-nums text-slate-600">{value}</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200">
        <div
          className={`h-full rounded-full ${color} transition-all duration-300`}
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`${label}: ${value}`}
        />
      </div>
    </div>
  );
}

export function SubscoresPanel({ subscores }: SubscoresPanelProps) {
  if (!subscores) return null;

  const entries = (Object.keys(LABELS) as (keyof SubscoresType)[]).map((key) => ({
    key,
    label: LABELS[key],
    value: subscores[key],
  }));

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold text-slate-800">Subscores</h3>
      <div className="grid gap-4 sm:grid-cols-2">
        {entries.map(({ key, label, value }) => (
          <Bar key={key} value={value} label={label} />
        ))}
      </div>
    </div>
  );
}
