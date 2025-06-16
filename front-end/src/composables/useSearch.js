import { ref, watch, nextTick } from 'vue'
import { apiService } from '@/services/api.js'

export function useDebounceSearch(delay = 300) {
  const searchQuery = ref('')
  const searchResults = ref([])
  const isSearching = ref(false)
  const suggestions = ref([])
  const searchCache = new Map()
  const suggestionsCache = new Map()
  
  let searchTimeout = null
  let suggestionsTimeout = null
  
  // Debounced search function
  const performSearch = async (query) => {
    if (!query || query.trim() === '' || query.trim().length < 2) {
      searchResults.value = []
      return
    }
    
    const normalizedQuery = query.trim().toLowerCase()
    
    // Check cache first
    if (searchCache.has(normalizedQuery)) {
      searchResults.value = searchCache.get(normalizedQuery)
      return
    }
    
    try {
      isSearching.value = true
      const response = await apiService.searchMeasurements(normalizedQuery, 100, 0)
      
      if (response.success) {
        // Transform data to match expected format
        const transformedData = response.data.map(measurement => ({
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
          // Additional metadata
          material: measurement.material,
          tool_name: measurement.tool_name,
          file_location: measurement.file_location,
          measurement_quality: measurement.measurement_quality,
          status: measurement.status
        }))
        
        searchResults.value = transformedData
        
        // Cache the results (limit cache size)
        if (searchCache.size > 50) {
          const firstKey = searchCache.keys().next().value
          searchCache.delete(firstKey)
        }
        searchCache.set(normalizedQuery, transformedData)
      }
    } catch (error) {
      console.error('Search error:', error)
      searchResults.value = []
    } finally {
      isSearching.value = false
    }
  }
  
  // Get search suggestions
  const getSuggestions = async (query) => {
    if (!query || query.trim().length < 2) {
      suggestions.value = []
      return
    }
    
    const normalizedQuery = query.trim().toLowerCase()
    
    // Check cache first
    if (suggestionsCache.has(normalizedQuery)) {
      suggestions.value = suggestionsCache.get(normalizedQuery)
      return
    }
    
    try {
      const response = await apiService.getSearchSuggestions(normalizedQuery, 8)
      
      if (response.success) {
        suggestions.value = response.data
        
        // Cache suggestions (limit cache size)
        if (suggestionsCache.size > 30) {
          const firstKey = suggestionsCache.keys().next().value
          suggestionsCache.delete(firstKey)
        }
        suggestionsCache.set(normalizedQuery, response.data)
      }
    } catch (error) {
      console.error('Suggestions error:', error)
      suggestions.value = []
    }
  }
  
  // Watch for search query changes with debouncing
  watch(searchQuery, (newQuery) => {
    // Clear previous timeouts
    if (searchTimeout) clearTimeout(searchTimeout)
    if (suggestionsTimeout) clearTimeout(suggestionsTimeout)
    
    if (!newQuery || newQuery.trim() === '' || newQuery.trim().length < 2) {
      searchResults.value = []
      suggestions.value = []
      return
    }
    
    // Debounce search
    searchTimeout = setTimeout(() => {
      performSearch(newQuery)
    }, delay)
    
    // Debounce suggestions (shorter delay)
    suggestionsTimeout = setTimeout(() => {
      getSuggestions(newQuery)
    }, delay / 2)
  }, { immediate: false })
  
  // Manual search trigger (for immediate search)
  const triggerSearch = async (query) => {
    if (searchTimeout) clearTimeout(searchTimeout)
    if (suggestionsTimeout) clearTimeout(suggestionsTimeout)
    
    searchQuery.value = query
    await nextTick()
    
    // Only search if query has 2+ characters
    if (query && query.trim().length >= 2) {
      await performSearch(query)
    }
  }
  
  // Clear cache
  const clearCache = () => {
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
    triggerSearch,
    clearCache,
    getCacheInfo
  }
}

export function useRealtimeSearch() {
  const {
    searchQuery,
    searchResults,
    isSearching,
    suggestions,
    triggerSearch,
    clearCache,
    getCacheInfo
  } = useDebounceSearch(300) // 300ms debounce
  
  return {
    searchQuery,
    searchResults,
    isSearching,
    suggestions,
    triggerSearch,
    clearCache,
    getCacheInfo
  }
}