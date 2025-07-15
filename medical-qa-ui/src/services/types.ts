export interface ChatMessage {
  id: number;
  message_type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  evaluation_score?: number;
  retrieved_context?: ContextDocument[];
}

export interface ContextDocument {
  question: string;
  answer: string;
  category?: string;
  similarity_score: number;
}

export interface ChatResponse {
  message_id: number;
  session_id: string;
  response: string;
  evaluation_score?: number;
  retrieved_context: ContextDocument[];
  response_time: number;
  timestamp: string;
  is_medical: boolean;
  query_type?: string;
}

export interface ChatSession {
  session_id: string;
  created_at: string;
  message_count: number;
  is_active: boolean;
}

export interface ChatHistoryResponse {
  session_id: string;
  messages: ChatMessage[];
  total_count: number;
  has_more: boolean;
}

export interface SendMessageRequest {
  message: string;
  session_id?: string;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}

export interface HealthStatus {
  status: string;
  timestamp: string;
  version: string;
  services: Record<string, any>;
  system_info: Record<string, any>;
}