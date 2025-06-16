<template>
  <v-card class="h-100" elevation="2">
    <v-card-title class="bg-success text-white">
      <v-icon start>mdi-table</v-icon>
      Statistical Information
    </v-card-title>
    <v-card-text class="pa-2">
      <v-data-table
        v-if="statisticsTable.length > 0"
        :headers="tableHeaders"
        :items="statisticsTable"
        :items-per-page="10"
        density="compact"
        class="statistics-table"
        hide-default-footer
      >
        <!-- Custom statistic name column -->
        <template v-slot:item.statistic="{ item }">
          <div class="font-weight-bold text-primary">
            {{ item.statistic }}
          </div>
        </template>
        
        <!-- Custom value columns for each measurement parameter -->
        <template v-for="param in measurementParameters" :key="param" v-slot:[`item.${param}`]="{ item }">
          <div class="parameter-values">
            <div v-for="(point, pointKey) in item[param]" :key="pointKey" class="value-chip">
              <v-chip size="x-small" :color="getValueColor(item.statistic)" variant="outlined">
                <span class="point-label">{{ pointKey }}:</span>
                <span class="point-value">{{ formatValue(point, item.statistic) }}</span>
              </v-chip>
            </div>
          </div>
        </template>
      </v-data-table>
      
      <!-- Fallback: show basic statistics from profile data if no table data -->
      <div v-else-if="profileData && profileData.length > 0" class="fallback-stats">
        <v-simple-table density="compact">
          <thead>
            <tr>
              <th>Statistic</th>
              <th>Value</th>
              <th>Unit</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="font-weight-bold">Mean</td>
              <td>{{ statistics.mean?.toFixed(4) || 'N/A' }}</td>
              <td>nm</td>
            </tr>
            <tr>
              <td class="font-weight-bold">Std Dev</td>
              <td>{{ statistics.std?.toFixed(4) || 'N/A' }}</td>
              <td>nm</td>
            </tr>
            <tr>
              <td class="font-weight-bold">Min</td>
              <td>{{ statistics.min?.toFixed(4) || 'N/A' }}</td>
              <td>nm</td>
            </tr>
            <tr>
              <td class="font-weight-bold">Max</td>
              <td>{{ statistics.max?.toFixed(4) || 'N/A' }}</td>
              <td>nm</td>
            </tr>
            <tr>
              <td class="font-weight-bold">Count</td>
              <td>{{ statistics.count?.toLocaleString() || '0' }}</td>
              <td>points</td>
            </tr>
          </tbody>
        </v-simple-table>
      </div>
      
      <!-- No data available -->
      <div v-else class="text-center pa-4 text-medium-emphasis">
        <v-icon size="48" class="mb-2">mdi-chart-line</v-icon>
        <div>No statistical data available</div>
        <div class="text-caption">Load measurement data to view statistics</div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed, watch } from 'vue'

const props = defineProps({
  profileData: {
    type: Array,
    default: () => []
  },
  statisticsTable: {
    type: Array,
    default: () => []
  }
})

// Debug: Watch for data changes
watch(() => props.profileData, (newData) => {
  console.log('StatisticalInfo received profileData:', newData?.length || 0, 'points')
}, { immediate: true })

watch(() => props.statisticsTable, (newData) => {
  console.log('StatisticalInfo received statisticsTable:', newData?.length || 0, 'rows')
}, { immediate: true })

// Computed properties for table structure
const measurementParameters = computed(() => {
  if (!props.statisticsTable || props.statisticsTable.length === 0) return []
  
  // Get all parameter keys (excluding 'statistic')
  const firstRow = props.statisticsTable[0]
  return Object.keys(firstRow).filter(key => key !== 'statistic')
})

const tableHeaders = computed(() => {
  const headers = [
    { title: 'Statistic', key: 'statistic', width: '150px', sortable: false }
  ]
  
  // Add headers for each measurement parameter
  measurementParameters.value.forEach(param => {
    headers.push({
      title: param.replace('_', ' '),
      key: param,
      sortable: false,
      width: '200px'
    })
  })
  
  return headers
})

// Fallback statistics calculation from profile data
const statistics = computed(() => {
  if (!props.profileData || props.profileData.length === 0) {
    return {
      mean: null,
      std: null,
      min: null,
      max: null,
      count: 0,
      range: null,
      median: null,
      rms: null
    }
  }

  const zValues = props.profileData.map(point => point.z)
  const count = zValues.length
  
  // Calculate basic statistics
  const min = Math.min(...zValues)
  const max = Math.max(...zValues)
  const range = max - min
  
  // Calculate mean
  const mean = zValues.reduce((sum, val) => sum + val, 0) / count
  
  // Calculate standard deviation
  const variance = zValues.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / count
  const std = Math.sqrt(variance)
  
  // Calculate median
  const sortedValues = [...zValues].sort((a, b) => a - b)
  const median = count % 2 === 0 
    ? (sortedValues[count / 2 - 1] + sortedValues[count / 2]) / 2
    : sortedValues[Math.floor(count / 2)]
  
  // Calculate RMS (Root Mean Square)
  const rms = Math.sqrt(zValues.reduce((sum, val) => sum + val * val, 0) / count)
  
  return {
    mean,
    std,
    min,
    max,
    count,
    range,
    median,
    rms
  }
})

// Helper functions
function formatValue(value, statistic) {
  if (value == null) return 'N/A'
  
  // Format numeric values based on statistic type
  if (typeof value === 'number') {
    if (statistic === 'COUNT') {
      return value.toLocaleString()
    }
    return value.toFixed(4)
  }
  
  return value.toString()
}

function getValueColor(statistic) {
  const colorMap = {
    'MEAN': 'primary',
    'STDEV': 'warning', 
    'MIN': 'success',
    'MAX': 'error',
    'RANGE': 'info'
  }
  return colorMap[statistic] || 'secondary'
}
</script>

<style scoped>
.statistics-table {
  font-size: 0.875rem;
}

.statistics-table :deep(.v-data-table__th) {
  font-weight: 600;
  font-size: 0.8rem;
  padding: 8px 12px;
}

.statistics-table :deep(.v-data-table__td) {
  padding: 8px 12px;
  vertical-align: top;
}

.parameter-values {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 180px;
}

.value-chip {
  margin-bottom: 2px;
}

.value-chip .v-chip {
  height: 20px;
  font-size: 0.7rem;
  min-width: 80px;
}

.point-label {
  font-weight: 600;
  margin-right: 4px;
}

.point-value {
  font-family: monospace;
}

.fallback-stats {
  max-height: 300px;
  overflow-y: auto;
}

.fallback-stats .v-table {
  font-size: 0.875rem;
}

.fallback-stats th {
  font-weight: 600;
  background-color: rgba(var(--v-theme-surface-variant), 0.5);
}

.fallback-stats td {
  padding: 8px 12px;
}
</style>