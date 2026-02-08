export interface MissingPagesBadgesProps {
  missingPages: string[] | null | undefined;
}

const KNOWN_LABELS: Record<string, string> = {
  contact: "Contact",
  about: "About",
  privacy: "Privacy",
  terms: "Terms",
  "privacy policy": "Privacy",
  "terms of service": "Terms",
  "terms of use": "Terms",
};

function labelFor(page: string): string {
  const key = page.toLowerCase().trim();
  return KNOWN_LABELS[key] ?? page;
}

export function MissingPagesBadges({ missingPages }: MissingPagesBadgesProps) {
  if (!missingPages?.length) return null;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="mb-3 text-lg font-semibold text-slate-800">Missing pages</h3>
      <p className="mb-3 text-sm text-slate-600">
        These expected pages were not found or could not be analyzed.
      </p>
      <div className="flex flex-wrap gap-2">
        {missingPages.map((page) => (
          <span
            key={page}
            className="inline-flex items-center rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-sm font-medium text-amber-800"
          >
            {labelFor(page)}
          </span>
        ))}
      </div>
    </div>
  );
}
