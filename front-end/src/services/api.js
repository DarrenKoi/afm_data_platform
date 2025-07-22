import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
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

  // Get all AFM files (parsed from data_dir_list.txt) for a specific tool
  async getAfmFiles(toolName = 'MAP608') {
    console.log(`🔍 Fetching AFM files from backend for tool: ${toolName}`)
    const params = new URLSearchParams({ tool: toolName })
    const response = await api.get(`/afm-files?${params}`)
    console.log('📊 AFM files response:', response)
    return response
  },


  // Get detailed AFM measurement data for a specific tool
  async getAfmFileDetail(filename, toolName = 'MAP608') {
    console.log(`🔍 Fetching AFM detail for filename: "${filename}" from tool: ${toolName}`)
    const params = new URLSearchParams({ tool: toolName })
    const response = await api.get(`/afm-files/detail/${encodeURIComponent(filename)}?${params}`)
    console.log('📊 Detail response:', response)
    return response
  },

  // Get wafer data for heatmap visualization
  async getWaferData(filename, toolName = 'MAP608') {
    console.log(`🔍 Fetching wafer data for filename: "${filename}" from tool: ${toolName}`)
    try {
      // Use the same detailed data endpoint since wafer data is part of measurement data
      const params = new URLSearchParams({ tool: toolName })
      const response = await api.get(`/afm-files/detail/${encodeURIComponent(filename)}?${params}`)
      
      if (response.success && response.data) {
        // Extract wafer data from the detailed response
        // Generate wafer position data based on available measurement points
        const waferData = []
        const points = response.data.available_points || []
        
        // Create wafer data from measurement points
        points.forEach((point, index) => {
          // Parse point name (e.g., "1_UL" -> point 1, position UL)
          const [pointNum, position] = point.split('_')
          
          // Generate wafer coordinates based on point position
          let x, y
          switch(position) {
            case 'UL': x = -3; y = 3; break  // Upper Left
            case 'UR': x = 3; y = 3; break   // Upper Right
            case 'LL': x = -3; y = -3; break // Lower Left
            case 'LR': x = 3; y = -3; break  // Lower Right
            case 'C': x = 0; y = 0; break    // Center
            default: 
              // For numbered points, arrange in a grid
              const gridSize = Math.ceil(Math.sqrt(points.length))
              x = (index % gridSize) * 2 - gridSize
              y = Math.floor(index / gridSize) * 2 - gridSize
          }
          
          // Get measurement value from summary data if available
          let value = 75 + Math.random() * 50 // Default random value
          if (response.data.summary && Array.isArray(response.data.summary)) {
            const meanData = response.data.summary.find(item => item.ITEM === 'MEAN')
            if (meanData && meanData[point]) {
              value = meanData[point]
            }
          }
          
          waferData.push({
            point: point,
            x: x,
            y: y,
            value: value,
            name: `Point ${pointNum}`,
            position: position
          })
        })
        
        console.log('📊 Generated wafer data:', waferData)
        return {
          success: true,
          data: waferData
        }
      } else {
        return {
          success: false,
          error: response.error || 'Failed to fetch wafer data',
          data: []
        }
      }
    } catch (error) {
      console.error('❌ Error fetching wafer data:', error)
      return {
        success: false,
        error: error.message,
        data: []
      }
    }
  },

  // Get profile data (x, y, z) for a specific measurement point and tool
  async getProfileData(filename, pointNumber, toolName = 'MAP608', siteInfo = null) {
    console.log(`🔍 [API] Fetching profile data for filename: "${filename}", point: ${pointNumber} from tool: ${toolName}`)
    console.log(`📍 [API] Site info received:`, siteInfo)
    console.log(`📍 [API] Site info type:`, typeof siteInfo)
    console.log(`📍 [API] Site info null check:`, siteInfo === null)
    
    const params = new URLSearchParams({ tool: toolName })
    if (siteInfo) {
      console.log(`📍 [API] Processing site info fields:`)
      console.log(`   site_id: "${siteInfo.site_id}" (${typeof siteInfo.site_id})`)
      console.log(`   site_x: "${siteInfo.site_x}" (${typeof siteInfo.site_x})`)
      console.log(`   site_y: "${siteInfo.site_y}" (${typeof siteInfo.site_y})`)
      console.log(`   point_no: "${siteInfo.point_no}" (${typeof siteInfo.point_no})`)
      
      if (siteInfo.site_id !== null && siteInfo.site_id !== undefined) {
        params.append('site_id', siteInfo.site_id)
        console.log(`   ✅ Added site_id: ${siteInfo.site_id}`)
      }
      if (siteInfo.site_x !== null && siteInfo.site_x !== undefined) {
        params.append('site_x', siteInfo.site_x)
        console.log(`   ✅ Added site_x: ${siteInfo.site_x}`)
      }
      if (siteInfo.site_y !== null && siteInfo.site_y !== undefined) {
        params.append('site_y', siteInfo.site_y)
        console.log(`   ✅ Added site_y: ${siteInfo.site_y}`)
      }
      if (siteInfo.point_no !== null && siteInfo.point_no !== undefined) {
        params.append('point_no', siteInfo.point_no)
        console.log(`   ✅ Added point_no: ${siteInfo.point_no}`)
      }
    } else {
      console.log(`⚠️ [API] No site info provided`)
    }
    
    console.log(`🔗 [API] Profile request URL: /afm-files/profile/${encodeURIComponent(filename)}/${encodeURIComponent(pointNumber)}?${params}`)
    const response = await api.get(`/afm-files/profile/${encodeURIComponent(filename)}/${encodeURIComponent(pointNumber)}?${params}`)
    console.log('📊 [API] Profile data response:', response)
    return response
  },

  // Get profile image for a specific measurement point and tool
  async getProfileImage(filename, pointNumber, toolName = 'MAP608', siteInfo = null) {
    console.log(`🔍 [API] Fetching profile image for filename: "${filename}", point: ${pointNumber} from tool: ${toolName}`)
    if (siteInfo) {
      console.log(`📍 [API] Site info provided:`, siteInfo)
    }
    
    const params = new URLSearchParams({ tool: toolName })
    if (siteInfo) {
      if (siteInfo.site_id !== null) params.append('site_id', siteInfo.site_id)
      if (siteInfo.site_x !== null) params.append('site_x', siteInfo.site_x)
      if (siteInfo.site_y !== null) params.append('site_y', siteInfo.site_y)
      if (siteInfo.point_no !== null) params.append('point_no', siteInfo.point_no)
    }
    
    console.log(`🔗 [API] Image request URL: /afm-files/image/${encodeURIComponent(filename)}/${encodeURIComponent(pointNumber)}?${params}`)
    const response = await api.get(`/afm-files/image/${encodeURIComponent(filename)}/${encodeURIComponent(pointNumber)}?${params}`)
    console.log('📊 [API] Profile image response:', response)
    return response
  },

  // Get the URL for serving a profile image
  getProfileImageUrl(filename, pointNumber, toolName = 'MAP608', siteInfo = null) {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api'
    const params = new URLSearchParams({ tool: toolName })
    
    if (siteInfo) {
      if (siteInfo.site_id !== null) params.append('site_id', siteInfo.site_id)
      if (siteInfo.site_x !== null) params.append('site_x', siteInfo.site_x)
      if (siteInfo.site_y !== null) params.append('site_y', siteInfo.site_y)
      if (siteInfo.point_no !== null) params.append('point_no', siteInfo.point_no)
    }
    
    const url = `${baseUrl}/afm-files/image-file/${encodeURIComponent(filename)}/${encodeURIComponent(pointNumber)}?${params}`
    console.log(`🔗 [API] Image URL generated: ${url}`)
    return url
  }
}

