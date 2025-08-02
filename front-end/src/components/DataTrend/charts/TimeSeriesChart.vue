<template>
  <div ref="chartContainer" :style="{ height: chartHeight + 'px' }"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as echarts from 'echarts'
import shineThemeData from '@/plugins/shine.json'

const props = defineProps({
  timeSeriesData: {
    type: Array,  // Array of series objects: [{name: 'site', data: [...]}, ...]
    default: () => []
  },
  selectedColumn: {
    type: String,
    default: ''
  },
  chartHeight: {
    type: Number,
    default: 400
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const chartContainer = ref(null)
let chartInstance = null

// Computed property to format the chart data
const chartData = computed(() => {
  if (!props.timeSeriesData || props.timeSeriesData.length === 0) {
    return { allTimestamps: [], series: [] }
  }

  // Collect all unique timestamps and sort them
  const allTimestampsSet = new Set()
  props.timeSeriesData.forEach(series => {
    if (series && series.data && Array.isArray(series.data)) {
      series.data.forEach(item => {
        if (item && item.timestamp) {
          allTimestampsSet.add(item.timestamp)
        }
      })
    }
  })
  
  const allTimestamps = Array.from(allTimestampsSet).sort((a, b) => {
    return new Date(a) - new Date(b)
  })
  
  // Format timestamps for display (Korean-friendly format: yy/mm/dd hh:mm:ss)
  const formattedTimestamps = allTimestamps.map(timestamp => {
    const date = new Date(timestamp)
    const year = String(date.getFullYear()).slice(-2)
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    
    return `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`
  })
  
  // Process each series
  const processedSeries = props.timeSeriesData.map((series, seriesIndex) => {
    if (!series || !series.data || !Array.isArray(series.data)) {
      return { name: series?.name || `Series ${seriesIndex}`, data: [], rawData: [] }
    }
    
    // Sort series data by timestamp
    const sortedData = [...series.data].sort((a, b) => {
      return new Date(a.timestamp) - new Date(b.timestamp)
    })
    
    // Convert to scatter plot format
    const scatterData = sortedData.map(item => {
      const timestampIndex = allTimestamps.indexOf(item.timestamp)
      return {
        value: [timestampIndex, item.value],
        timestamp: item.timestamp,
        lotId: item.lotId,
        recipe: item.recipe,
        site: item.site
      }
    })
    
    return {
      name: series.name,
      data: scatterData,
      rawData: sortedData
    }
  })

  return { 
    allTimestamps: formattedTimestamps, 
    series: processedSeries 
  }
})

function initChart() {
  if (!chartContainer.value) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  // Register the shine theme
  echarts.registerTheme('shine', shineThemeData)
  
  // Initialize chart with shine theme
  chartInstance = echarts.init(chartContainer.value, 'shine')

  const { allTimestamps, series } = chartData.value

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        const dataItem = params.data
        // Format timestamp to Korean-friendly format
        const date = new Date(dataItem.timestamp)
        const year = String(date.getFullYear()).slice(-2)
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        const hours = String(date.getHours()).padStart(2, '0')
        const minutes = String(date.getMinutes()).padStart(2, '0')
        const seconds = String(date.getSeconds()).padStart(2, '0')
        const formattedTime = `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`
        
        return `
          <div style="padding: 8px;">
            <div style="font-weight: bold; margin-bottom: 4px;">${params.seriesName}</div>
            <div>Time: ${formattedTime}</div>
            <div>Value: ${dataItem.value[1].toFixed(3)} nm</div>
            <div style="color: #666; font-size: 12px; margin-top: 4px;">
              Lot: ${dataItem.lotId || 'N/A'}<br/>
              Recipe: ${dataItem.recipe || 'N/A'}
            </div>
          </div>
        `
      }
    },
    legend: {
      data: series.map(s => s.name),  // Only show original site names
      top: 10,
      textStyle: {
        fontSize: 14,
        fontWeight: 'bold'
      },
      selectedMode: 'multiple'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: allTimestamps,
      name: 'Time',
      nameLocation: 'middle',
      nameGap: 40,
      nameTextStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      },
      axisLabel: {
        rotate: 45,
        fontSize: 13,
        margin: 10,
        interval: 0,
        fontWeight: '500'
      },
      axisTick: {
        alignWithLabel: true,
        length: 8
      }
    },
    yAxis: {
      type: 'value',
      name: `${props.selectedColumn}`,
      nameLocation: 'middle',
      nameGap: 60,
      nameTextStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      },
      axisLabel: {
        formatter: '{value}',
        fontSize: 13,
        fontWeight: '500'
      }
    },
    series: series.flatMap((seriesData, index) => {
      const color = colors[index % colors.length]
      
      return [
        // Line series for connections
        {
          name: `${seriesData.name}_line`,  // Different name to avoid legend conflict
          type: 'line',
          data: seriesData.data.map(item => item.value),
          lineStyle: {
            width: 2,
            color: color
          },
          symbol: 'none', // Hide symbols on line
          showSymbol: false,
          smooth: false,
          silent: true, // Make line non-interactive
          legendHoverLink: false
        },
        // Scatter series for points
        {
          name: seriesData.name,
          type: 'scatter',
          data: seriesData.data,
          symbolSize: 10,
          color: color,
          emphasis: {
            focus: 'series',
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }),
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        type: 'slider',
        start: 0,
        end: 100,
        height: 20,
        bottom: 5
      }
    ]
  }

  // Show loading animation if data is being loaded
  if (props.loading) {
    chartInstance.showLoading({
      text: 'Loading time series data...',
      color: '#1976d2',
      textColor: '#000',
      maskColor: 'rgba(255, 255, 255, 0.8)',
      zlevel: 0
    })
  } else {
    chartInstance.hideLoading()
  }

  chartInstance.setOption(option)
}

function handleResize() {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// Watch for data changes
watch([
  () => props.timeSeriesData,
  () => props.selectedColumn,
  () => props.loading
], () => {
  initChart()
}, { deep: true })

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
/* Chart container will be sized by parent */
</style>