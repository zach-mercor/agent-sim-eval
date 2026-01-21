export enum MessageRole {
  CANDIDATE = "candidate",
  SIM = "sim",
  SYSTEM = "system"
}

export enum SimulationStatus {
  IDLE = "idle",
  RUNNING = "running",
  COMPLETED = "completed",
  FAILED = "failed"
}

export interface AgentConfig {
  system_prompt: string;
  objective: string;
  model: string;
  temperature: number;
  max_tokens: number;
}

export interface Message {
  role: MessageRole;
  content: string;
  reasoning?: string;
  timestamp: string;
  turn_number: number;
}

export interface VerificationResult {
  success: boolean;
  explanation: string;
  timestamp: string;
}

export interface SimulationConfig {
  candidate_config: AgentConfig;
  sim_config: AgentConfig;
  verification_prompt: string;
  max_turns: number;
  first_speaker: MessageRole;
}

export interface SimulationState {
  simulation_id: string;
  config: SimulationConfig;
  status: SimulationStatus;
  messages: Message[];
  current_turn: number;
  verification_result?: VerificationResult;
  created_at: string;
  updated_at: string;
}

export interface StreamEvent {
  type: string;
  [key: string]: any;
}
