<template>
  <div>
    <div v-if="isLoading" class="text-center pa-4">
      <v-progress-circular indeterminate color="primary" size="small" />
      <p class="mt-2 text-caption">Loading...</p>
    </div>
    <div v-else-if="profileData.length > 0">
      <div ref="chartContainer" :style="{ width: '100%', height: `${chartHeight}px` }"></div>
      <div v-if="!compact" class="mt-2">
        <v-row dense>
          <v-col cols="12" md="4">
            <v-card variant="outlined" class="pa-2">
              <div class="text-caption text-medium-emphasis">Data Points</div>
              <div class="text-subtitle-2">{{ profileData.length.toLocaleString() }}</div>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card variant="outlined" class="pa-2">
              <div class="text-caption text-medium-emphasis">Surface Size</div>
              <div class="text-subtitle-2">{{ surfaceSize.x }} × {{ surfaceSize.y }} µm</div>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card variant="outlined" class="pa-2">
              <div class="text-caption text-medium-emphasis">Z Range</div>
              <div class="text-subtitle-2">{{ zRange.min.toFixed(3) }} to {{ zRange.max.toFixed(3) }} nm</div>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </div>
    <div v-else class="text-center pa-4">
      <v-icon size="32" color="grey">mdi-chart-scatter-plot</v-icon>
      <p class="text-body-2 mt-2 text-medium-emphasis">No data available</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

// Props
const props = defineProps({
  selectedPoint: {
    type: Number,
    default: null
  },
  profileData: {
    type: Array,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  chartHeight: {
    type: Number,
    default: 500
  },
  compact: {
    type: Boolean,
    default: false
  },
  chartType: {
    type: String,
    default: 'scatter'
  }
})

// Emits
const emit = defineEmits(['chart-type-changed'])

// Reactive data
const chartContainer = ref(null)
let chartInstance = null

// Computed properties
const surfaceSize = computed(() => {
  if (props.profileData.length === 0) return { x: 0, y: 0 }
  const maxX = Math.max(...props.profileData.map(p => p.x))
  const maxY = Math.max(...props.profileData.map(p => p.y))
  return { x: maxX.toFixed(1), y: maxY.toFixed(1) }
})

const zRange = computed(() => {
  if (props.profileData.length === 0) return { min: 0, max: 0 }
  const zValues = props.profileData.map(p => p.z)
  return {
    min: Math.min(...zValues),
    max: Math.max(...zValues)
  }
})

// Functions
function renderChart() {
  if (!chartContainer.value || props.profileData.length === 0) {
    console.log('Cannot render chart:', {
      hasContainer: !!chartContainer.value,
      dataLength: props.profileData.length,
      chartType: props.chartType,
      selectedPoint: props.selectedPoint
    })
    
    // Clear existing chart if no data
    if (chartInstance) {
      chartInstance.dispose()
      chartInstance = null
    }
    return
  }
  
  try {
    // Destroy existing chart
    if (chartInstance) {
      console.log('Disposing existing chart instance')
      chartInstance.dispose()
      chartInstance = null
    }
    
    // Ensure container is visible and has dimensions
    if (chartContainer.value.offsetWidth === 0 || chartContainer.value.offsetHeight === 0) {
      console.log('Container not ready, retrying...')
      setTimeout(() => renderChart(), 200)
      return
    }
    
    console.log('Creating new chart instance for:', props.chartType, 'with', props.profileData.length, 'data points')
    
    // Initialize ECharts instance
    chartInstance = echarts.init(chartContainer.value)
    
    let option = {}
    
    switch (props.chartType) {
      case 'scatter':
        option = createScatterChartOption()
        break
      case 'heatmap':
        option = createHeatmapChartOption()
        break
      case 'histogram':
        option = createHistogramChartOption()
        break
      default:
        option = createScatterChartOption()
    }
    
    chartInstance.setOption(option, {
      notMerge: true,
      replaceMerge: ['series', 'xAxis', 'yAxis', 'visualMap']
    })
    
    
    console.log('Chart rendered successfully:', props.chartType, 'for point:', props.selectedPoint)
    
  } catch (error) {
    console.error('Error rendering chart:', error)
    // Clean up on error
    if (chartInstance) {
      chartInstance.dispose()
      chartInstance = null
    }
  }
}

function createScatterChartOption() {
  const data = props.profileData.map(point => [point.x, point.y, point.z])
  
  return {
    title: {
      text: props.compact ? '' : `AFM Surface Profile - Point ${props.selectedPoint}`,
      left: 'center',
      textStyle: {
        fontSize: 14,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        const [x, y, z] = params.data
        return `X: ${x.toFixed(3)} µm<br/>Y: ${y.toFixed(3)} µm<br/>Z: ${z.toFixed(6)} nm`
      }
    },
    xAxis: {
      type: 'value',
      name: 'X (µm)',
      nameLocation: 'middle',
      nameGap: 30,
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      name: 'Y (µm)',
      nameLocation: 'middle',
      nameGap: 30,
      splitLine: { show: false }
    },
    visualMap: {
      min: zRange.value.min,
      max: zRange.value.max,
      dimension: 2,
      orient: 'vertical',
      right: 10,
      top: 'center',
      text: ['High', 'Low'],
      calculable: true,
      inRange: {
        color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
      }
    },
    series: [{
      type: 'scatter',
      data: data,
      symbolSize: 2,
      emphasis: {
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 1
        }
      }
    }],
    grid: {
      left: '10%',
      right: '15%',
      bottom: '15%',
      top: '15%'
    }
  }
}

