<template>
  <div>
    <!-- Main title card -->
    <v-card elevation="2" class="mb-4">
      <v-card-title class="bg-primary text-white">
        <v-icon start>mdi-dots-grid</v-icon>
        Detailed Measurement Points Data
      </v-card-title>
    </v-card>

    <!-- Display detailed data when available -->
    <div v-if="detailedData && detailedData.length > 0">
      <!-- Controls and filters -->
      <v-card elevation="2" class="mb-4">
        <v-card-text class="pa-4">
          <v-row align="center">
            <v-col cols="12" sm="6" md="4">
              <v-select
                v-model="selectedMeasurementPoint"
                :items="availableMeasurementPoints"
                label="Select Measurement Point"
                density="compact"
                variant="outlined"
                prepend-inner-icon="mdi-target"
                clearable
              />
            </v-col>
            
            <v-col cols="12" sm="6" md="4">
              <v-text-field
                v-model="searchFilter"
                label="Search in data"
                density="compact"
                variant="outlined"
                prepend-inner-icon="mdi-magnify"
                clearable
                placeholder="Search by Site ID, Point No, etc."
              />
            </v-col>
            
            <v-col cols="12" md="4" class="text-right">
              <v-chip 
                :color="filteredData.length > 0 ? 'primary' : 'grey'" 
                variant="outlined"
                size="large"
              >
                <v-icon start>mdi-table-row</v-icon>
                {{ filteredData.length.toLocaleString() }} rows
              </v-chip>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Data table -->
      <v-card elevation="2">
        <v-card-title class="bg-info text-white py-3">
          <v-icon start>mdi-table</v-icon>
          <span v-if="selectedMeasurementPoint">
            Point {{ selectedMeasurementPoint }} - Detailed Data
          </span>
          <span v-else>
            All Measurement Points - Detailed Data
          </span>
          <v-spacer />
          <v-btn
            v-if="filteredData.length > 0"
            icon="mdi-download"
            variant="text"
            color="white"
            @click="exportData"
            title="Export to CSV"
          />
        </v-card-title>
        
        <v-card-text class="pa-0">
          <v-data-table
            v-model:page="currentPage"
            :headers="tableHeaders"
            :items="filteredData"
            :items-per-page="itemsPerPage"
            :loading="loading"
            density="compact"
            class="measurement-points-table"
            hover
            show-current-page
          >
            <!-- Custom template for measurement point column -->
            <template v-slot:item.measurement_point="{ item }">
              <v-chip
                size="small"
                :color="getPointColor(item.measurement_point)"
                variant="outlined"
                class="font-weight-medium"
              >
                {{ item.measurement_point }}
              </v-chip>
            </template>

            <!-- Custom template for Point No column -->
            <template v-slot:item.Point_No="{ item }">
              <span class="font-weight-bold text-primary">
                {{ item['Point No'] || item.Point_No || 'N/A' }}
              </span>
            </template>

            <!-- Custom template for coordinate columns -->
            <template v-slot:item.X_um="{ item }">
              <span class="font-mono">{{ formatCoordinate(item['X (um)'] || item.X_um) }}</span>
            </template>
            
            <template v-slot:item.Y_um="{ item }">
              <span class="font-mono">{{ formatCoordinate(item['Y (um)'] || item.Y_um) }}</span>
            </template>

            <!-- Custom template for Site coordinates -->
            <template v-slot:item.Site_X="{ item }">
              <span class="font-mono">{{ formatCoordinate(item['Site X'] || item.Site_X) }}</span>
            </template>
            
            <template v-slot:item.Site_Y="{ item }">
              <span class="font-mono">{{ formatCoordinate(item['Site Y'] || item.Site_Y) }}</span>
            </template>

            <!-- Custom template for numeric values -->
            <template v-slot:item.Roughness_R="{ item }">
              <span class="font-mono">{{ formatNumericValue(item.Roughness_R || item['Roughness_R']) }}</span>
            </template>

            <template v-slot:item.pickup_count="{ item }">
              <span class="font-mono">{{ formatInteger(item.pickup_count) }}</span>
            </template>

            <template v-slot:item.Mileage="{ item }">
              <span class="font-mono">{{ formatNumericValue(item.Mileage) }}</span>
            </template>

            <!-- Custom template for Valid column -->
            <template v-slot:item.Valid="{ item }">
              <v-chip
                size="x-small"
                :color="item.Valid ? 'success' : 'error'"
                :variant="item.Valid ? 'elevated' : 'outlined'"
              >
                {{ item.Valid ? 'Valid' : 'Invalid' }}
              </v-chip>
            </template>

            <!-- Custom template for Methods ID -->
            <template v-slot:item.Methods_ID="{ item }">
              <v-chip
                size="x-small"
                color="secondary"
                variant="outlined"
              >
                {{ item['Methods ID'] || item.Methods_ID || 'N/A' }}
              </v-chip>
            </template>

            <!-- Loading template -->
            <template v-slot:loading>
              <v-skeleton-loader type="table-row@10" />
            </template>

            <!-- No data template -->
            <template v-slot:no-data>
              <v-empty-state
                icon="mdi-table-off"
                title="No measurement data found"
                text="No detailed measurement points match your current filters"
              />
            </template>
          </v-data-table>
        </v-card-text>
      </v-card>

      <!-- Summary information -->
      <v-card elevation="1" class="mt-4" variant="outlined">
        <v-card-text class="pa-3">
          <v-row>
            <v-col cols="12" sm="6" md="3">
              <v-alert density="compact" variant="tonal" color="primary">
                <div class="text-caption">Total Points</div>
                <div class="text-h6">{{ detailedData.length.toLocaleString() }}</div>
              </v-alert>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-alert density="compact" variant="tonal" color="info">
                <div class="text-caption">Measurement Points</div>
                <div class="text-h6">{{ availableMeasurementPoints.length }}</div>
              </v-alert>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-alert density="compact" variant="tonal" color="success">
                <div class="text-caption">Valid Points</div>
                <div class="text-h6">{{ validPointsCount.toLocaleString() }}</div>
              </v-alert>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-alert density="compact" variant="tonal" color="warning">
                <div class="text-caption">Data Columns</div>
                <div class="text-h6">{{ tableHeaders.length - 1 }}</div>
              </v-alert>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </div>
    
    <!-- No data message -->
    <div v-else class="text-center pa-6 text-medium-emphasis">
      <v-card elevation="2">
        <v-card-text class="pa-6">
          <v-icon size="64" class="mb-3">mdi-dots-grid</v-icon>
          <div class="text-h6 mb-2">No Detailed Measurement Data Available</div>
          <div class="text-body-2">Load measurement data to view detailed point-by-point measurements</div>
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  detailedData: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  groupKey: {
    type: String,
    default: ''
  }
})

