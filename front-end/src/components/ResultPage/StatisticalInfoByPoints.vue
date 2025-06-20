<template>
  <div>
    <!-- Main title card -->
    <v-card elevation="2" class="mb-3">
      <v-card-title class="bg-info text-white py-2 text-subtitle-1">
        <v-icon start size="small">mdi-chart-box-outline</v-icon>
        Statistics
      </v-card-title>
    </v-card>

    <!-- Display statistics when summary data is available -->
    <div v-if="summaryData && summaryData.length > 0">
      <!-- Debug information panel -->
      <v-alert type="info" density="compact" class="mb-2" v-if="summaryData.length > 0">
        <small>📊 Data: {{ summaryData.length }} records → {{ Object.keys(groupedByMeasurementPoints).length }} measurement groups | First record keys: {{ summaryData[0] ? Object.keys(summaryData[0]).join(', ') : 'None' }}</small>
      </v-alert>
      
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

        <v-window v-model="activeTab" class="statistics-window">
          <!-- Data Table Tab -->
          <v-window-item value="table">
            <div class="statistics-content-container">
              <!-- Show grouped data if available -->
              <div v-if="Object.keys(groupedByMeasurementPoints).length > 0">
                <!-- Create separate cards for each measurement point -->
                <v-row class="ma-0">
                  <v-col v-for="(pointData, pointName) in groupedByMeasurementPoints" :key="pointName" cols="12" sm="6"
                    md="3" lg="3" class="pa-2">
                    <v-card elevation="3" class="measurement-point-card">
                      <!-- Point header -->
                      <v-card-title class="bg-primary text-white py-2 text-body-2">
                        <v-icon start size="x-small">mdi-target</v-icon>
                        {{ pointName }}
                      </v-card-title>

                      <!-- Statistics table for this point -->
                      <v-card-text class="pa-2">
                        <v-data-table :headers="pointTableHeaders" :items="pointData" item-value="ITEM" density="compact"
                          class="statistics-table" hover hide-default-footer
                          @click:row="(event, { item }) => handleRowClick(event, { item }, pointName)">
                          <!-- Custom template for statistic name column -->
                          <template v-slot:item.ITEM="{ item }">
                            <v-chip size="small" :color="getStatisticColor(item.ITEM)" variant="outlined"
                              class="font-weight-medium">
                              {{ item.ITEM }}
                            </v-chip>
                          </template>

                          <!-- Custom template for value columns -->
                          <template v-for="header in valueHeaders" :key="header.key"
                            v-slot:[`item.${header.key}`]="{ item }">
                            <span class="font-mono">{{ formatValue(item[header.key], item.ITEM) }}</span>
                          </template>
                        </v-data-table>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </div>
              
              <!-- Show error message if data processing failed -->
              <div v-else class="text-center pa-6">
                <v-card elevation="2" class="pa-4">
                  <v-icon size="64" color="warning" class="mb-3">mdi-alert-circle-outline</v-icon>
                  <div class="text-h6 mb-2">Data Processing Issue</div>
                  <div class="text-body-2 mb-3">
                    Statistical data is available but could not be properly processed for display.
                  </div>
                  <v-btn color="primary" variant="outlined" size="small" @click="activeTab = 'chart'">
                    Try Chart View
                  </v-btn>
                </v-card>
              </div>
            </div>
          </v-window-item>

          <!-- Scatter Chart Tab -->
          <v-window-item value="chart">
            <div class="statistics-content-container">
              <!-- Chart Controls -->
              <v-row class="mb-4">
                <v-col cols="12" md="8">
                  <v-card variant="outlined">
                    <v-card-title class="text-subtitle-1">Chart Controls</v-card-title>
                    <v-card-text>
                      <v-row>
                        <v-col cols="12" sm="6" md="4">
                          <v-select v-model="selectedStatistic" :items="availableStatistics" label="Statistic Type"
                            density="compact" variant="outlined" />
                        </v-col>
                        <v-col cols="12" sm="6" md="8">
                          <v-select v-model="selectedMeasurements" :items="availableMeasurements"
                            label="Measurements to Show" multiple chips density="compact" variant="outlined" />
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
            </div>
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
  },
  compact: {
    type: Boolean,
    default: false
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
    console.log(`🏁 [StatisticalInfoByPoints] Has Site field:`, 'Site' in newData[0])
    
    // Check for data quality issues
    const hasValidStructure = newData.every(record => 
      record && typeof record === 'object' && 'ITEM' in record
    )
    console.log(`🏁 [StatisticalInfoByPoints] All records have valid structure:`, hasValidStructure)
    
    if (!hasValidStructure) {
      console.error(`❌ [StatisticalInfoByPoints] Invalid data structure detected`)
    }
  } else {
    console.warn(`⚠️ [StatisticalInfoByPoints] No valid summary data received`)
  }
}, { immediate: true })

