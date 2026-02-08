/** Types for CheckMate backend API (align with checkmate/schemas.py) */

export interface AnalyzeRequest {
  url: string;
}

export type AnalyzeStatus = "ok" | "na" | "error";

export type RiskSeverity = "HIGH" | "MED" | "LOW" | "UNCERTAIN";

export interface EvidenceItem {
  url?: string;
  snippet?: string;
  message?: string;
}

export interface RiskItem {
  severity: RiskSeverity;
  code?: string;
  title: string;
  notes?: string;
  evidence?: EvidenceItem[];
}

export interface PageSummary {
  url: string;
  status_code?: number;
  title?: string;
}

export interface Subscores {
  formatting: number;
  relevance: number;
  sources: number;
  risk: number;
}

export type WebsiteType = "functional" | "statistical" | "news_historical" | "company";

export interface AnalyzeResponse {
  status: AnalyzeStatus;
  overall_score: number | null;
  website_type?: WebsiteType | null;
  subscores?: Subscores;
  risks?: RiskItem[];
  missing_pages?: string[];
  analysis_limited?: boolean;
  limitations?: string[];
  pages_analyzed?: PageSummary[];
  domain_info?: Record<string, unknown>;
  security_info?: Record<string, unknown>;
  threat_intel?: Record<string, unknown>;
  debug?: Record<string, unknown>;
}
