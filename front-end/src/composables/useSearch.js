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
  
  // Debounced search function for AFM files
  const performSearch = async (query) => {
    if (!query || query.trim() === '' || query.trim().length < 2) {
      searchResults.value = []
      return
    }
    
    const normalizedQuery = query.trim().toLowerCase()
    console.log(`🔍 useSearch: Performing search for "${normalizedQuery}"`)
    
    // Check cache first
    if (searchCache.has(normalizedQuery)) {
      console.log('📋 useSearch: Using cached results')
      searchResults.value = searchCache.get(normalizedQuery)
      return
    }
    
    try {
      isSearching.value = true
      console.log('🌐 useSearch: Making API call to search AFM files')
      
      // Use the new AFM files search API
      const response = await apiService.searchAfmFiles(normalizedQuery)
      
      if (response.success) {
        console.log(`✅ useSearch: Found ${response.total} AFM measurements`)
        console.log('📊 useSearch: Sample raw data:', response.data.slice(0, 2))
        
        // Transform AFM file data to match expected format for the UI
        const transformedData = response.data.map(measurement => ({
          // UI-expected fields
          fab: 'SK_Hynix_ITC',
          lot_id: measurement.lot_id,
          wf_id: 'W01', // Default wafer ID since filenames don't contain this
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
          // Real AFM file metadata
          filename: measurement.filename,
          date: measurement.date,
          formatted_date: measurement.formatted_date,
          recipe_name: measurement.recipe_name,
          slot_number: measurement.slot_number,
          measured_info: measurement.measured_info,
          file_id: measurement.id
        }))
        
        console.log('✅ useSearch: Transformed data for UI:', transformedData.slice(0, 2))
        searchResults.value = transformedData
        
        // Cache the results (limit cache size)
        if (searchCache.size > 50) {
          const firstKey = searchCache.keys().next().value
          searchCache.delete(firstKey)
        }
        searchCache.set(normalizedQuery, transformedData)
      } else {
        console.log('⚠️ useSearch: Search API returned unsuccessful response')
        searchResults.value = []
      }
    } catch (error) {
      console.error('❌ useSearch: Search error:', error)
      searchResults.value = []
    } finally {
      isSearching.value = false
    }
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
    console.log(`⚡ useSearch: Manual search trigger for "${query}"`)
    
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
    triggerSearch,
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