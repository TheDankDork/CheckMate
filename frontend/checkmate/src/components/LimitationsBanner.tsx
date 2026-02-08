export interface LimitationsBannerProps {
  analysisLimited?: boolean;
  limitations: string[] | null | undefined;
}

export function LimitationsBanner({ analysisLimited, limitations }: LimitationsBannerProps) {
  const hasLimitations = analysisLimited || (limitations && limitations.length > 0);
  if (!hasLimitations) return null;

  const items = limitations ?? [];

  return (
    <div
      className="rounded-xl border border-amber-200 bg-amber-50 p-4 shadow-sm"
      role="alert"
      aria-label="Analysis limitations"
    >
      <h3 className="flex items-center gap-2 text-base font-semibold text-amber-900">
        <span aria-hidden>⚠</span> Analysis limitations
      </h3>
      {analysisLimited && items.length === 0 && (
        <p className="mt-2 text-sm text-amber-800">
          This analysis was limited. Results may be incomplete.
        </p>
      )}
      {items.length > 0 && (
        <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-amber-800">
          {items.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
