import { useState, useCallback } from "react";
import type { AnalyzeResponse } from "./api/types";
import { postAnalyze } from "./api/client";
import type { HomeState } from "./pages/Home";
import { Home } from "./pages/Home";

function normalizeUrl(raw: string): string {
  const trimmed = raw.trim();
  if (!trimmed) return trimmed;
  if (!/^https?:\/\//i.test(trimmed)) return `https://${trimmed}`;
  return trimmed;
}

function App() {
  const [state, setState] = useState<HomeState>("idle");
  const [lastRequestUrl, setLastRequestUrl] = useState<string | null>(null);
  const [data, setData] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onAnalyze = useCallback(async (url: string) => {
    const normalized = normalizeUrl(url);
    setError(null);
    setState("loading");
    setData(null);
    setLastRequestUrl(normalized);

    try {
      const response = await postAnalyze(normalized);
      setData(response);
      setState(response.status === "na" ? "na" : "success");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong. Try again or analyze another URL.");
      setState("error");
    }
  }, []);

  const onReset = useCallback(() => {
    setState("idle");
    setLastRequestUrl(null);
    setData(null);
    setError(null);
  }, []);

  return (
    <Home
      onAnalyze={onAnalyze}
      onReset={onReset}
      state={state}
      data={data}
      error={error}
      lastRequestUrl={lastRequestUrl}
      useMockForDemo={false}
    />
  );
}

export default App;
