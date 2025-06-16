# **데이터 시각화 - ECharts 연동하기**

## **ECharts 소개**

### **ECharts란 무엇인가?**

ECharts(Enterprise Charts)는 Apache 소프트웨어 재단에서 관리하는 오픈소스 데이터 시각화 라이브러리입니다. 원래 중국의 Baidu에서 개발했으며, 현재는 Apache 프로젝트로 전 세계적으로 활발히 사용되고 있습니다. 반도체 장비에서 생성되는 복잡한 데이터를 직관적으로 시각화하는 데 매우 적합한 도구입니다.

**💡 추가 학습 자료**
ECharts 공식 홈페이지(https://echarts.apache.org/examples/)에서 다양한 차트와 예제들을 볼 수 있으니 직접 코드를 확인하면서 구현하길 추천합니다.

### **ECharts의 주요 특징**

**강력한 성능** ECharts는 Canvas와 SVG 렌더링을 모두 지원하여 대용량 데이터도 부드럽게 표현할 수 있습니다. 특히 AFM 측정 데이터처럼 수만 개의 데이터 포인트를 가진 경우에도 성능 저하 없이 시각화가 가능합니다. 스트리밍 데이터나 실시간 업데이트가 필요한 대시보드에서도 안정적인 성능을 보여줍니다.

**다양한 차트 타입** 기본적인 선 그래프, 막대 그래프부터 히트맵, 3D 차트, 지도 기반 시각화까지 30가지 이상의 차트 타입을 제공합니다. 반도체 공정 데이터 분석에 자주 사용되는 박스플롯, 산점도 행렬, 평행 좌표계 등 고급 차트도 지원합니다.

**인터랙티브 기능** 사용자가 차트와 상호작용할 수 있는 다양한 기능을 제공합니다. 데이터 줌, 드래그, 툴팁, 범례 필터링 등으로 사용자가 원하는 데이터를 자유롭게 탐색할 수 있습니다. 이는 엔지니어가 특정 구간의 데이터를 세밀하게 분석할 때 매우 유용합니다.

### **다른 차트 라이브러리와의 비교**

| 특징             | ECharts           | Chart.js       | D3.js              | Highcharts  |
| ---------------- | ----------------- | -------------- | ------------------ | ----------- |
| **학습 곡선**    | 중간              | 쉬움           | 어려움             | 중간        |
| **차트 종류**    | 매우 많음 (30+)   | 기본적 (8개)   | 무제한 (직접 구현) | 많음 (20+)  |
| **성능**         | 매우 우수         | 보통           | 우수               | 우수        |
| **커스터마이징** | 높음              | 중간           | 매우 높음          | 높음        |
| **라이선스**     | Apache 2.0 (무료) | MIT (무료)     | BSD (무료)         | 상업용 유료 |
| **파일 크기**    | 큼 (\~1MB)        | 작음 (\~200KB) | 중간 (\~500KB)     | 큼 (\~1MB)  |

### **ECharts를 선택한 이유**

SK hynix ITC의 AFM Data Viewer 프로젝트에서 ECharts를 선택한 주요 이유는 다음과 같습니다:

1. **무료 라이선스**: Apache 2.0 라이선스로 상업적 사용에 제약이 없습니다.
2. **풍부한 차트 타입**: 반도체 데이터 분석에 필요한 다양한 시각화를 한 라이브러리로 해결할 수 있습니다.
3. **뛰어난 성능**: 대용량 측정 데이터를 처리해도 브라우저가 느려지지 않습니다.
4. **Vue.js와의 호환성**: Vue 컴포넌트로 쉽게 통합할 수 있습니다.

## **설치 및 기본 설정**

### **ECharts 설치하기**

프로젝트 디렉토리에서 다음 명령어를 실행합니다:

```bash
# ECharts 설치
npm install echarts
```

### **기본 설정**

**전체 ECharts 가져오기 (간단한 방법)**

```javascript
// main.js 또는 컴포넌트에서
import * as echarts from "echarts";

// 전역으로 사용하고 싶은 경우
app.config.globalProperties.$echarts = echarts;
```

**필요한 모듈만 가져오기 (권장 \- 번들 크기 최적화)**

```javascript
// 필요한 차트와 컴포넌트만 import
import { init } from "echarts/core";
import { LineChart, BarChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

// ECharts에 사용할 기능들 등록
echarts.use([
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  CanvasRenderer,
]);
```

### **Vue 컴포넌트에서 ECharts 통합하기**

## **핵심 통합 개념들**

### **1. 차트 인스턴스 생명주기 관리**

ECharts 인스턴스는 적절한 생명주기 (life cycle) 관리가 필수입니다:

```javascript
<template>
  <div ref="chartContainer" style="width: 100%; height: 400px;"></div>
</template>

<script setup>
import * as echarts from 'echarts'
import { ref, onMounted, onBeforeUnmount } from 'vue'

const chartContainer = ref(null)
const chart = ref(null)

const initChart = () => {
  // 기존 차트가 있다면 먼저 해제
  if (chart.value) {
    chart.value.dispose()
  }

  // 새 인스턴스 생성
  chart.value = echarts.init(chartContainer.value)

  // 차트 옵션은 ECharts 공식 홈페이지 예제 참조
  // https://echarts.apache.org/examples/
}

onMounted(() => {
  initChart()
})

onBeforeUnmount(() => {
  // 메모리 누수 방지를 위한 정리
  if (chart.value) {
    chart.value.dispose()
    chart.value = null
  }
})
</script>
```

**🔥 중요한 메모리 관리 포인트:**

- `onBeforeUnmount`에서 반드시 `dispose()` 호출
- 차트 참조를 `null`로 초기화
- 여러 차트가 있는 페이지에서는 더욱 중요

### **2. 반응형 크기 조정**

사용자가 브라우저 크기를 변경하거나 Vuetify 레이아웃이 변할 때 차트 크기 자동 조정:

```javascript
mounted() {
  this.initChart()

  // 윈도우 리사이즈 이벤트 등록
  window.addEventListener('resize', this.handleResize)
},
beforeUnmount() {
  window.removeEventListener('resize', this.handleResize)
  if (this.chart) {
    this.chart.dispose()
  }
},
methods: {
  handleResize() {
    if (this.chart) {
      this.chart.resize()
    }
  }
}
```

## **차트 컴포넌트 만들기**

### **재사용 가능한 차트 컴포넌트 설계**

실제 프로젝트에서는 차트를 재사용 가능한 컴포넌트로 만드는 것이 중요합니다. 다음은 AFM 데이터 뷰어에서 사용할 수 있는 범용 차트 컴포넌트 예제입니다.

**BaseChart.vue - 기본 차트 컴포넌트**

```javascript
<template>
  <div class="chart-container">
    <div ref="chartRef" :style="{ width: width, height: height }"></div>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  // 차트 옵션
  option: {
    type: Object,
    required: true
  },
  // 차트 크기
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: '400px'
  },
  // 테마
  theme: {
    type: String,
    default: 'light'
  }
})

const chart = ref(null)
const chartRef = ref(null)
const resizeObserver = ref(null)

const initChart = () => {
  // 기존 차트가 있으면 제거
  if (chart.value) {
    chart.value.dispose()
  }

  // 새 차트 인스턴스 생성
  chart.value = echarts.init(chartRef.value, props.theme)
  updateChart(props.option)
}

const updateChart = (option) => {
  if (chart.value && option) {
    chart.value.setOption(option, true)
  }
}

const addResizeListener = () => {
  window.addEventListener('resize', handleResize)
  // Vuetify 레이아웃 변경 감지
  resizeObserver.value = new ResizeObserver(handleResize)
  resizeObserver.value.observe(chartRef.value)
}

const removeResizeListener = () => {
  window.removeEventListener('resize', handleResize)
  if (resizeObserver.value) {
    resizeObserver.value.disconnect()
  }
}

const handleResize = () => {
  if (chart.value) {
    chart.value.resize()
  }
}

// Watch for option changes
watch(() => props.option, (newOption) => {
  updateChart(newOption)
}, { deep: true })

// Watch for theme changes
watch(() => props.theme, () => {
  initChart()
})

onMounted(() => {
  initChart()
  addResizeListener()
})

onBeforeUnmount(() => {
  removeResizeListener()
  if (chart.value) {
    chart.value.dispose()
    chart.value = null
  }
})
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
}
</style>
```

### **특화된 차트 컴포넌트 만들기**

BaseChart를 확장하여 특정 용도의 차트를 만들 수 있습니다:

**AFMLineChart.vue - AFM 측정 데이터용 라인 차트**

````javascript
<template>
  <v-card>
    <v-card-title>
      {{ title }}
      <v-spacer></v-spacer>
      <v-btn icon @click="exportChart">
        <v-icon>mdi-download</v-icon>
      </v-btn>
    </v-card-title>
    <v-card-text>
      <base-chart
        :option="chartOption"
        :height="height"
        ref="baseChart"
      />
    </v-card-text>
  </v-card>
</template>

<script setup>

import BaseChart from './BaseChart.vue'
import { computed, ref } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: 'AFM 측정 데이터'
  },
  data: {
    type: Array,
    required: true
  },
  xAxisLabel: {
    type: String,
    default: '측정 위치 (nm)'
  },
  yAxisLabel: {
    type: String,
    default: '높이 (nm)'
  },
  height: {
    type: String,
    default: '400px'
  }
})

