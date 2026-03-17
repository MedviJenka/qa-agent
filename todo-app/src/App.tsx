import { useState } from 'react';
import { AddTodo } from './components/AddTodo';
import { TodoList } from './components/TodoList';
import type { Todo } from './types';

export default function App() {
  const [todos, setTodos] = useState<Todo[]>([]);

  const addTodo = (text: string) => {
    if (!text.trim()) return;
    setTodos((prev) => [
      ...prev,
      { id: crypto.randomUUID(), text: text.trim(), done: false },
    ]);
  };

  const toggleTodo = (id: string) => {
    setTodos((prev) =>
      prev.map((t) => (t.id === id ? { ...t, done: !t.done } : t))
    );
  };

  const deleteTodo = (id: string) => {
    setTodos((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <main>
      <h1>Todo</h1>
      <AddTodo onAdd={addTodo} />
      <TodoList todos={todos} onToggle={toggleTodo} onDelete={deleteTodo} />
    </main>
  );
}
