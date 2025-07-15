import axios, { AxiosResponse } from 'axios';
import {
  ChatResponse,
  ChatHistoryResponse,
  ChatSession,
  SendMessageRequest,
  HealthStatus,
  ApiError
} from './types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_VERSION = '/api/v1';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}${API_VERSION}`,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error);
    
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    } else if (error.message) {
      throw new Error(error.message);
    } else {
      throw new Error('An unexpected error occurred');
    }
  }
);

export class ApiService {
  // Chat endpoints
  static async sendMessage(request: SendMessageRequest): Promise<ChatResponse> {
    const response: AxiosResponse<ChatResponse> = await apiClient.post('/chat/message', request);
    return response.data;
  }

  static async getChatHistory(sessionId: string, limit: number = 50, offset: number = 0): Promise<ChatHistoryResponse> {
    const response: AxiosResponse<ChatHistoryResponse> = await apiClient.get(
      `/chat/history/${sessionId}?limit=${limit}&offset=${offset}`
    );
    return response.data;
  }

  static async getChatSessions(limit: number = 20, offset: number = 0): Promise<ChatSession[]> {
    const response: AxiosResponse<ChatSession[]> = await apiClient.get(
      `/chat/sessions?limit=${limit}&offset=${offset}`
    );
    return response.data;
  }

  static async deleteChatSession(sessionId: string): Promise<void> {
    await apiClient.delete(`/chat/session/${sessionId}`);
  }

  // Health endpoint
  static async getHealth(): Promise<HealthStatus> {
    const response: AxiosResponse<HealthStatus> = await apiClient.get('/health/');
    return response.data;
  }

  // Utility methods
  static async checkApiConnection(): Promise<boolean> {
    try {
      await this.getHealth();
      return true;
    } catch (error) {
      console.error('API connection failed:', error);
      return false;
    }
  }
}