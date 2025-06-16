# AFM Data Platform 코드베이스 구조 가이드

이 가이드는 웹 개발 초보자를 위해 AFM Data Platform의 현재 코드 구조와 작동 방식을 설명합니다.

## 1. 개발 환경 설정 (Dev Setup)

### 프로젝트 구조
```
front-end/
├── src/                    # 소스 코드
├── package.json           # 프로젝트 설정 및 dependencies
├── vite.config.mjs       # Vite build tool 설정
└── node_modules/         # 설치된 패키지들
```

### 개발 서버 실행하기
```bash
cd front-end
npm install          # 필요한 패키지들을 설치
npm run dev          # 개발 서버 시작 (http://localhost:3000)
```

### 주요 Scripts
- `npm run dev`: 개발 서버 실행 (hot reload 포함)
- `npm run build`: Production용 빌드 생성
- `npm run preview`: 빌드된 파일을 미리보기
- `npm run lint`: 코드 품질 검사 및 자동 수정

## 2. Vuetify 설치 및 설정

### Vuetify란?
Google Material Design을 기반으로 한 Vue.js UI 컴포넌트 라이브러리입니다.

### 설정 파일: `src/plugins/vuetify.js`
```javascript
import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'

export default createVuetify({
  theme: {
    defaultTheme: 'light'
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: { mdi }
  }
})
```

### Font 설정 (vite.config.mjs에서)
```javascript
Fonts({
  google: {
    families: [
      { name: "Roboto", styles: "wght@100;300;400;500;700;900" },
      { name: "Noto Sans KR", styles: "wght@100;300;400;500;700;900" }
    ]
  }
})
```

## 3. Layout 설정

### 앱 구조
Vue 앱은 `src/App.vue`에서 시작하며, 전체 레이아웃을 정의합니다:

```vue
<template>
  <v-app>
    <AppHeader />
    <v-main>
      <RouterView />
    </v-main>
    <AppFooter />
  </v-app>
</template>
```

### AppHeader 컴포넌트 (`src/layouts/AppHeader.vue`)
```vue
<template>
  <v-app-bar color="primary" elevation="2">
    <v-app-bar-title>AFM Data Viewer</v-app-bar-title>
    <v-spacer />
    
    <!-- 네비게이션 버튼들 -->
    <v-btn v-for="link in links" :key="link.label" 
           class="mx-1" size="small" variant="text">
      <v-icon class="mr-1" :icon="link.icon" size="small" />
      <span class="text-caption">{{ link.label }}</span>
    </v-btn>
  </v-app-bar>
</template>

<script setup>
const links = [
  { icon: 'mdi-home', href: null, label: 'Home' },
  { icon: 'mdi-information', href: null, label: 'About' },
  { icon: 'mdi-help-circle', href: null, label: 'Help' },
  { icon: 'mdi-email', href: null, label: 'Contact' }
]
</script>
```

**주요 구성 요소:**
- `v-app-bar`: Vuetify의 상단 앱바 컴포넌트
- `v-app-bar-title`: 앱 제목
- `v-btn`: Material Design 버튼들
- `v-icon`: Material Design 아이콘 (mdi- prefix 사용)

### AppFooter 컴포넌트 (`src/layouts/AppFooter.vue`)
간단한 푸터로 저작권 정보나 추가 링크를 포함할 수 있습니다.

## 4. Main Page 구조 및 설정

### 페이지 구조 (`src/pages/MainPage.vue`)
```vue
<template>
  <v-container fluid class="pa-4">
    <!-- AFM 로고 -->
    <div class="text-center mb-6">
      <img alt="AFM Logo" src="@/assets/afm_logo2.png" 
           style="max-width: 400px; width: 100%; height: auto;">
    </div>

    <v-row justify="center">
      <!-- 왼쪽: 검색 및 결과 -->
      <v-col cols="12" lg="8" md="7">
        <SearchSection />
      </v-col>

      <!-- 오른쪽: 히스토리 및 데이터 그룹핑 -->
      <v-col cols="12" lg="4" md="5">
        <SearchHistoryCard />
        <ViewHistoryCard />
        <DataGroupingCard />
        <SavedGroupsCard />
      </v-col>
    </v-row>
  </v-container>
</template>
```

