# CLAUDE.md

This file defines how Claude Code should behave in the `samansport-erp-dashboard` repository.

It is the working instruction set for agent-assisted development in VS Code.

---

## 1. Project identity

This repository is for **SamanSport ERP Dashboard**.

The product is a modern application layer built on top of the existing **Tharanis ERP** data environment.

The goal is to provide:

- much better UI/UX than the legacy ERP surface
- easier access to business data
- useful reporting and analytics
- operational help, especially around inventory and business visibility
- a path from MVP to a shippable internal business application

This is **not** an ERP rebuild from scratch.

The system should evolve **on top of the existing MVP** and remain grounded in the current ERP integration context.

---

## 2. Official stack

The official frontend stack is:

- **Reflex**

Important:

- older Streamlit artifacts may still exist in history or transitional areas
- do not introduce new Streamlit-based work
- do not propose restarting from zero
- assume the project is continuing from the current MVP
- new frontend work should align with the Reflex direction

If old stack remnants are encountered, treat them as migration residue unless explicitly told otherwise.

---

## 3. Core development philosophy

Claude Code should optimize for:

- clarity
- continuity
- small safe increments
- file-based working memory
- reviewability
- maintainability
- shippability

Claude Code should **not** optimize for impressive rewrites, unnecessary abstraction, or speculative rebuilding.

Preferred behavior:

- extend the current system
- improve structure gradually
- keep changes easy to review
- keep architecture understandable
- preserve working functionality whenever possible

---

## 4. Git and branch rules

The repository follows this branch structure:

- `master`
- `dev`

### Meaning of branches

- `master` = stable, release-worthy state
- `dev` = integration branch
- `feature/*` = new functionality
- `fix/*` = bug fixes or repair work

### Working rule

Claude Code should assume that work is done from `dev` by creating one of:

- `feature/<short-name>`
- `fix/<short-name>`

Examples:

- `feature/inventory-alerts`
- `feature/reflex-shell-cleanup`
- `fix/date-filter-regression`
- `fix/export-format-bug`

### Strict rules

Claude Code should:

- never assume direct work on `master`
- avoid recommending direct commits to `master`
- avoid recommending direct commits to `dev` unless explicitly requested
- assume changes should land on a `feature/...` or `fix/...` branch first
- keep branch naming concise and descriptive

### Merge flow

The expected flow is:

1. branch from `dev`
2. work on `feature/...` or `fix/...`
3. merge into `dev`
4. validate and stabilize
5. merge `dev` into `master` only when release-worthy

---

## 5. Harness workflow

Claude Code should follow a three-role workflow:

1. **Planner**
2. **Builder**
3. **Evaluator**

These roles do not need to be separate autonomous agents in every session.
But the behavior must remain separated.

### Planner mode
Before coding meaningful work, Claude Code should:

- clarify the target
- define scope
- state assumptions
- identify affected areas
- propose the smallest reasonable implementation slice
- define acceptance criteria

### Builder mode
When implementing, Claude Code should:

- stay within agreed scope
- prefer small, focused edits
- avoid unrelated refactors
- preserve existing behavior unless change is intentional
- keep structure clean and explicit

### Evaluator mode
After implementation, Claude Code should:

- review the change independently
- check whether acceptance criteria were truly met
- call out risks, regressions, or missing tests
- avoid automatically declaring success
- distinguish between “implemented” and “validated”

---

## 6. Sprint-based working style

Meaningful work should be handled as small sprints, not vague long prompts.

Each sprint should ideally define:

- goal
- scope
- constraints
- files or modules likely affected
- acceptance criteria
- evaluation checks
- merge target

Claude Code should favor:

- one feature per branch
- one fix per branch
- one coherent sprint at a time

Claude Code should resist bundling unrelated work into one implementation.

---

## 7. Product and architecture behavior

Claude Code should treat the app as a product with operational value, not just a dashboard demo.

When making product decisions, bias toward:

- operator usability
- reporting usefulness
- internal business workflows
- inventory-related decision support
- stable data behavior
- production-appropriate structure

Do not treat this project as only a charting frontend.

The app is evolving toward a usable internal business application.

---

## 8. Coding behavior

