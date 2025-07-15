import { useState, useCallback, useRef, useEffect } from 'react';
import { ApiService } from '../services/api';
import { ChatMessage, ChatResponse } from '../services/types';
import { generateSessionId } from '../utils/helpers';

interface UseChatResult {
  messages: ChatMessage[];
  currentSessionId: string;
  isLoading: boolean;
  error: string | null;
  sendMessage: (message: string) => Promise<void>;
  clearChat: () => void;
  startNewChat: () => void;
  loadSession: (sessionId: string) => Promise<void>;
  retryLastMessage: () => Promise<void>;
}

export function useChat(): UseChatResult {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string>(() => generateSessionId());
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const lastMessageRef = useRef<string>('');

  const sendMessage = useCallback(async (message: string) => {
    if (isLoading || !message.trim()) return;

    lastMessageRef.current = message;
    setIsLoading(true);
    setError(null);

    // Add user message immediately
    const userMessage: ChatMessage = {
      id: Date.now(),
      message_type: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const response: ChatResponse = await ApiService.sendMessage({
        message,
        session_id: currentSessionId,
      });

      // Add assistant response
      const assistantMessage: ChatMessage = {
        id: response.message_id,
        message_type: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
        evaluation_score: response.evaluation_score,
        retrieved_context: response.retrieved_context,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      setError(errorMessage);
      
      // Add error message
      const errorMessageObj: ChatMessage = {
        id: Date.now() + 1,
        message_type: 'assistant',
        content: `❌ Error: ${errorMessage}. Please try again.`,
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, errorMessageObj]);
    } finally {
      setIsLoading(false);
    }
  }, [currentSessionId, isLoading]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const startNewChat = useCallback(() => {
    setMessages([]);
    setCurrentSessionId(generateSessionId());
    setError(null);
  }, []);

  const loadSession = useCallback(async (sessionId: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const history = await ApiService.getChatHistory(sessionId);
      setMessages(history.messages);
      setCurrentSessionId(sessionId);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load chat history';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const retryLastMessage = useCallback(async () => {
    if (lastMessageRef.current) {
      // Remove the last error message if present
      setMessages(prev => {
        const filtered = prev.filter(msg => 
          !(msg.message_type === 'assistant' && msg.content.includes('❌ Error:'))
        );
        return filtered;
      });
      
      await sendMessage(lastMessageRef.current);
    }
  }, [sendMessage]);

  return {
    messages,
    currentSessionId,
    isLoading,
    error,
    sendMessage,
    clearChat,
    startNewChat,
    loadSession,
    retryLastMessage,
  };
}
