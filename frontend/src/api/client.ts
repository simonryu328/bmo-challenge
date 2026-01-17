import type { Task, ExecutionStep, StreamCallbacks } from '../types';

const API_BASE = '/api';

interface SSEEvent {
  event_type: 'step' | 'tool_used' | 'final_output' | 'complete' | 'error';
  data: {
    step_number?: number;
    description?: string;
    timestamp?: string;
    tool?: string;
    output?: string;
    task_id?: string;
    error?: string;
  };
}

/**
 * Submit a task for processing (non-streaming)
 */
export async function submitTask(task: string, threadId: string = 'default'): Promise<Task> {
  const response = await fetch(`${API_BASE}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task, thread_id: threadId }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to submit task');
  }

  return response.json();
}

/**
 * Submit a task with SSE streaming
 */
export function submitTaskStream(
  task: string,
  threadId: string = 'default',
  callbacks: StreamCallbacks = {}
): () => void {
  const controller = new AbortController();

  (async () => {
    try {
      const response = await fetch(`${API_BASE}/tasks/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task, thread_id: threadId }),
        signal: controller.signal,
      });

      if (!response.ok) {
        const error = await response.json();
        callbacks.onError?.(new Error(error.detail || 'Failed to submit task'));
        return;
      }

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Parse SSE events from buffer
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data: SSEEvent = JSON.parse(line.slice(6));

              switch (data.event_type) {
                case 'step':
                  callbacks.onStep?.(data.data as ExecutionStep);
                  break;
                case 'tool_used':
                  callbacks.onToolUsed?.(data.data.tool!);
                  break;
                case 'final_output':
                  callbacks.onOutput?.(data.data.output!);
                  break;
                case 'complete':
                  callbacks.onComplete?.(data.data.task_id!);
                  break;
                case 'error':
                  callbacks.onError?.(new Error(data.data.error));
                  break;
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      if ((error as Error).name !== 'AbortError') {
        callbacks.onError?.(error as Error);
      }
    }
  })();

  return () => controller.abort();
}

/**
 * Get task history with pagination
 */
export async function getTasks(limit: number = 100, offset: number = 0): Promise<Task[]> {
  const response = await fetch(
    `${API_BASE}/tasks?limit=${limit}&offset=${offset}`
  );

  if (!response.ok) {
    throw new Error('Failed to fetch tasks');
  }

  return response.json();
}

/**
 * Get a specific task by ID
 */
export async function getTask(taskId: string): Promise<Task | null> {
  const response = await fetch(`${API_BASE}/tasks/${taskId}`);

  if (!response.ok) {
    if (response.status === 404) {
      return null;
    }
    throw new Error('Failed to fetch task');
  }

  return response.json();
}

/**
 * Get tasks by thread ID
 */
export async function getTasksByThread(threadId: string): Promise<Task[]> {
  const response = await fetch(`${API_BASE}/tasks/thread/${threadId}`);

  if (!response.ok) {
    throw new Error('Failed to fetch tasks');
  }

  return response.json();
}

/**
 * Delete a task by ID
 */
export async function deleteTask(taskId: string): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error('Failed to delete task');
  }

  return response.json();
}
