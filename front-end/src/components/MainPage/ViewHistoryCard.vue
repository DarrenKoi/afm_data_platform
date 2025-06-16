<template>
  <v-card class="mb-4" elevation="3">
    <v-card-title>
      <v-icon start>mdi-eye</v-icon>
      View History
      <v-spacer />
      <v-btn v-if="historyCount > 0" variant="text" size="small" @click="clearHistory">
        Clear
      </v-btn>
    </v-card-title>
    <v-divider />
    
    <v-list v-if="historyCount > 0" density="compact">
      <v-list-item 
        v-for="(item, index) in viewHistory" 
        :key="index"
        @click="viewDetails(item)"
        class="cursor-pointer"
      >
        <v-list-item-title class="text-body-2">
          {{ item.formatted_date || item.date }} - {{ item.recipe_name }} - {{ item.lot_id }}
        </v-list-item-title>
        <v-list-item-subtitle class="text-caption">
          Slot: {{ item.slot_number }} | {{ item.measured_info }} | {{ new Date(item.viewedAt).toLocaleString() }}
        </v-list-item-subtitle>
      </v-list-item>
    </v-list>
    <v-card-text v-else class="text-center text-medium-emphasis">
      No view history yet
    </v-card-text>
  </v-card>
</template>

<script setup>
// Props
defineProps({
  viewHistory: {
    type: Array,
    default: () => []
  },
  historyCount: {
    type: Number,
    default: 0
  }
})

// Emits
const emit = defineEmits(['view-details', 'clear-history'])

// Functions
function viewDetails(item) {
  emit('view-details', item)
}

function clearHistory() {
  emit('clear-history')
}
</script>