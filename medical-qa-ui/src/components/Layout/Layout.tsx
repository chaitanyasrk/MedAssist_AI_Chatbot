// ============================================================================
// src/components/Layout/Layout.tsx - All Layout Components
// ============================================================================

import React, { useState } from 'react';
import { Plus, MessageSquare, Trash2, Calendar, Clock, Menu, X, Activity, AlertCircle, CheckCircle, User, Bot } from 'lucide-react';
import { ChatSession } from '../../services/types';
import { formatTimestamp, truncateText } from '../../utils/helpers';
import { APP_CONFIG } from '../../utils/constants';

// ============================================================================
// Chat History Item Component
// ============================================================================

interface HistoryItemProps {
  session: ChatSession;
  isActive: boolean;
  onClick: () => void;
  onDelete: (sessionId: string) => void;
}

const HistoryItem: React.FC<HistoryItemProps> = ({ session, isActive, onClick, onDelete }) => {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (showDeleteConfirm) {
      onDelete(session.session_id);
      setShowDeleteConfirm(false);
    } else {
      setShowDeleteConfirm(true);
      // Auto-hide after 3 seconds
      setTimeout(() => setShowDeleteConfirm(false), 3000);
    }
  };

  const handleClick = () => {
    if (!showDeleteConfirm) {
      onClick();
    }
  };

  // Generate session title from ID or use a more user-friendly approach
  const sessionTitle = `Chat ${session.session_id.split('-').pop()?.substring(0, 6)}`;

  return (
    <div
      onClick={handleClick}
      className={`p-3 rounded-lg cursor-pointer transition-all duration-200 group ${
        isActive 
          ? 'bg-blue-100 border-l-4 border-blue-500' 
          : 'hover:bg-gray-50 border-l-4 border-transparent'
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3 flex-1 min-w-0">
          <MessageSquare className={`h-4 w-4 flex-shrink-0 ${
            isActive ? 'text-blue-600' : 'text-gray-400'
          }`} />
          <div className="flex-1 min-w-0">
            <div className={`text-sm font-medium truncate ${
              isActive ? 'text-blue-900' : 'text-gray-700'
            }`}>
              {sessionTitle}
            </div>
            <div className="flex items-center space-x-2 text-xs text-gray-500 mt-1">
              <Calendar className="h-3 w-3" />
              <span>{formatTimestamp(session.created_at)}</span>
              <span>•</span>
              <span>{session.message_count} messages</span>
            </div>
          </div>
        </div>
        
        <button
          onClick={handleDelete}
          className={`p-1 rounded transition-colors ${
            showDeleteConfirm 
              ? 'text-red-600 bg-red-100' 
              : 'text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100'
          }`}
          title={showDeleteConfirm ? 'Click again to confirm' : 'Delete chat'}
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

// ============================================================================
// New Chat Button Component
// ============================================================================

interface NewChatButtonProps {
  onClick: () => void;
  disabled?: boolean;
}

const NewChatButton: React.FC<NewChatButtonProps> = ({ onClick, disabled = false }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="w-full p-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white rounded-lg flex items-center justify-center space-x-2 transition-colors font-medium"
    >
      <Plus className="h-5 w-5" />
      <span>New Chat</span>
    </button>
  );
};

// ============================================================================
// API Status Component
// ============================================================================

interface ApiStatusProps {
  isConnected: boolean;
  onRefresh: () => void;
}

const ApiStatus: React.FC<ApiStatusProps> = ({ isConnected, onRefresh }) => {
  return (
    <div className={`p-3 rounded-lg border ${
      isConnected 
        ? 'bg-green-50 border-green-200' 
        : 'bg-red-50 border-red-200'
    }`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {isConnected ? (
            <CheckCircle className="h-4 w-4 text-green-600" />
          ) : (
            <AlertCircle className="h-4 w-4 text-red-600" />
          )}
          <span className={`text-sm font-medium ${
            isConnected ? 'text-green-800' : 'text-red-800'
          }`}>
            API {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        {!isConnected && (
          <button
            onClick={onRefresh}
            className="text-xs text-red-600 hover:text-red-800"
          >
            Retry
          </button>
        )}
      </div>
    </div>
  );
};

// ============================================================================
// Chat History Sidebar Component
// ============================================================================

interface ChatHistoryProps {
  sessions: ChatSession[];
  currentSessionId: string;
  loading: boolean;
  error: string | null;
  onSelectSession: (sessionId: string) => void;
  onNewChat: () => void;
  onDeleteSession: (sessionId: string) => void;
  onRefreshSessions: () => void;
  isConnected: boolean;
  onCheckConnection: () => void;
}

const ChatHistory: React.FC<ChatHistoryProps> = ({
  sessions,
  currentSessionId,
  loading,
  error,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  onRefreshSessions,
  isConnected,
  onCheckConnection
}) => {
  return (
    <div className="h-full flex flex-col bg-gray-50 border-r border-gray-200">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <h2 className="text-lg font-semibold text-gray-800">Chat History</h2>
        <p className="text-sm text-gray-600 mt-1">Your medical conversations</p>
      </div>

      {/* New Chat Button */}
      <div className="p-4">
        <NewChatButton onClick={onNewChat} disabled={loading} />
      </div>

      {/* API Status */}
      <div className="px-4 pb-4">
        <ApiStatus isConnected={isConnected} onRefresh={onCheckConnection} />
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto px-4">
        {loading && sessions.length === 0 && (
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <Activity className="h-8 w-8 text-gray-400 mx-auto mb-2 animate-pulse" />
              <p className="text-sm text-gray-500">Loading chat history...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg mb-4">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-4 w-4 text-red-500" />
              <span className="text-sm text-red-700">Failed to load history</span>
            </div>
            <button
              onClick={onRefreshSessions}
              className="text-xs text-red-600 hover:text-red-800 mt-1"
            >
              Try again
            </button>
          </div>
        )}

        {sessions.length === 0 && !loading && !error && (
          <div className="text-center py-8">
            <MessageSquare className="h-12 w-12 text-gray-300 mx-auto mb-3" />
            <p className="text-sm text-gray-500 mb-2">No chat history yet</p>
            <p className="text-xs text-gray-400">Start your first conversation!</p>
          </div>
        )}

        <div className="space-y-2">
          {sessions.map((session) => (
            <HistoryItem
              key={session.session_id}
              session={session}
              isActive={session.session_id === currentSessionId}
              onClick={() => onSelectSession(session.session_id)}
              onDelete={onDeleteSession}
            />
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <div className="text-xs text-gray-500 text-center">
          <p>{APP_CONFIG.name}</p>
          <p>v{APP_CONFIG.version}</p>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// Header Component
// ============================================================================

interface HeaderProps {
  onToggleSidebar: () => void;
  sidebarOpen: boolean;
  currentSessionId?: string;
  messageCount?: number;
}

const Header: React.FC<HeaderProps> = ({ 
  onToggleSidebar, 
  sidebarOpen, 
  currentSessionId,
  messageCount = 0 
}) => {
  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={onToggleSidebar}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors lg:hidden"
          >
            {sidebarOpen ? (
              <X className="h-5 w-5 text-gray-600" />
            ) : (
              <Menu className="h-5 w-5 text-gray-600" />
            )}
          </button>
          
          <div>
            <h1 className="text-xl font-semibold text-gray-800">
              {APP_CONFIG.name}
            </h1>
            {currentSessionId && (
              <p className="text-sm text-gray-600">
                Session: {currentSessionId.split('-').pop()?.substring(0, 8)} • {messageCount} messages
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="hidden sm:block">
            <div className="px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
              Online
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

// ============================================================================
// Main Layout Component
// ============================================================================

interface LayoutProps {
  children: React.ReactNode;
  sidebar: React.ReactNode;
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
  currentSessionId?: string;
  messageCount?: number;
}

const Layout: React.FC<LayoutProps> = ({ 
  children, 
  sidebar, 
  sidebarOpen, 
  onToggleSidebar,
  currentSessionId,
  messageCount
}) => {
  return (
    <div className="h-screen flex flex-col bg-gray-100">
      {/* Header */}
      <Header 
        onToggleSidebar={onToggleSidebar}
        sidebarOpen={sidebarOpen}
        currentSessionId={currentSessionId}
        messageCount={messageCount}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <div className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 transition-transform duration-300 ease-in-out w-80 flex-shrink-0 lg:relative absolute inset-y-0 left-0 z-50`}>
          {sidebar}
        </div>

        {/* Overlay for mobile */}
        {sidebarOpen && (
          <div 
            className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
            onClick={onToggleSidebar}
          />
        )}

        {/* Main Content */}
        <div className="flex-1 flex flex-col min-w-0">
          {children}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// Error Boundary Component
// ============================================================================

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}

