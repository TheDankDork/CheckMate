import { useState, useCallback } from "react";

const EXAMPLE_URL = "https://example.com";

export interface UrlInputCardProps {
  onAnalyze: (url: string) => void;
  disabled?: boolean;
  initialUrl?: string;
  /** Show a "Try example" link that runs analysis with EXAMPLE_URL */
  showExample?: boolean;
}

export function UrlInputCard({ onAnalyze, disabled = false, initialUrl = "", showExample = true }: UrlInputCardProps) {
  const [url, setUrl] = useState(initialUrl);
  const [error, setError] = useState<string | null>(null);

  const normalizeUrl = useCallback((raw: string): string => {
    const trimmed = raw.trim();
    if (!trimmed) return trimmed;
    if (!/^https?:\/\//i.test(trimmed)) return `https://${trimmed}`;
    return trimmed;
  }, []);

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      setError(null);
      const normalized = normalizeUrl(url);
      if (!normalized) {
        setError("Please enter a URL");
        return;
      }
      onAnalyze(normalized);
    },
    [url, normalizeUrl, onAnalyze]
  );

  return (
    <div className="relative rounded-2xl border-2 border-emerald-200/80 bg-gradient-to-br from-white to-emerald-50/30 p-6 shadow-lg shadow-emerald-900/5">
      <form onSubmit={handleSubmit} className="space-y-4">
        <label htmlFor="checkmate-url" className="block text-sm font-semibold text-slate-800">
          Website URL
        </label>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <input
            id="checkmate-url"
            type="url"
            value={url}
            onChange={(e) => {
              setUrl(e.target.value);
              setError(null);
            }}
            placeholder="https://example.com"
            disabled={disabled}
            className="flex-1 rounded-xl border-2 border-slate-200 bg-white px-4 py-3 text-slate-800 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/25 disabled:bg-slate-100 transition-colors"
            autoComplete="url"
            aria-invalid={!!error}
            aria-describedby={error ? "checkmate-url-error" : undefined}
          />
          <button
            type="submit"
            disabled={disabled}
            className="rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 px-6 py-3 font-semibold text-white shadow-md shadow-emerald-900/20 hover:from-emerald-500 hover:to-teal-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:opacity-50 min-h-[48px] shrink-0 transition-all"
          >
            Analyze
          </button>
        </div>
        {error && <p id="checkmate-url-error" className="text-sm text-red-600" role="alert">{error}</p>}
        {showExample && !error && (
          <p id="checkmate-url-hint" className="text-sm text-slate-500">
            Try example:{" "}
            <button
              type="button"
              onClick={() => onAnalyze(EXAMPLE_URL)}
              disabled={disabled}
              className="font-medium text-emerald-600 hover:underline focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 rounded min-h-[44px] min-w-[44px] inline-flex items-center justify-center"
            >
              {EXAMPLE_URL}
            </button>
          </p>
        )}
      </form>
    </div>
  );
}
