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

const processedData = computed(() => {
  if (props.profileData.length === 0) return { data: [], xAxis: [], yAxis: [] }
  
  // Get unique x and y values
  const xValues = [...new Set(props.profileData.map(p => p.x))].sort((a, b) => a - b)
  const yValues = [...new Set(props.profileData.map(p => p.y))].sort((a, b) => a - b)
  
  // Create a map for fast lookup
  const dataMap = new Map()
  props.profileData.forEach(point => {
    dataMap.set(`${point.x},${point.y}`, point.z)
  })
  
  // Create heatmap data
  const heatmapData = []
  xValues.forEach((x, xIndex) => {
    yValues.forEach((y, yIndex) => {
      const z = dataMap.get(`${x},${y}`)
      if (z !== undefined) {
        heatmapData.push([xIndex, yIndex, z])
      }
    })
  })
  
  return {
    data: heatmapData,
    xAxis: xValues.map(v => v.toFixed(2)),
    yAxis: yValues.map(v => v.toFixed(2))
  }
})

function initChart() {
  if (!chartContainer.value || props.profileData.length === 0) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartContainer.value)

  const { data, xAxis, yAxis } = processedData.value

  const option = {
    tooltip: {
      position: 'top',
      formatter: function(params) {
        const [xIndex, yIndex, value] = params.data
        return `X: ${xAxis[xIndex]} µm<br/>Y: ${yAxis[yIndex]} µm<br/>Z: ${value.toFixed(3)} nm`
      }
    },
    grid: {
      left: props.compact ? '8%' : '10%',
      right: props.compact ? '12%' : '15%',
      bottom: props.compact ? '10%' : '12%',
      top: props.compact ? '5%' : '8%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xAxis,
      name: 'X (µm)',
      nameLocation: 'middle',
      nameGap: 25,
      splitArea: {
        show: true
      },
      axisLabel: {
        rotate: 45,
        interval: Math.floor(xAxis.length / 10)
      }
    },
    yAxis: {
      type: 'category',
      data: yAxis,
      name: 'Y (µm)',
      nameLocation: 'middle',
      nameGap: 45,
      splitArea: {
        show: true
      },
      axisLabel: {
        interval: Math.floor(yAxis.length / 10)
      }
    },
    visualMap: {
      min: Math.min(...props.profileData.map(p => p.z)),
      max: Math.max(...props.profileData.map(p => p.z)),
      calculable: true,
      orient: 'vertical',
      right: 0,
      top: 'center',
      text: ['High', 'Low'],
      inRange: {
        color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
      },
      textStyle: {
        fontSize: props.compact ? 10 : 12
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
    }]
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