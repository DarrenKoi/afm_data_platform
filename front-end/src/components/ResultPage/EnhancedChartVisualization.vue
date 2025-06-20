<template>
  <div class="enhanced-charts" :style="{ height: `${chartHeight}px` }">
    <div v-if="isLoadingWaferData" class="text-center pa-4">
      <v-progress-circular indeterminate color="primary" size="small" />
      <p class="mt-2 text-caption">Loading wafer data...</p>
    </div>
    <div v-else-if="waferData.length > 0">
      <div 
        ref="waferHeatmapContainer" 
        class="heatmap-chart"
        :style="{ 
          width: '100%', 
          height: `${chartHeight}px`,
          minHeight: '400px'
        }"
      ></div>
    </div>
    <div v-else class="text-center pa-4">
      <v-icon size="32" color="grey">mdi-grid-off</v-icon>
      <p class="text-body-2 mt-2 text-medium-emphasis">No wafer data available</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { apiService } from '@/services/api.js'

const props = defineProps({
  filename: {
    type: String,
    required: true
  },
  chartHeight: {
    type: Number,
    default: 600
  },
  profileData: {
    type: Array,
    default: () => []
  },
  selectedPoint: {
    type: String,
    default: null
  }
})

// Emits
const emit = defineEmits(['point-selected'])

// Reactive data
const waferHeatmapContainer = ref(null)
const isLoadingWaferData = ref(true)
const waferData = ref([])
const selectedWaferPoint = ref(null)

// Chart instances
let waferHeatmapChart = null

// Fetch wafer data from API
async function fetchWaferData() {
  try {
    console.log('Fetching wafer data for filename:', props.filename)
    const result = await apiService.getWaferData(props.filename)
    console.log('Wafer data result:', result)
    
    // Since axios interceptor returns response.data directly, result is the JSON response
    if (result && result.success) {
      console.log('Wafer data points:', result.data?.length || 0)
      return result.data
    } else {
      console.error('Failed to fetch wafer data:', result?.error || 'Unknown error')
      return []
    }
  } catch (error) {
    console.error('Error fetching wafer data:', error)
    return []
  }
}


