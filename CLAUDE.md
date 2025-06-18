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

**IMPORTANT**: The user develops this web application on Windows while Claude Code operates through WSL (Windows Subsystem for Linux). These are separate environments with different capabilities:

### User's Windows Environment

- **Frontend Development**: User runs all npm commands and Vue.js development server
- **Backend Development**: User runs Python/Flask server and manages Python dependencies
- **File Editing**: User can edit files through VS Code or other Windows editors
- **Testing**: User tests the application through Windows browsers

### Claude's WSL Environment

- **File Operations**: Claude can read, edit, and analyze project files
- **Code Analysis**: Claude can examine code structure and provide recommendations
- **Limited Execution**: Claude cannot run npm commands, Python servers, or test applications
- **Git Operations**: Claude can perform git commands and file management

### Frontend

**IMPORTANT**: The user runs npm commands in their Windows development environment (not via WSL).
Do NOT execute npm commands using the Bash tool. The user handles all package management and development server operations.

**Target Platform**: This application is designed exclusively for desktop browsers and internal corporate use. No mobile responsiveness or mobile-specific features are required.

Commands the user runs in Windows:

- `npm install` - Install dependencies
- `npm run dev` - Start development server (http://localhost:3000)
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run linting with auto-fix

### Backend

The backend is a Flask application that provides API endpoints for the frontend.

**Backend Setup and Running** (user runs in Windows):

1. Install Python dependencies: `pip install -r requirements.txt`
2. Run the backend server: `python index.py`
3. Backend will be available at: http://localhost:5000
4. API endpoints available at: http://localhost:5000/api

**Note**: Claude cannot test Flask execution due to WSL environment limitations, but can analyze code structure and fix import/configuration issues.

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
- `GET /api/afm-files` - Get all parsed AFM file data from cached pickle file
- `GET /api/afm-files/detail/<group_key>` - Get detailed measurement data from pickle files
- `GET /api/afm-files/profile/<group_key>/<point_number>` - Get profile data (x,y,z) from profile_dir
- `GET /api/afm-files/image/<group_key>/<point_number>` - Get profile image metadata from tiff_dir
- `GET /api/afm-files/image-file/<group_key>/<point_number>` - Serve actual image file

**Real File Data Integration**:
The API uses a file-based caching system with scheduled parsing:

- **Data Source**: `itc-afm-data-platform-pjt-shared/AFM_DB/MAP608/data_dir_list.txt`
- **Cache File**: `itc-afm-data-platform-pjt-shared/AFM_DB/MAP608/data_dir_list_parsed.pkl`
- **File Pattern**: `#date#recipe_name#lot_id_time#slot_measured_info#.extension`
- **Parsed Fields**:
  - Date (YYMMDD format converted to YYYY-MM-DD)
  - Recipe name (e.g., FSOXCMP_DISHING_9PT, OXIDE_ETCH_3PT)
  - Lot ID (time portion removed, e.g., T7HQR42TA)
  - Slot number (e.g., 21, 15)
  - Measured info (e.g., 1, 2, repeat1, repeat2)
- **Data Directories**:
  - `data_dir_pickle/` - Contains pickle files with measurement data
  - `profile_dir/` - Contains profile data files (x,y,z coordinates)
  - `tiff_dir/` - Contains WebP images of profiles

**File-Based Caching System**:

- **Scheduler**: APScheduler runs hourly to parse and cache AFM data
- **Cache Structure**: 
  - `measurements`: Array of parsed AFM file metadata
  - `metadata`: Tool name, timestamp, statistics
- **Performance**: Pre-parsed data enables fast API responses
- **Fallback**: Automatic fallback to live parsing if cache doesn't exist
- **No In-Memory Storage**: All data persisted to disk for reliability

## AFM Tool Configuration

The platform supports multiple AFM tools across different fabrication facilities:

**Fab and Tool Mapping**:
```javascript
fab_toolname = {
  "WLPKG1": "MAP608",    // Currently active and implemented
  "R3": "MAPC01",        // Future tool support
  "M15": "5EAP1501",     // Future tool support
}
```

**Current Implementation**:
- **Active Tool**: MAP608 (WLPKG1 fab)
- **Data Location**: `itc-afm-data-platform-pjt-shared/AFM_DB/MAP608/`
- **Tool Selection**: Frontend tool selection interface allows switching between tools
- **Future Expansion**: Additional tools (MAPC01, 5EAP1501) can be added with corresponding data directories

**Tool Selection Interface**:
- Simplified UI showing only the selected tool name without secondary information
- Chip-based selection with visual indicators for active tool
- Extensible design for adding new tools from different fabs

## API Integration

The frontend uses Axios for API communication:

- **API Service**: `src/services/api.js` handles all backend communication
- **Base URL**: Configured via environment variables (`VITE_API_BASE_URL`)
- **Development**: Backend runs on port 5000, frontend on port 3000
- **CORS**: Properly configured for cross-origin requests
- **Data Loading**: Frontend fetches all AFM files at once and performs client-side filtering/search

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

### Documentation Consolidation Work

**What was accomplished**:

- **Eliminated duplication**: Combined similar content from reference folders and tutorial chapters
- **Improved organization**: Structured as progressive learning path rather than scattered topics
- **Enhanced explanations**: Added practical examples, analogies, and AFM-specific context
- **Streamlined access**: Single comprehensive file instead of navigating multiple folders
- **Maintained beginner focus**: Preserved tutorial's approachable tone for non-developers

The consolidated `claude.md` serves as the primary learning resource, making the documentation more accessible while preserving all technical details from the original reference materials.
