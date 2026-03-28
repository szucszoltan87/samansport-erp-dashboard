# Harness Plan for SamanSport ERP Dashboard

## Purpose

This document describes how to take the current MVP and evolve it into a sustainable, agent-friendly development workflow that can grow into a shippable product.

The goal is **not** to restart from zero.

The goal is to:

- keep building on top of the current MVP
- commit to the **Reflex** stack
- create a repeatable harness for Claude Code in VS Code
- separate planning, building, and evaluation
- keep the repository clean and predictable for both humans and agents

---

## Product Direction

This repository is for an app built on top of the existing **Tharanis ERP** data layer.

The app should provide:

- significantly better UI/UX than the legacy ERP surface
- faster access to operational data
- useful reporting and analytics
- inventory-related operational help
- a path from analytics MVP to a real internal business application

This is **not** a replacement ERP from scratch.

It is a modern operational layer built on top of the existing ERP.

---

## Core Decision

The frontend stack is now **Reflex**.

Older Streamlit artifacts may still exist in the history, but going forward:

- **Reflex is the official frontend**
- new work should follow the Reflex-based direction
- old stack leftovers should be treated as migration residue and cleaned up over time

---

## Development Branching Strategy

This repository follows the following Git structure:

- `master`
- `dev`

Work should **not** be committed directly to `master`.

Work should **not** usually be committed directly to `dev` either.

### Branching Rules

Create working branches from `dev` only:

- `feature/<short-name>`
- `fix/<short-name>`

Examples:

- `feature/inventory-alerts`
- `feature/reflex-dashboard-shell`
- `fix/sync-date-filter`
- `fix/report-export-bug`

### Merge Flow

The intended merge flow is:

1. `dev` → create `feature/...` or `fix/...`
2. work and commit on that branch
3. merge back into `dev`
4. test and stabilize in `dev`
5. merge `dev` into `master` only when the state is release-worthy
6. tag `master`indicating version after phase is complete. Naming convention should follow the existing tagging patter

### Practical Meaning

- `master` = stable, shippable state
- `dev` = integration branch
- `feature/*` = new functionality
- `fix/*` = bug fixes, regressions, repair work

This must be respected by both humans and Claude Code sessions.

---

## What the Harness Should Do

The harness is the working system around the codebase, not just the code itself.

It should help Claude Code and the human operator work in a disciplined way across longer development cycles.

The harness should ensure that every meaningful change goes through these roles:

1. **Planner**
2. **Builder**
3. **Evaluator**

At the beginning, these do **not** need to be three permanent autonomous agents.

In practice, especially early on, this can be:

- one lead Claude Code session
- using separate prompts, files, and checkpoints for each role

Later, once the process is stable, this can evolve into multi-agent execution.

---

## High-Level Roadmap

## Step 1 — Freeze the current baseline

### Goal
Create a known starting point before improving the structure.

### Why
The current repo already contains valuable work. Before changing process, you need a clean baseline that says:

- what currently works
- what is experimental
- what is obsolete
- what direction is official

### Output
- stable baseline on `dev`
- short baseline note in docs
- Reflex confirmed as official direction

---

## Step 2 — Clean and canonize the repository

### Goal
Make the repo easier to understand for both humans and Claude Code.

### Why
A noisy repo causes agent confusion and bad implementation choices.

Typical problems to reduce:

- leftover artifacts from earlier stack phases
- generated files mixed with source files
- unclear boundaries between app code, experiments, and docs
- temporary debugging residue committed into the repo

### Output
- cleaner file structure
- reduced ambiguity
- one clearer source of truth for architecture

---

## Step 3 — Define the product briefly but clearly

### Goal
Turn the MVP into a clearly stated product direction.

### Why
If the repo only describes a dashboard, the system will keep behaving like a dashboard project.
If the repo describes an operational ERP companion app, development choices become more coherent.

### Output
A short product brief covering:

- who the users are
- what problems the app solves
- what V1 is supposed to do
- what is out of scope for now

---

## Step 4 — Add harness documents to the repo

### Goal
Store the development logic in files, not in chat memory.

### Why
Long-running development becomes unreliable if everything depends on the latest conversation.

The repo should contain a harness area with durable artifacts.

### Suggested contents
- product brief
- architecture overview
- sprint backlog
- sprint contract template
- evaluator checklist
- release checklist
- handoff template

