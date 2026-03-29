# Sprint: keszlet-monitor-methodology

## Sprint Metadata

**Sprint title:** Készlet Monitor — In-app methodology & column explanations

**Branch type:** `feature`

**Branch name:** `feature/keszlet-monitor-methodology`

**Base branch:** `dev`

**Target merge branch:** `dev`

**Date opened:** 2026-03-29

**Status:** `in_progress`

---

## 1. Sprint Goal

Add in-app explanations to the Készlet Monitor so users can understand what the numbers mean without needing the external PDF report. Each column header gets a small info icon — hover for a short tooltip, click for detailed methodology on complex topics (ROP, IP, forecasting, status logic).

This sprint is about **product clarity and trust**, not about changing the monitor logic.

---

## 2. Sprint Type

UI/UX improvement

---

## 3. Why This Sprint Matters

Users currently need a separate PDF to understand the Készlet Monitor. The numbers (ROP, IP, Jav, stability classifications) are meaningless without context. Adding inline explanations:
- reduces support questions
- increases trust in the monitor's recommendations
- makes the tool self-documenting
- moves the product closer to a shippable internal application

---

## 4. Scope

- Small "i" info icons next to each column header in the monitor table
- Hover tooltip with a short explanation for each column
- Clickable modals for complex topics:
  - ROP formula and worked example
  - IP / Inventory Position definition
  - Forecasting method explanation
  - Status logic (RENDELJ vs OK)
  - Stability classification
  - Suggested order quantity (Jav)
- Compact legal disclaimer accessible from the methodology
- All content in Hungarian, matching the app language

---

## 5. Out of Scope

- No changes to monitor business logic or SQL
- No table redesign or layout overhaul
- No new pages or routes
- No new dependencies or frameworks
- No changes to other tabs (Értékesítés, Mozgástörténet)

---

## 6. Expected Files / Modules Affected

- `app_layer/samansport/pages/analytics.py` — state vars, column headers, tooltip/modal components

---

## 7. Product / User Impact

- Users can understand every column by hovering or clicking the info icon
- Complex methodology (ROP, forecasting) is accessible in-app via modals
- No need to reference the external PDF during daily use
- Monitor becomes a self-documenting operational tool

---

## 8. Technical Approach

- Add `methodology_modal: str` state variable to `InventoryMonitorState` (tracks which modal is open, empty string = none)
- Create helper function `_col_header_with_info()` that renders column name + info icon
- Info icon shows tooltip on hover (CSS title or Reflex tooltip)
- For complex columns, clicking the icon sets `methodology_modal` to a key, which opens an `rx.dialog`
- All content is static Hungarian text — no data dependencies
- Reuse existing styling patterns (COLORS, font sizes, spacing)

---

## 9. Constraints

- Must stay within Reflex
- Must not change existing table data or logic
- Must not break existing monitor functionality
- Column headers must remain compact
- Modals must be readable but not overwhelming

---

## 10. Dependencies

- Existing Készlet Monitor implementation (already working)
- Reflex tooltip and dialog components

---

## 11. Risks

- Tooltip behavior may vary across browsers
- Info icons could make narrow column headers feel cramped — mitigate with small icon size
- Modal content length needs to stay manageable

---

## 12. Acceptance Criteria

- Every column header in the monitor table has an "i" info icon
- Hovering over the icon shows a short tooltip explanation
- Complex columns (ROP, IP, Stab, Jav, St.) have clickable modals with detailed methodology
- Modal content covers: ROP formula, IP definition, forecasting method, status logic, stability, suggested quantities
- A worked example (SKU 4633) is included in the ROP modal
- A short disclaimer is accessible
- All text is in Hungarian
- Existing monitor functionality is unchanged
- No regressions in other tabs

---

## 13. Evaluation Checklist

- [ ] scope respected
- [ ] acceptance criteria met
- [ ] no obvious unrelated churn
- [ ] no known critical regression introduced
- [ ] UI behavior reviewed
- [ ] data behavior reviewed
- [ ] branch is appropriate for merge into `dev`

---

## 14. Testing / Validation Notes

- Manual UI review required: hover tooltips, modal open/close, content accuracy
- Check that table remains scrollable and usable with info icons
- Verify no regressions in Értékesítés and Mozgástörténet tabs

---

## 15. Merge Recommendation

Pending implementation and review.

---

## 16. Follow-Up Work

- Consider adding a standalone "Módszertan" page if the methodology grows
- Evaluate whether tooltips need mobile/touch support later

---

## 17. Handoff Summary

Pending completion.