// Computed property to group data by measurement points (Sites)
const groupedByMeasurementPoints = computed(() => {
  console.log(`🔧 [StatisticalInfoByPoints] Computing grouped data...`)
  console.log(`🔧 [StatisticalInfoByPoints] Props summaryData:`, props.summaryData)

  if (!props.summaryData || props.summaryData.length === 0) {
    console.log(`🔧 [StatisticalInfoByPoints] No summary data, returning empty groups`)
    return {}
  }

  try {
    const firstRecord = props.summaryData[0]
    console.log(`🔧 [StatisticalInfoByPoints] First record for grouping:`, firstRecord)
    console.log(`🔧 [StatisticalInfoByPoints] First record keys:`, Object.keys(firstRecord))

    const grouped = {}
    const allKeys = Object.keys(firstRecord)

    // Identify value columns (those with units or measurement types)
    const valueColumns = allKeys.filter(key =>
      key !== 'ITEM' && key !== 'Site' &&
      (key.includes('(') || key.includes('nm') || key.includes('um') ||
        key.includes('_H') || key.includes('Left') || key.includes('Right') || key.includes('Ref'))
    )

    console.log(`🔧 [StatisticalInfoByPoints] Value columns:`, valueColumns)

    // METHOD 1: Flask data structure with Site column
    if ('Site' in firstRecord) {
      console.log(`🔧 [StatisticalInfoByPoints] Using Flask format (Site column)`)
      
      const uniqueSites = [...new Set(props.summaryData.map(row => row.Site).filter(site => site !== null && site !== undefined))]
      console.log(`🔧 [StatisticalInfoByPoints] Unique sites:`, uniqueSites)

      if (uniqueSites.length > 0) {
        uniqueSites.forEach(site => {
          const siteRows = props.summaryData.filter(row => row.Site === site)
          console.log(`🔧 [StatisticalInfoByPoints] Site ${site} has ${siteRows.length} rows`)
          
          grouped[site] = siteRows.map(row => {
            const newRow = { ITEM: row.ITEM }
            // Add all value columns
            valueColumns.forEach(valueKey => {
              if (valueKey in row && row[valueKey] !== null && row[valueKey] !== undefined) {
                newRow[valueKey] = row[valueKey]
              }
            })
            return newRow
          })
        })
      }
    }
    
    // METHOD 2: Legacy format - look for point-like keys as columns
    if (Object.keys(grouped).length === 0) {
      console.log(`🔧 [StatisticalInfoByPoints] Trying legacy format`)
      
      const pointKeys = allKeys.filter(key =>
        key !== 'ITEM' && key !== 'Site' &&
        (key.includes('_UL') || key.includes('_LL') || key.includes('_UR') || 
         key.includes('_LR') || key.includes('_C') || key.match(/^\d+_/))
      )

      console.log(`🔧 [StatisticalInfoByPoints] Found point keys:`, pointKeys)

      if (pointKeys.length > 0) {
        pointKeys.forEach(pointKey => {
          grouped[pointKey] = props.summaryData.map(row => {
            const newRow = { ITEM: row.ITEM }
            
            // Add the point value
            if (pointKey in row && row[pointKey] !== null && row[pointKey] !== undefined) {
              newRow[pointKey] = row[pointKey]
            }
            
            // Add value columns
            valueColumns.forEach(valueKey => {
              if (valueKey in row && row[valueKey] !== null && row[valueKey] !== undefined) {
                newRow[valueKey] = row[valueKey]
              }
            })
            
            return newRow
          })
        })
      }
    }

    // METHOD 3: Fallback - create single group with all data
    if (Object.keys(grouped).length === 0) {
      console.log(`🔧 [StatisticalInfoByPoints] Using fallback single group`)
      
      const defaultPoint = 'All Measurements'
      grouped[defaultPoint] = props.summaryData.map(row => {
        const newRow = { ITEM: row.ITEM }
        
        // Add all non-ITEM columns
        Object.keys(row).forEach(key => {
          if (key !== 'ITEM' && row[key] !== null && row[key] !== undefined) {
            newRow[key] = row[key]
          }
        })
        
        return newRow
      })
    }

    console.log(`🔧 [StatisticalInfoByPoints] Final grouped data:`, grouped)
    console.log(`🔧 [StatisticalInfoByPoints] Groups created:`, Object.keys(grouped))
    
    // Validate grouped data
    const isValid = Object.keys(grouped).length > 0 && 
      Object.values(grouped).every(group => Array.isArray(group) && group.length > 0)
    
    if (!isValid) {
      console.error(`❌ [StatisticalInfoByPoints] Grouped data validation failed`)
      return {}
    }

    return grouped
    
  } catch (error) {
    console.error(`❌ [StatisticalInfoByPoints] Error in grouping data:`, error)
    return {}
  }
})

