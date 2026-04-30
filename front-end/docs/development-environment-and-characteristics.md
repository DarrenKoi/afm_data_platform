# Development Environment and Company Characteristics

This document summarizes the development environment and engineering characteristics
described across the frontend tutorial materials. It also notes a few observations
from the current project configuration.

## Company and Project Context

- The project is an internal SK hynix AFM Data Platform / AFM Data Viewer.
- The primary use case is semiconductor equipment and measurement data analysis.
- The intended users are engineers who understand equipment, process, or data
  analysis work, but may have limited prior web development experience.
- The application is positioned as a practical AI/DT tool: collect and process
  engineering data, visualize it clearly, and share it through an internal web app.

## Core Development Stack

### Backend

- Python is the backend language. The tutorials describe Python 3.11 as the
  selected runtime because of performance and debugging improvements.
- Flask is the backend web framework.
- Flask-CORS is used when frontend and backend run on separate local ports.
- The backend exposes REST-style JSON APIs under `/api/*`.
- WSGI is the production interface, with uWSGI mentioned as the common internal
  company runtime pattern.

Current backend dependencies in `requirements.txt` include:

- `Flask`
- `Flask-CORS`
- `requests`
- `numpy`
- `pandas`
- `pyarrow`
- `APScheduler`

### Frontend

- Vue 3 is the frontend framework.
- Vite is the frontend development server and build tool.
- Vuetify is the UI component framework, based on Material Design.
- Vue Router handles page routing.
- Pinia handles shared frontend state.
- Axios handles HTTP API calls.
- ECharts handles data visualization.
- Material Design Icons and Sass/SCSS are used for styling and UI assets.

Current frontend package configuration includes:

- `vue`
- `vite`
- `vuetify`
- `vue-router`
- `pinia`
- `axios`
- `echarts`
- `@mdi/font`
- `@tanstack/vue-query`
- `eslint`
- `vite-plugin-vuetify`
- `vite-plugin-vue-devtools`

## Local Development Environment

The tutorials describe local development as a split frontend/backend setup:

- Vue/Vite frontend server: port `3000`
- Flask backend server: port `5000`
- Frontend sends API requests to the Flask backend.
- CORS is required locally because the frontend and backend run on different
  origins.

Typical commands:

```bash
# Backend
python index.py

# Frontend
cd front-end
npm install
npm run dev
npm run build
npm run preview
npm run lint
```

The current Vite config also uses port `3000`, the `@` alias for `src`, Vuetify
auto-import, Vue auto-import helpers, and manual production chunks for large
dependencies such as Vuetify, ECharts, fonts, and vendor code.

## Internal Network and Tooling

- Node.js LTS is the expected JavaScript runtime; the tutorials recommend
  Node.js 20.x LTS.
- npm is the package manager.
- Inside the company network, npm package installation is expected to go through
  an internal Nexus proxy and use a longer fetch timeout for network stability.
- VS Code is the assumed editor.
- HCP provides a cloud/browser-based VS Code environment, allowing shared setup
  and more consistent team collaboration without requiring every developer to
  reproduce the full local environment manually.

This summary intentionally avoids duplicating internal hostnames or deployment
domains. Use the detailed tutorial chapters or approved internal documentation
when exact company URLs are needed.

## Deployment Model

The tutorials describe two modes:

### Development

- Vue dev server and Flask dev server run separately.
- API requests cross from the frontend origin to the backend origin.
- CORS must allow local frontend origins.

### Production

- The Vue app is built into static files.
- Flask serves both API routes and the built frontend assets.
- `/api/*` is handled by Flask API routes.
- Other routes fall back to `index.html` so Vue Router can handle client-side
  navigation.
- This single-server deployment reduces CORS complexity because frontend and API
  share the same origin.
- HCP Web App is the target internal deployment platform.

Note: The tutorials describe serving `front-end/dist` after `npm run build`.
The current backend code serves from `front-end` when that folder exists, so the
implementation and tutorial should be reviewed together before production
deployment.

## Frontend Architecture Characteristics

- The application is organized around pages, reusable components, stores,
  services, router configuration, styles, and assets.
- Vue Single File Components are the expected component format.
- The recommended Vue style is Composition API with `<script setup>`.
- Components should stay reusable where practical.
- Shared or cross-page state belongs in Pinia stores.
- Local UI state should stay inside components rather than being pushed into
  global stores unnecessarily.
- API logic should be modularized under service modules instead of being embedded
  directly in every component.

## Data and Visualization Characteristics

- The domain is data-heavy and measurement-heavy.
- The frontend is expected to support searching, filtering, charting, trend
  analysis, detailed measurement views, and comparison workflows.
- ECharts was selected because it supports many chart types, large datasets,
  interactive exploration, and commercial use through a permissive license.
- The tutorials emphasize importing only needed ECharts modules when bundle size
  matters.

## Security and Configuration Practices

- Environment-specific configuration should be handled with `.env` files.
- Frontend-exposed Vite variables must use the `VITE_` prefix.
- Secrets should not be committed.
- Production CORS should allow only approved origins.
- Avoid broad `origins="*"` CORS settings in production.
- Raw HTML rendering should be treated carefully because of XSS risk.
- API keys, passwords, secret keys, and internal host details should stay out of
  public or broadly shared documentation.

## Performance Practices

The tutorials call out performance as important because internal dashboard apps
can grow large and may process heavy measurement data.

Recommended practices include:

- Lazy-load route components.
- Lazy-load heavy dashboard panels and analysis tools.
- Split large bundles by vendor group.
- Import only the needed modules from large libraries.
- Optimize images and lazy-load them.
- Dispose ECharts instances on component unmount.
- Remove event listeners, intervals, timers, observers, and WebSocket references
  during component cleanup.
- Debounce search and high-frequency API calls.
- Use browser performance tooling and Vue DevTools during diagnosis.

## Engineering Culture and Learning Characteristics

- The documentation is pragmatic and tutorial-driven.
- It favors building usable tools early, then improving the architecture as the
  project grows.
- The team context assumes engineers may be stronger in semiconductor process,
  equipment, or data analysis than in frontend engineering.
- Frontend development is framed as a way to turn engineering ideas into shared
  tools quickly.
- The desired engineering profile combines semiconductor domain knowledge, data
  analysis, and software implementation ability.
- LLMs are encouraged for prototyping and tutoring, but the tutorials emphasize
  that humans still own architecture, requirements, validation, and debugging.
- TypeScript is recommended as a later growth path for larger collaborative
  applications.
- Nuxt or SSR may be useful for future public or SEO-sensitive applications, but
  the tutorials consider CSR sufficient for many internal dashboards.

## Source Coverage

This summary was extracted from the tutorial chapters under
`front-end/docs/tutorials`, especially:

- Chapter 1: project context, stack, HCP, target audience
- Chapter 2: Node.js, npm, internal network setup, Vite, VS Code
- Chapter 6: Vuetify and UI workflow
- Chapter 7: Vue Router and navigation strategy
- Chapter 8: ECharts and visualization choices
- Chapter 9: Pinia and state management
- Chapter 10: Axios, API services, environment variables
- Chapter 11: performance optimization
- Chapter 12: Flask/Vue API integration
- Chapter 13: HCP deployment model
- Chapter 14: engineering culture, AI/DT context, LLM usage, growth path
