# Evaluator Checklist

## Purpose

This document is used during the **evaluation phase** of a sprint.

Its purpose is to make sure that a change is reviewed independently after implementation and before merge into `dev`.

The evaluator should not simply ask “was code written?”

The evaluator should ask:

- was the right thing built?
- was the scope respected?
- is the change understandable?
- is it safe enough for `dev`?
- is anything important still unvalidated?

---

## How to Use This Checklist

Use this checklist for every meaningful `feature/...` or `fix/...` branch.

Recommended sequence:

1. read the sprint contract
2. inspect the implemented change
3. compare outcome against acceptance criteria
4. record open risks or gaps
5. decide whether it is ready for merge into `dev`

This checklist is intended for:

- human review
- Claude Code evaluator pass
- or both together

---

## Sprint Metadata

**Sprint title:**  
**Branch name:**  
**Branch type:** feature / fix  
**Base branch:** dev  
**Target merge branch:** dev  
**Evaluator:**  
**Date:**  
**Status:** pass / pass_with_notes / revision_needed / blocked  

---

## 1. Scope Review

### 1.1 Scope respected
- [ ] The implemented work matches the sprint scope
- [ ] No major unrelated work was bundled into the branch
- [ ] The branch still represents one coherent change
- [ ] The change is appropriate for a `feature/...` or `fix/...` branch

### Notes
...

---

## 2. Product Review

### 2.1 Product goal fit
- [ ] The change improves the product in the intended direction
- [ ] The change supports the stated user or business need
- [ ] The change aligns with the product brief
- [ ] The change does not silently shift product scope

### Notes
...

---

## 3. Architecture Review

### 3.1 Architectural fit
- [ ] The change fits the current architectural direction
- [ ] Reflex remains the frontend direction
- [ ] The implementation builds on the MVP rather than replacing it
- [ ] Boundaries between layers were respected reasonably well
- [ ] No unnecessary framework or structural churn was introduced

### Notes
...

---

## 4. Branch / Process Review

### 4.1 Workflow discipline
- [ ] Work appears to have been done in the correct branch model
- [ ] Change is suitable to merge into `dev`, not directly to `master`
- [ ] Sprint artifact exists or was updated where appropriate
- [ ] Relevant docs were updated if the change required it

### Notes
...

---

## 5. Functional Review

### 5.1 Correctness
- [ ] Acceptance criteria appear to be met
- [ ] Main user-facing behavior matches intent
- [ ] Fixes actually address the reported problem
- [ ] No obvious broken flow is visible in the changed area
- [ ] Edge cases were considered at least to a reasonable degree

### Notes
...

---

## 6. UI / UX Review

### 6.1 Experience quality
- [ ] UI behavior is understandable
- [ ] The change is consistent with the current app direction
- [ ] Empty states / missing data states are handled reasonably
- [ ] Labels, layout, and interaction feel coherent
- [ ] The change improves usability rather than just adding surface area

### Notes
...

---

## 7. Data / Integration Review

### 7.1 Data behavior
- [ ] The change handles expected data flows correctly
- [ ] Sync or freshness assumptions are still reasonable
- [ ] No obvious data-shape mismatch is introduced
- [ ] Integration behavior with ERP-backed data is still coherent
- [ ] Known data limitations are documented where needed

### Notes
...

---

## 8. Code Quality Review

### 8.1 Implementation quality
- [ ] Code is readable
- [ ] Naming is understandable
- [ ] Change size is reasonable for the sprint
- [ ] No unnecessary complexity was introduced
- [ ] No obvious dead or duplicated logic was added without reason
- [ ] The implementation is reviewable and maintainable

### Notes
...

---

## 9. Regression Review

### 9.1 Regression awareness
- [ ] No obvious regression is known in nearby functionality
- [ ] If there are known regressions, they are stated explicitly
- [ ] Existing behavior was preserved where expected
- [ ] Risky areas are identified honestly

### Notes
...

---

## 10. Validation Review

### 10.1 Actual validation performed
Mark what was actually done.

- [ ] Manual UI review
- [ ] Manual flow test
- [ ] Data behavior spot-check
- [ ] Edge case review
- [ ] Automated test run
- [ ] Build / type / lint check
- [ ] Documentation review
- [ ] None of the above fully completed

### Validation notes
Be precise. Distinguish between:
- implemented
- reviewed
- tested

...

---

## 11. Merge Readiness

### 11.1 Ready for `dev`?
- [ ] Ready to merge into `dev`
- [ ] Needs revision before merge into `dev`
- [ ] Blocked
- [ ] Better handled in a follow-up sprint before merge

### Reason
...

---

## 12. Known Gaps

List anything that is still missing, weak, or only partially validated.

Examples:
- edge case not yet tested
- UI state still rough
- no automated validation yet
- temporary implementation compromise
- follow-up cleanup needed

...

---

## 13. Follow-Up Recommendation

State the recommended next action:

- merge into `dev`
- revise in same branch
- split follow-up work into new `feature/...` branch
- create `fix/...` branch
- defer until dependency lands

...

---

## 14. Final Evaluator Summary

Write a concise summary covering:

- overall judgment
- what is good
- what is risky
- whether merge into `dev` is appropriate

...

---

# Quick Evaluator Version

## Evaluator Summary
**Sprint:**  
**Branch:**  
**Status:** pass / pass_with_notes / revision_needed / blocked  

## Core checks
- [ ] scope respected
- [ ] acceptance criteria met
- [ ] architecture fit acceptable
- [ ] no obvious regression
- [ ] docs updated if needed
- [ ] safe enough for `dev`

## Notes
...

## Merge recommendation
...