// Computed property for headers within each card
const pointTableHeaders = computed(() => {
  console.log(`🔧 [StatisticalInfoByPoints] Computing table headers...`)
  
  const headers = [{
    title: 'Statistic',
    key: 'ITEM',
    align: 'start',
    sortable: false,
    width: '100px'
  }]

  try {
    if (!props.summaryData || props.summaryData.length === 0) {
      console.log(`🔧 [StatisticalInfoByPoints] No data for headers, returning basic headers`)
      return headers
    }

    const firstRecord = props.summaryData[0]
    const allKeys = Object.keys(firstRecord)
    console.log(`🔧 [StatisticalInfoByPoints] All keys for headers:`, allKeys)

    // Find value columns (measurement data columns)
    const valueColumns = allKeys.filter(key =>
      key !== 'ITEM' && key !== 'Site' &&
      (key.includes('(') || key.includes('nm') || key.includes('um') ||
        key.includes('_H') || key.includes('Left') || key.includes('Right') || key.includes('Ref'))
    )

    console.log(`🔧 [StatisticalInfoByPoints] Value columns for headers:`, valueColumns)

    // If no measurement columns found, look for point columns
    if (valueColumns.length === 0) {
      console.log(`🔧 [StatisticalInfoByPoints] No measurement columns, looking for point columns`)
      
      const pointColumns = allKeys.filter(key =>
        key !== 'ITEM' && key !== 'Site' &&
        (key.includes('_UL') || key.includes('_LL') || key.includes('_UR') || 
         key.includes('_LR') || key.includes('_C') || key.match(/^\d+_/))
      )
      
      console.log(`🔧 [StatisticalInfoByPoints] Point columns found:`, pointColumns)
      valueColumns.push(...pointColumns)
    }

    // Final fallback: use all remaining columns
    if (valueColumns.length === 0) {
      console.log(`🔧 [StatisticalInfoByPoints] No specific columns found, using all remaining columns`)
      const remainingColumns = allKeys.filter(key => key !== 'ITEM' && key !== 'Site')
      valueColumns.push(...remainingColumns)
    }

    // Create headers for value columns
    valueColumns.forEach(key => {
      headers.push({
        title: key,
        key: key,
        align: 'end',
        sortable: false,
        width: '120px'
      })
    })

    console.log(`🔧 [StatisticalInfoByPoints] Final headers:`, headers.map(h => h.key))
    return headers
    
  } catch (error) {
    console.error(`❌ [StatisticalInfoByPoints] Error computing headers:`, error)
    return headers // Return basic headers on error
  }
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
  console.log(`📊 [StatisticalInfoByPoints] Computing chart data...`)
  
  try {
    if (!props.summaryData || props.summaryData.length === 0) {
      console.log(`📊 [StatisticalInfoByPoints] No summary data for chart`)
      return []
    }

    const grouped = groupedByMeasurementPoints.value
    console.log(`📊 [StatisticalInfoByPoints] Grouped data for chart:`, Object.keys(grouped))
    
    if (Object.keys(grouped).length === 0) {
      console.log(`📊 [StatisticalInfoByPoints] No grouped data for chart`)
      return []
    }

    const data = []

    // Validate selected statistic
    if (!selectedStatistic.value || !availableStatistics.value.includes(selectedStatistic.value)) {
      console.log(`📊 [StatisticalInfoByPoints] Invalid selected statistic: ${selectedStatistic.value}`)
      return []
    }

    // Validate selected measurements
    if (!selectedMeasurements.value || selectedMeasurements.value.length === 0) {
      console.log(`📊 [StatisticalInfoByPoints] No selected measurements for chart`)
      return []
    }

    console.log(`📊 [StatisticalInfoByPoints] Processing ${Object.keys(grouped).length} points for statistic: ${selectedStatistic.value}`)
    console.log(`📊 [StatisticalInfoByPoints] Selected measurements:`, selectedMeasurements.value)

    // Process each measurement point
    Object.keys(grouped).forEach((pointName, pointIndex) => {
      const pointData = grouped[pointName]
      console.log(`📊 [StatisticalInfoByPoints] Processing point ${pointName} with ${pointData.length} records`)

      // Find the row with the selected statistic
      const measurementData = pointData.find(row => row.ITEM === selectedStatistic.value)
      
      if (!measurementData) {
        console.warn(`📊 [StatisticalInfoByPoints] No data found for statistic ${selectedStatistic.value} in point ${pointName}`)
        return
      }

      console.log(`📊 [StatisticalInfoByPoints] Found data for ${selectedStatistic.value}:`, measurementData)

      // For each selected measurement type
      selectedMeasurements.value.forEach((measurement, measurementIndex) => {
        if (measurement in measurementData && 
            measurementData[measurement] !== null && 
            measurementData[measurement] !== undefined) {
          
          const value = parseFloat(measurementData[measurement])
          if (isNaN(value)) {
            console.warn(`📊 [StatisticalInfoByPoints] Invalid numeric value for ${measurement}: ${measurementData[measurement]}`)
            return
          }

          data.push({
            name: `${pointName}_${measurement}`,
            value: [pointIndex, value],
            measurement: measurement,
            point: pointName,
            itemIndex: measurementIndex
          })
          
          console.log(`📊 [StatisticalInfoByPoints] Added chart point: ${pointName} ${measurement} = ${value}`)
        } else {
          console.warn(`📊 [StatisticalInfoByPoints] Missing measurement ${measurement} in point ${pointName}`)
        }
      })
    })

    console.log(`📊 [StatisticalInfoByPoints] Generated ${data.length} chart data points`)
    return data
    
  } catch (error) {
    console.error(`❌ [StatisticalInfoByPoints] Error computing chart data:`, error)
    return []
  }
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
  console.log(`📊 [StatisticalInfoByPoints] Creating chart...`)
  
  if (!chartContainer.value) {
    console.warn('📊 [StatisticalInfoByPoints] Chart container not ready yet')
    return
  }

  if (chartInstance.value) {
    chartInstance.value.dispose()
    chartInstance.value = null
  }

  try {
    chartInstance.value = echarts.init(chartContainer.value)
    updateChart()
    console.log(`✅ [StatisticalInfoByPoints] Chart created successfully`)
  } catch (error) {
    console.error('❌ [StatisticalInfoByPoints] Failed to initialize chart:', error)
  }
}

function updateChart() {
  console.log(`📊 [StatisticalInfoByPoints] Updating chart...`)
  
  if (!chartInstance.value) {
    console.warn('📊 [StatisticalInfoByPoints] No chart instance to update')
    return
  }

  try {
    const grouped = groupedByMeasurementPoints.value
    const pointNames = Object.keys(grouped)
    const chartDataValue = chartData.value
    const seriesData = chartSeries.value

    console.log(`📊 [StatisticalInfoByPoints] Chart update data:`)
    console.log(`  - Point names: ${pointNames.length}`, pointNames)
    console.log(`  - Chart data points: ${chartDataValue.length}`)
    console.log(`  - Series count: ${seriesData.length}`)

    // Handle empty data case
    if (pointNames.length === 0 || chartDataValue.length === 0) {
      console.log(`📊 [StatisticalInfoByPoints] No data for chart, showing empty state`)
      
      const emptyOption = {
        title: {
          text: 'No Data Available',
          left: 'center',
          top: 'middle',
          textStyle: {
            fontSize: 18,
            color: '#999'
          }
        },
        xAxis: { show: false },
        yAxis: { show: false },
        series: []
      }
      
      chartInstance.value.setOption(emptyOption, true)
      return
    }

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
        formatter: function (params) {
          const pointName = pointNames[params.value[0]] || 'Unknown'
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
        },
        selectedMode: false  // Disable legend click functionality
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
          color: '#555',
          interval: 0  // Force all labels to be shown
        },
        axisLine: {
          lineStyle: {
            width: 2
          }
        },
        boundaryGap: true  // Ensure space for all categories
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
      series: seriesData
    }

    chartInstance.value.setOption(option, true)
    console.log(`✅ [StatisticalInfoByPoints] Chart updated successfully`)
    
  } catch (error) {
    console.error('❌ [StatisticalInfoByPoints] Error updating chart:', error)
  }
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
  console.log(`🚀 [StatisticalInfoByPoints] Component mounted`)
  console.log(`📊 [StatisticalInfoByPoints] Props at mount:`, {
    summaryDataLength: props.summaryData?.length,
    summaryDataSample: props.summaryData?.[0],
    compact: props.compact
  })
  console.log(`📊 [StatisticalInfoByPoints] Initial state:`, {
    selectedStatistic: selectedStatistic.value,
    selectedMeasurements: selectedMeasurements.value,
    availableStatistics: availableStatistics.value,
    availableMeasurements: availableMeasurements.value
  })
  
  // Initialize available measurements
  if (availableMeasurements.value.length > 0) {
    selectedMeasurements.value = availableMeasurements.value.slice(0, 3)
    console.log(`✅ [StatisticalInfoByPoints] Initialized selected measurements:`, selectedMeasurements.value)
  } else {
    console.log(`⚠️ [StatisticalInfoByPoints] No available measurements at mount time`)
  }
  
  // Log grouped data
  console.log(`📊 [StatisticalInfoByPoints] Grouped data at mount:`, groupedByMeasurementPoints.value)
  console.log(`📊 [StatisticalInfoByPoints] Chart data at mount:`, chartData.value)
})

// Watch for changes in available measurements to update selected measurements
watch(availableMeasurements, (newMeasurements) => {
  console.log(`🔄 [StatisticalInfoByPoints] Available measurements changed:`, newMeasurements)
  
  if (newMeasurements.length > 0 && selectedMeasurements.value.length === 0) {
    selectedMeasurements.value = newMeasurements.slice(0, 3)
    console.log(`✅ [StatisticalInfoByPoints] Auto-selected measurements:`, selectedMeasurements.value)
  }
}, { immediate: true })

onUnmounted(() => {
  // Clean up chart instance
  if (chartInstance.value) {
    chartInstance.value.dispose()
    chartInstance.value = null
  }
})
</script>

<style scoped>
/* Fixed height container to prevent tab height changes */
.statistics-window {
  height: 780px;
  min-height: 780px;
  max-height: 780px;
}

.statistics-content-container {
  height: 780px;
  overflow-y: auto;
  padding: 16px;
}

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
  .statistics-window {
    height: 400px;
    min-height: 400px;
    max-height: 400px;
  }

  .statistics-content-container {
    height: 400px;
  }

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
