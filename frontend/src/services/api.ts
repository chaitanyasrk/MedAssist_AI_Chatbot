import axios, { AxiosResponse } from 'axios';
import { 
  ChatRequest, 
  ChatResponse, 
  APIExecutionRequest, 
  APIExecutionResponse,
  Document,
  EvaluationMetrics
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use((config) => {
  console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(`❌ API Error:`, error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export class ApiService {
  // Health check
  static async healthCheck(): Promise<{ status: string; version: string }> {
    const response: AxiosResponse = await api.get('/health');
    return response.data;
  }

  // Chat endpoints
  static async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response: AxiosResponse<ChatResponse> = await api.post('/api/chat', request);
    return response.data;
  }

  // API execution
  static async executeAPI(request: APIExecutionRequest): Promise<APIExecutionResponse> {
    const response: AxiosResponse<APIExecutionResponse> = await api.post('/api/chat/execute-api', request);
    return response.data;
  }

  // Document management
  static async getDocuments(): Promise<{ documents: Document[] }> {
    const response: AxiosResponse = await api.get('/api/documents');
    return response.data;
  }

  static async uploadDocument(content: string, filename: string, documentType: string): Promise<{ message: string; document_id: string }> {
    const response: AxiosResponse = await api.post('/api/documents/upload', {
      content,
      filename,
      document_type: documentType
    });
    return response.data;
  }

  // Conversation management
  static async getConversation(conversationId: string): Promise<{ conversation: any }> {
    const response: AxiosResponse = await api.get(`/api/conversations/${conversationId}`);
    return response.data;
  }

  static async deleteConversation(conversationId: string): Promise<{ message: string }> {
    const response: AxiosResponse = await api.delete(`/api/conversations/${conversationId}`);
    return response.data;
  }

  // Evaluation endpoints
  static async getEvaluationMetrics(): Promise<EvaluationMetrics> {
    const response: AxiosResponse<EvaluationMetrics> = await api.get('/api/evaluation/metrics');
    return response.data;
  }

  static async getGoldenDataset(): Promise<{ dataset: any[] }> {
    const response: AxiosResponse = await api.get('/api/evaluation/golden-dataset');
    return response.data;
  }

  // Utility method for error handling
  static handleError(error: any): string {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.message) {
      return error.message;
    }
    return 'An unexpected error occurred';
  }
}

export default ApiService;