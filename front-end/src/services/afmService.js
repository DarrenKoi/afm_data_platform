import api from './api'

/**
 * AFM Data Service
 * Handles AFM file data retrieval and profile data operations
 */
export const afmService = {
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

  // Get profile data (x, y, z) for a specific measurement point and tool
  async getProfileData(filename, pointNumber, toolName = 'MAP608', siteInfo = null) {
    console.log(`🔍 [API] Fetching profile data for filename: "${filename}", point: ${pointNumber} from tool: ${toolName}`)
    console.log(`📍 [API] Site info received:`, siteInfo)
    
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
          
          // Handle standard wafer position codes (case-insensitive)
          const normalizedPosition = position ? position.toUpperCase() : ''
          switch(normalizedPosition) {
            case 'UL': x = -3; y = 3; break  // Upper Left
            case 'UR': x = 3; y = 3; break   // Upper Right
            case 'LL': x = -3; y = -3; break // Lower Left
            case 'LR': x = 3; y = -3; break  // Lower Right
            case 'C': x = 0; y = 0; break    // Center
            default: 
              // For all other cases (numbered points, custom naming), arrange in a grid
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
  }
}