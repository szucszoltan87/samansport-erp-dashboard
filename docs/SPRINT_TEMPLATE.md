# Sprint Template

Use this template for every meaningful `feature/...` or `fix/...` branch.

The purpose of this file is to make each sprint explicit, scoped, reviewable, and easier for Claude Code and humans to execute consistently.

---

## Sprint Metadata

**Sprint title:**  
Short descriptive name.

**Branch type:**  
`feature` or `fix`

**Branch name:**  
Example: `feature/inventory-alerts` or `fix/date-filter-regression`

**Base branch:**  
`dev`

**Target merge branch:**  
`dev`

**Owner:**  
Name of the human operator.

**Date opened:**  
YYYY-MM-DD

**Status:**  
`planned` / `in_progress` / `review` / `done` / `blocked`

---

## 1. Sprint Goal

Describe in 2–5 sentences what this sprint is supposed to achieve.

Good examples:
- Add a first usable inventory alert view in the Reflex app.
- Fix incorrect date-range filtering in the sales sync pipeline.
- Introduce a stable Reflex page shell and shared layout structure.

This section should explain the business or product purpose, not only the code change.

---

## 2. Sprint Type

Choose one:

- New feature
- Bug fix
- Refactor
- Stabilization
- UI/UX improvement
- Data/integration improvement
- Documentation / process improvement

If more than one applies, identify the primary type.

---

## 3. Why This Sprint Matters

Explain why this sprint is worth doing now.

Possible reasons:
- blocks another feature
- improves operator usability
- fixes a correctness problem
- reduces technical confusion
- supports productization
- improves release-readiness

This section helps prevent random or low-value work.

---

## 4. Scope

State what is included in this sprint.

Write this as a concrete list.

Example:
- add alert card component for low stock
- add alert threshold config source
- display alerts on inventory page
- handle empty-state UI

Be specific enough that the builder knows what to implement.

---

## 5. Out of Scope

State what is explicitly **not** part of this sprint.

This is important.

Example:
- no notification emails yet
- no user-specific settings yet
- no major inventory model redesign
- no export feature in this sprint

This prevents branch creep and overbuilding.

---

## 6. Expected Files / Modules Affected

List the files, folders, or modules that are likely to change.

Example:
- `frontend/...`
- `reflex_app/...`
- `api/...`
- `docs/...`
- `README.md`

This does not need to be perfect, but it should reflect expected impact.

---

## 7. Product / User Impact

Describe how the user experience or product behavior should improve after this sprint.

Examples:
- user can spot low-stock items without manually scanning tables
- user can trust date filtering for sales reports
- navigation becomes more consistent across pages

Keep this user-facing.

---

## 8. Technical Approach

Describe the intended implementation approach at a high level.

Keep this practical, not overly detailed.

Good things to mention:
- whether this is UI-only or crosses layers
- whether database or API behavior changes
- whether the work builds on existing components
- whether there are migration or compatibility concerns

This is the planner-to-builder bridge.

---

## 9. Constraints

List any important constraints.

Examples:
- must stay within Reflex
- do not restart architecture
- preserve current data shape
- avoid touching unrelated modules
- must be merge-safe into `dev`
- keep backward compatibility with current flow

This helps keep implementation disciplined.

---

## 10. Dependencies

List anything this sprint depends on.

Examples:
- existing product master data
- current Supabase table
- earlier shell/layout work
- API endpoint stability
- another branch being merged first

If there are none, say so explicitly.

---

## 11. Risks

List the main risks.

Examples:
- regression in existing report view
- ambiguous data semantics in ERP field mapping
- incomplete edge-case handling
- UX inconsistency if only part of shell is updated

This section is important for evaluation.

---

## 12. Acceptance Criteria

These are the conditions for saying the sprint is complete.

Write them as specific checks.

Example:
- low-stock alerts are visible in the Reflex inventory view
- empty state is handled cleanly
- alert logic does not break page rendering
- no unrelated pages are regressed
- code is understandable and scoped to the sprint

Avoid vague criteria like “works well.”

---

## 13. Evaluation Checklist

This is the evaluator section.

Check all that apply before merge into `dev`.

- scope respected
- acceptance criteria met
- no obvious unrelated churn
- no known critical regression introduced
- UI behavior reviewed
- data behavior reviewed
- docs updated if needed
- branch is appropriate for merge into `dev`

If some checks are not completed, state that clearly.

---

## 14. Testing / Validation Notes

Document what was actually validated.

Possible items:
- manual UI review completed
- specific flow tested end-to-end
- specific edge case checked
- no automated tests added
- automated tests added and passed
- not fully validated yet

Be explicit.  
Do not blur “implemented” and “tested.”

---

## 15. Merge Recommendation

Choose one:

- Ready to merge into `dev`
- Needs revision before merge into `dev`
- Blocked
- Ready for follow-up sprint, but not merge-ready yet

Add a short explanation.

---

## 16. Follow-Up Work

List what should happen after this sprint.

Examples:
- add notification handling later
- move thresholds to user settings
- add evaluator automation
- improve alert prioritization

This helps the backlog grow in a clean way.

---

## 17. Handoff Summary

Write a short summary for the next person or next Claude session.

Include:
- what changed
- what remains open
- anything that needs special attention
- any known temporary compromises

This should make continuation easier without relying on chat history.

---

# Quick Fill Version

Use this shorter version when you need speed.

## Sprint
**Title:**  
**Branch:**  
**Type:** feature / fix  
**Base:** dev  
**Target:** dev  
**Status:** planned / in_progress / review / done / blocked  

## Goal
...

## Scope
- ...
- ...
- ...

## Out of scope
- ...
- ...
- ...

## Files / modules likely affected
- ...
- ...
- ...

## Constraints
- ...
- ...
- ...

## Acceptance criteria
- ...
- ...
- ...

## Risks
- ...
- ...
- ...

## Validation
- ...
- ...
- ...

## Merge recommendation
...

## Handoff summary
...
