<template>
  <div ref="chartContainer" :style="{ width: '100%', height: `${chartHeight}px` }"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as echarts from 'echarts'

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
    default: 400
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const chartContainer = ref(null)
let chartInstance = null

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

  chartInstance = echarts.init(chartContainer.value)

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
      left: props.compact ? '8%' : '10%',
      right: props.compact ? '2%' : '5%',
      bottom: props.compact ? '15%' : '18%',
      top: props.compact ? '10%' : '12%',
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
      data: values,
      itemStyle: {
        color: '#2196f3'
      },
      emphasis: {
        itemStyle: {
          color: '#1976d2'
        }
      }
    }],
    graphic: statistics.value ? [{
      type: 'text',
      left: props.compact ? '8%' : '10%',
      top: props.compact ? '2%' : '3%',
      style: {
        text: `Mean: ${statistics.value.mean} nm\nStd: ${statistics.value.std} nm`,
        fontSize: props.compact ? 11 : 12,
        fill: '#666'
      }
    }] : []
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
</style>