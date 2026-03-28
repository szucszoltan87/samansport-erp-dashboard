# SamanSport ERP Dashboard

SamanSport ERP Dashboard is a modern application layer built on top of the existing **Tharanis ERP** data environment.

The purpose of the project is to provide a significantly better user experience than the legacy ERP interface while adding practical business value through modern reporting, analytics, and operational support tools.

## What the app targets

The app is intended to help users work with ERP data more effectively by providing:

- cleaner and faster UI/UX
- easier access to sales and inventory information
- better reporting and analytics
- operational support for inventory-related decisions
- a path from a reporting MVP toward a more complete internal business application

## Product philosophy

This project is **not** about replacing the underlying ERP from scratch.

Instead, it builds a modern operational layer on top of the existing ERP data and workflows, with the goal of improving usability, visibility, and decision support.

## Current direction

The project is evolving from an MVP into a more robust product.

Key direction:

- build on top of the existing MVP
- keep the current ERP integration context
- standardize on **Reflex** as the frontend stack
- develop the app in a disciplined, sprint-based way
- use an explicit harness workflow for planning, building, and evaluation

## Development workflow

Main Git branch structure:

- `master` — stable, release-worthy state
- `dev` — integration branch

Work should be done from `dev` using:

- `feature/<name>`
- `fix/<name>`

Flow:

1. create a working branch from `dev`
2. implement and test the change
3. merge back into `dev`
4. promote `dev` into `master` only when stable

## Quick Start

The active Reflex application lives in the `mvp/` folder.

```bash
cd mvp

# First time only: create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment config and fill in your values
cp .env.example .env

# Run the app
reflex run
```

The app will be available at `http://localhost:3000` by default.

---

## Repository Layout

```
mvp/                 Active Reflex frontend application
  rxconfig.py        Reflex configuration and app entry point
  samansport/        Reflex app package (pages, components, state)
  tharanis_client.py Data access layer (Supabase + SOAP fallback)
  models.py          Pydantic data models
  charts.py          Chart helpers
  helpers.py         Utility functions
  tests/             pytest test suite
  requirements.txt   Python dependencies

supabase/            Backend infrastructure
  migrations/        PostgreSQL DDL migrations (6 files)
  functions/         Deno Edge Functions (sync, refresh, hydration)

docs/                Project documentation and governance
  ARCHITECTURE.md    Broad system architecture overview
  BACKEND_ARCHITECTURE.md  Detailed data flow and sync patterns
  PRODUCT_BRIEF.md   Product goals and user targets
  HARNESS_PLAN.md    Development harness plan
  EVALUATOR_CHECKLIST.md  Pre-merge quality gate
  sprints/           Sprint artifacts per branch
```

---

## Status

The repository already contains a working MVP foundation.
The current focus is to harden the architecture, improve the development process, and evolve the system into a shippable product.
