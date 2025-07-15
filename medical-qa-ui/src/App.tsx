// ============================================================================
// Fixed App.tsx with Correct Imports
// ============================================================================

import React, { useState, useEffect, useCallback } from 'react';
import { ChatInterface } from './components/chat-component';
import { 
  ChatHistory, 
  Layout, 
  ErrorBoundary, 
  ConnectionStatus,
  LoadingSpinner,
  ErrorMessage 
} from './components/Layout/Layout';
import { useChat } from './hooks/useChat';
import { useChatHistory } from './hooks/useChatHistory';
import { useLocalStorage } from './hooks/useLocalStorage';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import { ApiService } from './services/api';

function App() {
  // State management
  const [sidebarOpen, setSidebarOpen] = useLocalStorage('sidebarOpen', true);
  const [isConnected, setIsConnected] = useState(true);
  const [isReconnecting, setIsReconnecting] = useState(false);
  const [appError, setAppError] = useState<string | null>(null);

  // Custom hooks
  const {
    messages,
    currentSessionId,
    isLoading: chatLoading,
    error: chatError,
    sendMessage,
    clearChat,
    startNewChat,
    loadSession,
    retryLastMessage
  } = useChat();

  const {
    sessions,
    loading: historyLoading,
    error: historyError,
    refreshSessions,
    deleteSession
  } = useChatHistory();

  // Check API connection
  const checkConnection = useCallback(async () => {
    try {
      setIsReconnecting(true);
      const connected = await ApiService.checkApiConnection();
      setIsConnected(connected);
      
      if (!connected) {
        setAppError('Unable to connect to the API server. Please check if the server is running.');
      } else {
        setAppError(null);
        // Refresh sessions when reconnected
        await refreshSessions();
      }
    } catch (error) {
      setIsConnected(false);
      setAppError('Connection failed. Please check your network connection.');
    } finally {
      setIsReconnecting(false);
    }
  }, [refreshSessions]);

  // Initial connection check
  useEffect(() => {
    checkConnection();
    
    // Set up periodic connection checks
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds
    
    return () => clearInterval(interval);
  }, [checkConnection]);

  // Handle session selection
  const handleSelectSession = useCallback(async (sessionId: string) => {
    try {
      await loadSession(sessionId);
      // Close sidebar on mobile after selecting session
      if (window.innerWidth < 1024) {
        setSidebarOpen(false);
      }
    } catch (error) {
      console.error('Failed to load session:', error);
    }
  }, [loadSession, setSidebarOpen]);

  // Handle new chat
  const handleNewChat = useCallback(() => {
    startNewChat();
    // Close sidebar on mobile after starting new chat
    if (window.innerWidth < 1024) {
      setSidebarOpen(false);
    }
  }, [startNewChat, setSidebarOpen]);

  // Handle delete session
  const handleDeleteSession = useCallback(async (sessionId: string) => {
    try {
      await deleteSession(sessionId);
      
      // If deleting current session, start a new one
      if (sessionId === currentSessionId) {
        startNewChat();
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  }, [deleteSession, currentSessionId, startNewChat]);

  // Handle send message
  const handleSendMessage = useCallback(async (message: string) => {
    try {
      await sendMessage(message);
      // Refresh sessions to update message count
      await refreshSessions();
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  }, [sendMessage, refreshSessions]);

  // Keyboard shortcuts
  useKeyboardShortcuts([
    {
      key: 'n',
      ctrlKey: true,
      callback: handleNewChat
    },
    {
      key: 'b',
      ctrlKey: true,
      callback: () => setSidebarOpen(prev => !prev)
    },
    {
      key: 'r',
      ctrlKey: true,
      shiftKey: true,
      callback: retryLastMessage
    }
  ]);

  // Handle window resize for responsive sidebar
  useEffect(() => {
    const handleResize = () => {
      // Auto-open sidebar on desktop, auto-close on mobile
      if (window.innerWidth >= 1024) {
        setSidebarOpen(true);
      } else {
        setSidebarOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [setSidebarOpen]);

  // Render sidebar
  const sidebar = (
    <ChatHistory
      sessions={sessions}
      currentSessionId={currentSessionId}
      loading={historyLoading}
      error={historyError}
      onSelectSession={handleSelectSession}
      onNewChat={handleNewChat}
      onDeleteSession={handleDeleteSession}
      onRefreshSessions={refreshSessions}
      isConnected={isConnected}
      onCheckConnection={checkConnection}
    />
  );

  // Show loading screen on initial load
  if (historyLoading && sessions.length === 0) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <LoadingSpinner size="lg" text="Loading Medical Q&A Assistant..." />
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="h-screen overflow-hidden">
        {/* Connection Status Bar */}
        <ConnectionStatus
          isConnected={isConnected}
          isReconnecting={isReconnecting}
          onReconnect={checkConnection}
        />

        {/* Main Layout */}
        <Layout
          sidebar={sidebar}
          sidebarOpen={sidebarOpen}
          onToggleSidebar={() => setSidebarOpen(prev => !prev)}
          currentSessionId={currentSessionId}
          messageCount={messages.length}
        >
          {/* App Error */}
          {appError && (
            <ErrorMessage
              message={appError}
              onRetry={checkConnection}
              onDismiss={() => setAppError(null)}
            />
          )}

          {/* Chat Interface */}
          <ChatInterface
            messages={messages}
            isLoading={chatLoading}
            onSendMessage={handleSendMessage}
            onRetryMessage={retryLastMessage}
            error={chatError}
          />
        </Layout>

        {/* Keyboard Shortcuts Help (Hidden but available) */}
        <div className="hidden">
          <div title="Keyboard Shortcuts">
            <p>Ctrl+N: New Chat</p>
            <p>Ctrl+B: Toggle Sidebar</p>
            <p>Ctrl+Shift+R: Retry Last Message</p>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}

export default App;