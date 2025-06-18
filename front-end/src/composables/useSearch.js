import { ref, watch, nextTick } from 'vue'
import { apiService, filterMeasurementsLocally } from '@/services/api.js'
import { useDataStore } from '@/stores/dataStore.js'

export function useDebounceSearch(delay = 300) {
  const dataStore = useDataStore()
  const searchQuery = ref('')
  const searchResults = ref([])
  const isSearching = ref(false)
  const suggestions = ref([])
  const allFileData = ref([]) // Store all loaded files for local filtering
  const searchCache = new Map()
  const suggestionsCache = new Map()
  
  let searchTimeout = null
  let suggestionsTimeout = null
  
  // Load all files for a tool (called once when tool changes)
  const loadAllFiles = async (toolName = 'MAP608') => {
    try {
      console.log(`🔄 useSearch: Loading all files for tool: ${toolName}`)
      isSearching.value = true
      
      const response = await apiService.getAfmFiles(toolName)
      
      if (response.success) {
        console.log(`✅ useSearch: Loaded ${response.total} AFM measurements for ${toolName}`)
        
        // Transform and store all file data
        const transformedData = response.data.map(measurement => ({
          // UI-expected fields
          fab: 'SK_Hynix_ITC',
          lot_id: measurement.lot_id,
          wf_id: 'W01', // Default wafer ID since filenames don't contain this
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
          // Real AFM file metadata
          filename: measurement.filename,
          date: measurement.date,
          formatted_date: measurement.formatted_date,
          recipe_name: measurement.recipe_name,
          slot_number: measurement.slot_number,
          measured_info: measurement.measured_info,
          file_id: measurement.id,
          tool_name: measurement.tool_name || toolName
        }))
        
        allFileData.value = transformedData
        console.log('✅ useSearch: Stored all file data for local filtering')
        
        // Clear cache when loading new data
        searchCache.clear()
        
        // If there's an active search query, apply filtering
        if (searchQuery.value && searchQuery.value.trim().length >= 2) {
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
  
  // Get search suggestions (simplified for AFM files)
  const getSuggestions = async (query) => {
    if (!query || query.trim().length < 2) {
      suggestions.value = []
      return
    }
    
    const normalizedQuery = query.trim().toLowerCase()
    console.log(`💡 useSearch: Getting suggestions for "${normalizedQuery}"`)
    
    // Check cache first
    if (suggestionsCache.has(normalizedQuery)) {
      console.log('📋 useSearch: Using cached suggestions')
      suggestions.value = suggestionsCache.get(normalizedQuery)
      return
    }
    
    try {
      // For now, generate simple suggestions based on common AFM search terms
      // You can enhance this later by calling a suggestions API endpoint
      const commonTerms = [
        'CMP', 'ETCH', 'DEPOSITION', 'POLISH', 'TRENCH',
        'FSOXCMP', 'OXIDE', 'METAL', 'POLY', 'NITRIDE',
        'STI', 'CONTACT', 'DAMASCENE', 'SPACER', 'GATE',
        'SHALLOW', 'INTERLAYER', 'VIA', 'BARRIER', 'COPPER',
        'HARD_MASK', 'DIELECTRIC', 'SOURCE_DRAIN', 'IMPLANT',
        'EPITAXY', 'SILICIDE'
      ]
      
      const matchingSuggestions = commonTerms
        .filter(term => term.toLowerCase().includes(normalizedQuery))
        .slice(0, 8)
      
      suggestions.value = matchingSuggestions
      console.log(`💡 useSearch: Generated ${matchingSuggestions.length} suggestions`)
      
      // Cache suggestions
      if (suggestionsCache.size > 30) {
        const firstKey = suggestionsCache.keys().next().value
        suggestionsCache.delete(firstKey)
      }
      suggestionsCache.set(normalizedQuery, matchingSuggestions)
      
    } catch (error) {
      console.error('❌ useSearch: Suggestions error:', error)
      suggestions.value = []
    }
  }
  
  // Watch for search query changes with debouncing
  watch(searchQuery, (newQuery) => {
    console.log(`🔄 useSearch: Search query changed to "${newQuery}"`)
    
    // Clear previous timeouts
    if (searchTimeout) clearTimeout(searchTimeout)
    if (suggestionsTimeout) clearTimeout(suggestionsTimeout)
    
    // Always perform local search (no minimum length restriction for showing all data)
    searchTimeout = setTimeout(() => {
      performLocalSearch(newQuery)
    }, delay)
    
    // Generate suggestions if query has content
    if (newQuery && newQuery.trim().length >= 1) {
      suggestionsTimeout = setTimeout(() => {
        getSuggestions(newQuery)
      }, delay / 2)
    } else {
      suggestions.value = []
    }
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
    if (suggestionsTimeout) clearTimeout(suggestionsTimeout)
    
    searchQuery.value = query
    await nextTick()
    
    // Perform local search immediately
    performLocalSearch(query)
  }
  
  // Clear cache
  const clearCache = () => {
    console.log('🗑️ useSearch: Clearing cache')
    searchCache.clear()
    suggestionsCache.clear()
  }
  
  // Get cache info for debugging
  const getCacheInfo = () => ({
    searchCacheSize: searchCache.size,
    suggestionsCacheSize: suggestionsCache.size
  })
  
  return {
    searchQuery,
    searchResults,
    isSearching,
    suggestions,
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
    suggestions,
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
    suggestions,
    allFileData,
    triggerSearch,
    loadAllFiles,
    clearCache,
    getCacheInfo
  }
}