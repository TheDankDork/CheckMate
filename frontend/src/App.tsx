import { useCallback, useState } from "react";
import { postAnalyze } from "./api/client";
import type { AnalyzeResponse } from "./api/types";
import Home from "./pages/Home";

export type AppState = "idle" | "loading" | "success" | "error";

const normalizeUrl = (value: string): string => {
  const trimmed = value.trim();
  if (!trimmed) {
    return "";
  }

  const hasScheme = /^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(trimmed);
  return hasScheme ? trimmed : `https://${trimmed}`;
};

function App() {
  const [state, setState] = useState<AppState>("idle");
  const [data, setData] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastUrl, setLastUrl] = useState<string | null>(null);

  const handleAnalyze = useCallback(async (url: string) => {
    const normalized = normalizeUrl(url);
    if (!normalized) {
      setError("Please enter a URL.");
      setState("error");
      return;
    }

    setState("loading");
    setError(null);
    setData(null);
    setLastUrl(normalized);

    try {
      const result = await postAnalyze(normalized);
      setData(result);
      setState("success");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
      setState("error");
    }
  }, []);

  const handleReset = useCallback(() => {
    setState("idle");
    setData(null);
    setError(null);
    setLastUrl(null);
  }, []);

  return (
    <Home
      state={state}
      data={data}
      error={error}
      lastUrl={lastUrl}
      onAnalyze={handleAnalyze}
      onReset={handleReset}
    />
  );
}

export default App;
