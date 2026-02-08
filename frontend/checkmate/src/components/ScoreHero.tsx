import type { AnalyzeStatus } from "../api/types";

export interface ScoreHeroProps {
  overallScore: number | null;
  status: AnalyzeStatus;
}

function getScoreLabel(score: number): string {
  if (score >= 80) return "Low risk";
  if (score >= 50) return "Mixed signals";
  return "High risk";
}

function getScoreColor(score: number): string {
  if (score >= 80) return "text-emerald-600";
  if (score >= 50) return "text-amber-600";
  return "text-red-600";
}

export function ScoreHero({ overallScore, status }: ScoreHeroProps) {
  const showNumeric = status === "ok" && overallScore != null && overallScore >= 0;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm">
      <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
        Overall legitimacy score
      </p>
      <div className="mt-2">
        {showNumeric ? (
          <>
            <span
              className={`text-5xl font-bold tabular-nums sm:text-6xl ${getScoreColor(overallScore)}`}
              aria-label={`Score: ${overallScore}`}
            >
              {overallScore}
            </span>
            <span className="ml-1 text-2xl text-slate-400 sm:text-3xl">/ 100</span>
            <p className="mt-2 text-lg font-medium text-slate-700">
              {getScoreLabel(overallScore)}
            </p>
          </>
        ) : (
          <span className="text-4xl font-bold text-slate-500 sm:text-5xl">N/A</span>
        )}
      </div>
    </div>
  );
}
