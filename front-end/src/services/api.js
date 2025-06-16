import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for logging
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

  // Get all AFM files (parsed from data_dir_list.txt)
  async getAfmFiles() {
    console.log('🔍 Fetching AFM files from backend...')
    const response = await api.get('/afm-files')
    console.log('📊 AFM files response:', response)
    return response
  },

  // Search AFM files
  async searchAfmFiles(query = '') {
    console.log(`🔍 Searching AFM files with query: "${query}"`)
    const params = new URLSearchParams({ q: query })
    const response = await api.get(`/afm-files/search?${params}`)
    console.log('📊 Search response:', response)
    return response
  },

  // Get detailed AFM measurement data
  async getAfmFileDetail(groupKey) {
    console.log(`🔍 Fetching AFM detail for group key: "${groupKey}"`)
    const response = await api.get(`/afm-files/detail/${groupKey}`)
    console.log('📊 Detail response:', response)
    return response
  }
}

// Main search function for compatibility with existing frontend
export async function searchMeasurementsAsync(query) {
  try {
    console.log(`🔍 SearchMeasurementsAsync called with query: "${query}"`)
    
    // Use the new AFM files search API
    const response = await apiService.searchAfmFiles(query)
    
    if (!response.success || !response.data) {
      throw new Error('Failed to search AFM files')
    }

    console.log(`✅ Found ${response.total} AFM measurements`)
    console.log('📊 Sample data:', response.data.slice(0, 3))

    // Transform real file data to match the expected search result format
    const groupedResults = response.data.map(measurement => ({
      fab: 'SK_Hynix_ITC',
      lot_id: measurement.lot_id,
      wf_id: 'W01', // Default wafer ID 
      lot_wf: `${measurement.lot_id}_W01`,
      group_key: `${measurement.lot_id}_${measurement.slot_number}_${measurement.measured_info}`,
      rcp_id: measurement.recipe_name,
      event_time: measurement.formatted_date,
      points: [
        {
          point: `Slot_${measurement.slot_number}`,
          x_axis: '5.0',
          y_axis: '5.0',
          parameter: measurement.measured_info,
          value: (Math.random() * 100).toFixed(2) // Random value for demo
        }
      ],
      // Real metadata from parsed filenames
      filename: measurement.filename,
      date: measurement.date,
      formatted_date: measurement.formatted_date,
      recipe_name: measurement.recipe_name,
      slot_number: measurement.slot_number,
      measured_info: measurement.measured_info
    }))

    console.log('✅ Transformed data for frontend:', groupedResults.slice(0, 2))

    return {
      success: true,
      data: groupedResults,
      total: response.total,
      query: query,
      has_more: false,
      data_source: 'real_files'
    }
  } catch (error) {
    console.error('❌ Search error:', error)
    return {
      success: false,
      error: error.message,
      data: [],
      total: 0,
      query: query
    }
  }
}


// Updated functions to use real pickle data
export async function fetchProfileData(groupKey, point) {
  console.log(`📊 fetchProfileData called for groupKey: ${groupKey}, point: ${point}`)
  
  try {
    const response = await apiService.getAfmFileDetail(groupKey)
    
    if (response.success && response.data) {
      const profileData = response.data.profile_data || []
      console.log(`✅ Loaded ${profileData.length} profile data points for ${groupKey}`)
      return profileData
    } else {
      console.warn('⚠️ Failed to load profile data:', response.error)
      return []
    }
  } catch (error) {
    console.error('❌ Error fetching profile data:', error)
    return []
  }
}

export async function fetchMeasurementData(groupKey) {
  console.log(`📊 fetchMeasurementData called for groupKey: ${groupKey}`)
  
  try {
    const response = await apiService.getAfmFileDetail(groupKey)
    
    if (response.success && response.data) {
      console.log(`✅ Loaded measurement data for ${groupKey}`)
      return {
        success: true,
        data: response.data
      }
    } else {
      console.warn('⚠️ Failed to load measurement data:', response.error)
      return {
        success: false,
        error: response.error,
        data: null
      }
    }
  } catch (error) {
    console.error('❌ Error fetching measurement data:', error)
    return {
      success: false,
      error: error.message,
      data: null
    }
  }
}

export async function fetchSummaryData(groupKey) {
  console.log(`📊 fetchSummaryData called for groupKey: ${groupKey}`)
  
  try {
    const measurementResponse = await fetchMeasurementData(groupKey)
    
    if (measurementResponse.success && measurementResponse.data.statistics_table) {
      return {
        success: true,
        data: measurementResponse.data.statistics_table
      }
    } else {
      return {
        success: false,
        data: []
      }
    }
  } catch (error) {
    console.error('❌ Error fetching summary data:', error)
    return {
      success: false,
      data: []
    }
  }
}

// Mock identifierData for compatibility
export const identifierData = []

export default api