// Local search function - filters pre-loaded data instead of making API calls
export function filterMeasurementsLocally(allData, query) {
  try {
    console.log(`🔍 FilterMeasurementsLocally called with query: "${query}" on ${allData.length} items`)
    
    if (!query || query.trim() === '' || query.trim().length < 2) {
      // Return all data sorted by date (latest first)
      const sortedData = [...allData].sort((a, b) => {
        const dateA = new Date(a.formatted_date)
        const dateB = new Date(b.formatted_date)
        return dateB - dateA
      })
      console.log(`✅ Returning all ${sortedData.length} measurements (sorted by latest first)`)
      return sortedData
    }
    
    const normalizedQuery = query.trim().toLowerCase()
    
    // Filter data based on query
    const filteredData = allData.filter(measurement => {
      const searchableText = [
        measurement.lot_id,
        measurement.recipe_name,
        measurement.date,
        measurement.formatted_date,
        measurement.slot_number?.toString(),
        measurement.measured_info?.toString()
      ].join(' ').toLowerCase()
      
      return searchableText.includes(normalizedQuery)
    })
    
    // Sort filtered results by date (latest first)
    const sortedData = filteredData.sort((a, b) => {
      const dateA = new Date(a.formatted_date)
      const dateB = new Date(b.formatted_date)
      return dateB - dateA
    })
    
    console.log(`✅ Filtered to ${sortedData.length} measurements matching "${query}"`)
    return sortedData
    
  } catch (error) {
    console.error('❌ Local filter error:', error)
    return []
  }
}

