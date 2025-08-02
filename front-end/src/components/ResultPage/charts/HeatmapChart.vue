<template>
  <div ref="chartContainer" :style="{ width: '100%', height: `${chartHeight}px` }"></div>
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
    default: 700
  },
  compact: {
    type: Boolean,
    default: false
  },
  clickable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['point-selected'])

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

  // Register the shine theme
  echarts.registerTheme('shine', shineThemeData)

  // Initialize chart with shine theme
  chartInstance = echarts.init(chartContainer.value, 'shine')

  const { data, xAxis, yAxis } = processedData.value

  // Use responsive margins that adapt to container size
  const containerWidth = chartContainer.value.offsetWidth
  const containerHeight = chartContainer.value.offsetHeight

  // Simple percentage-based margins for better data visualization
  const leftMargin = '10%'
  const rightMargin = '15%'  // Space for visual map
  const topMargin = '10%'
  const bottomMargin = '15%'

  const option = {
    tooltip: {
      position: 'top',
      formatter: function (params) {
        const [xIndex, yIndex, value] = params.data
        return `X: ${xAxis[xIndex]} µm<br/>Y: ${yAxis[yIndex]} µm<br/>Z: ${value.toFixed(3)} nm`
      }
    },
    grid: {
      left: leftMargin,
      right: rightMargin,
      top: topMargin,
      bottom: bottomMargin,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xAxis,
      name: 'X',
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
      name: 'Y',
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
      right: '5%',
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

  // Add click event listener if clickable
  if (props.clickable) {
    chartInstance.on('click', function (params) {
      if (params.componentType === 'series') {
        const [xIndex, yIndex, value] = params.data
        const xValue = xAxis[xIndex]
        const yValue = yAxis[yIndex]

        // Find the original data point
        const originalPoint = props.profileData.find(p =>
          Math.abs(p.x - parseFloat(xValue)) < 0.001 &&
          Math.abs(p.y - parseFloat(yValue)) < 0.001
        )

        if (originalPoint) {
          // Create a point object similar to what EnhancedChartVisualization emitted
          const pointNumber = (yIndex * xAxis.length + xIndex) + 1
          const emitPoint = {
            ...originalPoint,
            point: pointNumber,
            x: parseFloat(xValue),
            y: parseFloat(yValue),
            value: value
          }

          emit('point-selected', emitPoint)
        }
      }
    })
  }
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

<style scoped></style>
