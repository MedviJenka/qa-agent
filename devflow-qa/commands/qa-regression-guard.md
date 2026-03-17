---
description: QA regression guard — analyze PR changes, detect regression risks, generate Playwright tests, run them, and generate Allure report
---

# QA Regression Guard Command

Run a full regression risk analysis on the current branch: change analysis → parallel risk agents → Playwright test generation → **run tests + fix code errors + Allure report** → synthesized final report. Targets **React + TypeScript**.

## Usage

```
/qa-regression-guard           (analyze current branch vs main/master/develop)
/qa-regression-guard main      (analyze vs specific base branch)
```

## Phases

### Phase 0: Git Agent — validate branch

```
Task(subagent_type="git", run_in_background=false):
"OPERATION: validate-branch"
```

Extract from output: `branch`, `base_branch`, `branch_slug`.

If status is BLOCKED, report the reason to the user and stop.

### Phase 1: Change Analyzer (sequential)

```
Task(subagent_type="change-analyzer", run_in_background=false):
"Analyze changed files on this branch.
Base branch: {base_branch}
Current branch: {branch}
Branch slug: {branch_slug}
Write report to: .docs/qa/{branch_slug}/regression/change-analysis.md
Apply react-regression-patterns skill. Confirm when the report file is written."
```

Wait for completion before proceeding.

### Phase 2: Parallel QA Risk Agents

Spawn all three agents **in a single message** (run_in_background=false for each):

**React UI Flow Analyzer**
```
Task(subagent_type="react-ui-flow-analyzer", run_in_background=false):
"Analyze UI user flows for changed components.
Base branch: {base_branch}
Current branch: {branch}
Branch slug: {branch_slug}
Change analysis: .docs/qa/{branch_slug}/regression/change-analysis.md
Write report to: .docs/qa/{branch_slug}/regression/ui-flows.md
Apply react-regression-patterns skill. Confirm when the report file is written."
```

**Async Risk Agent**
```
Task(subagent_type="async-risk-agent", run_in_background=false):
"Detect async regression risks in changed components.
Base branch: {base_branch}
Current branch: {branch}
Branch slug: {branch_slug}
Change analysis: .docs/qa/{branch_slug}/regression/change-analysis.md
Write report to: .docs/qa/{branch_slug}/regression/async-risks.md
Apply react-regression-patterns skill. Confirm when the report file is written."
```

**UI Regression Agent**
```
Task(subagent_type="ui-regression-agent", run_in_background=false):
"Detect UI regression risks in changed components.
Base branch: {base_branch}
Current branch: {branch}
Branch slug: {branch_slug}
Change analysis: .docs/qa/{branch_slug}/regression/change-analysis.md
Write report to: .docs/qa/{branch_slug}/regression/ui-regression-risks.md
Apply react-regression-patterns skill. Confirm when the report file is written."
```

### Phase 3: Playwright Test Generator (sequential, after Phase 2)

```
Task(subagent_type="playwright-test-generator", run_in_background=false):
"Generate pytest-based Playwright (Python) tests for regression coverage, and write a test plan document.
Base branch: {base_branch}
Current branch: {branch}
Branch slug: {branch_slug}
Read inputs from:
  - .docs/qa/{branch_slug}/regression/ui-flows.md
  - .docs/qa/{branch_slug}/regression/async-risks.md
  - .docs/qa/{branch_slug}/regression/ui-regression-risks.md
Write test files under tests/test_qa/, organized by type:
  - tests/test_qa/sanity/         (smoke tests)
  - tests/test_qa/critical_flows/ (E2E user flows)
  - tests/test_qa/regression/     (regression guards)
  - tests/test_qa/edge_cases/     (loading, error, empty states)
Use pytest + Playwright Python; create test_*.py in each directory. Add tests/conftest.py if needed for page fixture.
Add Allure annotations to all generated tests: import allure; decorate each test function with @allure.title, @allure.severity, @allure.tag; wrap logical steps with allure.step() context managers.
Write a structured test plan document to: .docs/qa/{branch_slug}/regression/test-plan.md
  Sections: Scope, Test Types & Objectives, Sanity Tests, Critical User Flows, Regression Guards, Edge Cases, Selectors & Accessibility, Environment (include pytest run command with --alluredir=allure-results), Traceability.
When Playwright MCP is available and the app is running, use the browser tools to verify flows and refine selectors; if the user provided a base URL (e.g. http://localhost:5173), pass it to the agent.
Apply react-regression-patterns skill. Confirm which files were written."
```

Wait for completion before proceeding.

### Phase 4: Pytest Runner (sequential, after Phase 3)

