const API_BASE = '/api';

/**
 * Submit a task for processing (non-streaming)
 */
export async function submitTask(task, threadId = 'default') {
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
 * @param {string} task - The task description
 * @param {string} threadId - Thread ID for conversation context
 * @param {Object} callbacks - Event callbacks
 * @param {Function} callbacks.onStep - Called for each execution step
 * @param {Function} callbacks.onToolUsed - Called when a tool is used
 * @param {Function} callbacks.onOutput - Called with final output
 * @param {Function} callbacks.onComplete - Called when task is complete
 * @param {Function} callbacks.onError - Called on error
 * @returns {Function} Abort function to cancel the stream
 */
export function submitTaskStream(task, threadId = 'default', callbacks = {}) {
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

      const reader = response.body.getReader();
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
              const data = JSON.parse(line.slice(6));

              switch (data.event_type) {
                case 'step':
                  callbacks.onStep?.(data.data);
                  break;
                case 'tool_used':
                  callbacks.onToolUsed?.(data.data.tool);
                  break;
                case 'final_output':
                  callbacks.onOutput?.(data.data.output);
                  break;
                case 'complete':
                  callbacks.onComplete?.(data.data.task_id);
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
      if (error.name !== 'AbortError') {
        callbacks.onError?.(error);
      }
    }
  })();

  return () => controller.abort();
}

/**
 * Get task history with pagination
 */
export async function getTasks(limit = 100, offset = 0) {
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
export async function getTask(taskId) {
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
export async function getTasksByThread(threadId) {
  const response = await fetch(`${API_BASE}/tasks/thread/${threadId}`);

  if (!response.ok) {
    throw new Error('Failed to fetch tasks');
  }

  return response.json();
}

/**
 * Delete a task by ID
 */
export async function deleteTask(taskId) {
  const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error('Failed to delete task');
  }

  return response.json();
}