// Initialize wafer heat map
function initWaferHeatmap() {
  console.log('initWaferHeatmap called')
  console.log('waferHeatmapContainer.value:', waferHeatmapContainer.value)
  console.log('props.profileData.length:', props.profileData.length)
  
  if (!waferHeatmapContainer.value) {
    console.error('Wafer heatmap container not found!')
    return
  }
  
  // Use profile data if available, otherwise fall back to wafer data
  let dataToUse = []
  
  if (props.profileData && props.profileData.length > 0) {
    console.log('Using profile data for heat map')
    // Convert profile data to heat map format
    dataToUse = props.profileData.map(point => ({
      x: point.x || 0,
      y: point.y || 0,
      value: point.z || 0  // Use z value for heat map intensity
    }))
  } else if (waferData.value && waferData.value.length > 0) {
    console.log('Using wafer data for heat map')
    dataToUse = waferData.value
  }
  
  if (dataToUse.length === 0) {
    console.warn('No data available for heat map')
    return
  }
  
  // Validate data structure
  const validData = dataToUse.filter(d => 
    d && typeof d.x === 'number' && typeof d.y === 'number' && 
    (typeof d.value === 'number' || d.value === null || d.value === undefined)
  )
  
  if (validData.length === 0) {
    console.warn('No valid data points found for heat map')
    return
  }
  
  // Check container dimensions
  const containerWidth = waferHeatmapContainer.value.clientWidth
  const containerHeight = waferHeatmapContainer.value.clientHeight
  console.log('Container dimensions:', containerWidth, 'x', containerHeight)
  
  if (containerWidth === 0 || containerHeight === 0) {
    console.log('Container not ready, retrying...')
    setTimeout(() => initWaferHeatmap(), 200)
    return
  }
  
  if (waferHeatmapChart) {
    waferHeatmapChart.dispose()
  }
  
  console.log('Initializing ECharts...')
  try {
    waferHeatmapChart = echarts.init(waferHeatmapContainer.value)
    console.log('ECharts initialized successfully:', waferHeatmapChart)
  } catch (error) {
    console.error('Error initializing ECharts:', error)
    return
  }
  
  // Prepare data for heatmap using validated data
  const xValues = [...new Set(validData.map(d => d.x))].sort((a, b) => a - b)
  const yValues = [...new Set(validData.map(d => d.y))].sort((a, b) => a - b)
  
  const heatmapData = validData.map(d => [
    xValues.indexOf(d.x),
    yValues.indexOf(d.y),
    d.value || 0  // Use d.value instead of d.z, with fallback to 0
  ])
  
  const option = {
    tooltip: {
      position: 'top',
      formatter: function(params) {
        const [xIndex, yIndex, value] = params.data
        const dieX = xValues[xIndex]
        const dieY = yValues[yIndex]
        return `Die: (${dieX}, ${dieY})<br/>Value: ${(value || 0).toFixed(2)} nm<br/>Click to view details`
      }
    },
    xAxis: {
      type: 'category',
      data: xValues,
      name: 'Die X',
      nameLocation: 'middle',
      nameGap: 20,
      nameTextStyle: {
        fontSize: 11
      },
      splitArea: { show: true }
    },
    yAxis: {
      type: 'category',
      data: yValues,
      name: 'Die Y',
      nameLocation: 'middle',
      nameGap: 25,
      nameTextStyle: {
        fontSize: 11
      },
      splitArea: { show: true }
    },
    visualMap: {
      min: Math.min(...validData.map(d => d.value || 0)),
      max: Math.max(...validData.map(d => d.value || 100)),
      calculable: true,
      orient: 'vertical',
      right: 5,
      top: 'center',
      width: 15,
      text: ['High', 'Low'],
      textStyle: {
        fontSize: 10
      },
      inRange: {
        color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
      }
    },
    series: [{
      type: 'heatmap',
      data: heatmapData,
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
      left: '6%',
      right: '18%',
      bottom: '8%',
      top: '3%'
    }
  }
  
  console.log('Setting chart option...', option)
  try {
    waferHeatmapChart.setOption(option)
    console.log('Chart option set successfully')
  } catch (error) {
    console.error('Error setting chart option:', error)
  }
  
  // Add click event listener
  waferHeatmapChart.on('click', function(params) {
    if (params.componentType === 'series') {
      const [xIndex, yIndex] = params.data
      const dieX = xValues[xIndex]
      const dieY = yValues[yIndex]
      const point = waferData.value.find(d => d.x === dieX && d.y === dieY)
      
      if (point) {
        selectedWaferPoint.value = point
        console.log('Wafer point selected:', point)
        
        // Create a point object that matches the expected structure
        // For now, let's use a simple point number based on position
        const pointNumber = (yIndex * xValues.length + xIndex) + 1
        const emitPoint = {
          ...point,
          point: pointNumber,
          x: dieX,
          y: dieY
        }
        
        console.log('Emitting point:', emitPoint)
        emit('point-selected', emitPoint)
      }
    }
  })
}


// Handle window resize
function handleResize() {
  if (waferHeatmapChart) waferHeatmapChart.resize()
}

// Initialize data and charts
async function initializeData() {
  isLoadingWaferData.value = true
  
  try {
    console.log('Fetching wafer data...')
    waferData.value = await fetchWaferData()
    console.log('Wafer data fetched:', waferData.value.length, 'points')
    
    // Set loading to false first so the container renders
    isLoadingWaferData.value = false
    
    // Wait for DOM to be ready
    await nextTick()
    
    // Use a more robust approach to ensure DOM is ready
    let retryCount = 0
    const maxRetries = 20 // Maximum 2 seconds of retries
    
    const checkAndInit = () => {
      if (waferHeatmapContainer.value && 
          waferHeatmapContainer.value.clientWidth > 0 && 
          waferHeatmapContainer.value.clientHeight > 0) {
        console.log('DOM is ready, initializing wafer heatmap...')
        initWaferHeatmap()
      } else if (retryCount < maxRetries) {
        retryCount++
        setTimeout(checkAndInit, 100)
      } else {
        console.warn('Max retries reached, wafer heatmap initialization failed')
      }
    }
    
    // Start checking after a short delay
    setTimeout(checkAndInit, 200)
    
  } catch (error) {
    console.error('Error initializing data:', error)
    isLoadingWaferData.value = false
  }
}

// Watchers
watch(() => props.chartHeight, () => {
  if (waferHeatmapChart) {
    setTimeout(() => waferHeatmapChart.resize(), 100)
  }
})

// Watch for profile data changes
watch(() => props.profileData, (newProfileData) => {
  console.log('Profile data changed:', newProfileData?.length || 0, 'points')
  if (newProfileData && newProfileData.length > 0) {
    // Update heat map with new profile data
    nextTick(() => {
      initWaferHeatmap()
    })
  }
}, { deep: true })

// Lifecycle
onMounted(() => {
  console.log('EnhancedChartVisualization mounted')
  console.log('Filename:', props.filename)
  initializeData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (waferHeatmapChart) waferHeatmapChart.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.enhanced-charts {
  width: 100%;
  overflow: hidden;
  position: relative;
}

.heatmap-chart {
  border: 1px solid rgba(var(--v-theme-outline), 0.12);
  border-radius: 4px;
  background-color: transparent;
  overflow: hidden;
  min-width: 300px;
  min-height: 300px;
}

.heatmap-chart:hover {
  border-color: rgba(var(--v-theme-primary), 0.3);
}
</style>