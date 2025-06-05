# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

This is an AFM (Atomic Force Microscopy) data platform with a Vue.js front-end built using the Vuetify framework. The project uses a modern Vue 3 + Vuetify 3 stack with file-based routing and automatic component imports.

### Front-end Architecture

- **Framework**: Vue 3 with Composition API
- **UI Library**: Vuetify 3 (Material Design components)
- **State Management**: Pinia stores
- **Routing**: File-based routing with unplugin-vue-router (pages in `src/pages/` become routes)
- **Layouts**: Uses vite-plugin-vue-layouts-next for layout management
- **Auto-imports**: Components and Vue APIs are auto-imported via unplugin-vue-components and unplugin-auto-import

The front-end follows Vuetify's standard project structure:
- `src/pages/` - File-based routes (index.vue becomes `/`)
- `src/layouts/` - Layout templates (default.vue wraps pages)
- `src/components/` - Reusable Vue components
- `src/stores/` - Pinia state management stores
- `src/plugins/` - Plugin registration (Vuetify, Pinia, Router)
- `src/styles/` - SCSS styling configuration

## Common Development Commands

All commands should be run from the `front-end/` directory:

```bash
# Install dependencies
npm install

# Start development server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linting with auto-fix
npm run lint
```

## Development Notes

- The development server runs on port 3000
- Components are automatically imported - no need for manual imports
- Vue Router is auto-configured based on files in `src/pages/`
- Vuetify components and theming are configured via `src/plugins/vuetify.js`
- SCSS settings are in `src/styles/settings.scss`
- The project uses modern Sass API compilation