<template>
  <div class="histogram-chart-wrapper">
    <!-- Statistics Box Outside Chart -->
    <div v-if="statistics" class="statistics-box mb-3">
      <v-card variant="outlined" class="pa-4">
        <div class="d-flex align-center justify-space-around">
          <div class="text-center px-3">
            <div class="text-caption text-medium-emphasis mb-1">Mean</div>
            <div class="text-subtitle-1 font-weight-medium">{{ statistics.mean }} nm</div>
          </div>
          <v-divider vertical class="mx-2" />
          <div class="text-center px-3">
            <div class="text-caption text-medium-emphasis mb-1">Std Dev</div>
            <div class="text-subtitle-1 font-weight-medium">{{ statistics.std }} nm</div>
          </div>
          <v-divider vertical class="mx-2" />
          <div class="text-center px-3">
            <div class="text-caption text-medium-emphasis mb-1">Min</div>
            <div class="text-subtitle-1 font-weight-medium">{{ statistics.min }} nm</div>
          </div>
          <v-divider vertical class="mx-2" />
          <div class="text-center px-3">
            <div class="text-caption text-medium-emphasis mb-1">Max</div>
            <div class="text-subtitle-1 font-weight-medium">{{ statistics.max }} nm</div>
          </div>
        </div>
      </v-card>
    </div>
    
    <!-- Chart Container -->
    <div ref="chartContainer" :style="{ width: '100%', height: `${adjustedChartHeight}px` }"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as echarts from 'echarts'
import shineThemeData from '@/plugins/shine.json'

const props = defineProps({
  profileData: {
    type: Array,
    default: () => []
  },
  selectedPoint: {
    type: [Number, String],
    default: null
  },
  chartHeight: {
    type: Number,
    default: 500
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const chartContainer = ref(null)
let chartInstance = null

const adjustedChartHeight = computed(() => {
  // Subtract space for statistics box (approximately 70px)
  const statsBoxHeight = statistics.value ? 70 : 0
  return props.chartHeight - statsBoxHeight
})

const histogramData = computed(() => {
  if (props.profileData.length === 0) return { bins: [], values: [] }
  
  const zValues = props.profileData.map(p => p.z)
  const min = Math.min(...zValues)
  const max = Math.max(...zValues)
  const binCount = 50
  const binSize = (max - min) / binCount
  
  const bins = []
  const values = []
  
  for (let i = 0; i < binCount; i++) {
    const binStart = min + i * binSize
    const binEnd = binStart + binSize
    bins.push(`${binStart.toFixed(2)}-${binEnd.toFixed(2)}`)
    
    const count = zValues.filter(z => z >= binStart && z < binEnd).length
    values.push(count)
  }
  
  return { bins, values }
})

const statistics = computed(() => {
  if (props.profileData.length === 0) return null
  
  const zValues = props.profileData.map(p => p.z)
  const mean = zValues.reduce((a, b) => a + b, 0) / zValues.length
  const std = Math.sqrt(zValues.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / zValues.length)
  
  return {
    mean: mean.toFixed(3),
    std: std.toFixed(3),
    min: Math.min(...zValues).toFixed(3),
    max: Math.max(...zValues).toFixed(3)
  }
})

function initChart() {
  if (!chartContainer.value || props.profileData.length === 0) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  // Register the shine theme
  echarts.registerTheme('shine', shineThemeData)
  
  // Initialize chart with shine theme
  chartInstance = echarts.init(chartContainer.value, 'shine')

  const { bins, values } = histogramData.value

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        const param = params[0]
        return `Range: ${param.name} nm<br/>Count: ${param.value}`
      }
    },
    grid: {
      left: props.compact ? '10%' : '15%',
      right: props.compact ? '5%' : '10%',
      bottom: props.compact ? '18%' : '20%',
      top: props.compact ? '15%' : '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: bins,
      name: 'Z Value (nm)',
      nameLocation: 'middle',
      nameGap: 35,
      axisLabel: {
        rotate: 45,
        interval: Math.floor(bins.length / 8),
        fontSize: props.compact ? 10 : 12
      }
    },
    yAxis: {
      type: 'value',
      name: 'Count',
      nameLocation: 'middle',
      nameGap: 40
    },
    series: [{
      type: 'bar',
      data: values
    }],
    graphic: []
  }

  chartInstance.setOption(option)
}

function handleResize() {
  if (chartInstance) {
    chartInstance.resize()
  }
}

watch(() => props.profileData, () => {
  initChart()
}, { deep: true })

watch(() => props.chartHeight, () => {
  if (chartInstance) {
    chartInstance.resize()
  }
})

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.histogram-chart-wrapper {
  width: 100%;
}

.statistics-box {
  background: transparent;
}

.statistics-box .v-card {
  background: rgba(248, 250, 252, 0.8);
  border: 1px solid #e2e8f0;
}
</style>