function createHeatmapChartOption() {
  // Create a grid for heatmap
  const xValues = [...new Set(props.profileData.map(p => p.x))].sort((a, b) => a - b)
  const yValues = [...new Set(props.profileData.map(p => p.y))].sort((a, b) => a - b)
  
  const data = []
  props.profileData.forEach(point => {
    const xIndex = xValues.indexOf(point.x)
    const yIndex = yValues.indexOf(point.y)
    data.push([xIndex, yIndex, point.z])
  })
  
  return {
    title: {
      text: props.compact ? '' : `AFM Surface Heatmap - Point ${props.selectedPoint}`,
      left: 'center',
      textStyle: {
        fontSize: 14,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      position: 'top',
      formatter: function(params) {
        const [xIndex, yIndex, z] = params.data
        const x = xValues[xIndex]
        const y = yValues[yIndex]
        return `X: ${x?.toFixed(3)} µm<br/>Y: ${y?.toFixed(3)} µm<br/>Z: ${z?.toFixed(6)} nm`
      }
    },
    xAxis: {
      type: 'category',
      data: xValues.map(x => x.toFixed(1)),
      name: 'X (µm)',
      nameLocation: 'middle',
      nameGap: 30,
      splitArea: { show: true }
    },
    yAxis: {
      type: 'category',
      data: yValues.map(y => y.toFixed(1)),
      name: 'Y (µm)',
      nameLocation: 'middle',
      nameGap: 50,
      splitArea: { show: true }
    },
    visualMap: {
      min: zRange.value.min,
      max: zRange.value.max,
      calculable: true,
      orient: 'vertical',
      right: 10,
      top: 'center',
      text: ['High', 'Low'],
      inRange: {
        color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
      }
    },
    series: [{
      type: 'heatmap',
      data: data,
      label: {
        show: false
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }],
    grid: {
      left: '15%',
      right: '15%',
      bottom: '15%',
      top: '15%'
    }
  }
}

function createHistogramChartOption() {
  // Create histogram bins for Z values
  const zValues = props.profileData.map(p => p.z)
  const min = Math.min(...zValues)
  const max = Math.max(...zValues)
  const binCount = 50
  const binSize = (max - min) / binCount
  
  const bins = Array(binCount).fill(0)
  const binLabels = []
  
  for (let i = 0; i < binCount; i++) {
    binLabels.push((min + i * binSize).toFixed(3))
  }
  
  zValues.forEach(z => {
    const binIndex = Math.min(Math.floor((z - min) / binSize), binCount - 1)
    bins[binIndex]++
  })
  
  return {
    title: {
      text: props.compact ? '' : `Z-Value Distribution - Point ${props.selectedPoint}`,
      left: 'center',
      textStyle: {
        fontSize: 14,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        const param = params[0]
        return `Z Range: ${param.name} nm<br/>Count: ${param.value} points`
      }
    },
    xAxis: {
      type: 'category',
      data: binLabels,
      name: 'Z Value (nm)',
      nameLocation: 'middle',
      nameGap: 30,
      axisLabel: {
        rotate: 45,
        interval: Math.floor(binCount / 10)
      }
    },
    yAxis: {
      type: 'value',
      name: 'Frequency',
      nameLocation: 'middle',
      nameGap: 50
    },
    series: [{
      type: 'bar',
      data: bins,
      itemStyle: {
        color: '#1976d2'
      },
      emphasis: {
        itemStyle: {
          color: '#1565c0'
        }
      }
    }],
    grid: {
      left: '15%',
      right: '10%',
      bottom: '20%',
      top: '15%'
    }
  }
}

function handleResize() {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// Watchers
watch(() => props.chartType, () => {
  if (props.profileData.length > 0) {
    setTimeout(() => renderChart(), 50)
  }
})

watch(() => props.profileData, (newData, oldData) => {
  console.log('Profile data changed:', {
    oldLength: oldData?.length || 0,
    newLength: newData?.length || 0,
    chartType: props.chartType
  })
  if (newData && newData.length > 0) {
    setTimeout(() => renderChart(), 100)
  }
}, { deep: true })

watch(() => props.selectedPoint, (newPoint, oldPoint) => {
  console.log('Selected point changed:', { oldPoint, newPoint })
  if (props.profileData.length > 0) {
    setTimeout(() => renderChart(), 100)
  }
})

watch(() => props.chartHeight, () => {
  if (chartInstance) {
    setTimeout(() => chartInstance.resize(), 100)
  }
})

// Lifecycle
onMounted(() => {
  console.log('ChartVisualization mounted with:', {
    chartType: props.chartType,
    dataLength: props.profileData.length,
    selectedPoint: props.selectedPoint
  })
  
  // Add resize listener
  window.addEventListener('resize', handleResize)
  
  if (props.profileData.length > 0) {
    setTimeout(() => renderChart(), 100)
  }
})

onUnmounted(() => {
  console.log('ChartVisualization unmounted')
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  window.removeEventListener('resize', handleResize)
})
</script>