const baseChart = ref(null)

const chartOption = computed(() => {
  return {
    title: {
      show: false // 카드 타이틀 사용
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const point = params[0]
        return `${props.xAxisLabel}: ${point.axisValue}<br/>
                ${props.yAxisLabel}: ${point.value} nm`
      }
    },
    grid: {
      left: '10%',
      right: '5%',
      bottom: '15%',
      top: '10%'
    },
    xAxis: {
      type: 'category',
      name: props.xAxisLabel,
      nameLocation: 'middle',
      nameGap: 30,
      data: props.data.map(item => item.x)
    },
    yAxis: {
      type: 'value',
      name: props.yAxisLabel,
      nameLocation: 'middle',
      nameGap: 50
    },
    series: [{
      type: 'line',
      smooth: true,
      symbol: 'none',
      lineStyle: {
        color: '#1976D2',
        width: 2
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(25, 118, 210, 0.3)' },
            { offset: 1, color: 'rgba(25, 118, 210, 0.05)' }
          ]
        }
      },
      data: props.data.map(item => item.y)
    }],
    dataZoom: [{
      type: 'inside',
      start: 0,
      end: 100
    }, {
      type: 'slider',
      start: 0,
      end: 100
    }]
  }
})

const exportChart = () => {
  if (baseChart.value && baseChart.value.chart) {
    const url = baseChart.value.chart.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#fff'
    })

    const link = document.createElement('a')
    link.download = `${props.title}_${new Date().toISOString()}.png`
    link.href = url
    link.click()
  }
}
</script>