// Emits
const emit = defineEmits(['point-selected', 'point-data-loaded'])

// Reactive data
const selectedMeasurementPoint = ref(null)
const searchFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = ref(25)

// Computed properties
const availableMeasurementPoints = computed(() => {
  if (!props.detailedData || props.detailedData.length === 0) return []
  
  const points = new Set()
  props.detailedData.forEach(item => {
    if (item.measurement_point) {
      points.add(item.measurement_point)
    }
  })
  
  return Array.from(points).sort()
})

const filteredData = computed(() => {
  let filtered = props.detailedData || []
  
  // Filter by selected measurement point
  if (selectedMeasurementPoint.value) {
    filtered = filtered.filter(item => 
      item.measurement_point === selectedMeasurementPoint.value
    )
  }
  
  // Filter by search text
  if (searchFilter.value && searchFilter.value.trim()) {
    const searchTerm = searchFilter.value.toLowerCase().trim()
    filtered = filtered.filter(item => {
      // Search in key fields
      const searchableText = [
        item['Site ID'],
        item.Site_ID,
        item['Point No'],
        item.Point_No,
        item['Methods ID'],
        item.Methods_ID,
        item.measurement_point,
        item.statd
      ].filter(val => val != null)
       .join(' ')
       .toLowerCase()
      
      return searchableText.includes(searchTerm)
    })
  }
  
  return filtered
})

