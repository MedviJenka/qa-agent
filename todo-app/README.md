# Todo App

Minimal React + TypeScript todo app (Vite). Used to test QA agents (e.g. `/qa-risk`, `/qa-regression-guard`).

## Run

```bash
cd todo-app
npm install
npm run dev
```

Open http://localhost:5173. Add, toggle, and delete todos.

## Test with QA agent

From the **devflow** repo root (or from this directory with the plugin installed):

1. Create a branch: `git checkout -b feature/todo-qa-test`
2. In Claude Code, run: `/qa-risk` or `/qa-regression-guard`
3. Review the generated reports and (for regression guard) tests under `/tests`.
