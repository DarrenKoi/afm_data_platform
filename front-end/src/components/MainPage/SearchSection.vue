<template>
  <div class="px-2">
    <!-- Search Card -->
    <v-card class="pa-6 mb-4" elevation="3">
      <v-card-text>
        <v-text-field 
          v-model="realtimeSearch.searchQuery.value" 
          clearable 
          label="Search AFM measurements..."
          placeholder="Type 2+ characters to search (Fab ID, Lot ID, Tool, Recipe...)" 
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
      <v-card-title>
        <v-icon start>mdi-database-search</v-icon>
        {{ realtimeSearch.searchQuery.value ? 'Search Results' : 'Recent Measurements' }} ({{ realtimeSearch.searchResults.value.length }})
      </v-card-title>
      <v-divider />

      <v-list>
        <v-list-item v-for="(result, index) in realtimeSearch.searchResults.value" :key="index" class="border-b">
          <div>
            <v-list-item-title class="font-weight-bold">
              {{ result.fab }} - {{ result.lot_id }}
              <v-chip v-if="isInGroup(result.group_key)" size="x-small" color="success" class="ml-2">
                GROUPED
              </v-chip>
            </v-list-item-title>
            <v-list-item-subtitle class="mt-1">
              <v-chip size="small" color="primary" class="mr-2">WF: {{ result.wf_id }}</v-chip>
              <v-chip size="small" color="secondary" class="mr-2">{{ result.rcp_id }}</v-chip>
              <v-chip size="small" color="info" class="mr-2">{{ result.points?.length || 0 }} points</v-chip>
            </v-list-item-subtitle>
            <v-list-item-subtitle class="text-caption mt-1">
              {{ new Date(result.event_time).toLocaleString() }}
            </v-list-item-subtitle>
            <v-list-item-subtitle class="text-caption">
              Group Key: {{ result.group_key }}
            </v-list-item-subtitle>
          </div>

          <template v-slot:append>
            <div class="d-flex gap-2">
              <v-btn 
                variant="outlined" 
                size="small" 
                color="success"
                :disabled="isInGroup(result.group_key)"
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
    </v-card>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
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

// Watch for search results changes and emit to parent
watch(realtimeSearch.searchResults, (newResults) => {
  emit('search-performed', realtimeSearch.searchQuery.value, newResults)
}, { deep: true })

// Functions
function triggerInstantSearch() {
  if (!realtimeSearch.searchQuery.value) return
  realtimeSearch.triggerSearch(realtimeSearch.searchQuery.value)
}

function selectSuggestion(suggestion) {
  realtimeSearch.searchQuery.value = suggestion
  showSuggestions.value = false
  triggerInstantSearch()
}

function addToGroup(result) {
  emit('add-to-group', result)
}

function viewDetails(result) {
  emit('view-details', result)
}
</script>