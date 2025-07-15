export const APP_CONFIG = {
  name: 'Medical Q&A Assistant',
  version: '1.0.0',
  description: 'AI-powered medical information assistant',
  maxMessageLength: 2000,
  defaultSessionName: 'New Chat',
  autoSaveInterval: 5000, // 5 seconds
};

export const API_CONFIG = {
  baseUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
  retryAttempts: 3,
  retryDelay: 1000,
};

export const UI_CONFIG = {
  sidebarWidth: '320px',
  maxChatWidth: '800px',
  messageMaxWidth: '85%',
  animationDuration: 300,
  loadingDots: 3,
};

export const EVALUATION_CONFIG = {
  scoreColors: {
    excellent: 'text-green-600',
    good: 'text-blue-600', 
    fair: 'text-yellow-600',
    poor: 'text-red-600',
  },
  scoreRanges: {
    excellent: 0.8,
    good: 0.6,
    fair: 0.4,
    poor: 0.0,
  },
};

export const SAMPLE_QUESTIONS = [
  "What is diabetes and what are its main types?",
  "What are the symptoms of hypertension?",
  "How do vaccines work in the immune system?",
  "What causes heart disease?",
  "What is the difference between Type 1 and Type 2 diabetes?",
  "How is high blood pressure treated?",
  "What are the risk factors for cardiovascular disease?",
  "Explain how antibiotics work against bacterial infections",
];