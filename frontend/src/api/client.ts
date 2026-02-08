/**
 * Configure the backend base URL with VITE_API_BASE_URL in your .env file.
 * Defaults to http://localhost:5000 for local development.
 */
import type { AnalyzeResponse } from "./types";

const DEFAULT_BASE_URL = "http://localhost:5000";

export async function postAnalyze(url: string): Promise<AnalyzeResponse> {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || DEFAULT_BASE_URL;
  const response = await fetch(`${baseUrl}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  return (await response.json()) as AnalyzeResponse;
}
