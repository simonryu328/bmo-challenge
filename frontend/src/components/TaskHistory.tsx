import { useEffect, useState } from 'react';
import { getTasks } from '../api/client';
import type { Task } from '../types';
import './TaskHistory.css';

const TOOL_COLORS: Record<string, string> = {
  TextProcessorTool: '#8b5cf6',
  CalculatorTool: '#f59e0b',
  WeatherMockTool: '#06b6d4',
};

interface TaskHistoryProps {
  onSelectTask: (task: Task) => void;
  selectedTaskId: string | undefined;
  refreshTrigger: number;
}

export default function TaskHistory({ onSelectTask, selectedTaskId, refreshTrigger }: TaskHistoryProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTasks();
  }, [refreshTrigger]);

  const loadTasks = async () => {
    try {
      setIsLoading(true);
      const data = await getTasks(50, 0);
      setTasks(data);
      setError(null);
    } catch (err) {
      setError('Failed to load history');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading && tasks.length === 0) {
    return (
      <div className="task-history">
        <h2 className="task-history__title">Task History</h2>
        <div className="task-history__loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="task-history">
      <div className="task-history__header">
        <h2 className="task-history__title">Task History</h2>
        <button
          className="task-history__refresh"
          onClick={loadTasks}
          disabled={isLoading}
        >
          ↻
        </button>
      </div>

      {error && <div className="task-history__error">{error}</div>}

      {tasks.length === 0 ? (
        <div className="task-history__empty">
          No tasks yet. Submit one above!
        </div>
      ) : (
        <ul className="task-history__list">
          {tasks.map((task) => (
            <li key={task.id}>
              <button
                className={`task-history__item ${
                  selectedTaskId === task.id ? 'task-history__item--selected' : ''
                }`}
                onClick={() => onSelectTask(task)}
              >
                <span className="task-history__item-input">
                  {truncate(task.input_text, 50)}
                </span>
                <div className="task-history__item-meta">
                  <div className="task-history__item-tools">
                    {task.tools_used.map((tool) => (
                      <span
                        key={tool}
                        className="task-history__item-tool"
                        style={{ backgroundColor: TOOL_COLORS[tool] || '#6b7280' }}
                        title={tool}
                      />
                    ))}
                  </div>
                  <span className="task-history__item-time">
                    {formatRelativeTime(task.created_at)}
                  </span>
                </div>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength) + '...';
}

function formatRelativeTime(timestamp: string): string {
  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString();
  } catch {
    return '';
  }
}