### Output
A `/docs` or `/harness` area that Claude Code can read every time.

---

## Step 5 — Create project rules for Claude Code

### Goal
Make Claude Code start every task with the same context and rules.

### Why
Without fixed rules, agent behavior drifts between sessions.

### This should cover
- stack decisions
- architectural rules
- branch discipline
- coding conventions
- testing expectations
- how to plan work
- how to evaluate work
- what “done” means

### Output
A root-level `CLAUDE.md` that becomes the operating manual for Claude Code.

---

## Step 6 — Introduce sprint-based development

### Goal
Break work into small, reviewable units.

### Why
Large vague tasks create messy code and weak evaluation.
Smaller sprint units are much better for both agentic and human-supervised work.

### Each sprint should contain
- scope
- constraints
- files expected to change
- acceptance criteria
- evaluator checks
- release impact

### Output
Every serious change starts with a sprint contract, not with open-ended prompting.

---

## Step 7 — Separate builder and evaluator behavior

### Goal
Avoid a system where the same session writes code and declares victory.

### Why
A long-running app becomes more reliable when evaluation is treated as a separate stage.

### Evaluator should check
- correctness
- UX consistency
- integration fit
- data behavior
- regressions
- code quality
- shippability of that sprint

### Output
A lightweight but real QA gate before merging into `dev`.

---

## Step 8 — Build module by module

### Goal
Evolve the MVP into a product without restarting.

### Why
The current system already has working value. The right move is extension and hardening, not rebuild-from-zero.

### Good module progression
A sensible order could be:

1. core platform stabilization
2. Reflex shell and navigation consistency
3. auth / roles / configuration
4. product master and search
5. sales reporting
6. inventory workflows and operational helpers
7. alerts / recommendations / exceptions
8. admin tools and sync visibility
9. reporting polish and export quality
10. release hardening

### Output
A product that grows in controlled layers.

---

## Step 9 — Add release gates

### Goal
Make “done” and “ready for master” explicit.

### Why
Without release gates, `dev` becomes a permanent staging mess and `master` loses meaning.

### Release checks should include
- build passes
- required checks pass
- sprint contract satisfied
- evaluator signed off
- no critical known regressions
- docs updated where needed

### Output
A repeatable path from `dev` to `master`.

---

## Step 10 — Only then scale to multi-agent execution

### Goal
Increase speed only after process discipline exists.

### Why
Multiple agents on top of a vague process usually create more noise, not more leverage.

### Recommended sequence
Start with:
- one lead Claude Code session
- planner / builder / evaluator handled as separate stages

Then later move to:
- planner agent
- builder agent
- evaluator agent

### Output
A more autonomous workflow built on stable ground.

---

## Recommended Real-Life Workflow in VS Code

For now, use Claude Code like this:

### 1. Start from the correct branch
Always begin from `dev`, then create either:

- `feature/...`
- `fix/...`

### 2. Plan first
Before coding, create or update a sprint contract.

### 3. Build second
Use Claude Code to implement only the sprint scope.

### 4. Evaluate third
Run a separate evaluation pass.
Treat this as independent review, even if you use the same tool.

### 5. Merge only when the sprint passes
First into `dev`.
Only release `dev` into `master` when stable.

---

## Suggested Repository Documentation Set

Over time, the repo should include at least:

- `README.md`
- `CLAUDE.md`
- `docs/PRODUCT_BRIEF.md`
- `docs/ARCHITECTURE.md`
- `docs/HARNESS_PLAN.md`
- `docs/SPRINT_TEMPLATE.md`
- `docs/EVALUATOR_CHECKLIST.md`
- `docs/RELEASE_CHECKLIST.md`

This creates a durable working memory for the project.

---

## Definition of Success

This harness is working if:

- the repo is understandable quickly
- Claude Code behaves more consistently across sessions
- work happens in smaller, clearer sprints
- changes are easier to review
- `dev` stays usable
- `master` stays stable
- the app improves without chaotic rewrites
- the MVP evolves into a genuinely shippable product

---

## Immediate Next Move

The next practical phase is:

1. add this harness plan to the repo
2. add a proper `README.md`
3. create `CLAUDE.md`
4. define the first harnessed sprint
5. execute the sprint on a `feature/...` or `fix/...` branch from `dev`

That is the starting point for turning the current MVP into a sustainable product workflow.
