import { afmService } from './afmService'

/**
 * Data Processing Service
 * Handles data transformation and processing functions
 */

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
    const response = await afmService.getAfmFiles(toolName)
    
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
    
    const response = await afmService.getProfileData(cleanFilename, pointNumber, toolName)
    
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
    const response = await afmService.getAfmFileDetail(filename, toolName)
    
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