## **Vue와 ECharts 통합 시 고려사항**

### **차트 타입 선택 전략**

ECharts는 다양한 차트 타입을 제공하며, 각 차트의 구체적인 구현 코드는 [ECharts 공식 홈페이지](https://echarts.apache.org/examples/)에서 확인할 수 있습니다. Vue 통합에서 중요한 것은 차트 자체가 아니라 **어떻게 효과적으로 관리하느냐**입니다.

**반도체 데이터 분석에 적합한 차트 타입들:**

- **히트맵 (Heatmap)**: AFM 표면 형상 데이터, 웨이퍼 맵 표시
- **산점도 (Scatter Plot)**: 측정값 분포, 상관관계 분석
- **박스플롯 (Box Plot)**: 데이터 분포와 이상치 파악
- **선 그래프**: 시간별 트렌드 분석
- **복합 차트**: 여러 데이터를 동시 비교

### **차트 선택 시 Vue 통합 관점에서 고려할 점**

**1. 데이터 업데이트 빈도**
```javascript
// 실시간 업데이트가 필요한 차트
const realtimeCharts = ['line', 'bar'] // 빠른 업데이트 가능

// 정적 분석용 차트
const staticCharts = ['heatmap', 'boxplot'] // 대용량 데이터 처리 우수
````

**2. 렌더링 성능**

```javascript
// 대용량 데이터용 설정
const performanceOption = {
  animation: false, // 애니메이션 비활성화로 성능 향상
  progressive: 1000, // 점진적 렌더링 임계값
  progressiveThreshold: 3000,
};
```

**3. 상호작용 복잡도**

```javascript
// 복잡한 상호작용이 필요한 경우
const interactiveCharts = {
  tooltip: true,
  dataZoom: true,
  brush: true, // 데이터 선택 기능
  legend: { type: "scroll" },
};
```

## **반응형 차트 구현 전략**

### **화면 크기 대응 방법**

Vuetify와 ECharts를 함께 사용할 때 반응형 차트를 구현하는 핵심 전략입니다.

**Vue Composition API를 활용한 반응형 감지**

```javascript
<script>

import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useDisplay } from 'vuetify'

