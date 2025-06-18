<template>
  <div class="px-2">
    <!-- Search Card -->
    <v-card class="pa-6 mb-4" elevation="3">
      <v-card-text>
        <v-text-field 
          v-model="realtimeSearch.searchQuery.value" 
          clearable 
          label="Search AFM files..."
          placeholder="Search by Lot ID, Recipe, Date... (e.g., CMP, T7HQR42TA, ETCH, 250609)" 
          prepend-inner-icon="mdi-magnify"
          variant="outlined" 
          :loading="realtimeSearch.isSearching.value"
          @keyup.enter="triggerInstantSearch"
        >
          <!-- Search suggestions dropdown -->
          <template v-if="realtimeSearch.suggestions.value.length > 0" #append>
            <v-menu v-model="showSuggestions" offset-y>
              <template #activator="{ props }">
                <v-btn 
                  v-bind="props"
                  icon="mdi-chevron-down" 
                  variant="text"
                  size="small"
                  @click="showSuggestions = !showSuggestions"
                />
              </template>
              <v-list max-height="200">
                <v-list-item 
                  v-for="suggestion in realtimeSearch.suggestions.value" 
                  :key="suggestion"
                  @click="selectSuggestion(suggestion)"
                >
                  <v-list-item-title>{{ suggestion }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </template>
        </v-text-field>

        <!-- Real-time search indicator -->
        <div v-if="realtimeSearch.isSearching.value" class="text-center mt-2">
          <v-progress-linear indeterminate color="primary" height="2" />
          <p class="text-caption text-medium-emphasis mt-1">Searching...</p>
        </div>

        <!-- Search helper text -->
        <div v-if="realtimeSearch.searchQuery.value && realtimeSearch.searchQuery.value.length === 1" class="text-center mt-2">
          <p class="text-caption text-medium-emphasis">
            Type one more character to start searching...
          </p>
        </div>

        <!-- Search stats -->
        <div v-if="realtimeSearch.searchResults.value.length > 0 && realtimeSearch.searchQuery.value && realtimeSearch.searchQuery.value.length >= 2" class="text-center mt-2">
          <p class="text-caption text-medium-emphasis">
            Found {{ realtimeSearch.searchResults.value.length }} results
            <v-icon size="x-small" color="success">mdi-check-circle</v-icon>
          </p>
        </div>

        <!-- No results message -->
        <div v-if="realtimeSearch.searchResults.value.length === 0 && realtimeSearch.searchQuery.value && realtimeSearch.searchQuery.value.length >= 2 && !realtimeSearch.isSearching.value" class="text-center mt-2">
          <p class="text-caption text-medium-emphasis">
            No results found for "{{ realtimeSearch.searchQuery.value }}"
            <v-icon size="x-small" color="warning">mdi-alert-circle</v-icon>
          </p>
        </div>
      </v-card-text>
    </v-card>

    <!-- Search Results -->
    <v-card v-if="realtimeSearch.searchResults.value.length > 0" elevation="3">
      <v-card-title class="d-flex align-center">
        <v-icon start>mdi-database-search</v-icon>
        {{ realtimeSearch.searchQuery.value ? 'Search Results' : 'Recent Measurements' }} 
        ({{ filteredResults.length }}{{ filteredResults.length !== realtimeSearch.searchResults.value.length ? `/${realtimeSearch.searchResults.value.length}` : '' }})
        
        <v-spacer />
        
        <!-- Inner filter input -->
        <v-text-field
          v-model="innerFilter"
          density="compact"
          variant="outlined"
          placeholder="Filter results..."
          prepend-inner-icon="mdi-filter"
          clearable
          hide-details
          style="max-width: 300px;"
          class="ml-4"
        />
      </v-card-title>
      <v-divider />

      <!-- Results list with scrollable container -->
      <div class="results-container" :class="{ 'scrollable': filteredResults.length > maxVisibleItems }">
        <v-list>
          <v-list-item 
            v-for="(result, index) in displayedResults" 
            :key="index" 
            class="border-b"
          >
            <div class="w-100">
              <div class="d-flex flex-column">
                <div class="font-weight-bold text-body-1 mb-1">
                  📅 {{ result.formatted_date }}
                </div>
                <div class="font-weight-bold text-body-1 mb-1">
                  🔬 {{ result.recipe_name }}
                </div>
                <div class="font-weight-bold text-body-1 mb-2">
                  📦 {{ result.lot_id }}
                  <v-chip v-if="isInGroup(result.filename)" size="x-small" color="success" class="ml-2">
                    GROUPED
                  </v-chip>
                </div>
              </div>
              <v-list-item-subtitle class="mt-2">
                <v-chip size="small" color="primary" variant="outlined" class="mr-2 font-weight-medium">Slot: {{ result.slot_number }}</v-chip>
                <v-chip size="small" color="secondary" variant="outlined" class="mr-2 font-weight-medium">{{ result.measured_info }}</v-chip>
              </v-list-item-subtitle>
              <v-list-item-subtitle class="text-caption mt-1 text-grey">
                📁 {{ result.filename }}
              </v-list-item-subtitle>
            </div>

            <template v-slot:append>
              <div class="d-flex gap-2">
                <v-btn 
                  variant="outlined" 
                  size="small" 
                  color="success"
                  :disabled="isInGroup(result.filename)"
                  @click="addToGroup(result)"
                >
                  <v-icon start>mdi-plus</v-icon>
                  Add to Group
                </v-btn>
                <v-btn variant="outlined" size="small" @click="viewDetails(result)">
                  View Details
                </v-btn>
              </div>
            </template>
          </v-list-item>
        </v-list>
      </div>

      <!-- Results counter (only show when there are many results) -->
      <div v-if="filteredResults.length > maxVisibleItems" class="text-center pa-3 border-t">
        <div class="text-caption text-medium-emphasis">
          Showing {{ displayedResults.length }} results - scroll to see more
        </div>
      </div>
    </v-card>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useRealtimeSearch } from '@/composables/useSearch.js'

