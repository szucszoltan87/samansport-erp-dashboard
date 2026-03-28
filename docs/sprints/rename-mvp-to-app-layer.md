# Sprint: rename-mvp-to-app-layer

## Sprint Metadata

**Sprint title:** Rename `mvp/` to `app_layer/`

**Branch type:** feature

**Branch name:** `feature/rename-mvp-to-app-layer`

**Base branch:** `dev`

**Target merge branch:** `dev`

**Owner:** Zoltan Szucs

**Date opened:** 2026-03-28

**Status:** `in_progress`

---

## 1. Sprint Goal

Rename the `mvp/` folder to `app_layer/` and update all active references so the repository is structurally clearer and easier to understand for both humans and Claude Code sessions.

This sprint does not change product behavior. It is a mechanical path rename with targeted reference updates.

This sprint was explicitly deferred from `feature/reflex-structure-alignment` and is now being executed as its own focused sprint.

---

## 2. Sprint Type

Refactor / Stabilization

---

## 3. Why This Sprint Matters

The `mvp/` folder name is ambiguous and misleading:

- It implies the folder is a temporary prototype rather than the active application codebase
- It does not reflect what the folder actually contains: a Reflex frontend, domain/business logic, data access layer, models, config, and tests
- It creates confusion for new contributors and Claude Code sessions about where the "real app" lives
- `app_layer/` is a more accurate name — the folder is the application layer sitting above the Supabase/ERP infrastructure

This was identified as a follow-up item in the `reflex-structure-alignment` sprint and is now resolved.

---

## 4. Scope

- Rename `mvp/` to `app_layer/` via `git mv`
- Update `README.md`: Quick Start `cd mvp` → `cd app_layer`, Repository Layout table
- Update `docs/BACKEND_ARCHITECTURE.md`: mermaid diagram label and directory listing
- Update `docs/SECURITY_AUDIT.md`: path references to `mvp/`
- Update comment in `app_layer/samansport/pages/dashboard.py` that references `mvp/`
- Update `docs/sprints/reflex-structure-alignment.md`: mark follow-up item as addressed
- Create this sprint artifact

---

## 5. Out of Scope

- No Python import changes — the `samansport` package name is independent of the folder name
- No renaming of `_mvp_dir` variables in Python — these are dynamically resolved via `__file__` and are not broken by the folder rename
- No changes to `docs/archive/` — historical records should remain as written
- No changes to `run.bat` or `setup.bat` — legacy scripts that run from inside the folder
- No refactoring of business logic
- No Supabase changes
- No Reflex app behavior changes

---

## 6. Expected Files / Modules Affected

- `mvp/` → `app_layer/` (folder rename via `git mv`)
- `README.md` (update Quick Start and Repository Layout)
- `docs/BACKEND_ARCHITECTURE.md` (update mermaid diagram and directory listing)
- `docs/SECURITY_AUDIT.md` (update path references)
- `app_layer/samansport/pages/dashboard.py` (update stale comment)
- `docs/sprints/reflex-structure-alignment.md` (update follow-up note)
- `docs/sprints/rename-mvp-to-app-layer.md` (create — this file)

---

## 7. Product / User Impact

No user-facing impact. Developer experience improvement:

- The active application folder has a name that reflects its actual role
- New contributors and Claude Code sessions can immediately understand the folder structure
- Startup instructions in `README.md` use the correct path
- Architecture documentation uses consistent path references

---

## 8. Technical Approach

Mechanical rename sprint. No logic changes.

Steps:
1. `git mv mvp app_layer` — rename the folder, preserving full git history
2. Update `README.md` path references
3. Update `docs/BACKEND_ARCHITECTURE.md` path references
4. Update `docs/SECURITY_AUDIT.md` path references
5. Update stale comment in `app_layer/samansport/pages/dashboard.py`
6. Update follow-up note in `docs/sprints/reflex-structure-alignment.md`

Python imports are unaffected: `rxconfig.py` uses `app_name="samansport"` which is the Reflex app/package name, not the folder name. All `from samansport.xxx import` statements resolve to the `samansport/` package inside `app_layer/` — no changes needed.

---

## 9. Constraints

