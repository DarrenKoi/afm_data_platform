<template>
  <v-card class="mb-4" elevation="3">
    <v-card-title>
      <v-icon start>mdi-group</v-icon>
      Data Grouping ({{ groupedCount }})
      <v-spacer />
      <v-btn v-if="groupedCount > 0" variant="text" size="small" @click="clearGroup">
        Clear All
      </v-btn>
    </v-card-title>
    <v-divider />
    
    <v-list v-if="groupedCount > 0" density="compact">
      <v-list-item v-for="(item, index) in sortedGroupedData" :key="index">
        <v-list-item-title class="text-body-2">
          {{ item.formatted_date || item.date }} - {{ item.recipe_name }} - {{ item.lot_id }}
        </v-list-item-title>
        <v-list-item-subtitle class="text-caption">
          Slot: {{ item.slot_number }} | {{ item.measured_info }}
        </v-list-item-subtitle>
        
        <template v-slot:append>
          <v-btn variant="text" size="small" @click="removeFromGroup(item.filename)">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </template>
      </v-list-item>
    </v-list>
    
    <v-card-text v-else class="text-center text-medium-emphasis">
      No grouped data yet
    </v-card-text>

    <v-card-actions v-if="groupedCount > 0">
      <v-btn color="primary" @click="viewTrendAnalysis">
        <v-icon start>mdi-chart-line</v-icon>
        See Together
      </v-btn>
      <v-btn v-if="groupedCount > 1" color="secondary" variant="outlined" @click="saveCurrentGroup">
        <v-icon start>mdi-content-save</v-icon>
        Save Group
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

// Props
const props = defineProps({
  groupedData: {
    type: Array,
    default: () => []
  },
  groupedCount: {
    type: Number,
    default: 0
  }
})

// Computed property to sort grouped data by date (latest to oldest)
const sortedGroupedData = computed(() => {
  return [...props.groupedData].sort((a, b) => {
    // Sort by addedAt timestamp first (newest first), then by formatted_date as fallback
    const dateA = new Date(a.addedAt || a.formatted_date || a.date)
    const dateB = new Date(b.addedAt || b.formatted_date || b.date)
    return dateB - dateA // Latest first (descending order)
  })
})

// Emits
const emit = defineEmits(['remove-from-group', 'clear-group', 'view-trend-analysis', 'save-current-group'])

// Functions
function removeFromGroup(groupKey) {
  emit('remove-from-group', groupKey)
}

function clearGroup() {
  emit('clear-group')
}

function viewTrendAnalysis() {
  emit('view-trend-analysis')
}

function saveCurrentGroup() {
  emit('save-current-group')
}
</script>