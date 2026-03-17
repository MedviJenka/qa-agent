---
name: react-regression-patterns
description: Regression risk detection for React + TypeScript — state management, async bugs, UI rendering, and user flow analysis for Playwright test generation.
user-invocable: false
allowed-tools: Read, Grep, Glob
---

# React Regression Patterns

Reference for detecting regression risks in React + TypeScript code changes. Applies to the QA Regression Guard pipeline: change analysis, UI flow detection, async risk detection, UI rendering risk detection, and Playwright test generation.

## Iron Law

> **EVERY UI CHANGE RISKS BREAKING A USER FLOW**
>
> Treat each modified component as a regression surface. Any change to props, state shape,
> conditional rendering, or async logic can silently break user flows that were previously
> working. Static analysis is not optional — it is the minimum bar.

---

## Detection Categories

### 1. State Management Risks

Bugs introduced by changing how state is initialized, derived, or updated.

| Pattern | Risk | Signal |
|---------|------|--------|
| State initialized from prop | Stale state after parent re-render | `useState(props.value)` |
| Derived state in `useState` | Out-of-sync computed values | `useState(compute(data))` without `useMemo` |
| Mutating state directly | Renders not triggered | `state.items.push(x)` instead of `setState([...state.items, x])` |
| State update batching broken | Partial UI update | Multiple `setState` calls outside React batching context |

### 2. Async Risks

Race conditions and lifecycle bugs from async operations in React.

| Pattern | Risk | Signal |
|---------|------|--------|
| Missing `useEffect` dependency | Stale closure, effect doesn't re-run | Dependency used inside effect but absent from array |
| Extra `useEffect` dependency | Infinite loop | Object/array dep with new reference each render |
| No cleanup in `useEffect` | Memory leak, state update after unmount | `async` function in effect with no abort/flag |
| Stale closure in callback | Operates on old value | `useCallback` missing dep, captures stale variable |
| Race condition | Out-of-order response applied | Multiple in-flight requests, last response wins but first resolves second |
| `setState` after unmount | Warning + potential bug | No `mounted` flag or `AbortController` |

**Cleanup pattern**:
```typescript
useEffect(() => {
  const controller = new AbortController()
  fetchData({ signal: controller.signal }).then(setData)
  return () => controller.abort()
}, [dependency])
```

### 3. UI Rendering Risks

Conditional rendering bugs that make elements appear or disappear incorrectly.

| Pattern | Risk | Signal |
|---------|------|--------|
| Falsy short-circuit renders "0" | Unexpected text rendered | `{count && <List />}` when count can be 0 |
| Inverted boolean condition | Element hidden/shown wrong | `disabled={isReady}` instead of `disabled={!isReady}` |
| Missing loading state | Blank UI during fetch | No skeleton/spinner for async data |
| Missing error state | Silent failure | No error branch in async data render |
| Missing empty state | Blank area confuses user | No fallback when array is empty |
| Prop removed but JSX unchanged | Runtime error or silent gap | Prop used in JSX but no longer passed |

### 4. User Flow Risks

Navigation and interaction paths broken by component changes.

| Pattern | Risk | Signal |
|---------|------|--------|
| `onClick` removed from button | Interaction dead | Button renders but has no handler |
| `onSubmit` condition changed | Form can't submit | Submit gated on wrong condition |
| Navigation target changed | Redirect to wrong route | `navigate('/old-path')` updated to new path |
| Guard condition tightened | User locked out | Route guard now blocks valid users |
| Form field removed | Data not collected | Input removed but backend still expects it |

---

## Playwright Selector Guidance

Prefer selectors in this order (most to least stable):

1. `getByRole('button', { name: 'Submit' })` — semantic, resilient to CSS changes
2. `getByLabel('Email')` — form field by associated label
3. `getByTestId('submit-btn')` — explicit test ID (requires `data-testid` attribute)
4. `getByPlaceholder('Enter email')` — input by placeholder text
5. `getByText('Login')` — visible text (use sparingly; brittle for dynamic content)
6. CSS selector — last resort; breaks on class name changes

**Avoid**: `nth-child`, `nth-of-type`, positional selectors, implementation-coupled selectors.

---

## Severity Classification

| Severity | Meaning | Example |
|----------|---------|---------|
| BLOCKING | Will break a user flow or cause a runtime error | Submit button disabled when it should be enabled |
| SHOULD-FIX | Likely regression under normal use or concurrency | Stale closure causes wrong data to display |
| NIT | Hygiene issue; unlikely to cause regression in practice | Extra dep in `useEffect` causes unnecessary re-fetch |

---

## Checklist for Regression Analysis

- [ ] All `useEffect` deps present and correct
- [ ] Async effects have cleanup (abort controller or mounted flag)
- [ ] `disabled` conditions on buttons are correct booleans
- [ ] Conditional renders use `Boolean(value)` not truthy shortcut for number/string
- [ ] Loading state renders during async operations
- [ ] Error state renders on API failure
- [ ] Empty state renders when list/data is empty
- [ ] All `onClick`/`onSubmit` handlers present on interactive elements
- [ ] Navigation targets are current and correct
- [ ] State initialization does not depend on mutable props directly

---

## Extended References

- `references/async-patterns.md` — abort controllers, race condition prevention, concurrent render safety
- `references/rendering-risks.md` — conditional render edge cases, JSX boolean gotchas
- `references/playwright-patterns.md` — selector hierarchy, waiting strategies, mocking patterns
