<template>
  <div>
    <!-- Main title card -->
    <v-card elevation="2" class="mb-4">
      <v-card-title class="bg-info text-white">
        <v-icon start>mdi-chart-box-outline</v-icon>
        Statistical Information by Measurement Points
      </v-card-title>
    </v-card>

    <!-- Display statistics when summary data is available -->
    <div v-if="summaryData && summaryData.length > 0">
      <!-- Tabs for different views -->
      <v-card elevation="2">
        <v-tabs v-model="activeTab" bg-color="primary" slider-color="white">
          <v-tab value="table">
            <v-icon start>mdi-table</v-icon>
            Data Table
          </v-tab>
          <v-tab value="chart">
            <v-icon start>mdi-scatter-plot</v-icon>
            Scatter Chart
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <!-- Data Table Tab -->
          <v-window-item value="table">
            <v-card-text class="pa-4">
              <!-- Create separate cards for each measurement point -->
              <v-row>
                <v-col 
                  v-for="(pointData, pointName) in groupedByMeasurementPoints" 
                  :key="pointName"
                  cols="12" 
                  sm="6" 
                  md="3" 
                  lg="3"
                >
                  <v-card elevation="3" class="measurement-point-card">
                    <!-- Point header -->
                    <v-card-title class="bg-primary text-white">
                      <v-icon start>mdi-target</v-icon>
                      {{ pointName }}
                    </v-card-title>
                    
                    <!-- Statistics table for this point -->
                    <v-card-text class="pa-3">
                      <v-data-table
                        :headers="pointTableHeaders"
                        :items="pointData"
                        item-value="ITEM"
                        density="compact"
                        class="statistics-table"
                        hover
                        hide-default-footer
                        @click:row="(event, { item }) => handleRowClick(event, { item }, pointName)"
                      >
                        <!-- Custom template for statistic name column -->
                        <template v-slot:item.ITEM="{ item }">
                          <v-chip
                            size="small"
                            :color="getStatisticColor(item.ITEM)"
                            variant="outlined"
                            class="font-weight-medium"
                          >
                            {{ item.ITEM }}
                          </v-chip>
                        </template>

                        <!-- Custom template for value columns -->
                        <template v-for="header in valueHeaders" :key="header.key" v-slot:[`item.${header.key}`]="{ item }">
                          <span class="font-mono">{{ formatValue(item[header.key], item.ITEM) }}</span>
                        </template>
                      </v-data-table>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>

              <!-- Information about clickable rows -->
              <v-alert
                type="info"
                variant="tonal"
                density="compact"
                class="mt-4"
                prepend-icon="mdi-information"
              >
                Click on any row in the cards to view detailed measurement data for that statistic
              </v-alert>
            </v-card-text>
          </v-window-item>

          <!-- Scatter Chart Tab -->
          <v-window-item value="chart">
            <v-card-text class="pa-4">
              <!-- Chart Controls -->
              <v-row class="mb-4">
                <v-col cols="12" md="8">
                  <v-card variant="outlined">
                    <v-card-title class="text-subtitle-1">Chart Controls</v-card-title>
                    <v-card-text>
                      <v-row>
                        <v-col cols="12" sm="6" md="4">
                          <v-select
                            v-model="selectedStatistic"
                            :items="availableStatistics"
                            label="Statistic Type"
                            density="compact"
                            variant="outlined"
                          />
                        </v-col>
                        <v-col cols="12" sm="6" md="8">
                          <v-select
                            v-model="selectedMeasurements"
                            :items="availableMeasurements"
                            label="Measurements to Show"
                            multiple
                            chips
                            density="compact"
                            variant="outlined"
                          />
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>

              <!-- Chart Container -->
              <v-card variant="outlined">
                <v-card-text>
                  <div ref="chartContainer" style="width: 100%; height: 500px;"></div>
                </v-card-text>
              </v-card>
            </v-card-text>
          </v-window-item>
        </v-window>
      </v-card>
    </div>
    
    <!-- No data message -->
    <div v-else class="text-center pa-6 text-medium-emphasis">
      <v-card elevation="2">
        <v-card-text class="pa-6">
          <v-icon size="64" class="mb-3">mdi-chart-line-variant</v-icon>
          <div class="text-h6 mb-2">No Statistical Data Available</div>
          <div class="text-body-2">Load measurement data to view point-by-point statistics</div>
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script setup>
import { computed, watch, ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  summaryData: {
    type: Array,
    default: () => []
  }
})