const { mobile, tablet, desktop } = useDisplay()
const chartContainer = ref(null)
const chart = ref(null)

// Vuetify의 브레이크포인트를 활용한 반응형 옵션
const responsiveOption = computed(() => {
  const baseOption = {
    // 기본 차트 설정
  }

  // 모바일 최적화
  if (mobile.value) {
    return {
      ...baseOption,
      grid: { left: '15%', right: '5%', bottom: '25%' },
      legend: { orient: 'horizontal', bottom: 0 },
      tooltip: { trigger: 'axis' } // 모바일에서 더 쉬운 상호작용
    }
  }

  // 태블릿 최적화
  if (tablet.value) {
    return {
      ...baseOption,
      grid: { left: '12%', right: '8%', bottom: '15%' }
    }
  }

  // 데스크톱 기본 설정
  return baseOption
})

// 화면 크기 변경 시 차트 리사이즈
const handleResize = () => {
  if (chart.value) {
    chart.value.resize()
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})
</script>
```

### **성능 최적화와 메모리 관리**

Vue 애플리케이션에서 ECharts를 사용할 때 가장 중요한 부분입니다.

**대용량 데이터 처리 전략**

```javascript
<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'

// 데이터 최적화를 위한 컴포저블 함수
const useChartDataOptimization = () => {
  const maxDataPoints = ref(1000)

  const optimizeData = (data) => {
    if (data.length <= maxDataPoints.value) return data

    // 다운샘플링: LTTB 알고리즘 적용
    const step = Math.ceil(data.length / maxDataPoints.value)
    return data.filter((_, index) => index % step === 0)
  }

  const getPerformanceOption = (baseOption, dataSize) => {
    if (dataSize > 5000) {
      return {
        ...baseOption,
        animation: false, // 대용량 데이터에서 애니메이션 비활성화
        series: baseOption.series.map(series => ({
          ...series,
          large: true,
          largeThreshold: 2000,
          progressive: 5000,
          progressiveThreshold: 10000
        }))
      }
    }
    return baseOption
  }

  return { optimizeData, getPerformanceOption }
}
</script>
```

**메모리 누수 방지**

```javascript
<script>

import { ref, onBeforeUnmount } from 'vue'

// 차트 인스턴스 관리 컴포저블
const useChartManager = () => {
  const charts = ref(new Map())

  const createChart = (id, container, option) => {
    // 기존 차트 정리
    if (charts.value.has(id)) {
      charts.value.get(id).dispose()
    }

    const chart = echarts.init(container)
    chart.setOption(option)
    charts.value.set(id, chart)

    return chart
  }

  const removeChart = (id) => {
    if (charts.value.has(id)) {
      charts.value.get(id).dispose()
      charts.value.delete(id)
    }
  }

  const cleanupAllCharts = () => {
    charts.value.forEach(chart => chart.dispose())
    charts.value.clear()
  }

  // 컴포넌트 언마운트 시 자동 정리
  onBeforeUnmount(() => {
    cleanupAllCharts()
  })

  return { charts, createChart, removeChart, cleanupAllCharts }
}
</script>
```

**데이터 업데이트 최적화**

```javascript
// 데이터 변경 감지 및 효율적 업데이트
const useChartDataUpdate = (chart) => {
  const updateChart = (newData, updateType = "replace") => {
    if (!chart.value) return;

    if (updateType === "append") {
      // 실시간 데이터 추가 (차트 전체 재렌더링 방지)
      chart.value.appendData({
        seriesIndex: 0,
        data: newData,
      });
    } else {
      // 전체 데이터 교체 (notMerge: false로 성능 향상)
      chart.value.setOption(
        {
          series: [{ data: newData }],
        },
        { notMerge: false, lazyUpdate: true }
      );
    }
  };

  return { updateChart };
};
```

### **실시간 데이터 관리 전략**

AFM 장비에서 실시간으로 들어오는 데이터를 효율적으로 처리하는 Vue 통합 방법입니다.

**실시간 데이터 스트리밍 컴포저블**

```javascript
<script>

