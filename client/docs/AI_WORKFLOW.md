# AI Workflow History

This document captures how AI (Cursor) was used for the frontend competency exercise.

## 1. Context setting

**Prompt:** Create React inside the `client` folder, then build a frontend-only AI Learning Dashboard for the one-week competency exercise.

**Context provided to AI:**

- Existing monorepo layout (`client/`, `server/`)
- Exercise requirements: search/filter, validation, error handling, tests, README, seed data, AI workflow visibility
- Constraint: FE only in `client/` (no backend for this pass)

## 2. Planning

AI chose the **Frontend-heavy** option: **AI Learning Dashboard / Project Tracker**.

Planned architecture:

- Vite + React (already scaffolded)
- `localStorage` persistence with seed data
- Custom hook (`useProjects`) for state and CRUD
- Utility modules for validation and filtering (testable without DOM)
- Component-based UI: dashboard stats, filters, cards, modal form
- Vitest for unit/component tests
- Docs for README, reflection, and PR description

## 3. Code generation

AI generated:

- Data layer: `seedData.js`, `storage.js`, `validation.js`, `filters.js`
- UI: `Layout`, `DashboardStats`, `SearchFilters`, `ProjectList`, `ProjectCard`, `ProjectForm`, `ConfirmDialog`, `Toast`, `ErrorBoundary`
- App wiring via `useProjects` hook
- CSS for a cohesive dark dashboard theme

## 4. Refinement

Planned refinements during generation:

- Centralized constants for categories/statuses/priorities
- Explicit `StorageError` for persistence failures
- Form validation returns field-level errors for accessible UI
- Empty state when filters return no results
- Confirm dialog before delete

## 5. Testing

AI added:

- `validation.test.js` — required fields, URL/progress rules, tag limits
- `filters.test.js` — search, filter combinations, sorting, stats
- `ProjectForm.test.jsx` — validation display and edit mode
- `SearchFilters.test.jsx` — search input and clear filters

Commands used:

```bash
npm run test
npm run build
```

## 6. Debugging approach

If issues arise, the intended loop is:

1. Reproduce with `npm run test` or `npm run dev`
2. Isolate logic bugs in `utils/` tests first
3. Fix UI issues with component tests and manual verification
4. Re-run build to confirm production bundle

## 7. Review checklist

- [x] Core CRUD works
- [x] Search and filters work together
- [x] Validation blocks bad input
- [x] Errors surfaced to user (storage, boundary, form)
- [x] Seed data on first load
- [x] Tests pass
- [x] README and submission docs included

## 8. Example prompts used

1. `create react inside the client folder`
2. `create FE only in client folder` + full exercise brief
3. (Implicit follow-up) structure for dashboard, tests, and documentation

## 9. What I would do next with AI

- Add backend API in `server/` and swap storage layer for fetch calls
- Add integration tests with MSW
- Add accessibility audit and keyboard trap tests for modals
- Add stretch features: charts, export CSV, learning streaks
