# Sprint: reflex-structure-alignment

## Sprint Metadata

**Sprint title:** Reflex Structure Alignment

**Branch type:** feature

**Branch name:** `feature/reflex-structure-alignment`

**Base branch:** `dev`

**Target merge branch:** `dev`

**Owner:** Zoltan Szucs

**Date opened:** 2026-03-28

**Status:** `in_progress`

---

## 1. Sprint Goal

Align the repository structure around Reflex so the project is easier to understand, easier to extend, and less ambiguous for future contributors and Claude Code sessions.

This sprint does not add features or change app behavior. It improves structural clarity through targeted doc consolidation, a developer-facing Quick Start, and consistent placement of architecture documentation.

The goal is that after this sprint, a new engineer can open the repo, immediately understand where the active app lives, and know how to run it — without needing to dig through the folder tree.

---

## 2. Sprint Type

Stabilization / Documentation / process improvement

---

## 3. Why This Sprint Matters

Before this sprint, the repo has several structural ambiguities:

- `BACKEND_ARCHITECTURE.md` lives at the repo root alongside `README.md` and `CLAUDE.md`, not in `docs/` where all other architecture docs live
- `docs/ARCHITECTURE.md` references a "more detailed backend-specific architecture document" without naming or linking to it
- `README.md` describes the product but has no Quick Start — a new developer cannot run the app without exploring the folder tree manually
- The `mvp/` folder contains the entire active Reflex app but the name doesn't signal this clearly

These ambiguities slow down contributors, reduce Claude Code session quality, and make the project harder to onboard into.

---

## 4. Scope

- Move `BACKEND_ARCHITECTURE.md` from repo root to `docs/BACKEND_ARCHITECTURE.md`
- Update `docs/ARCHITECTURE.md` to explicitly name and link to `docs/BACKEND_ARCHITECTURE.md`
- Add a "Quick Start" section to `README.md` with run instructions for the Reflex app
- Add a "Repository Layout" section to `README.md` explaining what each top-level folder contains
- Create `docs/sprints/` directory and this sprint artifact

---

## 5. Out of Scope

- Renaming `mvp/` to a more descriptive name — valid improvement but a separate sprint (touches scripts, docs references, potentially Python paths)
- Reorganizing reference files at root (`Tharanis_API_doc.pdf`, connector JSON, design pages) — low clarity value, higher disruption risk
- Any changes to Python application code
- Any changes to Reflex app behavior or UI
- Any changes to Supabase functions or migrations
- Merging or rewriting the architecture docs — only linking and placement

---

## 6. Expected Files / Modules Affected

- `docs/sprints/reflex-structure-alignment.md` (create — this file)
- `BACKEND_ARCHITECTURE.md` (delete from root)
- `docs/BACKEND_ARCHITECTURE.md` (create — moved from root)
- `docs/ARCHITECTURE.md` (update — add explicit reference to backend doc)
- `README.md` (update — add Quick Start and Repository Layout sections)

---

## 7. Product / User Impact

No user-facing impact. This sprint improves developer experience:

- A new contributor can understand the repo layout without trial and error
- A new Claude Code session starts with less structural ambiguity
- Architecture documentation is in one consistent location
- Running the app locally requires no guesswork

---

## 8. Technical Approach

Doc-only sprint. No Python code changes. No Reflex code changes.

Steps:
1. Move `BACKEND_ARCHITECTURE.md` → `docs/BACKEND_ARCHITECTURE.md` (filesystem rename)
2. Add explicit link in `docs/ARCHITECTURE.md` (one paragraph update)
3. Add Quick Start + Repository Layout to `README.md` (two new sections)
4. Write this sprint artifact

All changes are in Markdown. Zero runtime impact.

---

## 9. Constraints

- No Python code changes
- No Reflex app behavior changes
- No Supabase changes
- Must stay on `feature/reflex-structure-alignment`
- Changes must be merge-safe into `dev`
- Must not disrupt existing doc references in CLAUDE.md or HARNESS_PLAN.md

---

## 10. Dependencies

None. This sprint is fully self-contained.

---

## 11. Risks

- **Low:** If `BACKEND_ARCHITECTURE.md` is referenced by path in other docs, those references will break. Mitigation: search for references before moving.
- **Low:** Quick Start instructions may become stale if the startup flow changes later. Mitigation: keep instructions minimal and tied to the actual `mvp/` structure.
- **None:** No code is touched, so no regression risk.

---

## 12. Acceptance Criteria

1. `BACKEND_ARCHITECTURE.md` no longer exists at repo root
2. `docs/BACKEND_ARCHITECTURE.md` contains the same content
3. `docs/ARCHITECTURE.md` explicitly names and links `docs/BACKEND_ARCHITECTURE.md`
4. `README.md` includes a working "Quick Start" section with run commands
5. `README.md` includes a "Repository Layout" section explaining `mvp/`, `supabase/`, `docs/`
6. This sprint artifact exists at `docs/sprints/reflex-structure-alignment.md`
7. No Python code was changed
8. No app behavior was changed
9. All internal doc cross-references are consistent

---

## 13. Evaluation Checklist

- [x] Scope respected — only doc moves and additions
- [x] Acceptance criteria met — see above
- [x] No obvious unrelated churn introduced
- [x] No known critical regression (doc-only sprint)
- [ ] UI behavior reviewed — N/A (no UI changes)
- [ ] Data behavior reviewed — N/A (no data changes)
- [x] Docs updated — primary purpose of this sprint
- [x] Branch is appropriate for merge into `dev`

---

## 14. Testing / Validation Notes

- Verified `BACKEND_ARCHITECTURE.md` moved correctly and content is identical
- Verified `docs/ARCHITECTURE.md` link to backend doc is accurate
- Verified `README.md` Quick Start instructions match the actual `mvp/` folder structure
- Searched for other references to `BACKEND_ARCHITECTURE.md` in the repo before moving
- No automated tests apply (doc-only sprint)
- Not validated end-to-end app run (out of scope for a doc sprint)

---

## 15. Merge Recommendation

Ready to merge into `dev`.

This is a low-risk, doc-only sprint with no code changes. Changes are minimal, focused, and reviewable. Acceptance criteria are met.

---

## 16. Follow-Up Work

- **Rename `mvp/`** → clearer name (e.g., `frontend/` or `app_layer/`) in a dedicated follow-up sprint. Requires updating startup scripts, doc references, and verifying Python import paths.
- **Organize root reference files** (`Tharanis_API_doc.pdf`, connector JSON, design pages) into a `reference/` or `docs/reference/` folder if the root continues to feel cluttered.
- **Add a `Makefile` or `start.sh`** at repo root for one-command startup, pointing into `mvp/`.

---

## 17. Handoff Summary

**What changed:**
- `BACKEND_ARCHITECTURE.md` moved from repo root to `docs/BACKEND_ARCHITECTURE.md`
- `docs/ARCHITECTURE.md` now explicitly references the backend architecture doc
- `README.md` now has Quick Start (run commands) and Repository Layout sections
- `docs/sprints/` folder created with this sprint artifact

**What remains open:**
- `mvp/` folder name is still ambiguous — proposed as follow-up sprint
- Root reference files (PDF, JSON, pages) remain at root

**Special attention:**
- The `mvp/` folder is the active Reflex app root. Run everything from inside it.
- `rxconfig.py` in `mvp/` is the Reflex startup configuration.

**Known temporary compromises:**
- None. This sprint is clean and self-contained.
