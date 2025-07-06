export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  contextUsed?: boolean;
  confidenceScore?: number;
  requiresApiExecution?: boolean;
  apiInfo?: APIInfo;
  suggestedFollowUps?: string[];
}

export interface APIInfo {
  endpoint: string;
  method: string;
  headers?: Record<string, string>;
  payloadSchema?: Record<string, any>;
  description: string;
}

export interface ChatRequest {
  query: string;
  conversation_id?: string;
  bearer_token?: string;
  include_context?: boolean;
}

export interface ChatResponse {
  response: string;
  context_used: boolean;
  confidence_score: number;
  requires_api_execution: boolean;
  api_info?: APIInfo;
  suggested_follow_ups?: string[];
  conversation_id?: string;
}

export interface APIExecutionRequest {
  api_endpoint: string;
  bearer_token: string;
  payload?: Record<string, any>;
}

export interface APIExecutionResponse {
  success: boolean;
  status_code: number;
  data: any;
  error?: string;
  headers?: Record<string, string>;
  url?: string;
}

export interface Document {
  document_id: string;
  filename: string;
  document_type: string;
  chunk_count: number;
  created_at: string;
}

export interface EvaluationMetrics {
  total_evaluations: number;
  average_scores: {
    correctness: number;
    relevance: number;
    completeness: number;
    overall: number;
  };
  score_distribution: Record<string, number>;
  recent_evaluations: Array<{
    query: string;
    overall_score: number;
    timestamp: string;
  }>;
}