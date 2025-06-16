<template>
  <v-card elevation="2">
    <v-card-title class="bg-info text-white">
      <v-icon start>mdi-chart-box-outline</v-icon>
      Statistical Information by Measurement Points
    </v-card-title>
    <v-card-text class="pa-4">
      <v-row v-if="Object.keys(statisticsData).length > 0">
        <v-col 
          v-for="(pointData, pointKey) in statisticsData" 
          :key="pointKey"
          cols="12" 
          md="6" 
          lg="4"
        >
          <v-card 
            variant="outlined" 
            class="point-card h-100"
            :class="`point-${pointKey.toLowerCase().replace('_', '-')}`"
          >
            <v-card-title class="bg-surface-variant">
              <v-icon start color="primary">mdi-target</v-icon>
              <span class="text-h6">{{ pointKey }}</span>
            </v-card-title>
            <v-card-text class="pa-3">
              <v-simple-table density="compact" class="point-stats-table">
                <thead>
                  <tr>
                    <th class="text-left">Parameter</th>
                    <th class="text-left">Statistic</th>
                    <th class="text-right">Value</th>
                  </tr>
                </thead>
                <tbody>
                  <template v-for="(paramValues, paramName) in getParameterData(pointData)" :key="paramName">
                    <tr v-for="(statValue, statIndex) in paramValues" :key="`${paramName}-${statIndex}`">
                      <td class="font-weight-medium">{{ paramName }}</td>
                      <td class="text-caption">{{ getStatisticName(statIndex, pointData.ITEM) }}</td>
                      <td class="text-right font-mono">
                        <v-chip 
                          size="x-small" 
                          :color="getStatisticColor(getStatisticName(statIndex, pointData.ITEM))"
                          variant="outlined"
                        >
                          {{ formatValue(statValue, getStatisticName(statIndex, pointData.ITEM)) }}
                        </v-chip>
                      </td>
                    </tr>
                  </template>
                </tbody>
              </v-simple-table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      
      <!-- No data message -->
      <div v-else class="text-center pa-6 text-medium-emphasis">
        <v-icon size="64" class="mb-3">mdi-chart-line-variant</v-icon>
        <div class="text-h6 mb-2">No Statistical Data Available</div>
        <div class="text-body-2">Load measurement data to view point-by-point statistics</div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed, watch } from 'vue'

const props = defineProps({
  statisticsData: {
    type: Object,
    default: () => ({})
  }
})

// Watch for data changes
watch(() => props.statisticsData, (newData) => {
  console.log('StatisticalInfoByPoints received data:', Object.keys(newData || {}))
}, { immediate: true })

// Get parameter data excluding 'ITEM' key
function getParameterData(pointData) {
  if (!pointData || typeof pointData !== 'object') return {}
  
  const { ITEM, ...parameters } = pointData
  return parameters
}

// Get statistic name by index
function getStatisticName(index, items) {
  if (!items || !Array.isArray(items) || index >= items.length) {
    return `Stat ${index + 1}`
  }
  return items[index]
}

// Format values based on statistic type
function formatValue(value, statisticName) {
  if (value == null) return 'N/A'
  
  if (typeof value === 'number') {
    // Format based on statistic type
    if (statisticName === 'COUNT' || statisticName === 'CNT') {
      return value.toLocaleString()
    }
    // Most AFM measurements are in nm scale
    return value.toFixed(3)
  }
  
  return value.toString()
}

// Get color for different statistics
function getStatisticColor(statisticName) {
  const colorMap = {
    'MEAN': 'primary',
    'AVERAGE': 'primary',
    'AVG': 'primary',
    'STDEV': 'warning',
    'STD': 'warning',
    'STDDEV': 'warning',
    'MIN': 'success',
    'MINIMUM': 'success',
    'MAX': 'error',
    'MAXIMUM': 'error',
    'RANGE': 'info',
    'COUNT': 'secondary',
    'CNT': 'secondary',
    'MEDIAN': 'purple',
    'RMS': 'orange'
  }
  
  const upperStat = statisticName?.toUpperCase()
  return colorMap[upperStat] || 'grey'
}
</script>

<style scoped>
.point-card {
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.point-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.point-1-ul {
  border-left-color: #1976d2;
}

.point-2-ul {
  border-left-color: #388e3c;
}

.point-3-ul {
  border-left-color: #f57c00;
}

.point-4-ul {
  border-left-color: #7b1fa2;
}

.point-5-ul {
  border-left-color: #d32f2f;
}

.point-stats-table {
  font-size: 0.875rem;
}

.point-stats-table th {
  font-weight: 600;
  background-color: rgba(var(--v-theme-surface-variant), 0.3);
  padding: 8px 12px;
}

.point-stats-table td {
  padding: 6px 12px;
  border-bottom: 1px solid rgba(var(--v-theme-outline), 0.12);
}

.font-mono {
  font-family: 'Courier New', monospace;
}

.v-chip.v-chip--size-x-small {
  font-size: 0.7rem;
  height: 20px;
  min-width: 60px;
}

/* Custom colors for different measurement points */
.point-1-ul .v-card-title {
  background-color: rgba(25, 118, 210, 0.1);
  color: #1976d2;
}

.point-2-ul .v-card-title {
  background-color: rgba(56, 142, 60, 0.1);
  color: #388e3c;
}

.point-3-ul .v-card-title {
  background-color: rgba(245, 124, 0, 0.1);
  color: #f57c00;
}

.point-4-ul .v-card-title {
  background-color: rgba(123, 31, 162, 0.1);
  color: #7b1fa2;
}

.point-5-ul .v-card-title {
  background-color: rgba(211, 47, 47, 0.1);
  color: #d32f2f;
}
</style>