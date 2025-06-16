# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

This is an AFM (Atomic Force Microscopy) data platform with a Vue.js front-end built using the Vuetify framework. The project uses a modern Vue 3 + Vuetify 3 stack with file-based routing and automatic component imports.

### Front-end Architecture

- **Framework**: Vue 3 with Composition API
- **UI Library**: Vuetify 3 (Material Design components)
- **State Management**: Pinia stores
- **Routing**: Manual route configuration (conventional Vue Router setup)
- **Layouts**: Uses vite-plugin-vue-layouts-next for layout management
- **Auto-imports**: Components and Vue APIs are auto-imported via unplugin-vue-components and unplugin-auto-import

The front-end follows this organized project structure:
- `src/pages/` - Page components (manually registered in router)
- `src/layouts/` - Layout components (AppHeader.vue, AppFooter.vue)
- `src/components/` - Reusable UI components (buttons, cards, charts, etc.)
- `src/stores/` - Pinia state management stores
- `src/plugins/` - Plugin registration (Vuetify, Pinia, Router)
- `src/styles/` - SCSS styling configuration

## Development Environment

### Frontend
**IMPORTANT**: The user runs npm commands in their own development environment (not via WSL). 
Do NOT execute npm commands using the Bash tool. The user handles all package management and development server operations.

**Target Platform**: This application is designed exclusively for desktop browsers and internal corporate use. No mobile responsiveness or mobile-specific features are required.

Common commands (user runs these):
- `npm install` - Install dependencies
- `npm run dev` - Start development server (http://localhost:3000)
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run linting with auto-fix

### Backend
The backend is a Flask application that provides API endpoints for the frontend.

**Backend Setup and Running**:
1. Navigate to the `back-end` directory
2. Install Python dependencies: `pip install -r requirements.txt`
3. Run the backend server: 
   - **Development**: `python run.py` or `python index.py`
   - **Production**: UWSGI server automatically uses `index.py`
4. Backend will be available at: http://localhost:5000
5. API endpoints available at: http://localhost:5000/api

**Production Deployment**:
- **Entry Point**: `index.py` (required for UWSGI server)
- **Cloud Setup**: Configured to work with cloud UWSGI deployment
- **No Configuration Changes Needed**: Production server automatically detects `index.py`

**Backend Architecture**:
- **Framework**: Flask with Blueprint structure
- **API Folder**: All API routes are organized in the `api/` folder
- **Scheduler**: APScheduler for background tasks (data cleanup, health checks)
- **CORS**: Configured for frontend communication
- **Data Service**: Generates realistic dummy AFM data for development

**API Endpoints**:
- `GET /api/health` - API health check
- `GET /api/afm-files` - Get all parsed AFM file data from data_dir_list.txt
- `GET /api/afm-files/search?q=<query>` - Search AFM files by query

**Real File Data Integration**:
The API parses real AFM file data from the `itc-afm-data-platform-pjt-shared/AFM_DB/MAP608/data_dir_list.txt` file:
- **File Pattern**: `#date#recipe_name#lot_id_time#slot_measured_info#.extension`
- **Parsed Fields**: 
  - Date (YYMMDD format converted to YYYY-MM-DD)
  - Recipe name (e.g., FSOXCMP_DISHING_9PT, OXIDE_ETCH_3PT)
  - Lot ID (time portion removed, e.g., T7HQR42TA)
  - Slot number (e.g., 21, 15)
  - Measured info (e.g., 1, 2, repeat1, repeat2)
- **Search Capabilities**: Search across lot_id, recipe_name, measured_info, date, and slot_number
- **Data Source**: Real files from the shared data directory, no dummy data

## API Integration

The frontend now uses Axios for API communication with real-time search capabilities:
- **API Service**: `src/services/api.js` handles all backend communication
- **Real-time Search**: `src/composables/useSearch.js` provides debounced search and caching
- **Base URL**: Configured via environment variables (`VITE_API_BASE_URL`)
- **Development**: Backend runs on port 5000, frontend on port 3000
- **CORS**: Properly configured for cross-origin requests

### Real-time Search Features
- **Debounced Search**: 300ms delay to prevent excessive API calls
- **Search Suggestions**: Auto-complete with cached suggestions
- **Client-side Caching**: Search results and suggestions cached for performance
- **Large Dataset Support**: Optimized for 10K-20K measurement records
- **Multi-field Search**: Searches across lot_id, fab_id, tool_name, recipe_name, material, process_step

## Development Notes

- The frontend development server runs on port 3000
- The backend development server runs on port 5000
- Components are automatically imported - no need for manual imports
- Vue Router is auto-configured based on files in `src/pages/`
- Vuetify components and theming are configured via `src/plugins/vuetify.js`
- SCSS settings are in `src/styles/settings.scss`
- The project uses modern Sass API compilation
- AFM logo (afm_logo2.png) and favicon are located in `src/assets/`

## Documentation Structure

The `front-end/docs/` folder contains comprehensive beginner-friendly guides for web development using this AFM data platform as a learning project:

### Documentation Organization

**Main Tutorial File**: `front-end/docs/claude.md`
- **Purpose**: Consolidated beginner's guide combining content from multiple sources
- **Target Audience**: Non-developer engineers at SK hynix who want to learn web development
- **Structure**: Progressive 3-chapter tutorial covering web basics through Vue.js fundamentals

**Tutorial Chapters**:
1. **Chapter 1: 시작하기 전에** - Web development basics, project overview, technology stack introduction
2. **Chapter 2: 개발 환경 구축하기** - Node.js installation, project setup, VS Code configuration
3. **Chapter 3: Vue 프로젝트 시작하기** - Vue.js fundamentals, component creation, project structure

**Reference Folders** (integrated into main tutorial):
- `01-web-basics/` - HTML/CSS/JavaScript fundamentals (content merged into Chapter 1)
- `02-project-structure/` - Detailed folder structure explanations (content merged into Chapters 1-3)  
- `03-configuration/` - Configuration files guide (content merged into Chapter 3)
- `tutorials/` - Original Korean tutorial chapters (source material for claude.md)

### Documentation Consolidation Work

**What was accomplished**:
- **Eliminated duplication**: Combined similar content from reference folders and tutorial chapters
- **Improved organization**: Structured as progressive learning path rather than scattered topics
- **Enhanced explanations**: Added practical examples, analogies, and AFM-specific context
- **Streamlined access**: Single comprehensive file instead of navigating multiple folders
- **Maintained beginner focus**: Preserved tutorial's approachable tone for non-developers

The consolidated `claude.md` serves as the primary learning resource, making the documentation more accessible while preserving all technical details from the original reference materials.