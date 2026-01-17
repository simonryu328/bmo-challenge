export interface ExecutionStep {
  step_number: number;
  description: string;
  timestamp: string;
}

export interface Task {
  id?: string;
  input_text: string;
  output_text: string;
  tools_used: string[];
  execution_steps: ExecutionStep[];
  created_at: string;
  thread_id: string;
}

export interface StreamCallbacks {
  onStep?: (step: ExecutionStep) => void;
  onToolUsed?: (tool: string) => void;
  onOutput?: (output: string) => void;
  onComplete?: (taskId: string) => void;
  onError?: (error: Error) => void;
}
