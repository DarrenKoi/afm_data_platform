import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for logging or adding auth headers
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`)
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for handling common errors
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error.response?.data?.message || error.message)
    return Promise.reject(error)
  }
)

// API service functions
export const apiService = {
  // Health check
  async healthCheck() {
    return await api.get('/health')
  },

  // Get AFM measurement data
  async getAfmData() {
    return await api.get('/afm-data')
  },

  // Get trend analysis data
  async getTrendData() {
    return await api.get('/trend-data')
  },

  // Get analysis results
  async getAnalysisResults() {
    return await api.get('/analysis-results')
  },

  // Get profile data for specific group and point
  async getProfileData(groupKey, point) {
    return await api.get(`/profile-data/${groupKey}/${point}`)
  },

  // Get summary data for specific group
  async getSummaryData(groupKey) {
    return await api.get(`/summary-data/${groupKey}`)
  },

  // Search AFM measurements with real-time filtering
  async searchMeasurements(query = '', limit = 50, offset = 0) {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
      offset: offset.toString()
    })
    return await api.get(`/measurements/search?${params}`)
  },

  // Get all measurements with pagination
  async getAllMeasurements(limit = 50, offset = 0) {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString()
    })
    return await api.get(`/measurements?${params}`)
  },

  // Get specific measurement details
  async getMeasurementDetails(measurementId) {
    return await api.get(`/measurements/${measurementId}`)
  },

  // Get measurement statistics
  async getMeasurementStats() {
    return await api.get('/measurements/stats')
  },

  // Get search suggestions for autocomplete
  async getSearchSuggestions(query, limit = 10) {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString()
    })
    return await api.get(`/measurements/suggestions?${params}`)
  },

  // Get wafer heat map data
  async getWaferData(groupKey) {
    return await api.get(`/wafer-data/${groupKey}`)
  },

  // Get enhanced profile data for specific die position
  async getEnhancedProfileData(groupKey, dieX, dieY) {
    return await api.get(`/enhanced-profile-data/${groupKey}/${dieX}/${dieY}`)
  }
}

// Search API compatibility layer
export async function searchMeasurementsAsync(query) {
  try {
    // Use the new real-time search API with larger limit for better UX
    const response = await apiService.searchMeasurements(query, 100, 0)
    
    if (!response.success || !response.data) {
      throw new Error('Failed to search measurements')
    }

    // Transform real measurement data to match the expected search result format
    const groupedResults = response.data.map(measurement => ({
      fab: measurement.fab_id,
      lot_id: measurement.lot_id,
      wf_id: measurement.wafer_id,
      lot_wf: `${measurement.lot_id}_${measurement.wafer_id}`,
      group_key: measurement.measurement_id,
      rcp_id: measurement.recipe_name,
      event_time: measurement.measurement_timestamp,
      points: [
        {
          point: 'Center',
          x_axis: measurement.scan_size_um.split('x')[0],
          y_axis: measurement.scan_size_um.split('x')[1],
          parameter: 'Height',
          value: measurement.mean_height_nm.toFixed(2)
        },
        {
          point: 'Roughness',
          x_axis: measurement.scan_size_um.split('x')[0],
          y_axis: measurement.scan_size_um.split('x')[1],
          parameter: 'RMS',
          value: measurement.rms_roughness_nm.toFixed(2)
        }
      ],
      // Additional metadata for enhanced functionality
      material: measurement.material,
      tool_name: measurement.tool_name,
      file_location: measurement.file_location,
      measurement_quality: measurement.measurement_quality,
      status: measurement.status
    }))

    return {
      success: true,
      data: groupedResults,
      total: response.total,
      query: query,
      has_more: response.has_more
    }
  } catch (error) {
    console.error('Search error:', error)
    return {
      success: false,
      error: error.message,
      data: [],
      total: 0,
      query: query
    }
  }
}

// Compatibility functions for existing dummy data usage
export async function fetchProfileData(groupKey, point) {
  try {
    const response = await apiService.getProfileData(groupKey, point)
    console.log('fetchProfileData response:', response)
    
    // Handle the axios interceptor response (response.data is already extracted)
    if (response && response.success && response.data && response.data.profile_data) {
      console.log('Profile data points found:', response.data.profile_data.length)
      return response.data.profile_data
    }
    throw new Error('Failed to fetch profile data or invalid response structure')
  } catch (error) {
    console.error('Profile data fetch error:', error)
    return []
  }
}

export async function fetchSummaryData(groupKey) {
  try {
    const response = await apiService.getSummaryData(groupKey)
    console.log('fetchSummaryData response:', response)
    
    // Handle the axios interceptor response (response.data is already extracted)
    if (response && response.success && response.data && response.data.summary_points) {
      console.log('Summary data points found:', response.data.summary_points.length)
      return response.data.summary_points
    }
    throw new Error('Failed to fetch summary data or invalid response structure')
  } catch (error) {
    console.error('Summary data fetch error:', error)
    return []
  }
}

// Mock identifierData for compatibility - this will be replaced with real search
export const identifierData = []

export default api