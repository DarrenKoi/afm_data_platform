<template>
  <v-card class="h-100" elevation="2">
    <v-card-title class="bg-primary text-white py-2 text-subtitle-1">
      <v-icon start size="small">mdi-information</v-icon>
      Information
    </v-card-title>
    <v-card-text class="pa-3">
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
              class="info-value"
              :class="[getValueClass(entry.key, index), props.compact ? 'text-body-2' : 'text-h6']"
            >
              {{ formatValue(entry.value, entry.key) }}
            </div>
          </div>
        </v-col>
      </v-row>
      
      <!-- Measurement Point Selection -->
      <div v-if="measurementPoints && measurementPoints.length > 0" class="mt-4 pt-3 border-t">
        <div class="text-subtitle-2 mb-2">
          <v-icon start size="small">mdi-target</v-icon>
          Select Measurement Point
        </div>
        <v-chip-group
          v-model="selectedChipIndex"
          mandatory
          selected-class="v-chip--selected"
        >
          <v-chip
            v-for="(point, index) in sortedMeasurementPoints"
            :key="point.point"
            :value="index"
            color="primary"
            variant="outlined"
            size="default"
            @click="$emit('point-selected', point.point)"
            :class="{ 'v-chip--selected': selectedPoint === point.point }"
            class="measurement-point-chip"
          >
            {{ point.point }}
          </v-chip>
        </v-chip-group>
      </div>
      
      <!-- Fallback message when no data -->
      <div v-else-if="informationEntries.length === 0" class="text-center pa-6 text-medium-emphasis">
        <v-icon size="48" class="mb-3">mdi-information-outline</v-icon>
        <div class="text-h6 mb-2">No Measurement Information Available</div>
        <div class="text-body-2">Load measurement data to view detailed information</div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

// Props
const props = defineProps({
  measurementInfo: {
    type: Object,
    default: () => ({})
  },
  compact: {
    type: Boolean,
    default: false
  },
  measurementPoints: {
    type: Array,
    default: () => []
  },
  selectedPoint: {
    type: String,
    default: null
  }
})

// Emits
defineEmits(['point-selected'])

// Local state
const selectedChipIndex = ref(0)

// Computed property to sort measurement points alphabetically
const sortedMeasurementPoints = computed(() => {
  if (!props.measurementPoints || props.measurementPoints.length === 0) {
    return []
  }
  
  return [...props.measurementPoints].sort((a, b) => {
    const pointA = (a.point || a).toString().toLowerCase()
    const pointB = (b.point || b).toString().toLowerCase()
    return pointA.localeCompare(pointB)
  })
})

// Watch for selected point changes to update chip selection
watch(() => props.selectedPoint, (newPoint) => {
  if (newPoint) {
    const index = sortedMeasurementPoints.value.findIndex(p => p.point === newPoint)
    if (index >= 0) {
      selectedChipIndex.value = index
    }
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
  font-size: 0.75rem;
  font-weight: 600;
  color: rgba(var(--v-theme-on-surface), 0.8);
  margin-bottom: 2px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-weight: 600;
  word-break: break-word;
}

.border-t {
  border-top: 1px solid rgba(var(--v-theme-outline), 0.12);
}

.v-chip-group {
  gap: 8px;
}

.v-chip--selected {
  background-color: rgb(var(--v-theme-primary)) !important;
  color: white !important;
}

.measurement-point-chip {
  height: 36px !important;
  padding: 0 16px !important;
  font-size: 0.875rem !important;
  font-weight: 600 !important;
  margin: 4px 8px 4px 0 !important;
}
</style>