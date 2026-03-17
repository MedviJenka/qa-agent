import type { Todo } from '../types';

interface TodoItemProps {
  todo: Todo;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
}

export function TodoItem({ todo, onToggle, onDelete }: TodoItemProps) {
  return (
    <li>
      <input
        type="checkbox"
        checked={todo.done}
        onChange={() => onToggle(todo.id)}
        aria-label={`Mark "${todo.text}" as ${todo.done ? 'incomplete' : 'done'}`}
      />
      <span style={{ textDecoration: todo.done ? 'line-through' : undefined }}>
        {todo.text}
      </span>
      <button
        type="button"
        onClick={() => onDelete(todo.id)}
        aria-label={`Delete "${todo.text}"`}
      >
        Delete
      </button>
    </li>
  );
}
