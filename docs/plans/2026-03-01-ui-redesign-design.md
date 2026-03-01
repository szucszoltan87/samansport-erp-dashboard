# UI Redesign Design - PulseERP Style

**Date**: 2026-03-01
**Branch**: UI_redesign

## Goal
Redesign the SamanSport ERP app UI to match the PulseERP reference screenshot style, while keeping existing Dashboard and Analytics functionality intact.

## Design Decisions

### Sidebar (Dark Charcoal)
- Background: `#1c1c2e`
- Brand: "SamanSport" + "ERP Analytics" in white/muted text
- Navigation: Dashboard + Analitika with SVG icons, white text
- Active nav: Coral/red-orange (`#e74c3c`) background highlight
- Settings item: Above user profile, near bottom
- User profile: Fixed bottom - avatar initials circle, name, role, logout icon

### Top Header
- Hungarian greeting (time-appropriate): "Jo reggelt" / "Jo napot" / "Jo estet"
- Subtitle line below greeting
- Right-aligned: Current date in Hungarian format

### Date Range Bar (Below Header, Inline)
- Horizontal row: Start date + End date + Refresh button
- Compact, subtle styling - always visible above content

### Main Content Area
- Background: `#f8fafc`
- Cards: White, 12px border-radius, subtle shadow, 1px border `#e5e7eb`

### Color Palette
- Primary accent: `#e74c3c` (coral/red - sidebar active)
- Charts/data: `#2563eb` (blue - kept for data visualization)
- Sidebar: `#1c1c2e` bg, `#ffffff` / `#9ca3af` text
- Success badges: green, Warning: orange/yellow, Error: red

### Pages Kept
1. **Dashboard**: KPI cards, revenue trend, quantities chart, top 10 products
2. **Analitika**: Product selector, metric/period/chart controls, charts, data tables
