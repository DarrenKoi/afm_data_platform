<template>
  <v-container fluid class="pa-4">
    <!-- Logo Header -->
    <div class="text-center mb-6">
      <img alt="AFM Logo" class="mb-4" src="@/assets/afm_logo2.png"
        style="max-width: 400px; width: 100%; height: auto;">
    </div>

    <!-- Tool Selection Interface -->
    <div class="text-center mb-6">
      <v-card class="pa-3 mx-auto" style="max-width: 300px;" elevation="2">
        <div class="d-flex justify-center align-center gap-3">
          <v-icon color="primary">mdi-tools</v-icon>
          <span class="text-h6 font-weight-medium mr-3">Tool:</span>
          <v-chip
            v-for="tool in availableTools"
            :key="tool.id"
            :color="selectedTool === tool.id ? 'primary' : 'default'"
            :variant="selectedTool === tool.id ? 'elevated' : 'outlined'"
            size="large"
            class="px-4"
            @click="selectTool(tool.id)"
          >
            <v-icon start :color="selectedTool === tool.id ? 'white' : 'primary'">
              {{ tool.icon }}
            </v-icon>
            <span class="font-weight-medium">{{ tool.name }}</span>
          </v-chip>
        </div>
      </v-card>
    </div>

    <v-row justify="center" style="max-width: 1400px; margin: 0 auto;">
      <!-- Left Column: Search & Results -->
      <v-col cols="12" lg="7" md="6">
        <SearchSection :search-results="searchResults" :is-searching="isSearching" :is-in-group="dataStore.isInGroup"
          @search-performed="handleSearchPerformed" @add-to-group="addToGroup" @view-details="viewDetails" />
      </v-col>

      <!-- Right Column: History & Data Grouping -->
      <v-col cols="12" lg="5" md="6">
        <div class="px-2">
          <!-- View History -->
          <ViewHistoryCard :view-history="dataStore.viewHistory" :history-count="dataStore.historyCount"
            @view-details="viewDetails" @clear-history="dataStore.clearHistory" />

          <!-- Data Grouping -->
          <DataGroupingCard :grouped-data="dataStore.groupedData" :grouped-count="dataStore.groupedCount"
            @remove-from-group="dataStore.removeFromGroup" @clear-group="dataStore.clearGroup"
            @view-trend-analysis="viewTrendAnalysis" @save-current-group="saveCurrentGroup" />

          <!-- Saved Groups -->
          <SavedGroupsCard :group-history="dataStore.groupHistory" :group-history-count="dataStore.groupHistoryCount"
            @load-saved-group="loadSavedGroup" @remove-from-group-history="dataStore.removeFromGroupHistory"
            @clear-group-history="dataStore.clearGroupHistory" />
        </div>
      </v-col>
    </v-row>

    <!-- Loading Dialog for SEE TOGETHER -->
    <v-dialog v-model="showLoadingDialog" max-width="400px" persistent>
      <v-card>
        <v-card-text class="text-center pa-6">
          <v-progress-circular
            indeterminate
            color="primary"
            size="64"
            class="mb-4"
          />
          <h3 class="text-h6 mb-2">Loading Measurement Data</h3>
          <p class="text-body-2 text-medium-emphasis">
            {{ loadingMessage }}
          </p>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Save Group Dialog -->
    <v-dialog v-model="showSaveDialog" max-width="500px" persistent>
      <v-card>
        <v-card-title class="text-h5 d-flex align-center">
          <v-icon color="primary" class="mr-2">mdi-content-save</v-icon>
          Save Data Group
        </v-card-title>
        
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="groupName"
                  label="Group Name *"
                  placeholder="Enter a name for this group"
                  variant="outlined"
                  :rules="[v => !!v || 'Group name is required']"
                  counter="50"
                  maxlength="50"
                  autofocus
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="groupDescription"
                  label="Description (Optional)"
                  placeholder="Add a description for this group"
                  variant="outlined"
                  rows="3"
                  counter="200"
                  maxlength="200"
                />
              </v-col>
              <v-col cols="12">
                <v-alert type="info" variant="tonal" class="mb-0">
                  <div class="text-body-2">
                    <strong>Group contains:</strong> {{ dataStore.groupedCount }} measurements
                  </div>
                </v-alert>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn
            color="grey"
            variant="text"
            @click="cancelSaveGroup"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            :disabled="!groupName.trim()"
            @click="confirmSaveGroup"
          >
            <v-icon start>mdi-content-save</v-icon>
            Save Group
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDataStore } from '@/stores/dataStore.js'

// Import components
import SearchSection from '@/components/MainPage/SearchSection.vue'
import ViewHistoryCard from '@/components/MainPage/ViewHistoryCard.vue'
import DataGroupingCard from '@/components/MainPage/DataGroupingCard.vue'
import SavedGroupsCard from '@/components/MainPage/SavedGroupsCard.vue'

const router = useRouter()
const dataStore = useDataStore()
const searchResults = ref([])
const isSearching = ref(false)

// Tool selection state
const selectedTool = ref('MAP608')
const availableTools = ref([
  {
    id: 'MAP608',
    name: 'MAP608',
    icon: 'mdi-microscope',
    description: 'Atomic Force Microscopy Analysis Tool',
    status: 'active'
  }
  // Future tools can be added here:
  // {
  //   id: 'MAP609',
  //   name: 'MAP609',
  //   icon: 'mdi-atom',
  //   description: 'Advanced AFM Analysis Tool',
  //   status: 'coming_soon'
  // }
])