const validPointsCount = computed(() => {
  if (!props.detailedData) return 0
  return props.detailedData.filter(item => item.Valid === true || item.Valid === 1).length
})

const tableHeaders = computed(() => {
  if (!props.detailedData || props.detailedData.length === 0) {
    return []
  }
  
  const sampleItem = props.detailedData[0]
  const headers = []
  
  // Always include measurement point first
  headers.push({
    title: 'Point',
    key: 'measurement_point',
    align: 'start',
    sortable: true,
    width: '100px'
  })
  
  // Define preferred column order and formatting
  const columnConfig = {
    'Point No': { title: 'Point No', key: 'Point_No', align: 'center', width: '90px' },
    'Point_No': { title: 'Point No', key: 'Point_No', align: 'center', width: '90px' },
    'Site ID': { title: 'Site ID', key: 'Site_ID', align: 'center', width: '80px' },
    'Site_ID': { title: 'Site ID', key: 'Site_ID', align: 'center', width: '80px' },
    'Site X': { title: 'Site X', key: 'Site_X', align: 'end', width: '100px' },
    'Site_X': { title: 'Site X', key: 'Site_X', align: 'end', width: '100px' },
    'Site Y': { title: 'Site Y', key: 'Site_Y', align: 'end', width: '100px' },
    'Site_Y': { title: 'Site Y', key: 'Site_Y', align: 'end', width: '100px' },
    'X (um)': { title: 'X (μm)', key: 'X_um', align: 'end', width: '100px' },
    'X_um': { title: 'X (μm)', key: 'X_um', align: 'end', width: '100px' },
    'Y (um)': { title: 'Y (μm)', key: 'Y_um', align: 'end', width: '100px' },
    'Y_um': { title: 'Y (μm)', key: 'Y_um', align: 'end', width: '100px' },
    'Methods ID': { title: 'Method', key: 'Methods_ID', align: 'center', width: '80px' },
    'Methods_ID': { title: 'Method', key: 'Methods_ID', align: 'center', width: '80px' },
    'Valid': { title: 'Valid', key: 'Valid', align: 'center', width: '80px' },
    'statd': { title: 'Status', key: 'statd', align: 'center', width: '80px' },
    'Roughness_R': { title: 'Roughness R', key: 'Roughness_R', align: 'end', width: '120px' },
    'pickup_count': { title: 'Pickup Count', key: 'pickup_count', align: 'end', width: '110px' },
    'Mileage': { title: 'Mileage', key: 'Mileage', align: 'end', width: '100px' }
  }
  
  // Add configured columns that exist in the data
  Object.keys(sampleItem).forEach(key => {
    if (key !== 'measurement_point' && key !== 'index') {
      const config = columnConfig[key]
      if (config) {
        headers.push({
          title: config.title,
          key: config.key,
          align: config.align,
          sortable: true,
          width: config.width
        })
      } else {
        // Add other columns with default formatting
        headers.push({
          title: key.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim(),
          key: key,
          align: typeof sampleItem[key] === 'number' ? 'end' : 'start',
          sortable: true,
          width: '120px'
        })
      }
    }
  })
  
  return headers
})

// Methods
function formatCoordinate(value) {
  if (value == null || value === undefined || value === '') return 'N/A'
  if (typeof value === 'number') {
    return value.toFixed(2)
  }
  return value.toString()
}

function formatNumericValue(value) {
  if (value == null || value === undefined || value === '') return 'N/A'
  if (typeof value === 'number') {
    if (Math.abs(value) >= 1000) {
      return value.toFixed(1)
    } else if (Math.abs(value) >= 1) {
      return value.toFixed(3)
    } else {
      return value.toFixed(4)
    }
  }
  return value.toString()
}

function formatInteger(value) {
  if (value == null || value === undefined || value === '') return 'N/A'
  if (typeof value === 'number') {
    return Math.round(value).toLocaleString()
  }
  return value.toString()
}

