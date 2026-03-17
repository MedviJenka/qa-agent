# Test Plan: Todo App

**App:** React + TypeScript todo app (Vite)  
**Scope:** Add todo, toggle done, delete todo, empty state.  
**Target:** `/tests` (sanity, critical_flows, regression, edge_cases) — pytest + Playwright.

---

## 1. Scope

| In scope | Out of scope |
|----------|--------------|
| Add todo (form submit, trim empty) | Persistence (localStorage/API) |
| Toggle todo (checkbox) | Auth, multi-user |
| Delete todo (button) | Filters (all/active/done) |
| Empty state message | Keyboard shortcuts |
| Main layout (heading, form, list) | Theming / a11y audit |

---

## 2. Test Types & Objectives

| Type | Directory | Objective |
|------|-----------|-----------|
| **Sanity** | `tests/sanity/` | App and main sections render without crash. |
| **Critical flows** | `tests/critical_flows/` | Add, toggle, delete flows work end-to-end. |
| **Regression** | `tests/regression/` | Guards for known risks (empty submit, toggle/delete state). |
| **Edge cases** | `tests/edge_cases/` | Empty state, single item, long text. |

---

## 3. Sanity Tests

| ID | Scenario | Steps | Expected |
|----|----------|--------|----------|
| S1 | Home renders | Goto `/` | `<main>` visible, heading "Todo" visible. |
| S2 | Add form visible | Goto `/` | Form with aria-label "Add todo", input "New todo text", button "Add" visible. |
| S3 | Empty state when no todos | Goto `/` (no todos) | Text "No todos yet. Add one above." visible. |

---

## 4. Critical User Flows

| ID | Flow | Steps | Expected |
|----|------|--------|----------|
| F1 | Add todo | Open app → type in input → click Add | New todo appears in list; input cleared. |
| F2 | Add todo (submit via Enter) | Open app → type in input → press Enter | Same as F1. |
| F3 | Toggle todo done | Add one todo → click its checkbox | Todo text shows line-through; checkbox checked. |
| F4 | Toggle todo incomplete | After F3 → click checkbox again | Line-through removed; checkbox unchecked. |
| F5 | Delete todo | Add one todo → click Delete | Todo removed from list. |
| F6 | Add multiple then delete one | Add 3 todos → delete the second | List shows 2 todos; correct one removed. |

---

## 5. Regression Guards

| ID | Risk | Test | Expected |
|----|------|------|----------|
| R1 | Empty submit | Submit with blank or whitespace-only input | No new todo added; no crash. |
| R2 | Toggle updates correct item | Add 2 todos → toggle first | Only first todo toggled. |
| R3 | Delete removes correct item | Add 2 todos → delete second | First todo remains. |
| R4 | List reflects state after add/toggle/delete | Add, toggle one, delete one | List matches expected items and done state. |

---

## 6. Edge Cases

| ID | Scenario | Steps | Expected |
|----|----------|--------|----------|
| E1 | Empty state after delete last | Add one todo → delete it | "No todos yet. Add one above." visible. |
| E2 | Single todo add/toggle/delete | Add one → toggle → delete | Empty state; no errors. |
| E3 | Long todo text | Add todo with very long text | Text visible (truncation or wrap acceptable). |
| E4 | Whitespace trimmed on add | Add "  hello  " | Todo shows as "hello" (trimmed). |

---

## 7. Selectors & Accessibility

- Prefer: `get_by_role("main")`, `get_by_role("form", { name: "Add todo" })`, `get_by_label("New todo text")`, `get_by_role("button", { name: "Add" })`, `get_by_role("list", { name: "Todo list" })`, `get_by_role("checkbox")`, `get_by_role("button", { name: "Delete" })`.
- Avoid fragile CSS or positional selectors.

---

## 8. Environment

- **Base URL:** `http://localhost:5173` (Vite dev server).
- **Run app:** `cd todo-app && npm run dev`.
- **Run tests:** From repo root or todo-app, run pytest with Playwright (e.g. `pytest tests/` or `playwright test` per project setup).

---

## 9. Traceability

| Source | Report / artifact |
|--------|-------------------|
| Change analysis | `.docs/qa/{branch}/regression/change-analysis.md` |
| UI flows | `.docs/qa/{branch}/regression/ui-flows.md` |
| Async / UI regression risks | `.docs/qa/{branch}/regression/async-risks.md`, `ui-regression-risks.md` |
| Generated tests | `tests/sanity/`, `tests/critical_flows/`, `tests/regression/`, `tests/edge_cases/` |
| Final report | `.docs/qa/{branch}/regression/qa-regression-report.md` |

This test plan aligns with the devflow-qa regression guard flow and the structure used by the Playwright test generator.