// Handle real-time search results from SearchSection component
function handleSearchPerformed(query, results) {
  if (query && results) {
    searchResults.value = results
    console.log('Real-time search results:', results.length, 'items')
  }
}

function viewDetails(measurement) {
  // Add to history
  dataStore.addToHistory(measurement)

  // Navigate to details with recipe ID in URL
  const recipeId = measurement.rcp_id || measurement.recipe_name || 'unknown'
  router.push(`/result/${encodeURIComponent(recipeId)}/${encodeURIComponent(measurement.filename)}`)
}

function addToGroup(measurement) {
  dataStore.addToGroup(measurement)
}

async function viewTrendAnalysis() {
  console.log('🚀 [MainPage] Starting trend analysis with grouped data...')
  
  if (dataStore.groupedCount === 0) {
    console.warn('⚠️ No measurements in group to analyze')
    return
  }
  
  // Show loading dialog
  loadingMessage.value = `Loading data for ${dataStore.groupedCount} measurements...`
  showLoadingDialog.value = true
  
  try {
    // Track loading progress
    let loadedCount = 0
    const totalCount = dataStore.groupedData.length
    
    // Load detailed data for all measurements in the group
    const loadPromises = dataStore.groupedData.map(async (measurement) => {
      if (!measurement.filename) {
        console.warn(`⚠️ Skipping measurement without filename:`, measurement)
        loadedCount++
        return null
      }
      
      try {
        console.log(`📊 Loading data for: ${measurement.filename}`)
        const toolName = measurement.tool || dataStore.selectedTool || 'MAP608'
        
        // Use the apiService to fetch detailed measurement data
        const { apiService } = await import('@/services/api.js')
        const response = await apiService.getAfmFileDetail(measurement.filename, toolName)
        
        // Update progress
        loadedCount++
        loadingMessage.value = `Loading measurement ${loadedCount} of ${totalCount}...`
        
        if (response.success && response.data) {
          return {
            filename: measurement.filename,
            tool: toolName,
            info: response.data.information || {},
            summary: response.data.summary || [],
            detailedData: response.data.data || [],
            availablePoints: response.data.available_points || []
          }
        } else {
          console.error(`❌ Failed to load data for ${measurement.filename}:`, response.error)
          return null
        }
      } catch (error) {
        console.error(`❌ Error loading ${measurement.filename}:`, error)
        loadedCount++
        return null
      }
    })
    
    // Wait for all measurements to load
    const results = await Promise.all(loadPromises)
    const validResults = results.filter(r => r !== null)
    
    console.log(`✅ Loaded ${validResults.length} out of ${dataStore.groupedData.length} measurements`)
    
    // Store the loaded data in sessionStorage to pass to DataTrendPage
    if (validResults.length > 0) {
      sessionStorage.setItem('groupDetailedData', JSON.stringify(validResults))
      
      // Hide loading dialog before navigation
      showLoadingDialog.value = false
      
      // Navigate to data trend page
      router.push('/result/data_trend')
    } else {
      console.error('❌ No valid data loaded, cannot proceed to trend analysis')
      showLoadingDialog.value = false
      // Could show an error dialog here
    }
    
  } catch (error) {
    console.error('❌ Error during trend analysis data loading:', error)
    showLoadingDialog.value = false
    // Could show an error dialog here
  }
}



// Loading dialog state
const showLoadingDialog = ref(false)
const loadingMessage = ref('')

// Save group dialog state
const showSaveDialog = ref(false)
const groupName = ref('')
const groupDescription = ref('')

function saveCurrentGroup() {
  // Set default name with current date and time to make it unique
  const now = new Date()
  const dateStr = now.toLocaleDateString()
  const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  groupName.value = `Group ${dateStr} ${timeStr}`
  groupDescription.value = ''
  showSaveDialog.value = true
}

function confirmSaveGroup() {
  if (groupName.value.trim()) {
    dataStore.saveCurrentGroupAsHistory(groupName.value.trim(), groupDescription.value.trim())
    showSaveDialog.value = false
    groupName.value = ''
    groupDescription.value = ''
  }
}

function cancelSaveGroup() {
  showSaveDialog.value = false
  groupName.value = ''
  groupDescription.value = ''
}

function loadSavedGroup(groupId) {
  dataStore.loadGroupFromHistory(groupId)
}

// Tool selection functions
function selectTool(toolId) {
  console.log(`🔧 Tool selected: ${toolId}`)
  selectedTool.value = toolId
  
  // Clear current search results when switching tools
  searchResults.value = []
  
  // Store selected tool in data store for use by other components
  dataStore.setSelectedTool(toolId)
  
  // Trigger initial data load for the selected tool
  loadToolData(toolId)
}

function getSelectedToolInfo() {
  const tool = availableTools.value.find(t => t.id === selectedTool.value)
  return tool ? `${tool.name} - ${tool.description}` : 'No tool selected'
}

async function loadToolData(toolId) {
  console.log(`📊 Loading data for tool: ${toolId}`)
  // The search composable will automatically reload data when the tool changes
  // via the watch on dataStore.selectedTool
}

// Initialize component
onMounted(() => {
  console.log('🚀 MainPage: Component mounted and ready for AFM file searches')
  
  // Initialize with stored tool selection
  const storedTool = dataStore.selectedTool
  if (storedTool && availableTools.value.find(t => t.id === storedTool)) {
    selectedTool.value = storedTool
    console.log(`🔧 MainPage: Restored tool selection: ${storedTool}`)
  } else {
    // Set default tool
    selectTool('MAP608')
  }
})

</script>
