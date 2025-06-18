<template>
  <v-card class="h-100" elevation="2">
    <v-card-title class="bg-primary text-white">
      <v-icon start>mdi-information</v-icon>
      Measurement Information
    </v-card-title>
    <v-card-text class="pa-6">
      <!-- Dynamic grid layout for any number of key-value pairs -->
      <v-row v-if="informationEntries.length > 0">
        <v-col 
          v-for="(entry, index) in informationEntries" 
          :key="entry.key"
          :cols="getColumnSize(informationEntries.length)"
          :md="getMdColumnSize(informationEntries.length)"
        >
          <div class="info-item">
            <div class="info-label">{{ formatLabel(entry.key) }}</div>
            <div 
              class="info-value text-h6"
              :class="getValueClass(entry.key, index)"
            >
              {{ formatValue(entry.value, entry.key) }}
            </div>
          </div>
        </v-col>
      </v-row>
      
      <!-- Fallback message when no data -->
      <div v-else class="text-center pa-6 text-medium-emphasis">
        <v-icon size="48" class="mb-3">mdi-information-outline</v-icon>
        <div class="text-h6 mb-2">No Measurement Information Available</div>
        <div class="text-body-2">Load measurement data to view detailed information</div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

// Props
const props = defineProps({
  measurementInfo: {
    type: Object,
    default: () => ({})
  }
})

// Computed property to convert measurementInfo object to array of entries
const informationEntries = computed(() => {
  if (!props.measurementInfo || typeof props.measurementInfo !== 'object') {
    return []
  }
  
  return Object.entries(props.measurementInfo)
    .filter(([key, value]) => value !== null && value !== undefined && value !== '')
    .map(([key, value]) => ({ key, value }))
})

// Functions
function formatLabel(key) {
  // Convert snake_case and camelCase to Title Case
  return key
    .replace(/[_-]/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}

function formatValue(value, key) {
  if (value === null || value === undefined) return 'N/A'
  
  // Special formatting for specific key types
  const lowerKey = key.toLowerCase()
  
  if (lowerKey.includes('time') || lowerKey.includes('date')) {
    try {
      return new Date(value).toLocaleString()
    } catch (error) {
      return value.toString()
    }
  }
  
  if (typeof value === 'number') {
    // Format numbers with appropriate precision
    if (Number.isInteger(value)) {
      return value.toLocaleString()
    } else {
      return value.toFixed(3)
    }
  }
  
  return value.toString()
}

function getColumnSize(totalItems) {
  // Responsive column sizing based on number of items
  if (totalItems <= 2) return 12
  if (totalItems <= 4) return 6
  if (totalItems <= 6) return 4
  return 3
}

function getMdColumnSize(totalItems) {
  // Medium screen column sizing
  if (totalItems <= 1) return 12
  if (totalItems <= 2) return 6
  if (totalItems <= 3) return 4
  if (totalItems <= 6) return 4
  return 3
}

function getValueClass(key, index) {
  // Assign different colors to values for visual distinction
  const colorClasses = [
    'text-primary',
    'text-success', 
    'text-info',
    'text-warning',
    'text-secondary',
    'text-purple'
  ]
  
  // Special colors for common keys
  const lowerKey = key.toLowerCase()
  if (lowerKey.includes('id')) return 'text-primary'
  if (lowerKey.includes('time') || lowerKey.includes('date')) return 'text-info'
  if (lowerKey.includes('recipe')) return 'text-warning'
  if (lowerKey.includes('lot')) return 'text-success'
  
  // Default cycling through colors
  return colorClasses[index % colorClasses.length]
}
</script>

<style scoped>
.info-item {
  margin-bottom: 8px;
}

.info-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: rgba(var(--v-theme-on-surface), 0.8);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-weight: 600;
  word-break: break-word;
}
</style>