import { ref, watch, nextTick } from 'vue'
import { apiService, filterMeasurementsLocally } from '@/services/api'
import { useDataStore } from '@/stores/dataStore.js'

export function useDebounceSearch(delay = 300) {
  const dataStore = useDataStore()
  const searchQuery = ref(dataStore.searchQuery || '')
  const searchResults = ref([])
  const isSearching = ref(false)
  const allFileData = ref([]) // Store all loaded files for local filtering
  const searchCache = new Map()
  
  let searchTimeout = null
  
  // Load all files for a tool (called once when tool changes)
  const loadAllFiles = async (toolName = 'MAP608') => {
    try {
      console.log(`🔄 useSearch: Loading all files for tool: ${toolName}`)
      isSearching.value = true
      
      const response = await apiService.getAfmFiles(toolName)
      
      if (response.success) {
        console.log(`✅ useSearch: Loaded ${response.total} AFM measurements for ${toolName}`)
        
        // Log the structure of the first measurement for debugging
        if (response.data && response.data.length > 0) {
          const firstMeasurement = response.data[0]
          console.log('📊 MEASUREMENT STRUCTURE FROM FLASK:')
          console.log('📊 Keys:', Object.keys(firstMeasurement))
          console.log('📊 Sample measurement:', firstMeasurement)
          
          // If we have detailed measurement data, log its structure too
          if (firstMeasurement.data_status) {
            console.log('📊 data_status columns:', Object.keys(firstMeasurement.data_status))
            console.log('📊 data_status sample rows:', {
              Site: firstMeasurement.data_status.Site?.slice(0, 5),
              ITEM: firstMeasurement.data_status.ITEM?.slice(0, 5),
              'Left_H (nm)': firstMeasurement.data_status['Left_H (nm)']?.slice(0, 5)
            })
          }
          
          if (firstMeasurement.data_detail) {
            console.log('📊 data_detail sites:', Object.keys(firstMeasurement.data_detail))
            const firstSite = Object.keys(firstMeasurement.data_detail)[0]
            if (firstSite) {
              console.log(`📊 ${firstSite} columns:`, Object.keys(firstMeasurement.data_detail[firstSite]))
            }
          }
        }
        
        // Simplified transformation - keep only essential fields from file list
        const transformedData = response.data.map(measurement => ({
          // Core identification fields
          unique_key: measurement.unique_key,
          filename: measurement.filename,
          date: measurement.date,
          formatted_date: measurement.formatted_date,
          recipe_name: measurement.recipe_name,
          lot_id: measurement.lot_id,
          slot_number: measurement.slot_number,
          time: measurement.time,
          measured_info: measurement.measured_info,
          tool_name: measurement.tool_name || toolName,
          
          // File availability indicators (with defaults for undefined)
          profile_dir_list: measurement.profile_dir_list || null,
          data_dir_list: measurement.data_dir_list || null,
          tiff_dir_list: measurement.tiff_dir_list || null,
          align_dir_list: measurement.align_dir_list || null,
          tip_dir_list: measurement.tip_dir_list || null,
          
          // Computed availability flags for easier UI usage (handle undefined gracefully)
          has_profile: measurement.profile_dir_list && measurement.profile_dir_list.length > 0,
          has_data: measurement.data_dir_list && measurement.data_dir_list.length > 0,
          has_image: measurement.tiff_dir_list && measurement.tiff_dir_list.length > 0,
          has_align: measurement.align_dir_list && measurement.align_dir_list.length > 0,
          has_tip: measurement.tip_dir_list && measurement.tip_dir_list.length > 0
          
          // Note: Detailed measurement data (info, data_status, data_detail) is loaded separately
          // via the detail endpoint when a specific measurement is selected
        }))
        
        allFileData.value = transformedData
        console.log(`✅ useSearch: Stored ${transformedData.length} simplified measurements for local filtering`)
        
        // Clear cache when loading new data
        searchCache.clear()
        
        // If there's an active search query, apply filtering
        if (searchQuery.value) {
          performLocalSearch(searchQuery.value)
        } else {
          // Show all data sorted by latest first
          const sortedData = filterMeasurementsLocally(transformedData, '')
          searchResults.value = sortedData
        }
      } else {
        console.log('⚠️ useSearch: Failed to load files')
        allFileData.value = []
        searchResults.value = []
      }
    } catch (error) {
      console.error('❌ useSearch: Error loading files:', error)
      allFileData.value = []
      searchResults.value = []
    } finally {
      isSearching.value = false
    }
  }

  // Local search function using pre-loaded data
  const performLocalSearch = (query) => {
    if (!query || query.trim() === '' || query.trim().length < 2) {
      // Show all data sorted by date
      const sortedData = filterMeasurementsLocally(allFileData.value, '')
      searchResults.value = sortedData
      return
    }
    
    const normalizedQuery = query.trim().toLowerCase()
    console.log(`🔍 useSearch: Performing local search for "${normalizedQuery}" on ${allFileData.value.length} items`)
    
    // Check cache first
    if (searchCache.has(normalizedQuery)) {
      console.log('📋 useSearch: Using cached results')
      searchResults.value = searchCache.get(normalizedQuery)
      return
    }
    
    // Filter locally
    const filteredData = filterMeasurementsLocally(allFileData.value, normalizedQuery)
    searchResults.value = filteredData
    
    console.log(`✅ useSearch: Local search found ${filteredData.length} results`)
    
    // Cache the results (limit cache size)
    if (searchCache.size > 50) {
      const firstKey = searchCache.keys().next().value
      searchCache.delete(firstKey)
    }
    searchCache.set(normalizedQuery, filteredData)
  }
  
  
  // Watch for search query changes with debouncing
  watch(searchQuery, (newQuery) => {
    console.log(`🔄 useSearch: Search query changed to "${newQuery}"`)
    
    // Clear previous timeout
    if (searchTimeout) clearTimeout(searchTimeout)
    
    // Sync with data store
    dataStore.setSearchQuery(newQuery)
    
    // Always perform local search (no minimum length restriction for showing all data)
    searchTimeout = setTimeout(() => {
      performLocalSearch(newQuery)
    }, delay)
  }, { immediate: false })

  // Watch for tool changes to reload data
  watch(() => dataStore.selectedTool, (newTool, oldTool) => {
    if (newTool && newTool !== oldTool) {
      console.log(`🔧 useSearch: Tool changed from ${oldTool} to ${newTool}, reloading data`)
      loadAllFiles(newTool)
    }
  }, { immediate: true })
  
  // Manual search trigger (for immediate search)
  const triggerSearch = async (query) => {
    console.log(`⚡ useSearch: Manual search trigger for "${query}"`)
    
    if (searchTimeout) clearTimeout(searchTimeout)
    
    searchQuery.value = query
    await nextTick()
    
    // Perform local search immediately
    performLocalSearch(query)
  }
  
  // Clear cache
  const clearCache = () => {
    console.log('🗑️ useSearch: Clearing cache')
    searchCache.clear()
  }
  
  // Get cache info for debugging
  const getCacheInfo = () => ({
    searchCacheSize: searchCache.size
  })
  
  return {
    searchQuery,
    searchResults,
    isSearching,
    allFileData,
    triggerSearch,
    loadAllFiles,
    clearCache,
    getCacheInfo
  }
}

export function useRealtimeSearch() {
  console.log('🚀 useSearch: Initializing real-time search for AFM files')
  
  const {
    searchQuery,
    searchResults,
    isSearching,
    allFileData,
    triggerSearch,
    loadAllFiles,
    clearCache,
    getCacheInfo
  } = useDebounceSearch(300) // 300ms debounce
  
  return {
    searchQuery,
    searchResults,
    isSearching,
    allFileData,
    triggerSearch,
    loadAllFiles,
    clearCache,
    getCacheInfo
  }
}