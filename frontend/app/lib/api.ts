import { SimulationConfig, SimulationState, StreamEvent } from '../types/simulation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export class SimulationAPI {
  static async createSimulation(config: SimulationConfig): Promise<{ simulation_id: string }> {
    const response = await fetch(`${API_BASE_URL}/simulations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });

    if (!response.ok) {
      throw new Error(`Failed to create simulation: ${response.statusText}`);
    }

    return response.json();
  }

  static async getSimulation(simulationId: string): Promise<SimulationState> {
    const response = await fetch(`${API_BASE_URL}/simulations/${simulationId}`);

    if (!response.ok) {
      throw new Error(`Failed to get simulation: ${response.statusText}`);
    }

    return response.json();
  }

  static async *runSimulation(simulationId: string): AsyncGenerator<StreamEvent> {
    const response = await fetch(`${API_BASE_URL}/simulations/${simulationId}/run`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`Failed to run simulation: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          try {
            const event: StreamEvent = JSON.parse(data);
            yield event;
          } catch (e) {
            console.error('Failed to parse SSE data:', e);
          }
        }
      }
    }
  }

  static async updateMessage(
    simulationId: string,
    turnNumber: number,
    content: string,
    reasoning?: string
  ): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/simulations/${simulationId}/messages/${turnNumber}`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content, reasoning }),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to update message: ${response.statusText}`);
    }
  }

  static async rerunFromTurn(simulationId: string, fromTurn: number): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/simulations/${simulationId}/rerun/${fromTurn}`,
      {
        method: 'POST',
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to rerun from turn: ${response.statusText}`);
    }
  }

  static async listModels(): Promise<{ anthropic: string[]; openai: string[] }> {
    const response = await fetch(`${API_BASE_URL}/models`);

    if (!response.ok) {
      throw new Error(`Failed to list models: ${response.statusText}`);
    }

    return response.json();
  }
}