Claude Code should prefer:

- readable code over clever code
- explicitness over magic
- incremental refactors over sweeping rewrites
- stable conventions over experimentation
- consistent naming
- clear folder responsibilities

Claude Code should avoid:

- introducing new frameworks without strong reason
- changing the official stack casually
- giant cross-cutting rewrites
- hidden coupling
- premature abstraction
- unnecessary complexity

When editing code:

- keep changes local when possible
- explain architectural impact when changes cross layers
- preserve existing intent unless the task explicitly changes it

---

## 9. Refactoring rules

Refactoring is allowed when it improves clarity or maintainability, but it must be disciplined.

Allowed:

- small structural cleanup near the active change
- removing obvious dead code related to the task
- improving naming or file clarity
- reducing duplication where directly relevant

Avoid:

- repo-wide rewrites during feature work
- large cosmetic-only churn
- changing many files without strong reason
- mixing migration work with unrelated feature work

If a refactor is bigger than the sprint itself, it should be proposed separately first.

---

## 10. Documentation rules

Claude Code should treat documentation as part of the product workflow.

When appropriate, update or create:

- `README.md`
- `CLAUDE.md`
- architecture notes
- sprint docs
- evaluator checklists
- release notes
- setup notes

Important: keep docs aligned with the actual current direction.

Do not leave outdated architectural claims in place if a change makes them false.

---

## 11. Testing and validation behavior

Claude Code should not assume code is correct just because it compiles or looks reasonable.

Validation should include, as relevant:

- logic review
- UI behavior review
- data flow review
- regression awareness
- edge-case awareness
- manual test suggestions
- automated tests when appropriate

If something has **not** been tested, say so clearly.

Distinguish between:

- implemented
- reviewed
- tested
- production-ready

These are not the same.

---

## 12. Quality bar before merge to `dev`

Before suggesting a change is ready to merge into `dev`, Claude Code should check:

- scope was respected
- solution matches the sprint goal
- no obvious unrelated churn was introduced
- code is understandable
- acceptance criteria are met
- known risks are stated
- docs are updated if needed

Before suggesting something is ready for `master`, the standard is higher:

- stable
- reviewed
- no critical known issues
- release-worthy

---

## 13. Communication style inside the repo workflow

Claude Code should communicate in a practical engineering style.

Preferred style:

- concise
- explicit
- honest about uncertainty
- focused on next action
- grounded in current repo reality

Avoid:

- hype
- excessive optimism
- pretending validation happened when it did not
- recommending full rewrites too quickly
- drifting into generic advice when repo-specific advice is needed

---

## 14. What Claude Code should do when starting a task

At the start of a non-trivial task, Claude Code should usually do this:

1. restate the target briefly
2. identify whether it is a `feature` or `fix`
3. propose the smallest safe implementation slice
4. identify the likely files/modules involved
5. state any important assumptions
6. then begin implementation

For bigger tasks, Claude Code should suggest creating or updating a sprint artifact first.

---

## 15. What Claude Code should avoid

Claude Code should avoid:

- restarting the project from zero
- replacing Reflex
- introducing parallel architecture without need
- assuming old stack files define the future direction
- mixing multiple features in one branch
- treating evaluation as optional
- silently changing product scope
- over-designing before the next usable increment

---

## 16. Preferred immediate operating pattern

Until a larger harness is fully in place, Claude Code should work like this:

- use `CLAUDE.md` as the main instruction file
- treat planner / builder / evaluator as explicit modes
- work from `dev` into `feature/...` or `fix/...`
- keep sprints small
- preserve momentum from the current MVP
- help evolve the repo toward a shippable product

---

## 17. Default repo assumption

Unless explicitly told otherwise, Claude Code should assume:

- this repo is active and evolving
- the current MVP is worth building on
- the frontend direction is Reflex
- the product target is a modern operational ERP companion app
- shipping quality matters
- clarity and maintainability matter as much as speed

---

## 18. Final instruction

When in doubt, choose the option that is:

- smaller
- clearer
- easier to review
- more aligned with Reflex
- more compatible with the existing MVP
- safer to merge into `dev`
- more likely to move the product toward a shippable state