- Must stay on `feature/rename-mvp-to-app-layer`
- No changes to Python business logic
- No changes to Reflex app behavior
- No Supabase changes
- Prefer `git mv` over delete+create to preserve git history
- Archive docs must not be modified
- Must be merge-safe into `dev`

---

## 10. Dependencies

Depends on `feature/reflex-structure-alignment` having been merged into `dev` first (it introduced the `docs/BACKEND_ARCHITECTURE.md` and `docs/sprints/` structure this sprint updates).

---

## 11. Risks

- **Low:** If a test runner or CI script references `mvp/` by absolute path string, it could break. Mitigation: search confirms no Python path strings hardcode `"mvp"` — all paths are dynamically resolved.
- **Low:** Developers with the old path cached locally (open terminals, IDE configs) will get a path error until they update. This is expected and not a code defect.
- **None:** No business logic is touched, so no regression risk.

---

## 12. Acceptance Criteria

1. `mvp/` folder no longer exists; `app_layer/` contains identical content with preserved git history
2. `README.md` Quick Start uses `cd app_layer`
3. `README.md` Repository Layout table references `app_layer/`
4. `docs/BACKEND_ARCHITECTURE.md` mermaid diagram and directory listing use `app_layer/`
5. `docs/SECURITY_AUDIT.md` path references updated to `app_layer/`
6. Comment in `app_layer/samansport/pages/dashboard.py` updated
7. `docs/sprints/reflex-structure-alignment.md` follow-up item updated to note it is resolved
8. No Python imports broken
9. No app behavior changed
10. `docs/archive/` files are untouched

---

## 13. Evaluation Checklist

- [ ] Scope respected — only path rename and targeted reference updates
- [ ] Acceptance criteria met — see above
- [ ] No obvious unrelated churn introduced
- [ ] No known critical regression (path rename only)
- [ ] UI behavior reviewed — N/A (no UI changes)
- [ ] Data behavior reviewed — N/A (no data changes)
- [ ] Docs updated — yes, path references updated
- [ ] Branch is appropriate for merge into `dev`

---

## 14. Testing / Validation Notes

- Verified with grep that no Python code hardcodes the string `"mvp"` as a path component
- Verified `rxconfig.py` uses `app_name="samansport"` — unaffected by folder rename
- Verified `samansport/` package imports are relative to `app_layer/` — unaffected
- Verified `_mvp_dir` variable in `state.py` and `dashboard.py` resolves dynamically via `__file__` — safe after rename
- Not validated with a live `reflex run` — manual test recommended after merge to `dev`

---

## 15. Merge Recommendation

Ready to merge into `dev` after evaluator review.

Low-risk mechanical rename. No logic changes. All reference updates are targeted and verified.

---

## 16. Follow-Up Work

- **Rename `_mvp_dir` variable** in `app_layer/samansport/state.py` and `app_layer/samansport/pages/dashboard.py` to `_app_layer_dir` — cosmetic cleanup, low priority, can be done in any passing sprint
- **Add a `Makefile` or `start.sh`** at repo root for one-command startup pointing into `app_layer/` — useful convenience improvement
- **Audit other docs** for remaining Streamlit-era references (`run.bat`, `setup.bat` still reference Streamlit) — low priority cleanup

---

## 17. Handoff Summary

**What changed:**
- `mvp/` folder renamed to `app_layer/` (git history preserved)
- `README.md` startup and layout sections updated
- `docs/BACKEND_ARCHITECTURE.md` diagram and directory listing updated
- `docs/SECURITY_AUDIT.md` path references updated
- Comment in `app_layer/samansport/pages/dashboard.py` updated
- `docs/sprints/reflex-structure-alignment.md` follow-up item marked as addressed

**What remains open:**
- `_mvp_dir` variable names in Python (functional but cosmetically stale) — proposed as minor follow-up
- `run.bat`/`setup.bat` still reference Streamlit — legacy issue, separate concern

**Special attention:**
- Run the app from inside `app_layer/` using `reflex run`
- `rxconfig.py` app name remains `"samansport"` — correct and unchanged
- Archive docs still say `mvp/` — intentional, they are historical records

**Known temporary compromises:**
- None. This sprint is clean and self-contained.
