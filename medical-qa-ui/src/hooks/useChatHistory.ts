import { useState, useEffect, useCallback } from 'react';
import { ApiService } from '../services/api';
import { ChatSession } from '../services/types';

interface UseChatHistoryResult {
  sessions: ChatSession[];
  loading: boolean;
  error: string | null;
  refreshSessions: () => Promise<void>;
  deleteSession: (sessionId: string) => Promise<void>;
}

export function useChatHistory(): UseChatHistoryResult {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshSessions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const sessionsData = await ApiService.getChatSessions();
      setSessions(sessionsData);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load chat sessions';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      await ApiService.deleteChatSession(sessionId);
      setSessions(prev => prev.filter(session => session.session_id !== sessionId));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete session';
      setError(errorMessage);
    }
  }, []);

  useEffect(() => {
    refreshSessions();
  }, [refreshSessions]);

  return {
    sessions,
    loading,
    error,
    refreshSessions,
    deleteSession,
  };
}
