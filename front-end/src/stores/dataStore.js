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

  // Actions (functions)
  function addToHistory(measurement) {
    // Remove if already exists
    viewHistory.value = viewHistory.value.filter(item => item.filename !== measurement.filename)
    
    // Add to beginning
    viewHistory.value.unshift({
      ...measurement,
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
    setSelectedTool
  }
})