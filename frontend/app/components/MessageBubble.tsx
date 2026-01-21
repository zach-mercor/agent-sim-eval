'use client';

import { Message, MessageRole } from '../types/simulation';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MessageBubbleProps {
  message: Message;
  isEditable: boolean;
  onEdit?: (content: string, reasoning?: string) => void;
  onRerun?: () => void;
}

export default function MessageBubble({ message, isEditable, onEdit, onRerun }: MessageBubbleProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(message.content);
  const [editedReasoning, setEditedReasoning] = useState(message.reasoning || '');
  const [showReasoning, setShowReasoning] = useState(false);

  const handleSave = () => {
    if (onEdit) {
      onEdit(editedContent, editedReasoning || undefined);
    }
    setIsEditing(false);
  };

  const handleRerun = () => {
    handleSave();
    if (onRerun) {
      onRerun();
    }
  };

  const bgColor = message.role === MessageRole.CANDIDATE
    ? 'bg-blue-50 border-blue-200'
    : 'bg-green-50 border-green-200';

  return (
    <div className={`border-2 rounded-xl overflow-hidden mb-4 ${bgColor} shadow-sm`}>
      {/* Header */}
      <div className="flex justify-between items-center px-4 py-2 bg-white border-b-2 border-gray-200">
        <div className="flex items-center gap-3">
          <span className="text-xs font-bold text-gray-700 uppercase tracking-wide">
            Turn {message.turn_number}
          </span>
          <span className="text-xs text-gray-500">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        </div>
        {isEditable && !isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="text-xs font-medium text-blue-600 hover:text-blue-800 hover:underline"
          >
            Edit
          </button>
        )}
      </div>

      {isEditing ? (
        <div className="p-4 space-y-4 bg-white">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wide">
              Content
            </label>
            <textarea
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              className="w-full p-3 border-2 border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows={6}
            />
          </div>

          {message.reasoning && (
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wide">
                Reasoning
              </label>
              <textarea
                value={editedReasoning}
                onChange={(e) => setEditedReasoning(e.target.value)}
                className="w-full p-3 border-2 border-gray-300 rounded-lg text-sm font-mono bg-gray-50 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                rows={5}
              />
            </div>
          )}

          <div className="flex gap-2 pt-2">
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Save (Edit Mode)
            </button>
            <button
              onClick={handleRerun}
              className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
            >
              Save & Rerun
            </button>
            <button
              onClick={() => {
                setEditedContent(message.content);
                setEditedReasoning(message.reasoning || '');
                setIsEditing(false);
              }}
              className="px-4 py-2 bg-gray-200 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-300 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-white">
          {/* Chain of Thought Section - Much more distinct */}
          {message.reasoning && (
            <div className="border-b-4 border-gray-200">
              <button
                onClick={() => setShowReasoning(!showReasoning)}
                className="w-full flex items-center justify-between px-4 py-3 bg-gradient-to-r from-purple-50 to-purple-100 hover:from-purple-100 hover:to-purple-150 transition-all"
              >
                <div className="flex items-center gap-3">
                  <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <span className="text-sm font-bold text-purple-700 uppercase tracking-wide">
                    Chain of Thought
                  </span>
                  <span className="text-xs text-purple-600 font-medium">
                    {showReasoning ? 'Click to hide' : 'Click to expand'}
                  </span>
                </div>
                <svg
                  className={`w-5 h-5 text-purple-600 transition-transform ${showReasoning ? 'rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              {showReasoning && (
                <div className="px-4 py-4 bg-gradient-to-br from-purple-50 via-purple-25 to-white">
                  <div className="prose prose-sm prose-purple max-w-none">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      className="text-xs font-mono text-purple-900 leading-relaxed"
                      components={{
                        p: ({ children }) => <p className="mb-2">{children}</p>,
                        code: ({ children }) => <code className="bg-purple-100 px-1 py-0.5 rounded text-purple-800">{children}</code>,
                        pre: ({ children }) => <pre className="bg-purple-100 p-2 rounded-lg overflow-x-auto">{children}</pre>,
                      }}
                    >
                      {message.reasoning}
                    </ReactMarkdown>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Model Output Section - Clearly separated */}
          <div className={message.reasoning ? 'bg-white' : ''}>
            <div className="flex items-center gap-3 px-4 py-3 bg-gradient-to-r from-blue-50 to-blue-100 border-b-2 border-blue-200">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              <span className="text-sm font-bold text-blue-700 uppercase tracking-wide">
                Model Output
              </span>
            </div>
            <div className="px-4 py-4 bg-white">
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  className="text-sm text-gray-800 leading-relaxed"
                  components={{
                    h1: ({ children }) => <h1 className="text-xl font-bold mb-3 text-gray-900">{children}</h1>,
                    h2: ({ children }) => <h2 className="text-lg font-bold mb-2 text-gray-900">{children}</h2>,
                    h3: ({ children }) => <h3 className="text-base font-bold mb-2 text-gray-900">{children}</h3>,
                    p: ({ children }) => <p className="mb-3">{children}</p>,
                    ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>,
                    li: ({ children }) => <li className="ml-2">{children}</li>,
                    code: ({ children }) => <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm text-gray-800 font-mono">{children}</code>,
                    pre: ({ children }) => <pre className="bg-gray-100 p-3 rounded-lg overflow-x-auto mb-3">{children}</pre>,
                    blockquote: ({ children }) => <blockquote className="border-l-4 border-blue-400 pl-4 italic my-3 text-gray-700">{children}</blockquote>,
                    strong: ({ children }) => <strong className="font-bold text-gray-900">{children}</strong>,
                    em: ({ children }) => <em className="italic">{children}</em>,
                    a: ({ children, href }) => <a href={href} className="text-blue-600 hover:text-blue-800 underline" target="_blank" rel="noopener noreferrer">{children}</a>,
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