### 주요 컴포넌트들

#### 1. SearchSection (`src/components/MainPage/SearchSection.vue`)
- 검색 입력 필드
- 검색 결과 표시
- "Add to Group" 및 "View Details" 버튼

#### 2. SearchHistoryCard (`src/components/MainPage/SearchHistoryCard.vue`)
- 최근 검색어 히스토리
- 검색 재실행 기능

#### 3. ViewHistoryCard (`src/components/MainPage/ViewHistoryCard.vue`)
- 조회한 측정 데이터 히스토리
- 빠른 재조회 기능

#### 4. DataGroupingCard (`src/components/MainPage/DataGroupingCard.vue`)
- 선택된 데이터들을 그룹으로 관리
- 트렌드 분석 기능

### State Management (Pinia Store)
```javascript
// src/stores/dataStore.js
export const useDataStore = defineStore('data', () => {
  const searchHistory = ref([])
  const viewHistory = ref([])
  const groupedData = ref([])
  
  function addToSearchHistory(query, resultCount) {
    searchHistory.value.unshift({
      id: Date.now(),
      query,
      resultCount,
      timestamp: new Date()
    })
  }
  
  function addToGroup(measurement) {
    if (!groupedData.value.find(item => item.id === measurement.id)) {
      groupedData.value.push(measurement)
    }
  }
  
  return {
    searchHistory,
    viewHistory, 
    groupedData,
    addToSearchHistory,
    addToGroup
  }
})
```

## 5. Results Page와 ECharts 통합

### ResultPage 구조 (`src/pages/ResultPage.vue`)
```vue
<template>
  <v-container class="pa-6">
    <!-- 헤더 (뒤로가기 버튼 포함) -->
    <div class="d-flex align-center mb-4">
      <v-btn variant="outlined" @click="goBack" class="mr-4">
        <v-icon start>mdi-arrow-left</v-icon>
        Back to Search
      </v-btn>
      <div>
        <h1 class="text-h4">AFM Measurement Details</h1>
        <p class="text-subtitle-1">Group Key: {{ groupKey }}</p>
      </div>
    </div>

    <!-- 측정 정보 -->
    <MeasurementInfo :measurement-info="measurementInfo" />
    
    <!-- 요약 데이터 테이블 -->
    <SummaryDataTable :summary-data="summaryData" />
    
    <!-- 측정 포인트 선택기 -->
    <MeasurementPointsSelector 
      :measurement-points="measurementPoints"
      @point-selected="selectPoint" />
    
    <!-- 차트 시각화 -->
    <ChartVisualization 
      :selected-point="selectedPoint"
      :profile-data="profileData" />
  </v-container>
</template>
```

### ECharts 통합 (`src/components/ResultPage/ChartVisualization.vue`)

#### ECharts 설치 및 Import
```javascript
import * as echarts from 'echarts'
```

#### 차트 컴포넌트 구조
```vue
<template>
  <v-card>
    <v-card-title>
      Profile Data Visualization - Point {{ selectedPoint }}
      
      <!-- 차트 타입 선택 버튼들 -->
      <v-btn-group density="compact">
        <v-btn @click="updateChartType('scatter')">Scatter</v-btn>
        <v-btn @click="updateChartType('heatmap')">Heatmap</v-btn>
        <v-btn @click="updateChartType('histogram')">Histogram</v-btn>
      </v-btn-group>
    </v-card-title>
    
    <v-card-text>
      <!-- 차트 컨테이너 -->
      <div ref="chartContainer" style="width: 100%; height: 500px;"></div>
      
      <!-- 데이터 요약 정보 -->
      <v-row class="mt-4">
        <v-col cols="4">
          <v-card variant="outlined">
            <v-card-subtitle>Data Points</v-card-subtitle>
            <v-card-title>{{ profileData.length.toLocaleString() }}</v-card-title>
          </v-card>
        </v-col>
        <v-col cols="4">
          <v-card variant="outlined">
            <v-card-subtitle>Surface Size</v-card-subtitle>
            <v-card-title>{{ surfaceSize.x }} × {{ surfaceSize.y }} µm</v-card-title>
          </v-card>
        </v-col>
        <v-col cols="4">
          <v-card variant="outlined">
            <v-card-subtitle>Z Range</v-card-subtitle>
            <v-card-title>{{ zRange.min.toFixed(3) }} to {{ zRange.max.toFixed(3) }} nm</v-card-title>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>
```

