<template>
  <div ref="chartContainer" :style="{ width: '100%', height: `${chartHeight}px` }"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
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

function initChart() {
  if (!chartContainer.value || props.profileData.length === 0) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartContainer.value)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        return `X: ${params.data[0].toFixed(3)} µm<br/>Y: ${params.data[1].toFixed(3)} µm<br/>Z: ${params.data[2].toFixed(3)} nm`
      }
    },
    grid: {
      left: props.compact ? '8%' : '10%',
      right: props.compact ? '2%' : '5%',
      bottom: props.compact ? '10%' : '12%',
      top: props.compact ? '5%' : '8%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: 'X (µm)',
      nameLocation: 'middle',
      nameGap: 25,
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#e0e0e0'
        }
      }
    },
    yAxis: {
      type: 'value',
      name: 'Y (µm)',
      nameLocation: 'middle',
      nameGap: 35,
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#e0e0e0'
        }
      }
    },
    visualMap: {
      min: Math.min(...props.profileData.map(p => p.z)),
      max: Math.max(...props.profileData.map(p => p.z)),
      dimension: 2,
      orient: 'vertical',
      right: 0,
      top: 'center',
      text: ['High', 'Low'],
      calculable: true,
      inRange: {
        color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
      },
      textStyle: {
        fontSize: props.compact ? 10 : 12
      }
    },
    series: [{
      type: 'scatter',
      symbolSize: props.compact ? 3 : 5,
      data: props.profileData.map(point => [point.x, point.y, point.z]),
      itemStyle: {
        opacity: 0.8
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