import { useState, FormEvent } from 'react';
import './TaskInput.css';

interface TaskInputProps {
  onSubmit: (task: string) => void;
  isLoading: boolean;
}

export default function TaskInput({ onSubmit, isLoading }: TaskInputProps) {
  const [task, setTask] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (task.trim() && !isLoading) {
      onSubmit(task.trim());
      setTask('');
    }
  };

  return (
    <form className="task-input" onSubmit={handleSubmit}>
      <input
        type="text"
        value={task}
        onChange={(e) => setTask(e.target.value)}
        placeholder="Enter a task (e.g., 'Convert hello to uppercase', 'Calculate 25 * 4', 'Weather in New York')"
        disabled={isLoading}
        className="task-input__field"
      />
      <button
        type="submit"
        disabled={!task.trim() || isLoading}
        className="task-input__button"
      >
        {isLoading ? (
          <>
            <span className="task-input__spinner"></span>
            Processing...
          </>
        ) : (
          'Submit'
        )}
      </button>
    </form>
  );
}
