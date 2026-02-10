import { useState } from "react";
import type { AnalyzeResponse } from "../api/types";
import type { AppState } from "../App";

export type HomeProps = {
  state: AppState;
  data: AnalyzeResponse | null;
  error: string | null;
  lastUrl: string | null;
  onAnalyze: (url: string) => void;
  onReset: () => void;
};

export default function Home({
  state,
  data,
  error,
  lastUrl,
  onAnalyze,
  onReset,
}: HomeProps) {
  const [urlInput, setUrlInput] = useState("");

  return (
    <div style={{ padding: "1.5rem", fontFamily: "sans-serif" }}>
      <header>
        <h1>CheckMate</h1>
        <p>Website legitimacy check (hackathon demo)</p>
      </header>

      <section>
        <label htmlFor="url-input">Website URL</label>
        <div>
          <input
            id="url-input"
            type="url"
            value={urlInput}
            onChange={(event) => setUrlInput(event.target.value)}
            placeholder="https://example.com"
          />
          <button type="button" onClick={() => onAnalyze(urlInput)}>
            Analyze
          </button>
          <button type="button" onClick={onReset}>
            Reset
          </button>
        </div>
      </section>

      <section>
        <p>State: {state}</p>
        {lastUrl ? <p>Last URL: {lastUrl}</p> : null}
        {error ? <p style={{ color: "crimson" }}>{error}</p> : null}
        {data ? (
          <pre style={{ whiteSpace: "pre-wrap" }}>
            {JSON.stringify(data, null, 2)}
          </pre>
        ) : null}
      </section>
    </div>
  );
}
