# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AFM (Atomic Force Microscopy) data platform with a Vue.js front-end built using the Vuetify framework. The project uses a modern Vue 3 + Vuetify 3 stack with automatic component imports and sophisticated data visualization capabilities for semiconductor wafer measurement analysis.

## Development Commands

**IMPORTANT**: The user runs these commands in their Windows development environment (not via WSL).

### Frontend Commands (run in `front-end/` directory)
```bash
npm run dev      # Start development server (http://localhost:3000)
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint with auto-fix
```

### Backend Commands (run in project root)
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

The backend uses a file-based caching system for AFM measurement data:

1. **Flask Application Structure**: 
   - `index.py` - Main Flask app with CORS configuration and static file serving
   - `api/routes.py` - REST API endpoints for AFM data retrieval
   - `api/utils/file_parser.py` - Utilities for parsing AFM file formats
   - `api/user_activity.py` - User activity tracking system

2. **Data Storage Pattern**: 
   - **Pickle Files**: Parsed AFM measurements stored in `itc-afm-data-platform-pjt-shared/AFM_DB/{TOOL}/data_dir_pickle/`
   - **Profile Data**: X,Y,Z coordinates stored in `profile_dir/` as pickle files
   - **Image Files**: TIFF images in `tiff_dir/` for visual analysis
   - **File Naming**: Pattern `#date#recipe_name#lot_id_time#slot_measured_info#.extension`

3. **Multi-Tool Support**: Each AFM tool (MAP608, MAPC01, 5EAP1501) has dedicated data directories

4. **No In-Memory Storage**: All data persisted to disk for reliability and scalability

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

### Core Data Endpoints
- `GET /api/health` - Health check
- `GET /api/afm-files?tool={toolname}` - Get all parsed AFM files for a tool (loads from pickle cache)
- `GET /api/afm-files/detail/<filename>?tool={toolname}` - Get detailed measurement data from pickle
- `GET /api/afm-files/profile/<filename>/<point_id>?tool={toolname}` - Get X,Y,Z coordinate data
- `GET /api/afm-files/image/<filename>/<point_id>?tool={toolname}` - Get image metadata
- `GET /api/afm-files/image-file/<filename>/<point_id>?tool={toolname}` - Serve TIFF image file

### User Activity Tracking
- `GET /api/user-activities` - Get all user activities
- `GET /api/my-activities` - Get current user's activities (uses LAST_USER cookie)
- `GET /api/current-user` - Get current user from cookie
- `GET /api/debug/cookies` - Debug endpoint for cookie inspection

## Performance Optimizations

1. **Code Splitting**: Vite configuration splits bundles by library (Vuetify, ECharts, fonts, vendor)
2. **Font Optimization**: Google Fonts (Roboto, Noto Sans KR) with preconnect hints and swap display
3. **Local Search Caching**: `useSearch.js` implements Map-based caching with size limits (50 entries)
4. **Component Auto-Imports**: Vite plugins eliminate manual imports for Vue APIs, components, and Pinia stores
5. **Lazy Loading**: Charts and heavy components loaded on-demand

## File Pattern Recognition

AFM files follow a specific naming convention that the backend parser recognizes:
```
#YYMMDD#RECIPE_NAME#LOT_ID_TIMESTAMP#SLOT_MEASURED_INFO#.extension
Example: #250609#FSOXCMP_DISHING_9PT#T7HQR42TA_250709#21_1#.pkl
```

This pattern is parsed into:
- `date`: 250609 (YYMMDD format)
- `recipe_name`: FSOXCMP_DISHING_9PT
- `lot_id`: T7HQR42TA_250709
- `slot_number`: 21
- `measured_info`: 1

## Development Notes

- **Auto-Imports**: Components, Vue APIs, and Pinia stores automatically imported - no manual imports needed
- **Charts Organization**: All visualization components should be placed in dedicated `charts/` folders
- **Data Units**: AFM measurement columns often contain "(nm)" suffix for nanometer units
- **Desktop Only**: Application designed for desktop browsers only (no mobile/tablet responsive design)
- **Production Entry**: Uses `index.py` as UWSGI-compatible entry point
- **CORS Configuration**: Hardcoded allowed origins in `index.py` for development and production URLs