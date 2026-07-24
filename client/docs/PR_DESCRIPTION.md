# Pull Request Description

## Summary

- Add **AI Learning Dashboard** frontend in `client/` for the competency exercise (frontend-heavy track).
- Implement learning item CRUD with dashboard stats, search/filter/sort, form validation, and `localStorage` persistence with seed data.
- Add Vitest tests plus README, AI workflow history, and reflection docs for submission.

## Project option

**Frontend-heavy:** AI Learning Dashboard / Project Tracker (FE only)

## Core features

- Dashboard summary (totals, status breakdown, average progress)
- Create / edit / delete learning items
- Search across title, description, tags, and notes
- Filter by status, category, priority; multiple sort options
- Client-side validation and user-facing error handling
- Seed data on first load; reset to sample data action
- Unit and component tests

## Test plan

- [ ] `cd client && npm install`
- [ ] `npm run dev` — app loads with seed items
- [ ] Create a new learning item with valid data
- [ ] Submit form with empty title — see validation errors
- [ ] Search for a tag (e.g. `rag`) — list filters correctly
- [ ] Filter by status **In progress** — only matching cards shown
- [ ] Edit an item and confirm changes persist after refresh
- [ ] Delete an item with confirmation dialog
- [ ] Click **Reset sample data** — seed set restored
- [ ] `npm run test` — all tests pass
- [ ] `npm run build` — production build succeeds

## AI usage

Documented in `client/docs/AI_WORKFLOW.md`.

## Out of scope (this PR)

- Backend API and database
- Authentication
- Stretch features (charts, export, streaks)

## Files of note

- `client/src/hooks/useProjects.js` — app state and CRUD
- `client/src/utils/validation.js` — form validation rules
- `client/src/utils/filters.js` — search/filter/sort logic
- `client/src/data/seedData.js` — initial sample data
- `client/docs/` — workflow, reflection, PR template