// Props
defineProps({
  searchResults: {
    type: Array,
    default: () => []
  },
  isSearching: {
    type: Boolean,
    default: false
  },
  isInGroup: {
    type: Function,
    default: () => false
  }
})

// Emits
const emit = defineEmits(['search-performed', 'add-to-group', 'view-details'])

// Real-time search functionality
const realtimeSearch = useRealtimeSearch()
const showSuggestions = ref(false)

// Inner filter functionality
const innerFilter = ref('')

// Results display configuration
const maxVisibleItems = ref(10) // Show 10 items initially, then scroll for more

// Computed property to filter search results
const filteredResults = computed(() => {
  if (!innerFilter.value || innerFilter.value.trim() === '') {
    return realtimeSearch.searchResults.value
  }
  
  const filterQuery = innerFilter.value.toLowerCase().trim()
  
  return realtimeSearch.searchResults.value.filter(result => {
    // Search across multiple fields
    const searchFields = [
      result.lot_id,
      result.recipe_name,
      result.formatted_date,
      result.date,
      result.slot_number?.toString(),
      result.measured_info?.toString(),
      result.filename
    ]
    
    return searchFields.some(field => 
      field && field.toString().toLowerCase().includes(filterQuery)
    )
  })
})

// Computed property for displayed results (all results with scrolling)
const displayedResults = computed(() => {
  return filteredResults.value
})

// Watch for search results changes and emit to parent
watch(realtimeSearch.searchResults, (newResults) => {
  // Clear inner filter when main search changes
  innerFilter.value = ''
  
  console.log(`🔍 SearchSection: Search results changed, emitting ${newResults.length} results`)
  console.log('📊 SearchSection: Sample result:', newResults[0])
  emit('search-performed', realtimeSearch.searchQuery.value, newResults)
}, { deep: true })

// Watch for filtered results changes and emit to parent
watch(filteredResults, (newFilteredResults) => {
  if (innerFilter.value) {
    console.log(`🔍 SearchSection: Filtered results changed, emitting ${newFilteredResults.length} results`)
    emit('search-performed', realtimeSearch.searchQuery.value, newFilteredResults)
  }
}, { deep: true })

onMounted(() => {
  console.log('🚀 SearchSection: Component mounted and ready for AFM file searches')
})

// Functions
function triggerInstantSearch() {
  console.log(`⚡ SearchSection: Triggering instant search for "${realtimeSearch.searchQuery.value}"`)
  if (!realtimeSearch.searchQuery.value) return
  realtimeSearch.triggerSearch(realtimeSearch.searchQuery.value)
}

function selectSuggestion(suggestion) {
  console.log(`💡 SearchSection: Selected suggestion "${suggestion}"`)
  realtimeSearch.searchQuery.value = suggestion
  showSuggestions.value = false
  triggerInstantSearch()
}

function addToGroup(result) {
  console.log(`➕ SearchSection: Adding to group:`, result)
  emit('add-to-group', result)
}

function viewDetails(result) {
  console.log(`👁️ SearchSection: Viewing details for:`, result)
  emit('view-details', result)
}

function toggleShowAll() {
  showAllResults.value = !showAllResults.value
  console.log(`📋 SearchSection: Toggled show all results to ${showAllResults.value}`)
}
</script>

<style scoped>
.results-container {
  transition: max-height 0.3s ease-in-out;
}

.results-container.scrollable {
  max-height: 600px;
  overflow-y: auto;
  border-radius: 4px;
}

/* Custom scrollbar styling */
.results-container.scrollable::-webkit-scrollbar {
  width: 8px;
}

.results-container.scrollable::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.results-container.scrollable::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.results-container.scrollable::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>