# AFM Data Platform Backend

This is the Flask backend for the AFM Data Platform.

## Setup and Installation

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Development Server**
   ```bash
   python run.py
   ```
   
   Or alternatively:
   ```bash
   python index.py
   ```

## Troubleshooting

### Port Access Issues
If you encounter socket access permission errors or "port already in use" errors:

1. **Try different ports**:
   ```bash
   PORT=5001 python index.py
   PORT=8000 python index.py
   ```

2. **Check if port 5000 is in use**:
   ```bash
   # Windows
   netstat -an | findstr :5000
   
   # Linux/Mac
   lsof -i :5000
   ```

3. **Update frontend API URL**: If using a different port, update `front-end/.env.development`:
   ```
   VITE_API_BASE_URL=http://127.0.0.1:5001/api
   ```

## Production Deployment

**Important**: This backend is designed to work with UWSGI servers in production mode.

- **Production Entry Point**: `index.py` (used by UWSGI server)
- **Development Entry Point**: `run.py` or `index.py` (for local testing)
- **UWSGI Configuration**: The production server will automatically use `index.py` as the main application entry point

## API Endpoints

The backend provides the following API endpoints:

### Health Check
- `GET /` - Backend health check
- `GET /api/health` - API health check

### AFM Data
- `GET /api/afm-data` - Get dummy AFM measurement data
- `GET /api/trend-data` - Get trend analysis data
- `GET /api/analysis-results` - Get analysis results
- `GET /api/profile-data/<group_key>/<point>` - Get profile data for specific measurement
- `GET /api/summary-data/<group_key>` - Get summary data for specific group

### Measurement Data (New)
- `GET /api/measurements/search?q=<query>&limit=<limit>&offset=<offset>` - Search measurements with real-time filtering
- `GET /api/measurements?limit=<limit>&offset=<offset>` - Get all measurements with pagination
- `GET /api/measurements/<measurement_id>` - Get specific measurement details
- `GET /api/measurements/stats` - Get measurement statistics and summaries

## Architecture

- **Framework**: Flask with Blueprints
- **CORS**: Configured for frontend communication (localhost:3000)
- **Scheduler**: APScheduler for background tasks
- **Data Service**: Generates realistic dummy AFM data
- **Measurement Data**: Realistic AFM measurement metadata with file locations
- **Parquet Support**: Reads from parquet files in shared-data folder (with fallback to generated data)
- **Real-time Search**: Fast text-based filtering across multiple metadata fields

## Configuration

- **Port**: 5000
- **Debug Mode**: Enabled in development
- **CORS Origins**: `http://localhost:3000` (frontend)

## Background Tasks

The backend includes APScheduler for running background tasks:
- Data cleanup (daily)
- Health checks (every 30 minutes)

## Data Structure

### Measurement Metadata Fields
- **Identifiers**: measurement_id, lot_id, wafer_id, fab_id
- **Equipment**: tool_name, recipe_name
- **Process**: material, process_step, operator
- **File Location**: file_location (path in shared-data folder)
- **Scan Parameters**: scan_size_um, resolution, scan_rate_hz, setpoint_nN
- **Results**: rms_roughness_nm, mean_height_nm, max_height_nm, min_height_nm
- **Quality**: measurement_quality, data_completeness_percent, status
- **Environment**: temperature_c, humidity_percent, shift

### Parquet File Support
- Place `afm_measurements.parquet` in `../shared-data/` directory
- Backend automatically detects and loads parquet data
- Falls back to generated dummy data if parquet file not available
- Use `generate_dummy_data.py` script to create sample parquet file

## Development Notes

- All dummy data is generated deterministically using seeds
- Profile data includes 3D surface measurements
- Summary data includes measurement point statistics
- APIs return consistent JSON format with success/error handling
- Real-time search works across lot_id, fab_id, tool_name, recipe_name, material, process_step
- Pagination supported with limit/offset parameters