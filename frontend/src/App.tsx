import { useState, useCallback } from 'react';
import TaskInput from './components/TaskInput';
import TaskResult from './components/TaskResult';
import TaskHistory from './components/TaskHistory';
import useStreamingTask from './hooks/useStreamingTask';
import type { Task } from './types';
import './App.css';

export default function App() {
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const {
    submit,
    isStreaming,
    currentTask,
    error,
    clear: clearCurrentTask,
  } = useStreamingTask();

  const handleSubmit = useCallback((taskText: string) => {
    setSelectedTask(null); // Clear selected history item
    submit(taskText);
  }, [submit]);

  const handleSelectTask = useCallback((task: Task) => {
    clearCurrentTask(); // Clear streaming task when selecting from history
    setSelectedTask(task);
  }, [clearCurrentTask]);

  // Determine which task to display
  // When streaming, show currentTask; otherwise show selectedTask or currentTask
  const displayTask = isStreaming ? currentTask : (selectedTask || currentTask);

  // Watch for streaming completion
  if (!isStreaming && currentTask?.id && selectedTask === null) {
    // Refresh history when a new task completes
    setTimeout(() => setRefreshTrigger((prev) => prev + 1), 100);
  }

  return (
    <div className="app">
      <header className="app__header">
        <h1 className="app__title">BMO Chat</h1>
        <p className="app__subtitle">Agent Task Runner</p>
      </header>

      <div className="app__content">
        <aside className="app__sidebar">
          <TaskHistory
            onSelectTask={handleSelectTask}
            selectedTaskId={selectedTask?.id}
            refreshTrigger={refreshTrigger}
          />
        </aside>

        <main className="app__main">
          <TaskInput
            onSubmit={handleSubmit}
            isLoading={isStreaming}
          />

          {error && (
            <div className="app__error">
              {error}
            </div>
          )}

          <TaskResult
            task={displayTask}
            isStreaming={isStreaming}
          />
        </main>
      </div>
    </div>
  );
}
