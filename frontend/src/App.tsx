import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, AlertCircle, CheckCircle, Key, Copy, Settings, FileText, BarChart3 } from 'lucide-react';
import { Message, ChatRequest, APIExecutionRequest } from './types';
import ApiService from './services/api';
import MessageRenderer from './components/MessageRender';
import LoadingIndicator from './components/LoadingIndicator';

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your **Conga CPQ Turbo API** troubleshooting assistant. I can help you with:\n\n- 🔐 **Authentication issues** (401, 403 errors)\n- 📋 **API endpoints** and payload structures\n- ⚡ **Performance problems** and timeouts\n- 🛠️ **Error code explanations**\n- 🔄 **Rate limiting** and best practices\n\nWhat can I help you troubleshoot today?',
      timestamp: new Date(),
      contextUsed: false,
      confidenceScore: 1.0
    }
  ]);
  
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [bearerToken, setBearerToken] = useState('');
  const [showTokenInput, setShowTokenInput] = useState(false);
  const [apiExecutionPending, setApiExecutionPending] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'error'>('connecting');

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Check API connection on mount
  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      await ApiService.healthCheck();
      setConnectionStatus('connected');
    } catch (error) {
      setConnectionStatus('error');
      setError('Unable to connect to the API server. Please ensure it\'s running on port 8000.');
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (message: string, token?: string) => {
    if (!message.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      const request: ChatRequest = {
        query: message,
        conversation_id: conversationId || undefined,
        bearer_token: token || bearerToken || undefined,
        include_context: true
      };

      const response = await ApiService.sendMessage(request);

      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        contextUsed: response.context_used,
        confidenceScore: response.confidence_score,
        requiresApiExecution: response.requires_api_execution,
        apiInfo: response.api_info,
        suggestedFollowUps: response.suggested_follow_ups
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Check if API execution is required
      if (response.requires_api_execution && response.api_info) {
        if (!bearerToken) {
          setApiExecutionPending(response.api_info);
          setShowTokenInput(true);
        } else {
          // Execute API automatically if token is available
          await executeApi(response.api_info, bearerToken);
        }
      }

    } catch (err) {
      const errorMessage = ApiService.handleError(err);
      setError(errorMessage);
      
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I apologize, but I encountered an error: **${errorMessage}**\n\nPlease try again or check if the API server is running.`,
        timestamp: new Date(),
        contextUsed: false,
        confidenceScore: 0.0
      };
      
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const executeApi = async (apiInfo: any, token: string, payload?: any) => {
    setIsLoading(true);
    
    try {
      const request: APIExecutionRequest = {
        api_endpoint: apiInfo.endpoint,
        bearer_token: token,
        payload: payload || undefined
      };

      const result = await ApiService.executeAPI(request);

      const apiResultMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `## 🚀 API Execution Result\n\n**Status**: ${result.success ? '✅ Success' : '❌ Failed'}\n**Status Code**: \`${result.status_code}\`\n\n**Response Data**:\n\`\`\`json\n${JSON.stringify(result.data, null, 2)}\n\`\`\`${result.error ? `\n\n**Error**: ${result.error}` : ''}`,
        timestamp: new Date(),
        contextUsed: false,
        confidenceScore: result.success ? 1.0 : 0.5
      };

      setMessages(prev => [...prev, apiResultMessage]);
      setApiExecutionPending(null);
      setShowTokenInput(false);

    } catch (err) {
      const errorMessage = ApiService.handleError(err);
      setError(errorMessage);
      
      const errorResponse: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `**API execution failed**: ${errorMessage}`,
        timestamp: new Date(),
        contextUsed: false,
        confidenceScore: 0.0
      };
      
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = () => {
    sendMessage(inputValue);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleTokenSubmit = () => {
    if (bearerToken && apiExecutionPending) {
      executeApi(apiExecutionPending, bearerToken);
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    sendMessage(question);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const formatConfidenceScore = (score?: number) => {
    if (!score) return '';
    return `${(score * 100).toFixed(0)}%`;
  };

  const clearConversation = () => {
    setMessages([{
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your **Conga CPQ Turbo API** troubleshooting assistant. I can help you with:\n\n- 🔐 **Authentication issues** (401, 403 errors)\n- 📋 **API endpoints** and payload structures\n- ⚡ **Performance problems** and timeouts\n- 🛠️ **Error code explanations**\n- 🔄 **Rate limiting** and best practices\n\nWhat can I help you troubleshoot today?',
      timestamp: new Date(),
      contextUsed: false,
      confidenceScore: 1.0
    }]);
    setConversationId(null);
    setError(null);
  };

  return (
    <div className="flex flex-col h-screen max-w-5xl mx-auto bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-primary-100 p-2 rounded-xl">
              <Bot className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                Conga CPQ Turbo API Assistant
              </h1>
              <div className="flex items-center space-x-2 text-sm">
                <span className="text-gray-500">AI-Powered Troubleshooting Helper</span>
                <div className="flex items-center space-x-1">
                  <div className={`w-2 h-2 rounded-full ${
                    connectionStatus === 'connected' ? 'bg-green-500' : 
                    connectionStatus === 'connecting' ? 'bg-yellow-500' : 'bg-red-500'
                  }`} />
                  <span className={`text-xs ${
                    connectionStatus === 'connected' ? 'text-green-600' : 
                    connectionStatus === 'connecting' ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {connectionStatus === 'connected' ? 'Connected' : 
                     connectionStatus === 'connecting' ? 'Connecting...' : 'Disconnected'}
                  </span>
                </div>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            {conversationId && (
              <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
                Session: {conversationId.slice(0, 8)}...
              </span>
            )}
            <button
              onClick={clearConversation}
              className="text-gray-400 hover:text-gray-600 p-2 rounded-lg hover:bg-gray-100"
              title="Clear conversation"
            >
              <FileText className="w-4 h-4" />
            </button>
            <button
              onClick={checkConnection}
              className="text-gray-400 hover:text-gray-600 p-2 rounded-lg hover:bg-gray-100"
              title="Check connection"
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 mx-6 mt-4 rounded animate-slide-up">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-400 mr-2" />
            <p className="text-red-700">{error}</p>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-400 hover:text-red-600"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Token Input Modal */}
      {showTokenInput && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mx-6 mt-4 rounded animate-slide-up">
          <div className="flex items-start">
            <Key className="w-5 h-5 text-yellow-400 mr-2 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-yellow-800 font-medium">Bearer Token Required</h3>
              <p className="text-yellow-700 text-sm mt-1">
                This operation requires API execution. Please provide your bearer token:
              </p>
              <div className="mt-3 flex space-x-2">
                <input
                  type="password"
                  value={bearerToken}
                  onChange={(e) => setBearerToken(e.target.value)}
                  placeholder="Bearer token..."
                  className="flex-1 px-3 py-2 border border-yellow-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                />
                <button
                  onClick={handleTokenSubmit}
                  disabled={!bearerToken}
                  className="px-4 py-2 bg-yellow-600 text-white rounded-md text-sm hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Execute API
                </button>
                <button
                  onClick={() => {
                    setShowTokenInput(false);
                    setApiExecutionPending(null);
                  }}
                  className="px-3 py-2 text-yellow-600 border border-yellow-300 rounded-md text-sm hover:bg-yellow-100 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6 custom-scrollbar">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start space-x-3 animate-fade-in ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.role === 'assistant' && (
              <div className="bg-primary-100 p-2 rounded-full flex-shrink-0">
                <Bot className="w-5 h-5 text-primary-600" />
              </div>
            )}
            
            <div
              className={`message-bubble ${
                message.role === 'user'
                  ? 'user-bubble'
                  : 'assistant-bubble'
              }`}
            >
              <MessageRenderer 
                content={message.content}
                className={message.role === 'user' ? 'text-white' : 'text-gray-900'}
              />
              
              {/* Message metadata */}
              {message.role === 'assistant' && (
                <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
                  <div className="flex items-center space-x-4 text-xs text-gray-500">
                    {message.contextUsed && (
                      <span className="flex items-center">
                        <CheckCircle className="w-3 h-3 mr-1 text-green-500" />
                        Context Used
                      </span>
                    )}
                    {message.confidenceScore !== undefined && (
                      <span>
                        Confidence: {formatConfidenceScore(message.confidenceScore)}
                      </span>
                    )}
                    <span>{message.timestamp.toLocaleTimeString()}</span>
                  </div>
                  <button
                    onClick={() => copyToClipboard(message.content)}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                    title="Copy message"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                </div>
              )}

              {/* API Info */}
              {message.apiInfo && (
                <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <h4 className="font-medium text-blue-900 text-sm">🔗 API Information:</h4>
                  <div className="mt-2 space-y-1 text-xs text-blue-800">
                    <div><strong>Endpoint:</strong> <code className="bg-blue-100 px-1 rounded">{message.apiInfo.method} {message.apiInfo.endpoint}</code></div>
                    <div><strong>Description:</strong> {message.apiInfo.description}</div>
                  </div>
                </div>
              )}

              {/* Suggested follow-ups */}
              {message.suggestedFollowUps && message.suggestedFollowUps.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs text-gray-500 mb-2">💡 Suggested follow-ups:</p>
                  <div className="space-y-1">
                    {message.suggestedFollowUps.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => handleSuggestedQuestion(suggestion)}
                        className="block w-full text-left text-xs text-primary-600 hover:text-primary-800 hover:bg-primary-50 px-2 py-1 rounded border border-primary-200 transition-colors"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {message.role === 'user' && (
              <div className="bg-gray-100 p-2 rounded-full flex-shrink-0">
                <User className="w-5 h-5 text-gray-600" />
              </div>
            )}
          </div>
        ))}

        {/* Typing indicator */}
        {isLoading && (
          <div className="flex items-start space-x-3 animate-fade-in">
            <div className="bg-primary-100 p-2 rounded-full">
              <Bot className="w-5 h-5 text-primary-600" />
            </div>
            <div className="assistant-bubble">
              <LoadingIndicator type="dots" size="md" />
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 bg-white px-6 py-4">
        <div className="flex space-x-3">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about API troubleshooting, error codes, authentication..."
            disabled={isLoading || connectionStatus !== 'connected'}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          />
          <button
            onClick={handleSubmit}
            disabled={isLoading || !inputValue.trim() || connectionStatus !== 'connected'}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center transition-all"
          >
            {isLoading ? (
              <LoadingIndicator type="spinner" size="sm" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
        
        <div className="mt-2 text-xs text-gray-500 text-center">
          Ask questions about Conga CPQ Turbo API troubleshooting, authentication, error codes, and more.
        </div>
      </div>
    </div>
  );
};

export default App;