// Emits for row click events
const emit = defineEmits(['row-click', 'statistic-selected'])

// Tab and chart management
const activeTab = ref('table')
const chartContainer = ref(null)
const chartInstance = ref(null)

// Chart controls
const selectedStatistic = ref('MEAN')
const selectedMeasurements = ref(['Left_H (nm)', 'Right_H (nm)', 'Ref_H (nm)'])

// Available options for controls
const availableStatistics = ref(['MEAN', 'STDEV', 'MIN', 'MAX', 'RANGE'])
const availableMeasurements = computed(() => {
  if (!props.summaryData || props.summaryData.length === 0) return []
  
  const firstRecord = props.summaryData[0]
  const allKeys = Object.keys(firstRecord)
  
  return allKeys.filter(key => 
    key !== 'ITEM' && 
    (key.includes('(') || key.includes('nm') || key.includes('_H'))
  )
})

// Watch for data changes
watch(() => props.summaryData, (newData) => {
  console.log(`🏁 [StatisticalInfoByPoints] Received summary data:`)
  console.log(`🏁 [StatisticalInfoByPoints] Type:`, typeof newData)
  console.log(`🏁 [StatisticalInfoByPoints] Is Array:`, Array.isArray(newData))
  console.log(`🏁 [StatisticalInfoByPoints] Length:`, newData?.length || 0)
  console.log(`🏁 [StatisticalInfoByPoints] Full data:`, newData)
  
  if (newData && newData.length > 0) {
    console.log(`🏁 [StatisticalInfoByPoints] First record:`, newData[0])
    console.log(`🏁 [StatisticalInfoByPoints] First record keys:`, Object.keys(newData[0]))
    console.log(`🏁 [StatisticalInfoByPoints] Has ITEM field:`, 'ITEM' in newData[0])
  } else {
    console.warn(`⚠️ [StatisticalInfoByPoints] No valid summary data received`)
  }
}, { immediate: true })

// Computed property to group data by measurement points
const groupedByMeasurementPoints = computed(() => {
  console.log(`🔧 [StatisticalInfoByPoints] Computing grouped data...`)
  console.log(`🔧 [StatisticalInfoByPoints] Props summaryData:`, props.summaryData)
  
  if (!props.summaryData || props.summaryData.length === 0) {
    console.log(`🔧 [StatisticalInfoByPoints] No summary data, returning empty groups`)
    return {}
  }
  
  const firstRecord = props.summaryData[0]
  console.log(`🔧 [StatisticalInfoByPoints] First record for grouping:`, firstRecord)
  console.log(`🔧 [StatisticalInfoByPoints] First record keys:`, Object.keys(firstRecord))
  
  const grouped = {}
  
  // Get all keys except ITEM to find measurement points
  const allKeys = Object.keys(firstRecord)
  const measurementPointKeys = allKeys.filter(key => key !== 'ITEM')
  
  console.log(`🔧 [StatisticalInfoByPoints] Measurement point keys:`, measurementPointKeys)
  
  // Find which keys represent measurement points (like "1_UL", "2_UL") vs value columns (like "Left_H (nm)")
  const pointKeys = measurementPointKeys.filter(key => 
    key.includes('_UL') || key.includes('_LL') || key.includes('_UR') || key.includes('_LR') || 
    key.includes('_C') || key.match(/^\d+_/)
  )
  const valueKeys = measurementPointKeys.filter(key => 
    !pointKeys.includes(key) && (key.includes('(') || key.includes('nm') || key.includes('_H'))
  )
  
  console.log(`🔧 [StatisticalInfoByPoints] Point keys:`, pointKeys)
  console.log(`🔧 [StatisticalInfoByPoints] Value keys:`, valueKeys)
  
  // If we have specific measurement point keys (like 1_UL, 2_UL)
  if (pointKeys.length > 0) {
    pointKeys.forEach(pointKey => {
      grouped[pointKey] = props.summaryData.map(row => {
        const newRow = { ITEM: row.ITEM }
        // Add the value for this specific point
        newRow[pointKey] = row[pointKey]
        // Add other value columns if they exist
        valueKeys.forEach(valueKey => {
          newRow[valueKey] = row[valueKey]
        })
        return newRow
      })
    })
  } else {
    // Fallback: treat all non-ITEM columns as value columns and create one group
    const defaultPoint = 'Measurement Point'
    grouped[defaultPoint] = props.summaryData.map(row => {
      const newRow = { ITEM: row.ITEM }
      valueKeys.forEach(valueKey => {
        newRow[valueKey] = row[valueKey]
      })
      return newRow
    })
  }
  
  console.log(`🔧 [StatisticalInfoByPoints] Grouped data:`, grouped)
  return grouped
})