class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback?: React.ReactNode },
  ErrorBoundaryState
> {
  constructor(props: { children: React.ReactNode; fallback?: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.setState({ error, errorInfo });
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full mx-4">
            <div className="bg-white rounded-lg shadow-lg p-6 text-center">
              <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-800 mb-2">
                Something went wrong
              </h2>
              <p className="text-gray-600 mb-4">
                The application encountered an unexpected error. Please refresh the page to try again.
              </p>
              <div className="space-y-2">
                <button
                  onClick={() => window.location.reload()}
                  className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  Refresh Page
                </button>
                <details className="text-left">
                  <summary className="text-sm text-gray-500 cursor-pointer hover:text-gray-700">
                    View Error Details
                  </summary>
                  <div className="mt-2 p-3 bg-gray-100 rounded text-xs text-gray-700 overflow-auto max-h-32">
                    <pre>{this.state.error?.toString()}</pre>
                  </div>
                </details>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// ============================================================================
// Loading Spinner Component
// ============================================================================

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ size = 'md', text }) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <Activity className={`${sizeClasses[size]} text-blue-500 animate-spin mb-2`} />
      {text && (
        <p className="text-sm text-gray-600">{text}</p>
      )}
    </div>
  );
};

// ============================================================================
// Error Message Component
// ============================================================================

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onRetry, onDismiss }) => {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 m-4">
      <div className="flex items-start space-x-3">
        <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="text-sm font-medium text-red-800">
            Error
          </h3>
          <p className="text-sm text-red-700 mt-1">
            {message}
          </p>
          {(onRetry || onDismiss) && (
            <div className="flex space-x-2 mt-3">
              {onRetry && (
                <button
                  onClick={onRetry}
                  className="text-xs bg-red-100 hover:bg-red-200 text-red-800 px-3 py-1 rounded transition-colors"
                >
                  Try Again
                </button>
              )}
              {onDismiss && (
                <button
                  onClick={onDismiss}
                  className="text-xs text-red-600 hover:text-red-800"
                >
                  Dismiss
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// Connection Status Component
// ============================================================================

interface ConnectionStatusProps {
  isConnected: boolean;
  isReconnecting: boolean;
  onReconnect: () => void;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ 
  isConnected, 
  isReconnecting, 
  onReconnect 
}) => {
  if (isConnected) return null;

  return (
    <div className="bg-yellow-50 border-b border-yellow-200 px-4 py-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <AlertCircle className="h-4 w-4 text-yellow-600" />
          <span className="text-sm text-yellow-800">
            {isReconnecting ? 'Reconnecting...' : 'Connection lost'}
          </span>
        </div>
        {!isReconnecting && (
          <button
            onClick={onReconnect}
            className="text-sm text-yellow-700 hover:text-yellow-900 font-medium"
          >
            Reconnect
          </button>
        )}
      </div>
    </div>
  );
};

export { 
  ChatHistory, 
  HistoryItem, 
  NewChatButton, 
  Header, 
  Layout, 
  ErrorBoundary, 
  LoadingSpinner, 
  ErrorMessage, 
  ApiStatus,
  ConnectionStatus 
};