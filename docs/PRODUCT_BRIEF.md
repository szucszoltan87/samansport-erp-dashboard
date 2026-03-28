# Product Brief

## Product Name

**SamanSport ERP Dashboard**

---

## 1. Product Summary

SamanSport ERP Dashboard is a modern application layer built on top of the existing **Tharanis ERP** data environment.

The purpose of the product is to give internal users a significantly better way to work with ERP data than the legacy ERP interface allows today.

The app is intended to improve:

- usability
- speed of access to data
- visibility into operations
- reporting quality
- inventory-related decision support

This product is **not** a rebuild of the underlying ERP.

It is a modern operational and reporting layer built on top of the current ERP data and workflows.

---

## 2. Product Vision

The long-term vision is to create an internal business application that makes everyday ERP-related work easier, faster, and more actionable.

The product should gradually evolve from an MVP analytics app into a more complete operational tool that helps users:

- understand business performance more quickly
- navigate sales and inventory data more easily
- identify issues earlier
- make better operational decisions
- reduce dependency on a poor legacy interface

The app should feel modern, clear, fast, and trustworthy.

---

## 3. Problem Statement

The existing ERP environment contains valuable business data, but the user experience is limited.

Typical issues with legacy ERP surfaces include:

- clunky UI/UX
- slow or inconvenient access to data
- poor visibility across business metrics
- limited practical reporting
- weak operational support for day-to-day decisions
- too much manual interpretation by the user

As a result, users spend more time extracting and interpreting information than they should.

The opportunity is to build a cleaner application layer on top of the same ERP data so users can work faster and make better decisions.

---

## 4. Target Users

The main target users are internal business users who need regular access to ERP-driven operational data.

Likely user types include:

### 4.1 Operational users
People who need day-to-day visibility into sales, inventory, and stock movement.

### 4.2 Management / decision-makers
Users who want faster reporting, performance visibility, and higher-level operational insight.

### 4.3 Admin or support users
Users who may need to monitor sync behavior, data freshness, or system reliability over time.

The product should primarily optimize for **internal usability and business usefulness**, not public-facing presentation.

---

## 5. Core User Needs

The product should help users do the following well:

- access business data faster
- understand key business metrics more easily
- navigate sales and inventory information in a modern UI
- identify important changes or exceptions earlier
- reduce friction compared to the legacy ERP experience
- rely on data that feels stable and understandable

For the inventory area in particular, the product should help users move beyond passive reporting and toward practical operational support.

---

## 6. Product Goals

### 6.1 Short-term goals
- stabilize the MVP foundation
- standardize the frontend direction on **Reflex**
- improve structure and maintainability
- provide a cleaner and more useful reporting experience
- make the repo and development workflow more sustainable

### 6.2 Medium-term goals
- improve operational workflows around inventory and business visibility
- introduce more useful decision-support views
- improve product consistency and reliability
- strengthen evaluation, release discipline, and merge safety

### 6.3 Long-term goals
- evolve the app into a genuinely shippable internal business application
- reduce dependence on the legacy ERP interface for common workflows
- create a trustworthy operational layer on top of ERP data

---

## 7. Version 1 Focus

Version 1 should focus on being a **usable, valuable, modern internal business app**, not a giant all-in-one ERP replacement.

The V1 emphasis should be:

- modern Reflex-based UI shell
- clean navigation and layout
- strong reporting foundations
- good sales and inventory visibility
- practical inventory support features
- stable data behavior
- release-ready internal usability

V1 should aim to be clearly more usable and more useful than working directly in the legacy ERP for the covered workflows.

---

## 8. Likely V1 Capability Areas

The product will likely need to support these areas in V1 or near-V1 form:

### 8.1 Dashboard / overview
A clear entry point that surfaces important business signals.

### 8.2 Sales reporting
Views that make sales data easier to inspect, compare, and interpret.

### 8.3 Inventory visibility
Clearer understanding of stock levels and stock-related patterns.

### 8.4 Stock movement analysis
Usable visibility into warehouse movement history and trends.

### 8.5 Operational helpers
Features that support action, not just reporting, especially around inventory.

### 8.6 Data freshness / reliability visibility
Enough visibility so users can trust what they are seeing.

These areas should be prioritized in small, high-value increments.

---

## 9. Product Principles

The product should follow these principles:

### 9.1 Build on the MVP
Do not restart from zero.
The product should evolve from the current MVP.

### 9.2 Respect the existing ERP reality
The product is built on top of a live legacy ERP data source.
It should work with that reality, not ignore it.

### 9.3 Usability over complexity
If a feature is technically impressive but does not improve usability or business value, it should not be prioritized.

### 9.4 Clear over clever
The app should feel understandable and stable.

### 9.5 Small safe increments
The product should grow through disciplined, sprint-sized steps.

### 9.6 Internal business value first
The main measure of success is whether internal users can work better and faster.

---

## 10. Out of Scope for Now

The following are explicitly out of scope for now:

- rebuilding the ERP from scratch
- replacing all legacy ERP workflows immediately
- introducing a large multi-product platform vision too early
- speculative architecture redesign without product value
- broad framework experimentation outside the chosen direction
- public-facing productization
- solving every business workflow in V1

This helps keep the project realistic and focused.

---

## 11. Technical Direction

The official frontend direction is:

- **Reflex**

The app should continue building on top of the current system rather than being restarted.

The product should be developed in a way that is:

- maintainable
- reviewable
- branch-disciplined
- sprint-based
- compatible with Claude Code assisted development

The development workflow is part of product sustainability.

---

## 12. Success Criteria

The product is moving in the right direction if:

- users can access important ERP-related information more easily
- the app is clearly more usable than the legacy interface in the covered workflows
- reporting becomes faster and more actionable
- inventory-related workflows become easier to understand and act on
- the system feels stable and trustworthy
- the repo becomes easier to maintain and evolve
- features can be delivered without chaos or repeated rewrites

---

## 13. Current Product Position

The current state should be thought of as:

**an MVP foundation with real value, now being matured into a sustainable product**

This means the next phase is not “start over.”

The next phase is:

- stabilize
- structure
- clarify
- improve
- expand in disciplined steps

---

## 14. Immediate Product Development Priorities

The immediate priorities are:

1. establish a sustainable harness and repo workflow
2. align the project around Reflex
3. strengthen product clarity and documentation
4. continue evolving the MVP in small, useful increments
5. move toward a release-worthy internal application

This is the operating direction for the next stage of the project.
