'use client';

import { useState } from 'react';
import { SimulationConfig, MessageRole, Message, VerificationResult } from './types/simulation';
import { SimulationAPI } from './lib/api';
import ConfigPanel from './components/ConfigPanel';
import SimulationRun from './components/SimulationRun';

interface SimulationRunState {
  simulationId: string;
  runNumber: number;
  messages: Message[];
  verificationResult: VerificationResult | null;
  isRunning: boolean;
  currentSpeaker: MessageRole | null;
  streamingContent: { candidate: string; sim: string };
  streamingReasoning: { candidate: string; sim: string };
}

export default function Home() {
  const [config, setConfig] = useState<SimulationConfig | null>(null);
  const [runs, setRuns] = useState<SimulationRunState[]>([]);
  const [isAnyRunning, setIsAnyRunning] = useState(false);

  const handleStartSimulation = async (newConfig: SimulationConfig, numberOfRuns: number) => {
    try {
      setConfig(newConfig);
      setIsAnyRunning(true);

      // Initialize all runs
      const initialRuns: SimulationRunState[] = [];
      for (let i = 0; i < numberOfRuns; i++) {
        initialRuns.push({
          simulationId: '',
          runNumber: i + 1,
          messages: [],
          verificationResult: null,
          isRunning: true,
          currentSpeaker: null,
          streamingContent: { candidate: '', sim: '' },
          streamingReasoning: { candidate: '', sim: '' },
        });
      }
      setRuns(initialRuns);

      // Run all simulations in parallel - COMPLETELY ISOLATED
      const runPromises = initialRuns.map(async (run, index) => {
        try {
          // Create a NEW simulation for this run (complete isolation)
          const { simulation_id } = await SimulationAPI.createSimulation(newConfig);

          // Update this specific run with its simulation ID
          setRuns((prev) => {
            const updated = [...prev];
            updated[index] = { ...updated[index], simulationId: simulation_id };
            return updated;
          });

          // Run this simulation and update ONLY this run's state
          for await (const event of SimulationAPI.runSimulation(simulation_id)) {
            switch (event.type) {
              case 'turn_start':
                setRuns((prev) => {
                  const updated = [...prev];
                  updated[index] = {
                    ...updated[index],
                    currentSpeaker: event.speaker === 'candidate' ? MessageRole.CANDIDATE : MessageRole.SIM,
                    streamingContent: { candidate: '', sim: '' },
                    streamingReasoning: { candidate: '', sim: '' },
                  };
                  return updated;
                });
                break;

              case 'content_delta':
                const contentSpeaker = event.speaker as 'candidate' | 'sim';
                setRuns((prev) => {
                  const updated = [...prev];
                  updated[index] = {
                    ...updated[index],
                    streamingContent: {
                      ...updated[index].streamingContent,
                      [contentSpeaker]: updated[index].streamingContent[contentSpeaker] + event.delta,
                    },
                  };
                  return updated;
                });
                break;

              case 'reasoning_delta':
                const reasoningSpeaker = event.speaker as 'candidate' | 'sim';
                setRuns((prev) => {
                  const updated = [...prev];
                  updated[index] = {
                    ...updated[index],
                    streamingReasoning: {
                      ...updated[index].streamingReasoning,
                      [reasoningSpeaker]: updated[index].streamingReasoning[reasoningSpeaker] + event.delta,
                    },
                  };
                  return updated;
                });
                break;

              case 'message_complete':
                setRuns((prev) => {
                  const updated = [...prev];
                  updated[index] = {
                    ...updated[index],
                    messages: [...updated[index].messages, event.message as Message],
                    streamingContent: { candidate: '', sim: '' },
                    streamingReasoning: { candidate: '', sim: '' },
                    currentSpeaker: null,
                  };
                  return updated;
                });
                break;

              case 'verification_complete':
                setRuns((prev) => {
                  const updated = [...prev];
                  updated[index] = {
                    ...updated[index],
                    verificationResult: event.result as VerificationResult,
                  };
                  return updated;
                });
                break;

              case 'simulation_complete':
                setRuns((prev) => {
                  const updated = [...prev];
                  updated[index] = {
                    ...updated[index],
                    isRunning: false,
                    currentSpeaker: null,
                  };
                  return updated;
                });
                break;

              case 'error':
                console.error(`Run ${index + 1} error:`, event.message);
                setRuns((prev) => {
                  const updated = [...prev];
                  updated[index] = {
                    ...updated[index],
                    isRunning: false,
                    currentSpeaker: null,
                  };
                  return updated;
                });
                break;
            }
          }
        } catch (error) {
          console.error(`Failed to run simulation ${index + 1}:`, error);
          setRuns((prev) => {
            const updated = [...prev];
            updated[index] = {
              ...updated[index],
              isRunning: false,
            };
            return updated;
          });
        }
      });

      // Wait for all runs to complete
      await Promise.all(runPromises);
      setIsAnyRunning(false);
    } catch (error) {
      console.error('Failed to start simulations:', error);
      alert('Failed to start simulations. Check console for details.');
      setIsAnyRunning(false);
    }
  };

  // Calculate pass@k statistics
  const completedRuns = runs.filter((r) => r.verificationResult !== null);
  const passedRuns = completedRuns.filter((r) => r.verificationResult?.success);
  const passRate = completedRuns.length > 0 ? (passedRuns.length / completedRuns.length) * 100 : 0;

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          Agent Simulation Platform
        </h1>

        <ConfigPanel onStartSimulation={handleStartSimulation} isRunning={isAnyRunning} />

        {/* Pass@k Statistics */}
        {runs.length > 0 && (
          <div className="bg-white border-2 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-bold mb-4">Pass@{runs.length} Statistics</h2>
            <div className="grid grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">{runs.length}</div>
                <div className="text-sm text-gray-600">Total Runs</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">{passedRuns.length}</div>
                <div className="text-sm text-gray-600">Passed</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-red-600">
                  {completedRuns.length - passedRuns.length}
                </div>
                <div className="text-sm text-gray-600">Failed</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">{passRate.toFixed(1)}%</div>
                <div className="text-sm text-gray-600">Pass Rate</div>
              </div>
            </div>
          </div>
        )}

        {/* Simulation Runs */}
        <div className="space-y-6">
          {runs.map((run, index) => (
            config && (
              <SimulationRun
                key={`${run.simulationId}-${index}`}
                runNumber={run.runNumber}
                config={config}
                messages={run.messages}
                verificationResult={run.verificationResult}
                isRunning={run.isRunning}
                currentSpeaker={run.currentSpeaker}
                streamingContent={run.streamingContent}
                streamingReasoning={run.streamingReasoning}
              />
            )
          ))}
        </div>
      </div>
    </div>
  );
}