// Computed property for headers within each card
const pointTableHeaders = computed(() => {
  const headers = [{
    title: 'Statistic',
    key: 'ITEM',
    align: 'start',
    sortable: false,
    width: '100px'
  }]
  
  // Add headers for value columns
  if (props.summaryData && props.summaryData.length > 0) {
    const firstRecord = props.summaryData[0]
    const allKeys = Object.keys(firstRecord)
    
    // Find value columns (columns that contain measurement data)
    const valueColumns = allKeys.filter(key => 
      key !== 'ITEM' && 
      (key.includes('(') || key.includes('nm') || key.includes('_H') || 
       key.includes('Left') || key.includes('Right') || key.includes('Ref'))
    )
    
    // If no specific value columns found, use all non-ITEM columns except point keys
    if (valueColumns.length === 0) {
      const pointKeys = allKeys.filter(key => 
        key.includes('_UL') || key.includes('_LL') || key.includes('_UR') || key.includes('_LR') || 
        key.includes('_C') || key.match(/^\d+_/)
      )
      valueColumns.push(...allKeys.filter(key => key !== 'ITEM' && !pointKeys.includes(key)))
    }
    
    valueColumns.forEach(key => {
      headers.push({
        title: key,
        key: key,
        align: 'end',
        sortable: false,
        width: '120px'
      })
    })
  }
  
  return headers
})

// Computed property to get only value headers (excluding ITEM)
const valueHeaders = computed(() => {
  return pointTableHeaders.value.filter(header => header.key !== 'ITEM')
})

// Handle row click events
function handleRowClick(event, { item }, pointName = null) {
  console.log('Statistical row clicked:', item, 'from point:', pointName)
  // Include point information in the emitted data
  const enrichedItem = { ...item, selectedPoint: pointName }
  emit('row-click', enrichedItem)
  emit('statistic-selected', item.ITEM)
}

// Format values based on statistic type
function formatValue(value, statisticName) {
  if (value == null || value === undefined || value === '') return 'N/A'
  
  if (typeof value === 'number') {
    // Format based on statistic type
    const upperStat = statisticName?.toUpperCase()
    if (upperStat === 'COUNT' || upperStat === 'CNT') {
      return value.toLocaleString()
    }
    
    // Most AFM measurements are in nm scale - use appropriate precision
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

// Chart data preparation
const chartData = computed(() => {
  if (!props.summaryData || props.summaryData.length === 0) return []
  
  const grouped = groupedByMeasurementPoints.value
  const data = []
  
  // Get the index of the selected statistic
  const statisticIndex = availableStatistics.value.indexOf(selectedStatistic.value)
  if (statisticIndex === -1) return []
  
  // Process each measurement point
  Object.keys(grouped).forEach((pointName, pointIndex) => {
    const pointData = grouped[pointName]
    
    // For each selected measurement type
    selectedMeasurements.value.forEach((measurement, measurementIndex) => {
      const measurementData = pointData.find(row => row.ITEM === selectedStatistic.value)
      if (measurementData && measurementData[measurement] !== undefined) {
        data.push({
          name: `${pointName}_${measurement}`,
          value: [pointIndex + 1, measurementData[measurement]],
          measurement: measurement,
          point: pointName,
          itemIndex: measurementIndex
        })
      }
    })
  })
  
  return data
})

// Chart series configuration
const chartSeries = computed(() => {
  const series = []
  const colors = ['#1976d2', '#388e3c', '#f57c00', '#d32f2f', '#7b1fa2', '#00796b']
  
  selectedMeasurements.value.forEach((measurement, index) => {
    const seriesData = chartData.value.filter(item => item.measurement === measurement)
    
    series.push({
      name: measurement,
      type: 'scatter',
      data: seriesData.map(item => item.value),
      symbolSize: 8,
      itemStyle: {
        color: colors[index % colors.length]
      }
    })
  })
  
  return series
})

// Create and update chart
function createChart() {
  if (!chartContainer.value) {
    console.warn('Chart container not ready yet')
    return
  }
  
  if (chartInstance.value) {
    chartInstance.value.dispose()
    chartInstance.value = null
  }
  
  try {
    chartInstance.value = echarts.init(chartContainer.value)
    updateChart()
  } catch (error) {
    console.error('Failed to initialize chart:', error)
  }
}

function updateChart() {
  if (!chartInstance.value) return
  
  const pointNames = Object.keys(groupedByMeasurementPoints.value)
  
  const option = {
    title: {
      text: `${selectedStatistic.value} Values by Measurement Points`,
      left: 'center',
      textStyle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#333'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        const pointName = pointNames[params.value[0] - 1] || 'Unknown'
        return `${params.seriesName}<br/>Point: ${pointName}<br/>Value: ${params.value[1]}`
      },
      textStyle: {
        fontSize: 14,
        fontWeight: '500'
      }
    },
    legend: {
      top: '8%',
      left: 'center',
      textStyle: {
        fontSize: 14,
        fontWeight: '600'
      }
    },
    grid: {
      left: '12%',
      right: '10%',
      bottom: '18%',
      top: '22%'
    },
    xAxis: {
      type: 'category',
      name: 'Measurement Points',
      nameLocation: 'middle',
      nameGap: 35,
      nameTextStyle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333'
      },
      data: pointNames,
      axisLabel: {
        rotate: 45,
        fontSize: 13,
        fontWeight: '600',
        color: '#555'
      },
      axisLine: {
        lineStyle: {
          width: 2
        }
      }
    },
    yAxis: {
      type: 'value',
      name: `${selectedStatistic.value} (nm)`,
      nameLocation: 'middle',
      nameGap: 50,
      nameTextStyle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333'
      },
      axisLabel: {
        fontSize: 13,
        fontWeight: '600',
        color: '#555'
      },
      axisLine: {
        lineStyle: {
          width: 2
        }
      }
    },
    series: chartSeries.value
  }
  
  chartInstance.value.setOption(option, true)
}

