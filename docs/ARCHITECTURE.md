# Architecture Overview

## Purpose

This document gives a product-level and system-level architecture view of the repository.

It is intended to be the **broad architectural map** for the project.

If the repository also contains a more detailed backend-specific architecture document, that document should be treated as a deeper technical companion rather than a replacement for this overview.

---

## 1. Architecture Intent

SamanSport ERP Dashboard is a modern application layer built on top of the existing **Tharanis ERP** data environment.

The architecture must support these goals:

- better UI/UX than the legacy ERP surface
- reliable access to ERP-backed business data
- useful reporting and analytics
- inventory-related operational support
- gradual evolution from MVP into a shippable internal business application
- sustainable development with Claude Code assistance

This architecture is not meant for a full ERP rebuild.

It is meant to provide a stable and extensible layer **on top of** the current ERP.

---

## 2. High-Level System Shape

The system should be thought of as five broad layers:

1. **Frontend application layer**
2. **Application / domain logic layer**
3. **Data access and sync layer**
4. **Persistence and cache layer**
5. **External ERP data source**

At a high level:

- users interact with a modern app UI
- the app reads business data through controlled access layers
- cached / persisted data is preferred for speed and stability
- background synchronization keeps the system fresh
- the legacy ERP remains the underlying source system

---

## 3. Main Architectural Principle

The product should use the legacy ERP as a data source, but should not expose users directly to legacy ERP usability problems.

That means the architecture should favor:

- fast reads
- stable user-facing flows
- explicit sync behavior
- clear data ownership boundaries
- product-level usability over source-system awkwardness

---

## 4. Main Layers

## 4.1 Frontend Layer

### Official direction
The official frontend direction is:

- **Reflex**

### Responsibility
The frontend layer is responsible for:

- page structure
- navigation
- user interaction
- presentation of reporting and operational views
- consistent UI patterns
- modern UX

### Desired qualities
The frontend should be:

- consistent
- understandable
- responsive
- modular
- easy to extend
- clearly separated from raw source-system complexity

---

## 4.2 Application / Domain Layer

### Responsibility
This layer should translate raw ERP-backed data into product behavior.

Typical responsibilities:

- business-oriented view preparation
- feature logic
- filtering and shaping data for the UI
- operational helper logic
- decision-support logic
- page-level orchestration

### Desired qualities
This layer should become the place where product intelligence grows.

It should not be just a thin charting wrapper.

Over time, this is where inventory-related help, alerts, summaries, and workflow-oriented logic should live.

---

## 4.3 Data Access and Sync Layer

### Responsibility
This layer is responsible for:

- reading cached business data
- managing sync freshness rules
- triggering background refreshes where needed
- isolating frontend and product logic from direct source-system complexity

### Desired qualities
This layer should be:

- explicit
- stable
- testable
- aware of staleness and refresh timing
- safe under repeated access

This is one of the most important layers in the system because it protects the product from legacy ERP slowness and quirks.

---

## 4.4 Persistence / Cache Layer

### Responsibility
This layer stores application-usable copies of ERP-backed data.

Typical responsibilities:

- entity tables
- sync metadata
- freshness tracking
- lock / concurrency protection
- historical data hydration
- reliable fast reads for the app

### Desired qualities
This layer should support:

- predictable reads
- repeatable sync behavior
- controlled refresh logic
- separation between source-system latency and user-facing latency

This layer is critical for making the app feel fast and trustworthy.

---

## 4.5 External Source Layer

### Responsibility
This layer is the underlying legacy ERP data source.

In this project, that means:

- **Tharanis ERP / Tharanis SOAP API**

### Architectural stance
This layer is a dependency, not the product itself.

The app should:

- respect its constraints
- work with its data model
- isolate its complexity where possible
- avoid leaking source-system awkwardness into the user experience

---

## 5. Current Direction of the Repository

The repository should be understood as evolving from an MVP toward a more productized structure.

At a broad level, the current direction is:

- keep the existing MVP foundation
- standardize on Reflex
- strengthen system clarity
- improve repo structure
- support sustainable feature growth
- introduce harness-driven delivery discipline

This means the architecture should support **evolution**, not restart.

---

## 6. Architectural Priorities

The highest architectural priorities for the next phase are:

### 6.1 Frontend alignment
Move the visible product direction clearly toward Reflex and reduce ambiguity from prior stack phases.

### 6.2 Strong system boundaries
Make frontend, domain logic, sync logic, and persistence responsibilities clearer over time.

### 6.3 Product-oriented modules
Organize work around business capabilities, not only around screens.

### 6.4 Stable data behavior
Users must be able to trust what they see.

### 6.5 Merge-safe growth
Architecture should evolve in sprint-sized increments that are safe to merge into `dev`.

---

## 7. Suggested Capability Areas

The app is likely to grow across these capability areas:

- dashboard / overview
- sales reporting
- inventory visibility
- stock movement analysis
- operational inventory helpers
- sync / freshness visibility
- exports and reporting convenience
- admin and support tooling

These should grow in modules, not as one giant monolith of mixed logic.

---

## 8. Architectural Constraints

The system should respect the following constraints:

- build on top of the current MVP
- do not restart from zero
- keep Reflex as the official frontend direction
- preserve a practical relationship with the existing ERP
- avoid unnecessary framework churn
- avoid mixing unrelated changes in one sprint
- keep the repo understandable for both humans and Claude Code

---

## 9. Development Architecture

The project is not only a software system; it is also being set up as a sustainable development system.

That means the architecture must be compatible with:

- branch-based delivery
- sprint-based implementation
- planner / builder / evaluator workflow
- file-based project memory
- disciplined merge flow

### Branching model
Development should follow:

- `master`
- `dev`
- `feature/*`
- `fix/*`

The architecture should evolve through small increments on top of this structure.

---

## 10. Desired Future Shape

Over time, the ideal architecture should become:

- a clean Reflex frontend
- a clearer application/domain layer
- stable ERP-backed data access
- trustworthy cached / persisted business data
- product modules that reflect real user needs
- supportable operational tooling
- release-ready internal application quality

The system should gradually become easier to reason about, not harder.

---

## 11. Non-Goals

The architecture should not drift into these non-goals:

- full ERP replacement
- speculative platform overdesign
- framework experimentation without product value
- giant rewrites that reset momentum
- UI-only thinking with no product logic evolution
- architecture diagrams that do not reflect actual repo direction

---

## 12. Definition of Good Architectural Progress

Architectural progress is good if:

- the repo becomes easier to understand
- responsibilities between layers become clearer
- new features are easier to add safely
- UI and product behavior become more consistent
- ERP-backed data handling becomes more trustworthy
- developers and Claude Code can work with less ambiguity
- the app moves closer to being a shippable product

---

## 13. Immediate Architectural Focus

The next practical architectural focus should be:

1. clarify repo structure
2. align on Reflex direction
3. preserve and strengthen the sync/data backbone
4. organize product work in smaller modules
5. use sprint-driven changes instead of open-ended evolution

This is the architectural direction for the next stage of the project.
