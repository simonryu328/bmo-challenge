import { useState } from 'react';
import './ExecutionSteps.css';

export default function ExecutionSteps({ steps, isStreaming }) {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!steps || steps.length === 0) {
    return null;
  }

  return (
    <div className="execution-steps">
      <button
        className="execution-steps__header"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className="execution-steps__title">
          Execution Trace
          {isStreaming && <span className="execution-steps__streaming">streaming...</span>}
        </span>
        <span className="execution-steps__toggle">
          {isExpanded ? '▼' : '▶'}
        </span>
      </button>

      {isExpanded && (
        <ol className="execution-steps__list">
          {steps.map((step, index) => (
            <li
              key={index}
              className={`execution-steps__item ${
                isStreaming && index === steps.length - 1
                  ? 'execution-steps__item--active'
                  : ''
              }`}
            >
              <span className="execution-steps__number">
                Step {step.step_number}
              </span>
              <span className="execution-steps__description">
                {step.description}
              </span>
              <span className="execution-steps__time">
                {formatTime(step.timestamp)}
              </span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

function formatTime(timestamp) {
  try {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  } catch {
    return '';
  }
}
