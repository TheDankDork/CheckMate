/**
 * Bar graph: score 0–100 with risk-level ranges.
 * Shows High risk (0–50), Mixed (50–80), Low risk (80–100) and a marker at the current score.
 */
export interface ScoreBarProps {
  /** Score from 0 to 100; if null/NaN, bar is shown without a marker */
  score: number | null;
}

const RANGES = [
  { min: 0, max: 50, label: "High risk", bg: "bg-red-500", text: "text-red-700" },
  { min: 50, max: 80, label: "Mixed signals", bg: "bg-amber-500", text: "text-amber-700" },
  { min: 80, max: 100, label: "Low risk", bg: "bg-emerald-500", text: "text-emerald-700" },
] as const;

export function ScoreBar({ score }: ScoreBarProps) {
  const hasScore =
    score != null && !Number.isNaN(score) && score >= 0 && score <= 100;
  const value = hasScore ? Math.round(score) : null;

  return (
    <div
      className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
      role="img"
      aria-label={
        value != null
          ? `Score bar: ${value} out of 100, ${value >= 80 ? "low risk" : value >= 50 ? "mixed signals" : "high risk"}`
          : "Score bar: no score"
      }
    >
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3">
        Score by risk level
      </p>
      {/* Bar with overlay marker */}
      <div className="relative w-full">
        <div className="flex h-8 w-full rounded-lg overflow-hidden border border-slate-200 bg-slate-100">
          {RANGES.map((r) => (
            <div
              key={r.label}
              className={`${r.bg} flex-shrink-0`}
              style={{ width: `${r.max - r.min}%` }}
              title={`${r.min}–${r.max}: ${r.label}`}
            />
          ))}
        </div>
        {value != null && (
          <div
            className="absolute top-0 w-1 h-8 rounded-full bg-slate-900 shadow-md border-2 border-white pointer-events-none -translate-x-1/2"
            style={{ left: `${value}%` }}
            title={`Score: ${value}`}
            aria-hidden
          />
        )}
      </div>
      {/* Scale 0–100 */}
      <div className="flex justify-between mt-2 text-xs text-slate-500">
        <span>0</span>
        <span>100</span>
      </div>
      {/* Risk range legend */}
      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs">
        {RANGES.map((r) => (
          <span key={r.label} className={r.text}>
            {r.min}–{r.max}: {r.label}
          </span>
        ))}
      </div>
      {value != null && (
        <p className="mt-2 text-sm text-slate-700">
          Your score: <strong>{value}</strong> / 100
        </p>
      )}
    </div>
  );
}
