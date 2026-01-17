import ExecutionSteps from './ExecutionSteps';
import type { Task } from '../types';
import './TaskResult.css';

const TOOL_COLORS: Record<string, string> = {
  TextProcessorTool: '#8b5cf6',
  CalculatorTool: '#f59e0b',
  WeatherMockTool: '#06b6d4',
};

interface TaskResultProps {
  task: Task | null;
  isStreaming: boolean;
}

export default function TaskResult({ task, isStreaming }: TaskResultProps) {
  if (!task) {
    return (
      <div className="task-result task-result--empty">
        <p>Enter a task above to get started</p>
        <div className="task-result__examples">
          <p>Try one of these:</p>
          <ul>
            <li>"Convert hello world to uppercase"</li>
            <li>"Calculate 25 * 4 + 10"</li>
            <li>"What's the weather in San Francisco?"</li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="task-result">
      <div className="task-result__header">
        <h3 className="task-result__input">"{task.input_text}"</h3>
        {task.created_at && (
          <span className="task-result__timestamp">
            {formatDate(task.created_at)}
          </span>
        )}
      </div>

      {task.tools_used && task.tools_used.length > 0 && (
        <div className="task-result__tools">
          {task.tools_used.map((tool) => (
            <span
              key={tool}
              className="task-result__tool-badge"
              style={{ backgroundColor: TOOL_COLORS[tool] || '#6b7280' }}
            >
              {formatToolName(tool)}
            </span>
          ))}
        </div>
      )}

      {task.output_text && (
        <div className="task-result__output">
          <label className="task-result__label">Result</label>
          <pre className="task-result__output-text">{task.output_text}</pre>
        </div>
      )}

      <ExecutionSteps
        steps={task.execution_steps}
        isStreaming={isStreaming}
      />
    </div>
  );
}

function formatToolName(tool: string): string {
  return tool.replace('Tool', '').replace(/([A-Z])/g, ' $1').trim();
}

function formatDate(timestamp: string): string {
  try {
    const date = new Date(timestamp);
    return date.toLocaleString();
  } catch {
    return '';
  }
}
