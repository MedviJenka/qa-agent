# DevFlow QA Plugin

QA regression guard: change analysis, UI/async/regression risk detection, Playwright test generation. Command: **/qa-regression-guard**.

## Skill name (important)

The plugin uses **one skill**: `react-regression-patterns`. The skill folder must be installed as **react-regression-patterns** (not "qa-regression-guard" or "devflow-qa"). If you see "Unknown skill: qa-regression-guard", the installed copy has the wrong skill name somewhere — fix it to `react-regression-patterns`.

## Install (manual)

From the devflow repo root:

```powershell
$claude = "$env:USERPROFILE\.claude"
New-Item -ItemType Directory -Force "$claude\commands\devflow" | Out-Null
New-Item -ItemType Directory -Force "$claude\agents\devflow" | Out-Null
Copy-Item plugins\devflow-qa\commands\qa-regression-guard.md "$claude\commands\devflow\" -Force
Copy-Item plugins\devflow-qa\agents\*.md "$claude\agents\devflow\" -Force
Copy-Item -Recurse -Force plugins\devflow-qa\skills\react-regression-patterns "$claude\skills\"
```

Restart Claude Code. Run `/qa-regression-guard`.

## If you still see "Unknown skill"

1. In `%USERPROFILE%\.claude\skills\` ensure the folder is named **react-regression-patterns** (not qa-regression-guard).
2. Remove any folder or file under `.claude\skills\` named **qa-regression-guard** or **devflow-qa** if you had renamed it.
3. Re-copy the skill: `Copy-Item -Recurse -Force plugins\devflow-qa\skills\react-regression-patterns "$claude\skills\"`