// Main search function for compatibility with existing frontend - now uses local filtering
export async function searchMeasurementsAsync(query, toolName = 'MAP608') {
  try {
    console.log(`🔍 SearchMeasurementsAsync called with query: "${query}" for tool: ${toolName}`)
    
    // Get all AFM files for the tool
    const response = await apiService.getAfmFiles(toolName)
    
    if (!response.success || !response.data) {
      throw new Error('Failed to load AFM files')
    }

    console.log(`✅ Loaded ${response.total} AFM measurements from ${toolName}`)

    // Transform real file data to match the expected search result format
    const transformedData = response.data.map(measurement => ({
      fab: 'SK_Hynix_ITC',
      lot_id: measurement.lot_id,
      wf_id: 'W01', // Default wafer ID 
      lot_wf: `${measurement.lot_id}_W01`,
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

    // Apply local filtering
    const filteredResults = filterMeasurementsLocally(transformedData, query)

    console.log('✅ Transformed and filtered data for frontend:', filteredResults.slice(0, 2))

    return {
      success: true,
      data: filteredResults,
      total: filteredResults.length,
      total_available: transformedData.length,
      query: query,
      tool: toolName,
      has_more: false,
      data_source: 'real_files_local_filter'
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
export async function fetchProfileData(filename, point, toolName = 'MAP608') {
  console.log(`📊 fetchProfileData called for filename: ${filename}, point: ${point}, tool: ${toolName}`)
  
  try {
    // Remove .csv extension from filename if present
    const cleanFilename = filename.replace('.csv', '')
    
    // Keep the full measurement point with site info (e.g., "1_UL")
    // The backend needs this to construct the correct file path
    const pointNumber = point
    
    console.log(`🔄 Calling getProfileData with cleanFilename: ${cleanFilename}, pointNumber: ${pointNumber}`)
    
    const response = await apiService.getProfileData(cleanFilename, pointNumber, toolName)
    
    if (response.success && response.data) {
      console.log(`✅ Loaded ${response.data.length} profile data points for ${cleanFilename}, point ${pointNumber}`)
      return response.data
    } else {
      console.warn('⚠️ Failed to load profile data:', response.error)
      return []
    }
  } catch (error) {
    console.error('❌ Error fetching profile data:', error)
    return []
  }
}

export async function fetchMeasurementData(filename, toolName = 'MAP608') {
  console.log(`🔍 fetchMeasurementData called for filename: ${filename}, tool: ${toolName}`)
  
  try {
    const response = await apiService.getAfmFileDetail(filename, toolName)
    
    console.log(`📦 Raw API response:`, response)
    console.log(`📦 Response success:`, response.success)
    console.log(`📦 Response data keys:`, response.data ? Object.keys(response.data) : 'No data')
    
    if (response.success && response.data) {
      console.log(`✅ Loaded measurement data for ${filename}`)
      
      // Log detailed structure
      const data = response.data
      console.log(`📊 Information data:`, data.information)
      console.log(`📊 Summary data type:`, typeof data.summary, 'length:', Array.isArray(data.summary) ? data.summary.length : 'not array')
      console.log(`📊 Summary data sample:`, Array.isArray(data.summary) ? data.summary.slice(0, 2) : data.summary)
      console.log(`📊 Data records type:`, typeof data.data, 'length:', Array.isArray(data.data) ? data.data.length : 'not array')
      console.log(`📊 Available points:`, data.available_points)
      console.log(`📊 Raw data_status:`, data.raw_data_status)
      
      // Transform Flask response format to frontend expected format
      const transformedData = {
        ...response.data,
        // Map Flask keys to frontend expected keys
        info: data.information,           // information -> info
        summaryData: data.summary,        // summary -> summaryData for StatisticalInfoByPoints
        profileData: data.data,           // data -> profileData for charts
        // Keep original keys for backward compatibility
        information: data.information,
        summary: data.summary,
        data: data.data
      }
      
      console.log(`🔄 Transformed data keys:`, Object.keys(transformedData))
      console.log(`🔄 Frontend-expected info:`, transformedData.info ? 'Available' : 'Missing')
      console.log(`🔄 Frontend-expected summaryData:`, transformedData.summaryData ? 'Available' : 'Missing')
      console.log(`🔄 Frontend-expected profileData:`, transformedData.profileData ? 'Available' : 'Missing')
      
      return {
        success: true,
        data: transformedData
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

export async function fetchSummaryData(filename, toolName = 'MAP608') {
  console.log(`📊 fetchSummaryData called for filename: ${filename}, tool: ${toolName}`)
  
  try {
    const measurementResponse = await fetchMeasurementData(filename, toolName)
    
    if (measurementResponse.success && measurementResponse.data.summaryData) {
      console.log(`📊 Summary data found:`, measurementResponse.data.summaryData)
      return {
        success: true,
        data: measurementResponse.data.summaryData
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