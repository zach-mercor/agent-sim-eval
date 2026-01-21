'use client';

import { Message, MessageRole } from '../types/simulation';
import MessageBubble from './MessageBubble';
import { useRef, useEffect, useState } from 'react';

interface AgentPanelProps {
  title: string;
  role: MessageRole;
  model: string;
  messages: Message[];
  isStreaming: boolean;
  streamingContent?: string;
  streamingReasoning?: string;
  onModelChange?: (model: string) => void;
  availableModels?: string[];
  onEditMessage?: (turnNumber: number, content: string, reasoning?: string) => void;
  onRerunFromTurn?: (turnNumber: number) => void;
}

export default function AgentPanel({
  title,
  role,
  model,
  messages,
  isStreaming,
  streamingContent,
  streamingReasoning,
  onModelChange,
  availableModels,
  onEditMessage,
  onRerunFromTurn,
}: AgentPanelProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [userHasScrolled, setUserHasScrolled] = useState(false);

  const isScrolledToBottom = () => {
    if (!scrollContainerRef.current) return true;
    const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
    return scrollHeight - scrollTop - clientHeight < 50; // 50px threshold
  };

  const scrollToBottom = () => {
    // Only auto-scroll if user hasn't manually scrolled up
    if (!userHasScrolled || isScrolledToBottom()) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      setUserHasScrolled(false);
    }
  };

  const handleScroll = () => {
    if (isScrolledToBottom()) {
      setUserHasScrolled(false);
    } else {
      setUserHasScrolled(true);
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent, streamingReasoning]);

  const filteredMessages = messages.filter((msg) => msg.role === role);

  const titleColor = role === MessageRole.CANDIDATE ? 'bg-blue-600' : 'bg-green-600';

  return (
    <div className="flex flex-col h-full border rounded-lg overflow-hidden">
      {/* Header */}
      <div className={`${titleColor} text-white p-4`}>
        <h2 className="text-lg font-bold mb-2">{title}</h2>
        {onModelChange && availableModels ? (
          <select
            value={model}
            onChange={(e) => onModelChange(e.target.value)}
            className="w-full p-2 text-sm text-gray-800 rounded"
          >
            {availableModels.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        ) : (
          <div className="text-sm opacity-90">{model}</div>
        )}
      </div>

      {/* Messages */}
      <div
        ref={scrollContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto p-4 bg-gray-50"
      >
        {filteredMessages.length === 0 && !isStreaming && (
          <div className="text-center text-gray-500 mt-8">
            No messages yet
          </div>
        )}

        {filteredMessages.map((message) => (
          <MessageBubble
            key={message.turn_number}
            message={message}
            isEditable={true}
            onEdit={(content, reasoning) => {
              if (onEditMessage) {
                onEditMessage(message.turn_number, content, reasoning);
              }
            }}
            onRerun={() => {
              if (onRerunFromTurn) {
                onRerunFromTurn(message.turn_number + 1);
              }
            }}
          />
        ))}

        {/* Streaming message */}
        {isStreaming && (streamingContent || streamingReasoning) && (
          <div className={`border-2 rounded-xl overflow-hidden mb-4 shadow-sm ${
            role === MessageRole.CANDIDATE ? 'bg-blue-50 border-blue-200' : 'bg-green-50 border-green-200'
          }`}>
            {/* Header */}
            <div className="flex items-center gap-3 px-4 py-2 bg-white border-b-2 border-gray-200">
              <span className="text-xs font-bold text-gray-700 uppercase tracking-wide">
                Turn {filteredMessages.length + 1}
              </span>
              <span className="flex items-center gap-2 text-xs text-yellow-600 font-medium">
                <span className="inline-block w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></span>
                Streaming...
              </span>
            </div>

            <div className="bg-white">
              {/* Chain of Thought - Streaming */}
              {streamingReasoning && (
                <div className="border-b-4 border-gray-200">
                  <div className="flex items-center gap-3 px-4 py-3 bg-gradient-to-r from-purple-50 to-purple-100">
                    <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    <span className="text-sm font-bold text-purple-700 uppercase tracking-wide">
                      Chain of Thought
                    </span>
                  </div>
                  <div className="px-4 py-4 bg-gradient-to-br from-purple-50 via-purple-25 to-white">
                    <div className="text-xs font-mono text-purple-900 leading-relaxed whitespace-pre-wrap">
                      {streamingReasoning}
                      <span className="inline-block w-2 h-3 bg-purple-400 ml-1 animate-pulse"></span>
                    </div>
                  </div>
                </div>
              )}

              {/* Model Output - Streaming */}
              {streamingContent && (
                <div>
                  <div className="flex items-center gap-3 px-4 py-3 bg-gradient-to-r from-blue-50 to-blue-100 border-b-2 border-blue-200">
                    <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                    <span className="text-sm font-bold text-blue-700 uppercase tracking-wide">
                      Model Output
                    </span>
                  </div>
                  <div className="px-4 py-4 bg-white">
                    <div className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">
                      {streamingContent}
                      <span className="inline-block w-2 h-4 bg-blue-400 ml-1 animate-pulse"></span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
