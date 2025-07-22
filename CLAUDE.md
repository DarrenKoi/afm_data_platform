# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AFM (Atomic Force Microscopy) data platform with a Vue.js front-end built using the Vuetify framework. The project uses a modern Vue 3 + Vuetify 3 stack with automatic component imports and sophisticated data visualization capabilities.

## Development Commands

**IMPORTANT**: The user runs these commands in their Windows development environment (not via WSL).

### Frontend Commands
```bash
npm run dev      # Start development server (http://localhost:3000)
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint with auto-fix
```

### Backend Commands
```bash
pip install -r requirements.txt  # Install Python dependencies
python index.py                  # Run Flask server (http://localhost:5000)
```

## High-Level Architecture

### Frontend Architecture

The frontend implements several sophisticated patterns that require understanding multiple files:

1. **Auto-Import System**: Components, Vue APIs, and Pinia stores are automatically imported without explicit import statements. This is configured through Vite plugins in `vite.config.mjs`.

2. **Local-First Search Strategy**: The application loads all AFM file data once per tool selection, then performs all filtering and searching locally. This is implemented in:
   - `src/services/api.js` - Fetches all data at once
   - `src/composables/useSearch.js` - Implements debounced local search with caching
   - `src/stores/dataStore.js` - Manages cached data and search results

3. **Persistent State Management**: User preferences and history are persisted to localStorage through Pinia store watchers. This includes:
   - View history (recently viewed measurements)
   - Grouped data (measurements selected for comparison)
   - Group history (saved measurement groups)
   - Selected tool preference

4. **Component Organization Pattern**: All chart components are separated into dedicated `charts/` folders within their parent component directories:
   ```
   components/
   ├── ResultPage/
   │   └── charts/         # Result page specific charts
   ├── DataTrend/
   │   └── charts/         # Data trend specific charts
   ```

5. **Plugin Loading Order**: Plugins are loaded in a specific order in `src/plugins/index.js`:
   ```javascript
   Vuetify → Router → Pinia
   ```
   This order ensures proper dependency resolution.

### Backend Architecture

The backend uses a file-based caching system with scheduled parsing:

1. **Scheduled Data Processing**: APScheduler runs hourly to parse AFM files and cache results to pickle files
2. **File Pattern Parsing**: Files follow pattern `#date#recipe_name#lot_id_time#slot_measured_info#.extension`
3. **No In-Memory Storage**: All data persisted to disk for reliability and scalability
4. **Tool-Specific Data Directories**: Each AFM tool has its own data directory structure

### API Integration Pattern

The API service implements several key patterns:

1. **Axios Interceptors**: Request/response logging and error handling
2. **Environment-Based Configuration**: API base URL from `VITE_API_BASE_URL`
3. **Data Transformation**: Special methods like `getWaferData()` transform backend data for visualization
4. **Local Caching**: Search results are cached with size limits to improve performance

## Key Architectural Decisions

1. **Why Local Search?**: With thousands of AFM files, loading all data once and filtering locally provides instant search results without API latency.

2. **Why Auto-Imports?**: Reduces boilerplate and improves developer experience, especially for frequently used components and composables.

3. **Why File-Based Backend?**: Allows for reliable data persistence, easy debugging, and compatibility with corporate cloud deployment.

4. **Why Separate Chart Components?**: Enables reuse across different pages and maintains clear separation of visualization logic.

## Development Environment Constraints

**IMPORTANT**: Claude Code operates through WSL while the user develops on Windows:

- **Claude CAN**: Read/edit files, analyze code, perform git operations
- **Claude CANNOT**: Run npm commands, execute Python servers, test applications
- **User Handles**: All package management, server execution, and testing

## AFM Tool Configuration

The platform supports multiple AFM tools:

```javascript
fab_toolname = {
  "WLPKG1": "MAP608",    // Currently active
  "R3": "MAPC01",        // Future support
  "M15": "5EAP1501",     // Future support
}
```

Each tool has its own data directory: `itc-afm-data-platform-pjt-shared/AFM_DB/{TOOL_NAME}/`

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/afm-files?tool={toolname}` - Get all files for a tool (cached)
- `GET /api/afm-files/detail/<group_key>` - Get measurement details
- `GET /api/afm-files/profile/<group_key>/<point_number>` - Get x,y,z data
- `GET /api/afm-files/image/<group_key>/<point_number>` - Get image metadata
- `GET /api/afm-files/image-file/<group_key>/<point_number>` - Serve image file

## Performance Optimizations

1. **Code Splitting**: Separate chunks for Vuetify, ECharts, and fonts
2. **Font Optimization**: Google Fonts with preconnect hints
3. **Search Caching**: Results cached with size limits in `useSearch` composable
4. **Lazy Component Loading**: Charts loaded on-demand

## Development Notes

- Components are automatically imported - no manual imports needed
- All charts should be placed in dedicated `charts/` folders
- Data columns often contain "(nm)" suffix in their names
- The application is designed for desktop browsers only (no mobile support needed)
- Production deployment uses `index.py` as entry point for UWSGI compatibility