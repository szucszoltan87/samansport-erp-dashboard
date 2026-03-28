# Release Checklist

## Purpose

This checklist is used before promoting work from `dev` to `master`.

`master` should represent a stable, release-worthy state.

This checklist exists to prevent premature promotion of unstable or poorly reviewed work.

---

## Release Context

**Release name / tag:**  
**Date:**  
**Prepared by:**  
**Source branch:** `dev`  
**Target branch:** `master`  
**Status:** ready / not_ready / blocked  

---

## 1. Release Scope

### 1.1 What is included?
List the main features, fixes, and improvements expected in this release.

- ...
- ...
- ...

### 1.2 What is explicitly not included?
State important omissions or deferred items.

- ...
- ...
- ...

---

## 2. Branch Discipline Check

- [ ] Release candidate is coming from `dev`
- [ ] Work was merged into `dev` through `feature/...` or `fix/...` branches
- [ ] There is no known reason to bypass the normal flow
- [ ] `master` is being treated as stable / release-worthy

### Notes
...

---

## 3. Documentation Check

- [ ] `README.md` is still broadly accurate
- [ ] `CLAUDE.md` still reflects current project direction
- [ ] architecture docs are not obviously outdated
- [ ] sprint artifacts are in acceptable shape
- [ ] release notes or summary exist if needed

### Notes
...

---

## 4. Product Check

- [ ] Release moves the product in the intended direction
- [ ] Changes align with the product brief
- [ ] No silent product-scope drift has been introduced
- [ ] The release improves usability and/or business value
- [ ] The release is worth promoting to stable state

### Notes
...

---

## 5. Frontend / UX Check

- [ ] Reflex remains the official frontend direction
- [ ] Main navigation / shell behavior is coherent
- [ ] Major user-facing flows are understandable
- [ ] No major UX regression is known
- [ ] Empty or error states are not obviously broken

### Notes
...

---

## 6. Data / Integration Check

- [ ] ERP-backed data behavior is acceptable
- [ ] Sync or freshness behavior is acceptable for release
- [ ] No known critical data mismatch is unresolved
- [ ] Known data limitations are documented if necessary
- [ ] Release does not undermine trust in the data surface

### Notes
...

---

## 7. Stability Check

- [ ] No known critical blocker remains
- [ ] No known major regression remains
- [ ] Important fixes are included
- [ ] Release is stable enough for intended users
- [ ] Open issues are acceptable for a stable branch

### Notes
...

---

## 8. Validation Check

Mark what has actually been validated.

- [ ] Main flows manually reviewed
- [ ] Key UI paths checked
- [ ] Important bug fixes verified
- [ ] Data behavior spot-checked
- [ ] Automated checks passed
- [ ] Build / type / lint status acceptable
- [ ] Evaluator reviews completed for major included work

### Notes
Be explicit about what was actually verified and what was not.

...

---

## 9. Quality Bar Check

- [ ] Included branches were appropriate in size and scope
- [ ] Work is understandable enough to maintain
- [ ] No obvious architecture damage was introduced
- [ ] Release is not just “works on my machine”
- [ ] Release is genuinely appropriate for `master`

### Notes
...

---

## 10. Known Issues

List all known issues that still exist at release time.

For each issue, note:
- severity
- user impact
- whether it is acceptable for `master`

### Known issues
- ...
- ...
- ...

---

## 11. Go / No-Go Decision

Choose one:

- [ ] Go — merge `dev` into `master`
- [ ] No-Go — keep work in `dev`
- [ ] Go with known limitations
- [ ] Blocked pending fixes

### Reason
...

---

## 12. Post-Release Follow-Up

List any work that should happen immediately after release.

Examples:
- hotfix candidate
- documentation update
- follow-up cleanup sprint
- monitoring check
- UI polish follow-up

...

---

## 13. Final Release Summary

Write a concise summary of:

- what this release means
- why it is or is not ready
- any meaningful limitations
- next expected action

...

---

# Quick Release Version

## Release
**Name:**  
**Date:**  
**Source:** dev  
**Target:** master  
**Status:** ready / not_ready / blocked  

## Core checks
- [ ] docs acceptable
- [ ] major flows reviewed
- [ ] no critical blocker known
- [ ] product direction intact
- [ ] data behavior acceptable
- [ ] safe for `master`

## Known issues
...

## Decision
Go / No-Go / Go with limitations

## Notes
...
