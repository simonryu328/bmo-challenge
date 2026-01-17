import { useState, useCallback, useRef } from 'react';
import { submitTaskStream } from '../api/client';
import type { Task, ExecutionStep } from '../types';

interface UseStreamingTaskReturn {
  submit: (taskText: string, threadId?: string) => void;
  cancel: () => void;
  clear: () => void;
  isStreaming: boolean;
  currentTask: Task | null;
  error: string | null;
}

/**
 * Custom hook for managing streaming task submission
 */
export default function useStreamingTask(): UseStreamingTaskReturn {
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentTask, setCurrentTask] = useState<Task | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<(() => void) | null>(null);

  const submit = useCallback((taskText: string, threadId: string = 'default') => {
    // Reset state
    setIsStreaming(true);
    setError(null);
    setCurrentTask({
      input_text: taskText,
      output_text: '',
      tools_used: [],
      execution_steps: [],
      created_at: new Date().toISOString(),
      thread_id: threadId,
    });

    // Cancel any existing stream
    if (abortRef.current) {
      abortRef.current();
    }

    // Start streaming
    abortRef.current = submitTaskStream(taskText, threadId, {
      onStep: (step: ExecutionStep) => {
        setCurrentTask((prev) => prev ? {
          ...prev,
          execution_steps: [...prev.execution_steps, step],
        } : null);
      },

      onToolUsed: (tool: string) => {
        setCurrentTask((prev) => prev ? {
          ...prev,
          tools_used: prev.tools_used.includes(tool)
            ? prev.tools_used
            : [...prev.tools_used, tool],
        } : null);
      },

      onOutput: (output: string) => {
        setCurrentTask((prev) => prev ? {
          ...prev,
          output_text: output,
        } : null);
      },

      onComplete: (taskId: string) => {
        setCurrentTask((prev) => prev ? {
          ...prev,
          id: taskId,
        } : null);
        setIsStreaming(false);
        abortRef.current = null;
      },

      onError: (err: Error) => {
        setError(err.message);
        setIsStreaming(false);
        abortRef.current = null;
      },
    });
  }, []);

  const cancel = useCallback(() => {
    if (abortRef.current) {
      abortRef.current();
      abortRef.current = null;
      setIsStreaming(false);
    }
  }, []);

  const clear = useCallback(() => {
    cancel();
    setCurrentTask(null);
    setError(null);
  }, [cancel]);

  return {
    submit,
    cancel,
    clear,
    isStreaming,
    currentTask,
    error,
  };
}
