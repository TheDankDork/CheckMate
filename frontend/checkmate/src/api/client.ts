/**
 * CheckMate API client.
 *
 * Set VITE_API_BASE_URL in .env (e.g. VITE_API_BASE_URL=https://api.example.com)
 * to point at the backend. If unset, defaults to http://localhost:5000.
 */

import type { AnalyzeResponse } from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5000";

export async function postAnalyze(url: string): Promise<AnalyzeResponse> {
  const res = await fetch(`${BASE_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });

  const json = await res.json().catch(() => ({}));

  if (!res.ok) {
    const message =
      typeof json?.message === "string"
        ? json.message
        : `Request failed (${res.status})`;
    throw new Error(message);
  }

  return json as AnalyzeResponse;
}