function getPointColor(pointName) {
  if (!pointName) return 'grey'
  
  const colorMap = {
    '1_UL': 'primary',
    '2_UL': 'success', 
    '3_UL': 'warning',
    '4_UL': 'error',
    '5_UL': 'info',
    '1_LL': 'purple',
    '2_LL': 'orange',
    '3_LL': 'cyan',
    '4_LL': 'pink',
    '5_LL': 'indigo'
  }
  
  return colorMap[pointName] || 'secondary'
}

function exportData() {
  if (!filteredData.value || filteredData.value.length === 0) return
  
  // Create CSV content
  const headers = tableHeaders.value.map(h => h.title).join(',')
  const rows = filteredData.value.map(item => 
    tableHeaders.value.map(header => {
      const value = item[header.key]
      if (value == null || value === undefined) return ''
      return typeof value === 'string' && value.includes(',') ? `"${value}"` : value
    }).join(',')
  ).join('\n')
  
  const csvContent = headers + '\n' + rows
  
  // Download CSV
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `measurement_points_${selectedMeasurementPoint.value || 'all'}_${new Date().toISOString().split('T')[0]}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

// Watch for measurement point selection changes
watch(selectedMeasurementPoint, (newPoint, oldPoint) => {
  if (newPoint && newPoint !== oldPoint) {
    console.log(`🎯 [MeasurementPoints] Selected point changed to:`, newPoint)
    
    // Extract point number from measurement point name (e.g., "1_UL" -> "1")
    const pointNumber = extractPointNumber(newPoint)
    
    // Emit point selection event
    emit('point-selected', {
      measurementPoint: newPoint,
      pointNumber: pointNumber,
      groupKey: props.groupKey
    })
  }
})

// Watch for data changes and auto-select first measurement point
watch(() => props.detailedData, (newData) => {
  console.log(`🔍 [MeasurementPoints] Received detailed data:`)
  console.log(`🔍 [MeasurementPoints] Length:`, newData?.length || 0)
  
  if (newData && newData.length > 0) {
    console.log(`🔍 [MeasurementPoints] First record:`, newData[0])
    console.log(`🔍 [MeasurementPoints] Available measurement points:`, availableMeasurementPoints.value)
    
    // Auto-select first measurement point if none selected
    if (!selectedMeasurementPoint.value && availableMeasurementPoints.value.length > 0) {
      selectedMeasurementPoint.value = availableMeasurementPoints.value[0]
      console.log(`🔍 [MeasurementPoints] Auto-selected point:`, selectedMeasurementPoint.value)
    }
    
    // Emit data loaded event
    emit('point-data-loaded', {
      totalPoints: newData.length,
      availablePoints: availableMeasurementPoints.value,
      groupKey: props.groupKey
    })
  }
}, { immediate: true })

// Helper function to extract point number from measurement point name
function extractPointNumber(measurementPoint) {
  if (!measurementPoint) return null
  
  // Extract first number from measurement point (e.g., "1_UL" -> "1", "2_LL" -> "2")
  const match = measurementPoint.match(/^(\d+)/)
  return match ? parseInt(match[1]) : null
}
</script>

<style scoped>
.measurement-points-table {
  border: none;
}

.measurement-points-table :deep(.v-data-table__tr:hover) {
  background-color: rgba(var(--v-theme-primary), 0.08);
}

.measurement-points-table :deep(.v-data-table-header) {
  background-color: rgba(var(--v-theme-surface), 0.8);
}

.measurement-points-table :deep(.v-data-table__th) {
  font-weight: 600;
  font-size: 0.875rem;
  padding: 8px 12px;
  border-bottom: 2px solid rgba(var(--v-theme-outline), 0.2);
}

.measurement-points-table :deep(.v-data-table__td) {
  padding: 8px 12px;
  font-size: 0.9rem;
  border-bottom: 1px solid rgba(var(--v-theme-outline), 0.1);
}

.font-mono {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  font-weight: 500;
}

.v-chip {
  font-weight: 600;
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .measurement-points-table :deep(.v-data-table__th),
  .measurement-points-table :deep(.v-data-table__td) {
    padding: 6px 8px;
    font-size: 0.8rem;
  }
  
  .font-mono {
    font-size: 0.8rem;
  }
}
</style>