// Watch for chart updates
watch([selectedStatistic, selectedMeasurements, () => props.summaryData], () => {
  if (activeTab.value === 'chart') {
    nextTick(() => {
      setTimeout(() => {
        updateChart()
      }, 10)
    })
  }
}, { deep: true })

watch(activeTab, (newTab) => {
  if (newTab === 'chart') {
    nextTick(() => {
      // Add a small delay to ensure DOM is fully rendered
      setTimeout(() => {
        createChart()
      }, 50)
    })
  }
})

// Lifecycle
onMounted(() => {
  // Initialize available measurements
  if (availableMeasurements.value.length > 0) {
    selectedMeasurements.value = availableMeasurements.value.slice(0, 3)
  }
})

onUnmounted(() => {
  // Clean up chart instance
  if (chartInstance.value) {
    chartInstance.value.dispose()
    chartInstance.value = null
  }
})
</script>

<style scoped>
.measurement-point-card {
  height: 100%;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.measurement-point-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.measurement-point-card .v-card-title {
  font-size: 1rem;
  font-weight: 600;
  padding: 12px 16px;
}

.statistics-table {
  border: none;
}

.statistics-table :deep(.v-data-table__tr:hover) {
  background-color: rgba(var(--v-theme-primary), 0.08);
  cursor: pointer;
}

.statistics-table :deep(.v-data-table-header) {
  background-color: rgba(var(--v-theme-surface), 0.5);
}

.statistics-table :deep(.v-data-table__th) {
  font-weight: 600;
  font-size: 0.9rem;
  padding: 8px 12px;
}

.statistics-table :deep(.v-data-table__td) {
  padding: 8px 12px;
  font-size: 1rem;
}

.font-mono {
  font-family: 'Courier New', monospace;
  font-size: 1.1rem;
  font-weight: 600;
}

.v-chip {
  font-weight: 600;
  font-size: 0.7rem;
}

.v-alert {
  border-left: 4px solid rgb(var(--v-theme-info));
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .measurement-point-card .v-card-title {
    font-size: 0.9rem;
    padding: 10px 12px;
  }
  
  .statistics-table :deep(.v-data-table__th),
  .statistics-table :deep(.v-data-table__td) {
    padding: 6px 8px;
    font-size: 0.9rem;
  }
  
  .font-mono {
    font-size: 1rem;
  }
  
  .v-chip {
    font-size: 0.65rem;
  }
}
</style>