```
Task(subagent_type="pytest-runner", run_in_background=false):
"Run the generated pytest tests, fix any test code errors, and generate the Allure HTML report.
Base URL: {base_url}
Tests root: tests/
Allure results dir: allure-results/
Allure report dir: allure-report/

Steps:
1. Run: pytest tests/test_qa/ --alluredir=allure-results -v --tb=short
2. Fix any TEST CODE ERRORS (import errors, fixture errors, wrong selectors, syntax errors) — max 3 iterations.
   Do NOT fix AssertionError failures — those are real app findings.
3. After no more code errors remain (or after 3 iterations), run:
   allure generate allure-results -o allure-report --clean
   allure open allure-report
4. Report: pass/fail counts, fixes applied, app behavior failures found, allure report path.

Write pytest run results to: .docs/qa/{branch_slug}/regression/pytest-results.md"
```

Wait for completion before proceeding.

Extract from output:
- `pytest_passed`: number of tests that passed
- `pytest_failed`: number of app behavior failures
- `pytest_fixed`: number of test code errors fixed
- `allure_report_path`: path to generated report (e.g. `allure-report/index.html`)

### Phase 5: QA Regression Synthesizer (sequential)

```
Task(subagent_type="qa-regression-synthesizer", run_in_background=false):
"Mode: review
Aggregate the regression analysis reports for branch {branch} (base: {base_branch}).

Read these reports:
  - .docs/qa/{branch_slug}/regression/change-analysis.md
  - .docs/qa/{branch_slug}/regression/ui-flows.md
  - .docs/qa/{branch_slug}/regression/async-risks.md
  - .docs/qa/{branch_slug}/regression/ui-regression-risks.md
  - .docs/qa/{branch_slug}/regression/test-plan.md
  - .docs/qa/{branch_slug}/regression/pytest-results.md

Pytest run summary: {pytest_passed} passed · {pytest_failed} failed (app) · {pytest_fixed} code errors fixed.
Allure report: {allure_report_path}

Compute Risk Score:
  - HIGH: Any BLOCKING finding, or any async race condition, or security blocking
  - MEDIUM: Multiple SHOULD-FIX findings, or any broken UI flow
  - LOW: Only NITs or no findings

Write the final report to: .docs/qa/{branch_slug}/regression/qa-regression-report.md

Report format:
---
# QA Regression Report
**Branch**: {branch} → {base_branch}
**Risk Score**: HIGH | MEDIUM | LOW

## Summary
{1-3 sentence overview}

## Changed Components
{bullet list from change-analysis}

## Regression Risks

### Async Risks
{findings with severity}

### UI Regression Risks
{findings with severity}

### UI Flows Affected
{affected flows}

## Test Execution
**Pytest**: {N} passed · {N} failed (app failures) · {N} code errors fixed across {iterations} iteration(s)
**Allure report**: {allure_report_path}

### App Behavior Failures
{list of failing tests with assertion message, or "None — all tests passed"}

## Playwright Tests Generated
{count by type; all tests include Allure decorators}

## Test Plan
**Document**: .docs/qa/{branch_slug}/regression/test-plan.md
{1-2 sentence scope summary}

## Allure Report
**Path**: {allure_report_path} (already generated and opened)
**Re-open**: `allure open allure-report`
**Re-run**: `pytest tests/ --base-url={base_url} --alluredir=allure-results && allure serve allure-results`

## Recommendation
{Merge / Fix before merge / Block merge}
---

Confirm when the file is written and state the Risk Score."
```

### Phase 6: Report to user

After the synthesizer completes:
- State the **Risk Score** (HIGH / MEDIUM / LOW).
- Show pytest execution summary: passed / failed / code errors fixed.
- State whether the Allure report was opened automatically.
- Show the path to the final report: `.docs/qa/{branch_slug}/regression/qa-regression-report.md`.
- Show where tests are: `tests/test_qa/` (by type: sanity, critical_flows, regression, edge_cases).
- Show the test plan: `.docs/qa/{branch_slug}/regression/test-plan.md`.
- If any app behavior failures exist, list the test names and assertions.
- If Risk Score is HIGH, state that the branch should be fixed before merge.

## Architecture

```
/qa-regression-guard (orchestrator — you)
  └── Phase 0: git validate-branch
  └── Phase 1: change-analyzer (sequential)
  └── Phase 2: react-ui-flow-analyzer + async-risk-agent + ui-regression-agent (parallel)
  └── Phase 3: playwright-test-generator (sequential)
        writes: tests/test_qa/**/*.py (Allure-annotated, absolute URLs), test-plan.md
  └── Phase 4: pytest-runner (sequential)
        runs: pytest → fixes code errors (max 3x) → allure generate → allure open
        writes: pytest-results.md, allure-results/, allure-report/
  └── Phase 5: qa-regression-synthesizer (sequential)
        reads: all 5 reports + pytest-results.md
        writes: qa-regression-report.md (includes Test Execution + Allure path)
  └── Phase 6: Summarize — Risk Score, test results, Allure report path
```

You only orchestrate. You do not perform analysis, detect risks, generate tests, or run tests yourself; the agents do.
