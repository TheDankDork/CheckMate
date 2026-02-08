import type { AnalyzeStatus } from "../api/types";

export interface ScoreHeroProps {
  overallScore: number | null;
  status: AnalyzeStatus;
}

function getScoreStyles(score: number): { text: string; bg: string; bar: string } {
  if (score >= 80) return { text: "text-emerald-700", bg: "from-emerald-50 to-teal-50", bar: "bg-emerald-500" };
  if (score >= 50) return { text: "text-amber-700", bg: "from-amber-50 to-orange-50", bar: "bg-amber-500" };
  return { text: "text-red-700", bg: "from-red-50 to-rose-50", bar: "bg-red-500" };
}

export function ScoreHero({ overallScore, status }: ScoreHeroProps) {
  const showNumeric = status === "ok" && overallScore != null && !Number.isNaN(overallScore) && overallScore >= 0;
  const styles = showNumeric ? getScoreStyles(overallScore) : { text: "text-slate-600", bg: "from-slate-50 to-slate-100", bar: "bg-slate-400" };

  return (
    <div
      className={`rounded-2xl border border-slate-200/90 bg-gradient-to-br ${styles.bg} p-10 text-center shadow-lg overflow-hidden relative`}
      role="region"
      aria-label="Overall score"
    >
      <div className={`absolute top-0 left-0 right-0 h-1 ${styles.bar}`} aria-hidden />
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
        Overall score
      </p>
      <div className="mt-4">
        {showNumeric ? (
          <>
            <span
              className={`text-6xl font-bold tabular-nums sm:text-7xl ${styles.text}`}
              aria-label={`Score: ${overallScore} out of 100`}
            >
              {overallScore}
            </span>
            <span className="ml-2 text-3xl text-slate-400 sm:text-4xl">/ 100</span>
            <p className={`mt-3 text-xl font-semibold ${styles.text}`}>
              {overallScore >= 80 ? "Low risk" : overallScore >= 50 ? "Mixed signals" : "High risk"}
            </p>
          </>
        ) : (
          <span className={`text-5xl font-bold ${styles.text} sm:text-6xl`} aria-label="Score not available">N/A</span>
        )}
      </div>
    </div>
  );
}
