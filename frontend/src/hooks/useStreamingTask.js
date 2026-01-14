import { useState, useCallback, useRef } from 'react';
import { submitTaskStream } from '../api/client';

/**
 * Custom hook for managing streaming task submission
 */
export default function useStreamingTask() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentTask, setCurrentTask] = useState(null);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);

  const submit = useCallback((taskText, threadId = 'default') => {
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
      onStep: (step) => {
        setCurrentTask((prev) => ({
          ...prev,
          execution_steps: [...prev.execution_steps, step],
        }));
      },

      onToolUsed: (tool) => {
        setCurrentTask((prev) => ({
          ...prev,
          tools_used: prev.tools_used.includes(tool)
            ? prev.tools_used
            : [...prev.tools_used, tool],
        }));
      },

      onOutput: (output) => {
        setCurrentTask((prev) => ({
          ...prev,
          output_text: output,
        }));
      },

      onComplete: (taskId) => {
        setCurrentTask((prev) => ({
          ...prev,
          id: taskId,
        }));
        setIsStreaming(false);
        abortRef.current = null;
      },

      onError: (err) => {
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
