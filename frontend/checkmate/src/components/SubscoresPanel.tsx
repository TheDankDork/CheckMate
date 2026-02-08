import type { Subscores as SubscoresType } from "../api/types";

export interface SubscoresPanelProps {
  subscores: SubscoresType | null | undefined;
}

const LABELS: Record<keyof SubscoresType, string> = {
  formatting: "Formatting",
  relevance: "Relevance",
  sources: "Sources",
  risk: "Safety",
};

function Bar({ value, label }: { value: number; label: string }) {
  const num = typeof value === "number" && !Number.isNaN(value) ? value : 0;
  const pct = Math.max(0, Math.min(100, num));
  const color =
    pct >= 80 ? "bg-emerald-500" : pct >= 50 ? "bg-amber-500" : "bg-red-500";

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="font-medium text-slate-700">{label}</span>
        <span className="tabular-nums text-slate-600">{num}</span>
      </div>
      <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-200">
        <div
          className={`h-full rounded-full ${color} transition-all duration-300`}
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={num}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`${label}: ${num}`}
        />
      </div>
    </div>
  );
}

export function SubscoresPanel({ subscores }: SubscoresPanelProps) {
  const entries =
    subscores
      ? (Object.keys(LABELS) as (keyof SubscoresType)[]).map((key) => ({
          key,
          label: LABELS[key],
          value: subscores[key],
        }))
      : [];

  return (
    <div className="card">
      <div className="h-1 w-10 rounded-full bg-emerald-500 mb-4" aria-hidden />
      <h3 className="section-title mb-5">Subscores</h3>
      {entries.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {entries.map(({ key, label, value }) => (
            <Bar key={key} value={value} label={label} />
          ))}
        </div>
      ) : (
        <p className="text-slate-500" aria-live="polite">No subscore data available.</p>
      )}
    </div>
  );
}
