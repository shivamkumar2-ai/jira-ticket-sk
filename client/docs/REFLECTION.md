# Reflection

## What went well

- Scoping to **frontend-only** kept the exercise focused and shippable in a short window.
- Splitting **validation** and **filtering** into pure utilities made tests fast and reliable.
- A single `useProjects` hook kept UI components simple and readable.
- Seed data gives reviewers immediate context without manual setup.

## What was challenging

- Balancing exercise completeness (tests, docs, error handling) with minimal dependencies.
- Designing filters that feel useful without overbuilding (many sort/filter combinations).
- Local-only persistence limits multi-device use — acceptable for FE scope but worth calling out.

## How AI helped

- Accelerated boilerplate: component structure, test files, and documentation skeleton.
- Suggested a sensible default data model for an AI learning tracker.
- Helped maintain consistent naming and file layout across the app.

## What I reviewed manually

- Validation rules match product intent (required fields, sensible limits).
- UX flow: create → edit → filter → delete with confirmation.
- README instructions are accurate for install/run/test.
- Tests assert real behavior, not implementation details.

## Growth areas

- Add API integration and optimistic UI patterns when backend is introduced.
- Expand component test coverage for delete flow and error boundary.
- Improve accessibility: focus management in modals, live region patterns.

## If I had another day (Stretch)

- Progress charts by category
- Export/import JSON backup
- Dark/light theme toggle
- Learning streaks and due dates with reminders

## Competency alignment

This project demonstrates AI-assisted delivery with visible workflow documentation, working core features, automated tests, and clear setup instructions — aligned with the frontend-heavy competency exercise expectations.