import { ref, onMounted, onBeforeUnmount } from 'vue'

const useRealtimeChart = (chart, maxDataPoints = 1000) => {
  const realtimeData = ref([])
  const isUpdating = ref(false)
  const updateInterval = ref(null)
  const errorCount = ref(0)

  // 데이터 버퍼 관리
  const addDataPoint = (newPoint) => {
    realtimeData.value.push(newPoint)

    // 메모리 관리: 최대 데이터 포인트 제한
    if (realtimeData.value.length > maxDataPoints) {
      realtimeData.value = realtimeData.value.slice(-maxDataPoints)
    }
  }

  // 배치 업데이트로 성능 향상
  const updateChart = () => {
    if (!chart.value || isUpdating.value) return

    isUpdating.value = true

    requestAnimationFrame(() => {
      chart.value.setOption({
        series: [{
          data: realtimeData.value
        }]
      }, {
        notMerge: false,
        lazyUpdate: true,
        silent: true // 이벤트 트리거 방지로 성능 향상
      })

      isUpdating.value = false
    })
  }

  // 에러 처리와 재연결 로직
  const fetchRealtimeData = async () => {
    try {
      const response = await fetch('/api/afm/realtime')
      if (!response.ok) throw new Error(`HTTP ${response.status}`)

      const newData = await response.json()
      newData.forEach(addDataPoint)
      updateChart()

      errorCount.value = 0 // 성공 시 에러 카운트 리셋
    } catch (error) {
      errorCount.value++
      console.error(`실시간 데이터 오류 (${errorCount.value}회):`, error)

      // 연속 에러 시 업데이트 간격 조정
      if (errorCount.value > 5) {
        stopRealtimeUpdate()
        setTimeout(startRealtimeUpdate, 5000) // 5초 후 재시도
      }
    }
  }

  const startRealtimeUpdate = () => {
    if (updateInterval.value) return

    updateInterval.value = setInterval(fetchRealtimeData, 1000)
  }

  const stopRealtimeUpdate = () => {
    if (updateInterval.value) {
      clearInterval(updateInterval.value)
      updateInterval.value = null
    }
  }

  onMounted(startRealtimeUpdate)
  onBeforeUnmount(stopRealtimeUpdate)

  return {
    realtimeData,
    startRealtimeUpdate,
    stopRealtimeUpdate,
    isUpdating
  }
}
</script>
```

### **Vuetify와 ECharts 통합 전략**

Vue 3 + Vuetify + ECharts의 효과적인 통합 방법입니다.

**테마 연동 시스템**

```javascript
<script setup>

import { computed } from 'vue'
import { useTheme } from 'vuetify'

