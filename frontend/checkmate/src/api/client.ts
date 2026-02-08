/**
 * CheckMate API client.
 *
 * In dev: uses relative /api (Vite proxies to http://localhost:5000) — no CORS.
 * In prod: set VITE_API_BASE_URL to your backend (e.g. https://api.example.com).
 */

import type { AnalyzeResponse } from "./types";

const BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  (import.meta.env.DEV ? "/api" : "http://localhost:5000");
const REQUEST_TIMEOUT_MS = 90000;

export async function postAnalyze(url: string): Promise<AnalyzeResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const apiUrl = `${BASE_URL.replace(/\/$/, "")}/analyze`;
    const res = await fetch(apiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    const text = await res.text();
    const json = text ? (() => { try { return JSON.parse(text); } catch { return {}; } })() : {};

    if (!res.ok) {
      const message =
        typeof json?.message === "string"
          ? json.message
          : typeof json?.error === "string"
            ? json.error
            : `Request failed (${res.status})`;
      throw new Error(message);
    }

    return (json as AnalyzeResponse) || { status: "error", overall_score: null };
  } catch (err) {
    clearTimeout(timeoutId);
    if (err instanceof Error) {
      if (err.name === "AbortError")
        throw new Error("Request timed out. The analysis can take up to 90 seconds—please try again.");
      throw err;
    }
    throw new Error("Network or server error. Try again or analyze another URL.");
  }
}
