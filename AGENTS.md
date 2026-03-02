# Repository Guidelines

## Project Structure & Module Organization
- Backend (Flask) lives in `api/` and `index.py`.
- API route modules: `api/routes.py`, `api/afm_routes.py`, `api/activity_routes.py`, `api/image_routes.py`.
- Backend utilities are in `api/utils/` (parsing, Mongo helpers, logging).
- Frontend (Vue 3 + Vite + Vuetify) lives in `front-end/`.
- UI pages are in `front-end/src/pages/`, reusable components in `front-end/src/components/`, state in `front-end/src/stores/`, shared services in `front-end/src/services/`.
- Root Python scripts such as `generate_afm_data.py` and `regenerate_cache.py` are maintenance/data utilities.

## Build, Test, and Development Commands
- Backend setup: `pip install -r requirements.txt`
- Run backend locally: `python index.py` (default `http://127.0.0.1:5000`)
- Frontend setup: `cd front-end && npm install`
- Run frontend dev server: `npm run dev` (Vite)
- Frontend production build: `npm run build`
- Preview frontend build: `npm run preview`
- Lint frontend: `npm run lint` (ESLint with auto-fix)

## Coding Style & Naming Conventions
- Python: 4-space indentation, `snake_case` for files/functions, keep route and utility concerns separated.
- Vue/JS: 2-space indentation (see `front-end/.editorconfig`), component files in `PascalCase` (for example `MainPage.vue`).
- Composables follow `useXxx.js` (for example `useSearch.js`); service modules use descriptive `camelCase` exports.
- Run `npm run lint` before opening a PR for frontend changes.

## Testing Guidelines
- No automated test suite is currently configured in this repository.
- For now, validate changes with manual smoke checks:
  - Backend: `GET /api/health` returns success.
  - Frontend: search, chart rendering, and result/detail navigation.
- When adding tests, prefer:
  - Frontend: Vitest + Vue Test Utils under `front-end/src/**/__tests__/`.
  - Backend: `pytest` under `tests/` with route-level API coverage.

## Commit & Pull Request Guidelines
- Existing history uses short, imperative commit subjects (for example, `search bar updated`, `logger fix`).
- Keep commits focused by concern (`backend`, `front-end`, or `data script`), and avoid mixing unrelated refactors.
- PRs should include:
  - What changed and why.
  - Affected modules/endpoints.
  - Manual validation steps run.
  - Screenshots/GIFs for UI changes.
  - Linked issue/ticket when available.

## Security & Configuration Tips
- Start from `.env.example`; do not commit secrets or internal host details.
- Review CORS changes carefully in `index.py` and document new allowed origins in PR notes.
