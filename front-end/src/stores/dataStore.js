import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const STORAGE_KEYS = {
  VIEW_HISTORY: 'afm_view_history',
  GROUPED_DATA: 'afm_grouped_data',
  GROUP_HISTORY: 'afm_group_history',
  SELECTED_TOOL: 'afm_selected_tool'
}

function loadFromStorage(key, defaultValue = []) {
  try {
    const stored = localStorage.getItem(key)
    return stored ? JSON.parse(stored) : defaultValue
  } catch (error) {
    console.error(`Error loading ${key} from localStorage:`, error)
    return defaultValue
  }
}

function saveToStorage(key, data) {
  try {
    localStorage.setItem(key, JSON.stringify(data))
  } catch (error) {
    console.error(`Error saving ${key} to localStorage:`, error)
  }
}

export const useDataStore = defineStore('data', () => {
  // State (reactive references)
  const viewHistory = ref(loadFromStorage(STORAGE_KEYS.VIEW_HISTORY))
  const groupedData = ref(loadFromStorage(STORAGE_KEYS.GROUPED_DATA))
  const groupHistory = ref(loadFromStorage(STORAGE_KEYS.GROUP_HISTORY))
  const selectedTool = ref(loadFromStorage(STORAGE_KEYS.SELECTED_TOOL, 'MAP608'))
  const maxHistoryItems = ref(10)

  // Getters (computed properties)
  const historyCount = computed(() => viewHistory.value.length)
  const groupedCount = computed(() => groupedData.value.length)
  const groupHistoryCount = computed(() => groupHistory.value.length)
  const isInGroup = computed(() => (filename) => {
    return groupedData.value.some(item => item.filename === filename)
  })

  const validGroupedData = computed(() => {
    return groupedData.value.filter(item => 
      item.filename && (item.rcp_id || item.recipe_name)
    )
  })

  const groupedDataSummary = computed(() => {
    if (groupedData.value.length === 0) return null
    
    const summary = {
      total: groupedData.value.length,
      valid: validGroupedData.value.length,
      fabs: [...new Set(groupedData.value.map(item => item.fab || 'Unknown'))],
      tools: [...new Set(groupedData.value.map(item => item.tool || selectedTool.value))],
      recipes: [...new Set(groupedData.value.map(item => item.rcp_id || item.recipe_name || 'Unknown'))],
      dateRange: getDateRange(groupedData.value)
    }
    
    return summary
  })

  // Actions (functions)
  function addToHistory(measurement) {
    // Remove if already exists
    viewHistory.value = viewHistory.value.filter(item => item.filename !== measurement.filename)
    
    // Add to beginning with explicit tool tracking
    viewHistory.value.unshift({
      ...measurement,
      tool_name: measurement.tool_name || measurement.tool || selectedTool.value,
      viewedAt: new Date().toISOString()
    })
    
    // Keep only max items
    if (viewHistory.value.length > maxHistoryItems.value) {
      viewHistory.value = viewHistory.value.slice(0, maxHistoryItems.value)
    }
    
    // Save to localStorage
    saveToStorage(STORAGE_KEYS.VIEW_HISTORY, viewHistory.value)
  }

  function clearHistory() {
    viewHistory.value = []
    saveToStorage(STORAGE_KEYS.VIEW_HISTORY, viewHistory.value)
  }


  function addToGroup(measurement) {
    // Check if already in group
    if (!isInGroup.value(measurement.filename)) {
      groupedData.value.push({
        ...measurement,
        tool_name: measurement.tool_name || measurement.tool || selectedTool.value,
        addedAt: new Date().toISOString()
      })
      
      // Save to localStorage
      saveToStorage(STORAGE_KEYS.GROUPED_DATA, groupedData.value)
    }
  }

  function removeFromGroup(filename) {
    groupedData.value = groupedData.value.filter(item => item.filename !== filename)
    saveToStorage(STORAGE_KEYS.GROUPED_DATA, groupedData.value)
  }

  function clearGroup() {
    groupedData.value = []
    saveToStorage(STORAGE_KEYS.GROUPED_DATA, groupedData.value)
  }

  function saveCurrentGroupAsHistory(name, description = '') {
    if (groupedData.value.length === 0) return
    
    const groupSnapshot = {
      id: Date.now().toString(),
      name: name || `Group ${new Date().toLocaleDateString()}`,
      description: description.trim(),
      items: [...groupedData.value],
      tools: [...new Set(groupedData.value.map(item => item.tool_name || item.tool || selectedTool.value))],
      createdAt: new Date().toISOString(),
      itemCount: groupedData.value.length
    }
    
    // Remove if name already exists
    groupHistory.value = groupHistory.value.filter(item => item.name !== groupSnapshot.name)
    
    // Add to beginning
    groupHistory.value.unshift(groupSnapshot)
    
    // Keep only max items
    if (groupHistory.value.length > maxHistoryItems.value) {
      groupHistory.value = groupHistory.value.slice(0, maxHistoryItems.value)
    }
    
    // Save to localStorage
    saveToStorage(STORAGE_KEYS.GROUP_HISTORY, groupHistory.value)
  }

  function loadGroupFromHistory(groupId) {
    const savedGroup = groupHistory.value.find(item => item.id === groupId)
    if (savedGroup) {
      groupedData.value = [...savedGroup.items]
      saveToStorage(STORAGE_KEYS.GROUPED_DATA, groupedData.value)
    }
  }

  function removeFromGroupHistory(groupId) {
    groupHistory.value = groupHistory.value.filter(item => item.id !== groupId)
    saveToStorage(STORAGE_KEYS.GROUP_HISTORY, groupHistory.value)
  }

  function clearGroupHistory() {
    groupHistory.value = []
    saveToStorage(STORAGE_KEYS.GROUP_HISTORY, groupHistory.value)
  }

  function setSelectedTool(toolId) {
    selectedTool.value = toolId
    saveToStorage(STORAGE_KEYS.SELECTED_TOOL, toolId)
  }

  // Helper function to get date range from measurements
  function getDateRange(measurements) {
    if (!measurements || measurements.length === 0) return null
    
    const dates = measurements
      .map(item => new Date(item.event_time || item.formatted_date || new Date()))
      .filter(date => !isNaN(date))
      .sort((a, b) => a - b)
    
    if (dates.length === 0) return null
    
    return {
      earliest: dates[0],
      latest: dates[dates.length - 1],
      span: dates[dates.length - 1] - dates[0]
    }
  }

  // Helper function to organize data by tool
  function organizeDataByTool(measurements) {
    const toolGroups = {}
    
    measurements.forEach(measurement => {
      const toolName = measurement.tool_name || measurement.tool || selectedTool.value || 'MAP608'
      if (!toolGroups[toolName]) {
        toolGroups[toolName] = []
      }
      toolGroups[toolName].push(measurement)
    })
    
    return toolGroups
  }

  // Helper function to validate measurement for navigation
  function validateMeasurementForNavigation(measurement) {
    if (!measurement) return false
    
    const hasFilename = !!(measurement.filename)
    const hasRecipe = !!(measurement.rcp_id || measurement.recipe_name)
    
    return hasFilename && hasRecipe
  }

  // Helper function to prepare measurement data for result page navigation
  function prepareMeasurementForNavigation(measurement) {
    if (!validateMeasurementForNavigation(measurement)) {
      throw new Error('Invalid measurement data for navigation')
    }
    
    return {
      filename: measurement.filename,
      recipeId: measurement.rcp_id || measurement.recipe_name,
      tool: measurement.tool || selectedTool.value || 'MAP608'
    }
  }

  // Return everything that should be exposed
  return {
    // State
    viewHistory,
    groupedData,
    groupHistory,
    selectedTool,
    maxHistoryItems,
    
    // Getters
    historyCount,
    groupedCount,
    groupHistoryCount,
    isInGroup,
    validGroupedData,
    groupedDataSummary,
    
    // Actions
    addToHistory,
    clearHistory,
    addToGroup,
    removeFromGroup,
    clearGroup,
    saveCurrentGroupAsHistory,
    loadGroupFromHistory,
    removeFromGroupHistory,
    clearGroupHistory,
    setSelectedTool,
    
    // Helper functions
    getDateRange,
    validateMeasurementForNavigation,
    prepareMeasurementForNavigation,
    organizeDataByTool
  }
})