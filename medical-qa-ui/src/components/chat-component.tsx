// ============================================================================
// Chat Interface Components
// ============================================================================

import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, RotateCcw, Copy, Download, AlertCircle, User, Bot, Clock, Star, FileText } from 'lucide-react';
import { ChatMessage, ContextDocument } from '../services/types';
import { formatTime, getEvaluationColor, getEvaluationLabel, validateMessage, formatResponseTime, copyToClipboard } from '../utils/helpers';
import { SAMPLE_QUESTIONS } from '../utils/constants';

// ============================================================================
// Loading Indicator Component
// ============================================================================

interface LoadingIndicatorProps {
  text?: string;
}

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ text = "AI is thinking..." }) => {
  return (
    <div className="flex items-center space-x-2 p-4 bg-gray-50 rounded-lg max-w-xs">
      <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
      <span className="text-sm text-gray-600">{text}</span>
      <div className="flex space-x-1">
        <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
        <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
        <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
      </div>
    </div>
  );
};

// ============================================================================
// Evaluation Score Component
// ============================================================================

interface EvaluationScoreProps {
  score?: number;
  responseTime?: number;
  compact?: boolean;
}

const EvaluationScore: React.FC<EvaluationScoreProps> = ({ score, responseTime, compact = false }) => {
  if (!score && !responseTime) return null;

  const scoreColor = getEvaluationColor(score);
  const scoreLabel = getEvaluationLabel(score);

  if (compact) {
    return (
      <div className="flex items-center space-x-2 text-xs text-gray-500">
        {score && (
          <div className="flex items-center space-x-1">
            <Star className="h-3 w-3" />
            <span className={scoreColor}>{(score * 100).toFixed(0)}%</span>
          </div>
        )}
        {responseTime && (
          <div className="flex items-center space-x-1">
            <Clock className="h-3 w-3" />
            <span>{formatResponseTime(responseTime)}</span>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="mt-2 p-2 bg-gray-50 rounded-lg border">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Star className="h-4 w-4 text-yellow-500" />
          <span className="text-sm font-medium text-gray-700">Response Quality</span>
        </div>
        {score && (
          <div className="flex items-center space-x-2">
            <span className={`text-sm font-semibold ${scoreColor}`}>{scoreLabel}</span>
            <span className={`text-xs ${scoreColor}`}>({(score * 100).toFixed(0)}%)</span>
          </div>
        )}
      </div>
      {responseTime && (
        <div className="flex items-center space-x-2 mt-1">
          <Clock className="h-3 w-3 text-gray-400" />
          <span className="text-xs text-gray-500">Response time: {formatResponseTime(responseTime)}</span>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// Context Sources Component
// ============================================================================

interface ContextSourcesProps {
  contexts: ContextDocument[];
}

const ContextSources: React.FC<ContextSourcesProps> = ({ contexts }) => {
  if (!contexts || contexts.length === 0) return null;

  return (
    <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
      <div className="flex items-center space-x-2 mb-2">
        <FileText className="h-4 w-4 text-blue-600" />
        <span className="text-sm font-medium text-blue-800">Knowledge Sources</span>
      </div>
      <div className="space-y-2">
        {contexts.slice(0, 3).map((context, index) => (
          <div key={index} className="text-xs bg-white p-2 rounded border">
            <div className="font-medium text-gray-700 mb-1">{context.question}</div>
            <div className="text-gray-600 line-clamp-2">{context.answer.substring(0, 100)}...</div>
            <div className="flex justify-between items-center mt-1">
              {context.category && (
                <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
                  {context.category}
                </span>
              )}
              <span className="text-gray-500">
                Relevance: {(context.similarity_score * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ============================================================================
// Message Bubble Component
// ============================================================================

interface MessageBubbleProps {
  message: ChatMessage;
  onRetry?: () => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onRetry }) => {
  const [copied, setCopied] = useState(false);
  const isUser = message.message_type === 'user';
  const isError = message.content.includes('❌ Error:');

  const handleCopy = async () => {
    const success = await copyToClipboard(message.content);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-2 max-w-[85%]`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-blue-500 ml-2' : 'bg-gray-200 mr-2'
        }`}>
          {isUser ? (
            <User className="h-4 w-4 text-white" />
          ) : (
            <Bot className={`h-4 w-4 ${isError ? 'text-red-500' : 'text-gray-600'}`} />
          )}
        </div>

        {/* Message Content */}
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          <div className={`px-4 py-2 rounded-lg ${
            isUser 
              ? 'bg-blue-500 text-white' 
              : isError
                ? 'bg-red-50 border border-red-200 text-red-800'
                : 'bg-gray-100 text-gray-800'
          }`}>
            <div className="whitespace-pre-wrap break-words">
              {message.content}
            </div>
            
            {/* Action Buttons */}
            {!isUser && (
              <div className="flex items-center space-x-2 mt-2 pt-2 border-t border-gray-200">
                <button
                  onClick={handleCopy}
                  className="text-xs text-gray-500 hover:text-gray-700 flex items-center space-x-1"
                  title="Copy message"
                >
                  <Copy className="h-3 w-3" />
                  <span>{copied ? 'Copied!' : 'Copy'}</span>
                </button>
                
                {isError && onRetry && (
                  <button
                    onClick={onRetry}
                    className="text-xs text-blue-500 hover:text-blue-700 flex items-center space-x-1"
                    title="Retry message"
                  >
                    <RotateCcw className="h-3 w-3" />
                    <span>Retry</span>
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Timestamp */}
          <div className="text-xs text-gray-500 mt-1 px-1">
            {formatTime(message.timestamp)}
          </div>

          {/* Evaluation Score for Assistant Messages */}
          {!isUser && !isError && (
            <EvaluationScore 
              score={message.evaluation_score} 
              compact={true}
            />
          )}

          {/* Context Sources for Assistant Messages */}
          {!isUser && !isError && message.retrieved_context && message.retrieved_context.length > 0 && (
            <ContextSources contexts={message.retrieved_context} />
          )}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// Message Input Component
// ============================================================================

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

const MessageInput: React.FC<MessageInputProps> = ({ 
  onSendMessage, 
  disabled = false, 
  placeholder = "Ask a medical question..." 
}) => {
  const [message, setMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const validation = validateMessage(message);
    
    if (!validation.isValid) {
      setError(validation.error || 'Invalid message');
      return;
    }

    onSendMessage(message);
    setMessage('');
    setError(null);
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleSampleQuestion = (question: string) => {
    setMessage(question);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  return (
    <div className="border-t bg-white p-4">
      {/* Sample Questions */}
      {message === '' && (
        <div className="mb-4">
          <div className="text-sm text-gray-600 mb-2">Try asking:</div>
          <div className="flex flex-wrap gap-2">
            {SAMPLE_QUESTIONS.slice(0, 3).map((question, index) => (
              <button
                key={index}
                onClick={() => handleSampleQuestion(question)}
                className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
                disabled={disabled}
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-3 p-2 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2">
          <AlertCircle className="h-4 w-4 text-red-500" />
          <span className="text-sm text-red-700">{error}</span>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex space-x-2">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none max-h-32"
            style={{ minHeight: '42px' }}
          />
          <div className="absolute bottom-2 right-2 text-xs text-gray-400">
            {message.length}/2000
          </div>
        </div>
        
        <button
          type="submit"
          disabled={disabled || !message.trim()}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center min-w-[44px]"
        >
          {disabled ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <Send className="h-5 w-5" />
          )}
        </button>
      </form>
    </div>
  );
};

// ============================================================================
// Main Chat Interface Component
// ============================================================================

interface ChatInterfaceProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSendMessage: (message: string) => void;
  onRetryMessage?: () => void;
  error?: string | null;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ 
  messages, 
  isLoading, 
  onSendMessage, 
  onRetryMessage,
  error 
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isLoading]);

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Chat Messages */}
      <div 
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-4"
      >
        {messages.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <Bot className="h-16 w-16 text-gray-300 mb-4" />
            <h2 className="text-xl font-semibold text-gray-700 mb-2">
              Medical Q&A Assistant
            </h2>
            <p className="text-gray-500 max-w-md">
              Ask me any medical or healthcare-related question. I'll provide evidence-based information to help you learn.
            </p>
            <p className="text-xs text-gray-400 mt-2">
              Remember: This is for educational purposes only. Always consult healthcare professionals for personal medical advice.
            </p>
          </div>
        )}

        {messages.map((message) => (
          <MessageBubble 
            key={message.id} 
            message={message} 
            onRetry={onRetryMessage}
          />
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <LoadingIndicator text="Analyzing your question..." />
          </div>
        )}

        {error && (
          <div className="flex justify-center">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 max-w-md">
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-red-500" />
                <span className="text-sm text-red-700">Connection Error</span>
              </div>
              <p className="text-sm text-red-600 mt-1">{error}</p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <MessageInput 
        onSendMessage={onSendMessage}
        disabled={isLoading}
        placeholder="Ask about symptoms, conditions, treatments, or general medical information..."
      />
    </div>
  );
};

export { ChatInterface, MessageBubble, MessageInput, LoadingIndicator, EvaluationScore, ContextSources };