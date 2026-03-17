import { useState, FormEvent } from 'react';

interface AddTodoProps {
  onAdd: (text: string) => void;
}

export function AddTodo({ onAdd }: AddTodoProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onAdd(input);
    setInput('');
  };

  return (
    <form onSubmit={handleSubmit} role="form" aria-label="Add todo">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="What to do?"
        aria-label="New todo text"
      />
      <button type="submit">Add</button>
    </form>
  );
}
