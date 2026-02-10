export type AnalyzeRequest = {
  url: string;
};

export type EvidenceItem = {
  url?: string;
  snippet?: string;
  message?: string;
};

export type RiskItem = {
  severity: "HIGH" | "MED" | "LOW" | "UNCERTAIN";
  code?: string;
  title: string;
  notes?: string;
  evidence?: EvidenceItem[];
};

export type Subscores = {
  formatting: number;
  relevance: number;
  sources: number;
  risk: number;
};

export type PageAnalyzed = {
  url: string;
  status_code?: number;
  title?: string;
};

export type AnalyzeResponse = {
  status: "ok" | "na";
  overall_score: number | null;
  subscores?: Subscores;
  risks?: RiskItem[];
  missing_pages?: string[];
  analysis_limited?: boolean;
  limitations?: string[];
  pages_analyzed?: PageAnalyzed[];
  domain_info?: unknown;
  security_info?: unknown;
  threat_intel?: unknown;
  debug?: unknown;
};
