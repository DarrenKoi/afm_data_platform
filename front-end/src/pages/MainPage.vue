<template>
  <v-container fluid class="pa-4">
    <!-- Logo Header -->
    <div class="text-center mb-6">
      <img alt="AFM Logo" class="mb-4" src="@/assets/afm_logo2.png"
        style="max-width: 400px; width: 100%; height: auto;">
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
import { searchMeasurementsAsync } from '@/services/api.js'

// Import components
import SearchSection from '@/components/MainPage/SearchSection.vue'
import ViewHistoryCard from '@/components/MainPage/ViewHistoryCard.vue'
import DataGroupingCard from '@/components/MainPage/DataGroupingCard.vue'
import SavedGroupsCard from '@/components/MainPage/SavedGroupsCard.vue'

const router = useRouter()
const dataStore = useDataStore()
const searchResults = ref([])
const isSearching = ref(false)

// Handle real-time search results from SearchSection component
function handleSearchPerformed(query, results) {
  if (query && results) {
    searchResults.value = results
    console.log('Real-time search results:', results.length, 'items')
  }
}

// Legacy search function for backward compatibility
async function performSearch(query) {
  if (!query) return
  isSearching.value = true

  try {
    const response = await searchMeasurementsAsync(query)
    if (response.success) {
      searchResults.value = response.data
      console.log('Search results:', searchResults.value)
    }
  } catch (error) {
    console.error('Search error:', error)
  } finally {
    isSearching.value = false
  }
}

function viewDetails(measurement) {
  // Add to history
  dataStore.addToHistory(measurement)

  // Navigate to details with recipe ID in URL
  const recipeId = measurement.rcp_id || measurement.recipe_name || 'unknown'
  router.push(`/result/${encodeURIComponent(recipeId)}/${measurement.group_key}`)
}

function addToGroup(measurement) {
  dataStore.addToGroup(measurement)
}

function viewTrendAnalysis() {
  router.push('/result/data_trend')
}



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

</script>
