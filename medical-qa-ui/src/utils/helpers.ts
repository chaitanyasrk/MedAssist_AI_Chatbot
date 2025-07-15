import { EVALUATION_CONFIG } from './constants';

export const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffInMs = now.getTime() - date.getTime();
  const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
  const diffInHours = Math.floor(diffInMinutes / 60);
  const diffInDays = Math.floor(diffInHours / 24);

  if (diffInMinutes < 1) {
    return 'Just now';
  } else if (diffInMinutes < 60) {
    return `${diffInMinutes}m ago`;
  } else if (diffInHours < 24) {
    return `${diffInHours}h ago`;
  } else if (diffInDays < 7) {
    return `${diffInDays}d ago`;
  } else {
    return date.toLocaleDateString();
  }
};

export const formatTime = (timestamp: string): string => {
  return new Date(timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};

export const getEvaluationColor = (score?: number): string => {
  if (!score) return EVALUATION_CONFIG.scoreColors.fair;
  
  if (score >= EVALUATION_CONFIG.scoreRanges.excellent) {
    return EVALUATION_CONFIG.scoreColors.excellent;
  } else if (score >= EVALUATION_CONFIG.scoreRanges.good) {
    return EVALUATION_CONFIG.scoreColors.good;
  } else if (score >= EVALUATION_CONFIG.scoreRanges.fair) {
    return EVALUATION_CONFIG.scoreColors.fair;
  } else {
    return EVALUATION_CONFIG.scoreColors.poor;
  }
};

export const getEvaluationLabel = (score?: number): string => {
  if (!score) return 'No Score';
  
  if (score >= EVALUATION_CONFIG.scoreRanges.excellent) {
    return 'Excellent';
  } else if (score >= EVALUATION_CONFIG.scoreRanges.good) {
    return 'Good';
  } else if (score >= EVALUATION_CONFIG.scoreRanges.fair) {
    return 'Fair';
  } else {
    return 'Poor';
  }
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};

export const generateSessionId = (): string => {
  return `session-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
};

export const validateMessage = (message: string): { isValid: boolean; error?: string } => {
  if (!message.trim()) {
    return { isValid: false, error: 'Message cannot be empty' };
  }
  
  if (message.length > 2000) {
    return { isValid: false, error: 'Message is too long (max 2000 characters)' };
  }
  
  return { isValid: true };
};

export const formatResponseTime = (timeInSeconds: number): string => {
  if (timeInSeconds < 1) {
    return `${Math.round(timeInSeconds * 1000)}ms`;
  } else {
    return `${timeInSeconds.toFixed(1)}s`;
  }
};

export const scrollToBottom = (element: HTMLElement, smooth: boolean = true): void => {
  element.scrollTo({
    top: element.scrollHeight,
    behavior: smooth ? 'smooth' : 'auto'
  });
};

export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    console.error('Failed to copy to clipboard:', error);
    return false;
  }
};

export const downloadAsText = (content: string, filename: string): void => {
  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};