## Architecture 

  /qa-regression-guard
           │
           ▼
  ┌─────────────────────────────────────────────────────┐
  │ Phase 0 · git                                        │
  │  validate-branch → branch, base_branch, branch_slug │
  └─────────────────────┬───────────────────────────────┘
                        │ BLOCKED → stop
                        ▼
  ┌─────────────────────────────────────────────────────┐
  │ Phase 1 · change-analyzer                           │
  │  git diff → classify .tsx/.ts files                 │
  │  → change-analysis.md  (Risk: HIGH/MED/LOW)         │
  └─────────────────────┬───────────────────────────────┘
                        │ sequential (all 3 read this file)
            ┌───────────┼───────────┐
            ▼           ▼           ▼
  ┌──────────────┐ ┌──────────┐ ┌────────────────────┐
  │ Phase 2a     │ │ Phase 2b │ │ Phase 2c           │
  │ ui-flow-     │ │ async-   │ │ ui-regression-     │
  │ analyzer     │ │ risk-    │ │ agent              │
  │              │ │ agent    │ │                    │
  │ JSX → flows, │ │ useEffect│ │ conditional render,│
  │ selectors,   │ │ races,   │ │ disabled state,    │
  │ interaction  │ │ stale    │ │ empty/error/loading│
  │ points       │ │ closures │ │ states             │
  │              │ │          │ │                    │
  │ ui-flows.md  │ │async-    │ │ui-regression-      │
  │              │ │risks.md  │ │risks.md            │
  └──────┬───────┘ └────┬─────┘ └─────────┬──────────┘
         └──────────────┴─────────────────┘
                        │ all 3 complete (parallel)
                        ▼
  ┌─────────────────────────────────────────────────────┐
  │ Phase 3 · playwright-test-generator                 │
  │  reads: ui-flows + async-risks + ui-regression      │
  │  → tests/sanity/         (smoke, CRITICAL severity) │
  │  → tests/critical_flows/ (E2E, CRITICAL)            │
  │  → tests/regression/     (guards, NORMAL)           │
  │  → tests/edge_cases/     (states, MINOR)            │
  │  → test-plan.md                                     │
  │  all tests annotated with @allure.title/severity/   │
  │  tag + allure.step() wrappers                       │
  │  if Playwright MCP available: verifies live DOM     │
  └─────────────────────┬───────────────────────────────┘
                        │
                        ▼
  ┌─────────────────────────────────────────────────────┐
  │ Phase 4 · pytest-runner                             │
  │  1. pytest tests/ --base-url=... --alluredir=...    │
  │  2. classify output:                                │
  │     • ImportError/SyntaxError/fixture error         │
  │       → TEST CODE ERROR → fix test file → retry    │
  │     • AssertionError                                │
  │       → APP FAILURE → record, do not touch         │
  │  3. max 3 iterations                                │
  │  4. allure generate allure-results -o allure-report │
  │  5. allure open allure-report   ← opens browser    │
  │  → pytest-results.md                               │
  └─────────────────────┬───────────────────────────────┘
                        │
                        ▼
  ┌─────────────────────────────────────────────────────┐
  │ Phase 5 · qa-regression-synthesizer                 │
  │  reads: all 5 analysis reports + pytest-results.md  │
  │  computes Risk Score:                               │
  │    HIGH   → any BLOCKING or async race condition    │
  │    MEDIUM → multiple SHOULD-FIX                     │
  │    LOW    → only NITs                               │
  │  → qa-regression-report.md                         │
  └─────────────────────┬───────────────────────────────┘
                        │
                        ▼
                Phase 6 · you (orchestrator)
                prints Risk Score, paths, Allure cmd

  ---
  3. Agents — roles and boundaries

  Agent: git
  Model: haiku
  Reads: git status/log
  Writes: nothing
  Never does: modify files
  ────────────────────────────────────────
  Agent: change-analyzer
  Model: inherit
  Reads: git diff
  Writes: change-analysis.md
  Never does: modify source
  ────────────────────────────────────────
  Agent: react-ui-flow-analyzer
  Model: inherit
  Reads: change-analysis.md + JSX source
  Writes: ui-flows.md
  Never does: modify source
  ────────────────────────────────────────
  Agent: async-risk-agent
  Model: inherit
  Reads: change-analysis.md + TS source
  Writes: async-risks.md
  Never does: modify source
  ────────────────────────────────────────
  Agent: ui-regression-agent
  Model: inherit
  Reads: change-analysis.md + TSX source
  Writes: ui-regression-risks.md
  Never does: modify source
  ────────────────────────────────────────
  Agent: playwright-test-generator
  Model: inherit
  Reads: 3 risk reports
  Writes: tests/**/*.py, test-plan.md
  Never does: modify app source
  ────────────────────────────────────────
  Agent: pytest-runner
  Model: inherit
  Reads: test files + pytest output
  Writes: pytest-results.md, allure-report/
  Never does: modify app source
  ────────────────────────────────────────
  Agent: qa-regression-synthesizer
  Model: haiku
  Reads: all 5 reports + pytest-results.md
  Writes: qa-regression-report.md
  Never does: re-analyze code

  Why haiku for git and synthesizer? They do simple structured tasks (git commands, read-and-aggregate).     
  Cheaper and faster. The analysis agents use inherit (Sonnet/Opus) because they reason over code.

  ---
  4. Data flow

  git diff
    └─▶ change-analysis.md
            ├─▶ ui-flows.md          ─┐
            ├─▶ async-risks.md        ├─▶ tests/**/*.py
            └─▶ ui-regression-risks.md┘   test-plan.md
                                              │
                                              ▼
                                      pytest run
                                      allure generate
                                              │
                                              ▼
                                      pytest-results.md
                                              │
                     ┌────────────────────────┘
                     ├── change-analysis.md
                     ├── ui-flows.md
                     ├── async-risks.md
                     ├── ui-regression-risks.md
                     └── test-plan.md
                              │
                              ▼
                      qa-regression-report.md

  ---
  5. Output artifacts

  .docs/qa/{branch}/regression/
    ├── change-analysis.md        Phase 1
    ├── ui-flows.md               Phase 2a
    ├── async-risks.md            Phase 2b
    ├── ui-regression-risks.md    Phase 2c
    ├── test-plan.md              Phase 3
    ├── pytest-results.md         Phase 4
    └── qa-regression-report.md   Phase 5  ← final verdict

  tests/
    ├── conftest.py               base URL + markers
    ├── sanity/                   6 smoke tests
    ├── critical_flows/           E2E flows
    ├── regression/               BLOCKING/SHOULD-FIX guards
    └── edge_cases/               loading/error/empty states

  allure-results/                 raw pytest output (JSON)
  allure-report/                  generated HTML report ← opens in browser

  ---
  6. Plugin structure on disk

  plugins/devflow-qa/
    ├── .claude-plugin/plugin.json   manifest (name, agents, skills)
    ├── commands/
    │   └── qa-regression-guard.md  the orchestrator script
    ├── agents/
    │   ├── git.md                  (copy of shared agent)
    │   ├── change-analyzer.md
    │   ├── react-ui-flow-analyzer.md
    │   ├── async-risk-agent.md
    │   ├── ui-regression-agent.md
    │   ├── playwright-test-generator.md
    │   ├── pytest-runner.md        ← new
    │   └── qa-regression-synthesizer.md
    ├── skills/
    │   └── react-regression-patterns/SKILL.md
    └── test-plans/
        └── todo-app-test-plan.md   reference example

  After install → ~/.claude/
    ├── commands/devflow/qa-regression-guard.md
    ├── agents/devflow/change-analyzer.md  (+ all others)
    └── skills/react-regression-patterns/SKILL.md

  ---
  7. The skill: react-regression-patterns

  Every analysis agent loads this skill at the start of its work. It defines:
  - Iron Law: never invent findings not present in the diff
  - Detection categories: Async Risks, UI Rendering Risks, User Flow Risks
  - Severity tiers: BLOCKING → SHOULD-FIX → NIT
  - Selector preference order: role → label → testid → placeholder → CSS

  It's the shared quality standard that keeps all agents consistent.

  ---
  8. What makes pytest-runner different from the others

  All other agents are read-only analyzers — they never change files they didn't create. pytest-runner is the
   only agent that:
  1. Executes code (runs pytest + allure via Bash)
  2. Mutates files it didn't create (fixes test files when it finds code errors)
  3. Has a retry loop (up to 3 iterations)
  4. Opens the browser (allure open)

  It makes the hard distinction between "the test is broken" (code error → fix) and "the app is broken"      
  (assertion failure → record as finding).