const useChartTheme = () => {
  const theme = useTheme()

  // Vuetify 테마에 따른 ECharts 설정
  const chartTheme = computed(() => {
    return theme.global.name.value === 'dark' ? 'dark' : 'light'
  })

  // 테마별 색상 팔레트 매핑
  const chartColors = computed(() => {
    const currentTheme = theme.current.value
    return {
      primary: currentTheme.colors.primary,
      secondary: currentTheme.colors.secondary,
      success: currentTheme.colors.success,
      warning: currentTheme.colors.warning,
      error: currentTheme.colors.error,
      background: currentTheme.colors.background,
      surface: currentTheme.colors.surface
    }
  })

  // ECharts 옵션에 테마 색상 적용
  const applyThemeToOption = (baseOption) => {
    return {
      ...baseOption,
      backgroundColor: chartColors.value.background,
      textStyle: {
        color: currentTheme.colors.onBackground
      },
      color: [
        chartColors.value.primary,
        chartColors.value.secondary,
        chartColors.value.success,
        chartColors.value.warning,
        chartColors.value.error
      ]
    }
  }

  return { chartTheme, chartColors, applyThemeToOption }
}
</script>
```

**레이아웃 통합과 사용자 경험**

```javascript
<template>
  <v-container fluid>
    <v-row>
      <v-col
        cols="12" md="6" lg="4"
        v-for="chart in charts"
        :key="chart.id"
      >
        <v-card :loading="chart.loading" elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon :color="chart.status.color" class="mr-2">
              {{ chart.status.icon }}
            </v-icon>
            {{ chart.title }}
            <v-spacer></v-spacer>

            <!-- 차트별 액션 메뉴 -->
            <v-menu>
              <template v-slot:activator="{ props }">
                <v-btn icon="mdi-dots-vertical" v-bind="props"></v-btn>
              </template>
              <v-list>
                <v-list-item @click="exportChart(chart.id)">
                  <v-list-item-title>이미지로 저장</v-list-item-title>
                </v-list-item>
                <v-list-item @click="toggleFullscreen(chart.id)">
                  <v-list-item-title>전체화면</v-list-item-title>
                </v-list-item>
                <v-list-item @click="refreshChart(chart.id)">
                  <v-list-item-title>새로고침</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-card-title>

          <v-card-text>
            <!-- 에러 상태 표시 -->
            <v-alert
              v-if="chart.error"
              type="error"
              density="compact"
              class="mb-3"
            >
              차트 로드 오류: {{ chart.error }}
            </v-alert>

            <!-- 차트 컨테이너 -->
            <div
              :ref="`chart-${chart.id}`"
              :style="{ height: getChartHeight(chart.type) }"
              class="chart-container"
            >
              <!-- 로딩 상태 -->
              <v-skeleton-loader
                v-if="chart.loading"
                type="image"
              ></v-skeleton-loader>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
```

## **에러 처리와 사용자 경험 개선**

Vue와 ECharts 통합에서 중요한 것은 안정적인 에러 처리와 우수한 사용자 경험입니다.

### **에러 처리 전략**

```javascript
<script setup>
import { ref, onMounted } from 'vue'

const useChartErrorHandling = () => {
  const chartErrors = ref(new Map())
  const retryAttempts = ref(new Map())
  const maxRetries = 3

  const handleChartError = (chartId, error) => {
    console.error(`Chart ${chartId} error:`, error)
    chartErrors.value.set(chartId, error.message)

    // 자동 재시도 로직
    const attempts = retryAttempts.value.get(chartId) || 0
    if (attempts < maxRetries) {
      retryAttempts.value.set(chartId, attempts + 1)
      setTimeout(() => {
        retryChart(chartId)
      }, 2000 * Math.pow(2, attempts)) // 지수 백오프
    }
  }

  const retryChart = (chartId) => {
    chartErrors.value.delete(chartId)
    // 차트 재초기화 로직
  }

  const clearError = (chartId) => {
    chartErrors.value.delete(chartId)
    retryAttempts.value.delete(chartId)
  }

  return {
    chartErrors,
    handleChartError,
    retryChart,
    clearError
  }
}
</script>
```

## **통합 베스트 프랙티스 요약**

### **1. 생명주기 관리**

- `onMounted`에서 차트 초기화
- `onBeforeUnmount`에서 확실한 정리
- 컴포넌트 재사용 시 적절한 초기화

### **2. 데이터 관리**

- 대용량 데이터는 다운샘플링 적용
- 실시간 데이터는 버퍼 크기 제한
- 메모리 누수 방지를 위한 적극적 정리

### **3. 사용자 경험**

- 로딩 상태 표시 (스켈레톤 또는 스피너)
- 에러 상황 명확한 피드백
- 반응형 디자인으로 모든 기기 지원

### **4. 성능 최적화**

- 차트 업데이트 시 `lazyUpdate: true` 사용
- 애니메이션은 필요시에만 활성화
- `requestAnimationFrame`으로 렌더링 최적화

### **5. Vuetify 통합**

- 테마 변경 시 차트 색상 자동 동기화
- 카드 레이아웃으로 일관된 UI 제공
- 반응형 그리드로 다양한 화면 크기 대응

**📊 실제 구현 시에는 ECharts 공식 홈페이지의 예제를 참고하여 구체적인 차트 코드를 작성하고, 여기서 제시한 Vue 통합 패턴을 적용하는 것이 가장 효율적입니다.**

```

```