#### ECharts 구현 세부사항

**1. 차트 초기화**
```javascript
function renderChart() {
  // 기존 차트 제거
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  
  // ECharts 인스턴스 생성
  chartInstance = echarts.init(chartContainer.value)
  
  // 차트 옵션 설정
  let option = {}
  switch (chartType.value) {
    case 'scatter':
      option = createScatterChartOption()
      break
    case 'heatmap':
      option = createHeatmapChartOption()
      break
    case 'histogram':
      option = createHistogramChartOption()
      break
  }
  
  chartInstance.setOption(option, true)
}
```

**2. Scatter Plot 옵션**
```javascript
function createScatterChartOption() {
  const data = props.profileData.map(point => [point.x, point.y, point.z])
  
  return {
    title: {
      text: `AFM Surface Profile - Point ${props.selectedPoint}`,
      left: 'center'
    },
    tooltip: {
      formatter: function(params) {
        const [x, y, z] = params.data
        return `X: ${x.toFixed(3)} µm<br/>Y: ${y.toFixed(3)} µm<br/>Z: ${z.toFixed(6)} nm`
      }
    },
    xAxis: { type: 'value', name: 'X (µm)' },
    yAxis: { type: 'value', name: 'Y (µm)' },
    visualMap: {
      min: zRange.value.min,
      max: zRange.value.max,
      dimension: 2,
      inRange: {
        color: ['#313695', '#4575b4', '#74add1', /* ... 더 많은 색상 */ '#a50026']
      }
    },
    series: [{
      type: 'scatter',
      data: data,
      symbolSize: 2
    }]
  }
}
```

**3. 반응형 차트**
```javascript
// 윈도우 리사이즈 시 차트 크기 조정
function handleResize() {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 컴포넌트 마운트 시 이벤트 리스너 등록
onMounted(() => {
  window.addEventListener('resize', handleResize)
})

// 컴포넌트 언마운트 시 정리
onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  window.removeEventListener('resize', handleResize)
})
```

## 6. 데이터 흐름

### 1. 사용자 검색 → 결과 표시
```
MainPage → SearchSection → searchApi.js → 검색 결과 표시
```

### 2. 세부 정보 조회
```
검색 결과 클릭 → router.push('/result/groupKey') → ResultPage → 데이터 로딩
```

### 3. 차트 데이터 로딩
```
MeasurementPointsSelector → selectPoint() → fetchProfileData() → ChartVisualization
```

## 7. 주요 개념 정리

### Vue 3 Composition API
- `ref()`: 반응형 데이터 생성
- `computed()`: 계산된 속성
- `onMounted()`, `onUnmounted()`: 생명주기 훅

### Vuetify 컴포넌트
- `v-container`, `v-row`, `v-col`: 그리드 시스템
- `v-card`: Material Design 카드
- `v-btn`: 버튼 컴포넌트
- `v-icon`: 아이콘 컴포넌트

### ECharts 통합
- 컨테이너 ref를 통한 DOM 접근
- 차트 인스턴스 생명주기 관리
- 데이터 변경 시 차트 업데이트

이 가이드를 통해 AFM Data Platform의 코드 구조와 각 부분이 어떻게 연결되어 작동하는지 이해할 수 있습니다.