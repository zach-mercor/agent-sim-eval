'use client';

import { Message, MessageRole, VerificationResult, SimulationConfig } from '../types/simulation';
import AgentPanel from './AgentPanel';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface SimulationRunProps {
  runNumber: number;
  config: SimulationConfig;
  messages: Message[];
  verificationResult: VerificationResult | null;
  isRunning: boolean;
  currentSpeaker: MessageRole | null;
  streamingContent: { candidate: string; sim: string };
  streamingReasoning: { candidate: string; sim: string };
}

export default function SimulationRun({
  runNumber,
  config,
  messages,
  verificationResult,
  isRunning,
  currentSpeaker,
  streamingContent,
  streamingReasoning,
}: SimulationRunProps) {
  return (
    <div className="border-2 rounded-lg p-4 bg-white">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Run #{runNumber}</h3>
        {verificationResult && (
          <span
            className={`px-3 py-1 rounded-full text-sm font-semibold ${
              verificationResult.success
                ? 'bg-green-100 text-green-700'
                : 'bg-red-100 text-red-700'
            }`}
          >
            {verificationResult.success ? '✓ PASSED' : '✗ FAILED'}
          </span>
        )}
        {isRunning && !verificationResult && (
          <span className="px-3 py-1 rounded-full text-sm font-semibold bg-yellow-100 text-yellow-700">
            ⏳ Running...
          </span>
        )}
      </div>

      {/* Two-panel view */}
      <div className="grid grid-cols-2 gap-4 h-[500px]">
        <AgentPanel
          title="Candidate"
          role={MessageRole.CANDIDATE}
          model={config.candidate_config.model}
          messages={messages}
          isStreaming={isRunning && currentSpeaker === MessageRole.CANDIDATE}
          streamingContent={streamingContent.candidate}
          streamingReasoning={streamingReasoning.candidate}
        />

        <AgentPanel
          title="Sim"
          role={MessageRole.SIM}
          model={config.sim_config.model}
          messages={messages}
          isStreaming={isRunning && currentSpeaker === MessageRole.SIM}
          streamingContent={streamingContent.sim}
          streamingReasoning={streamingReasoning.sim}
        />
      </div>

      {/* Verification Result */}
      {verificationResult && (
        <div className={`mt-4 rounded-xl overflow-hidden border-2 shadow-md ${
          verificationResult.success
            ? 'border-green-300 bg-green-50'
            : 'border-red-300 bg-red-50'
        }`}>
          <div className={`flex items-center gap-3 px-4 py-3 ${
            verificationResult.success
              ? 'bg-gradient-to-r from-green-100 to-green-200'
              : 'bg-gradient-to-r from-red-100 to-red-200'
          }`}>
            {verificationResult.success ? (
              <svg className="w-6 h-6 text-green-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ) : (
              <svg className="w-6 h-6 text-red-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
            <span className={`text-lg font-bold uppercase tracking-wide ${
              verificationResult.success ? 'text-green-800' : 'text-red-800'
            }`}>
              Verification: {verificationResult.success ? 'PASSED' : 'FAILED'}
            </span>
          </div>
          <div className="px-4 py-4 bg-white">
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                className="text-sm text-gray-800 leading-relaxed"
                components={{
                  p: ({ children }) => <p className="mb-2">{children}</p>,
                  ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                  ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                  strong: ({ children }) => <strong className="font-bold text-gray-900">{children}</strong>,
                  em: ({ children }) => <em className="italic">{children}</em>,
                  code: ({ children }) => <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono">{children}</code>,
                }}
              >
                {verificationResult.explanation}
              </ReactMarkdown>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
