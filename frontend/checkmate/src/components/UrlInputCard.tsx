import { useState, useCallback } from "react";

export interface UrlInputCardProps {
  onAnalyze: (url: string) => void;
  disabled?: boolean;
  initialUrl?: string;
}

export function UrlInputCard({ onAnalyze, disabled = false, initialUrl = "" }: UrlInputCardProps) {
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
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <form onSubmit={handleSubmit} className="space-y-4">
        <label htmlFor="checkmate-url" className="block text-sm font-medium text-slate-700">
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
            className="flex-1 rounded-lg border border-slate-300 px-4 py-2.5 text-slate-800 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 disabled:bg-slate-100"
            autoComplete="url"
          />
          <button
            type="submit"
            disabled={disabled}
            className="rounded-lg bg-emerald-600 px-5 py-2.5 font-medium text-white hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:opacity-50"
          >
            Analyze
          </button>
        </div>
        {error && <p className="text-sm text-red-600" role="alert">{error}</p>}
      </form>
    </div>
  );
}
