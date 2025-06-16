# 페이지와 컴포넌트 이해하기

## 페이지 vs 컴포넌트의 차이점

### 📄 **페이지 (Pages)**
- **역할**: 사용자가 직접 방문하는 완전한 화면
- **특징**: URL이 있고, 브라우저 주소창에서 접근 가능
- **위치**: `src/pages/` 폴더
- **예시**: 검색 페이지, 로그인 페이지, 마이페이지

### 🧩 **컴포넌트 (Components)**
- **역할**: 페이지의 일부분을 담당하는 재사용 가능한 조각
- **특징**: 여러 페이지에서 공통으로 사용
- **위치**: `src/components/`, `src/layouts/` 폴더
- **예시**: 버튼, 헤더, 검색창, 차트

**비유로 이해하기** 🏠
- **페이지**: 집 전체 (거실, 침실, 주방)
- **컴포넌트**: 가구나 가전제품 (소파, 침대, 냉장고)
  - 소파는 거실에도, 침실에도 놓을 수 있음 (재사용)

## 우리 프로젝트의 페이지들

### 1. MainPage.vue - 메인 검색 페이지

**URL**: `/` (홈페이지)
**역할**: AFM 데이터를 검색하고 결과를 보여주는 첫 화면

```vue
<template>
  <v-container fluid class="pa-4">
    <!-- 로고 -->
    <div class="text-center mb-6">
      <img src="@/assets/afm_logo2.png" alt="AFM Logo">
    </div>

    <v-row justify="center">
      <!-- 왼쪽: 검색 + 결과 -->
      <v-col cols="12" lg="8" md="7">
        <!-- 검색 카드 -->
        <v-card class="pa-6 mb-4">
          <v-text-field 
            v-model="searchQuery"
            @keyup.enter="performSearch"
            label="Search AFM measurements..."
          />
          <v-btn @click="performSearch">Search</v-btn>
        </v-card>
        
        <!-- 검색 결과 -->
        <v-card v-if="searchResults.length > 0">
          <!-- 결과 목록 표시 -->
        </v-card>
      </v-col>

      <!-- 오른쪽: 기록 + 그룹핑 -->
      <v-col cols="12" lg="4" md="5">
        <!-- 검색 기록 -->
        <v-card class="mb-4">
          <v-card-title>Search History</v-card-title>
          <!-- 기록 목록 -->
        </v-card>
        
        <!-- 데이터 그룹핑 -->
        <v-card>
          <v-card-title>Data Grouping</v-card-title>
          <!-- 그룹핑된 데이터 -->
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useDataStore } from '@/stores/dataStore.js'

// 반응형 데이터
const searchQuery = ref('')
const searchResults = ref([])
const isSearching = ref(false)

// 외부 기능 가져오기
const router = useRouter()
const dataStore = useDataStore()

// 함수들
function performSearch() {
  // 검색 로직
}

function viewDetails(measurement) {
  // 상세 페이지로 이동
  router.push(`/result/${measurement.group_key}`)
}
</script>
```

**주요 기능**:
- ✅ AFM 데이터 검색
- ✅ 실시간 검색 결과 표시
- ✅ 검색 기록 저장 및 표시
- ✅ 데이터 그룹핑 기능
- ✅ 상세 페이지로 이동

### 2. ResultPage.vue - 결과 상세 페이지

**URL**: `/result/:groupKey` (예: `/result/R3_T7HQK84T1_14`)
**역할**: 선택한 측정 데이터의 자세한 정보를 보여줌

```vue
<template>
  <v-container class="pa-6">
    <!-- 뒤로가기 버튼 -->
    <div class="d-flex align-center mb-4">
      <v-btn @click="goBack" class="mr-4">
        <v-icon left>mdi-arrow-left</v-icon>
        Back to Search
      </v-btn>
      
      <div>
        <h1>AFM Measurement Details</h1>
        <p>Group Key: {{ groupKey }}</p>
      </div>
    </div>

    <!-- 측정 정보 카드 -->
    <v-card class="mb-4">
      <v-card-title>Measurement Information</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-list>
              <v-list-item>
                <v-list-item-title>Fab ID</v-list-item-title>
                <v-list-item-subtitle>{{ measurementInfo.fab }}</v-list-item-subtitle>
              </v-list-item>
              <!-- 다른 정보들... -->
            </v-list>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 데이터 시각화 (미래 구현 예정) -->
    <v-card>
      <v-card-title>AFM Data Visualization</v-card-title>
      <v-card-text>
        <div class="text-center pa-8">
          <v-icon size="64">mdi-chart-scatter-plot</v-icon>
          <p>데이터 시각화가 여기에 구현될 예정입니다</p>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// URL에서 groupKey 가져오기
const groupKey = ref(route.params.groupKey)
const measurementInfo = ref({})

// 페이지가 로드될 때 실행
onMounted(() => {
  // groupKey를 파싱해서 정보 추출
  const parts = groupKey.value.split('_')
  if (parts.length >= 3) {
    measurementInfo.value = {
      fab: parts[0],
      lot_id: parts[1],
      wf_id: parts[2],
      // ...
    }
  }
})

function goBack() {
  router.push('/')
}
</script>
```

**주요 기능**:
- ✅ URL에서 그룹키 파라미터 읽기
- ✅ 측정 데이터 상세 정보 표시
- ✅ 뒤로가기 기능
- 🔄 데이터 시각화 (구현 예정)

### 3. DataTrendPage.vue - 트렌드 분석 페이지

**URL**: `/result/data_trend`
**역할**: 그룹핑된 여러 데이터를 함께 분석

```vue
<template>
  <v-container class="pa-6">
    <!-- 헤더 -->
    <div class="d-flex align-center mb-4">
      <v-btn @click="goBack" class="mr-4">
        <v-icon left>mdi-arrow-left</v-icon>
        Back to Search
      </v-btn>
      
      <div>
        <h1>AFM Data Trend Analysis</h1>
        <p>Comparing {{ dataStore.groupedCount }} measurements</p>
      </div>
    </div>

    <!-- 선택된 측정들 -->
    <v-card class="mb-4">
      <v-card-title>Selected Measurements</v-card-title>
      <v-card-text>
        <v-row>
          <v-col 
            v-for="item in dataStore.groupedData" 
            cols="12" sm="6" md="4"
          >
            <v-card variant="outlined">
              <v-card-title>{{ item.fab }} - {{ item.lot_id }}</v-card-title>
              <!-- 측정 정보 -->
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 분석 탭들 -->
    <v-card>
      <v-tabs v-model="activeTab">
        <v-tab value="time-series">Time Series</v-tab>
        <v-tab value="comparison">Parameter Comparison</v-tab>
        <v-tab value="correlation">Correlation Analysis</v-tab>
      </v-tabs>

      <v-window v-model="activeTab">
        <!-- 각 탭별 내용 -->
      </v-window>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useDataStore } from '@/stores/dataStore.js'

const router = useRouter()
const dataStore = useDataStore()
const activeTab = ref('time-series')

function goBack() {
  router.push('/')
}
</script>
```

**주요 기능**:
- ✅ 그룹핑된 데이터 목록 표시
- ✅ 탭별 분석 화면
- 🔄 실제 차트/그래프 (구현 예정)

## 우리 프로젝트의 컴포넌트들

### 1. AppHeader.vue - 상단 헤더

**위치**: `src/layouts/AppHeader.vue`
**역할**: 모든 페이지 상단에 공통으로 나타나는 네비게이션

```vue
<template>
  <v-app-bar color="primary" elevation="2">
    <v-app-bar-title>AFM Data Viewer</v-app-bar-title>

    <v-spacer />

    <!-- 네비게이션 링크들 -->
    <v-btn v-for="link in links" :key="link.label">
      <v-icon>{{ link.icon }}</v-icon>
      <span>{{ link.label }}</span>
    </v-btn>
  </v-app-bar>
</template>

<script setup>
const links = [
  { icon: 'mdi-home', label: 'Home', href: null },
  { icon: 'mdi-information', label: 'About', href: null },
  { icon: 'mdi-help-circle', label: 'Help', href: null },
  { icon: 'mdi-email', label: 'Contact', href: null },
]
</script>
```

### 2. AppFooter.vue - 하단 푸터

**위치**: `src/layouts/AppFooter.vue`
**역할**: 모든 페이지 하단에 저작권 정보 표시

```vue
<template>
  <v-footer app height="40">
    <div class="text-caption text-disabled">
      © 2025 ITC AFM Data Platform
    </div>
  </v-footer>
</template>
```

## 컴포넌트가 조합되는 방식

```vue
<!-- App.vue - 최상위 컴포넌트 -->
<template>
  <v-app>
    <AppHeader />          ← 항상 상단에
    
    <v-main>
      <router-view />      ← 페이지가 여기에 들어감
    </v-main>              ↗ MainPage, ResultPage, DataTrendPage 중 하나
    
    <AppFooter />          ← 항상 하단에
  </v-app>
</template>
```

**실행 흐름**:
1. 사용자가 URL 접속
2. Router가 해당하는 페이지 컴포넌트 선택
3. App.vue에서 헤더 + 페이지 + 푸터 조합
4. 브라우저에 완성된 화면 표시

## 직접 해보기 🎯

### 1. 페이지 구조 분석하기
1. `MainPage.vue`를 열어보세요
2. `<template>` 섹션에서 화면 구조를 찾아보세요:
   - 로고가 어디에 있는지
   - 검색창이 어떻게 만들어져 있는지
   - 검색 결과가 어떻게 표시되는지

### 2. 컴포넌트 연결 확인하기
1. `App.vue`를 열어보세요
2. `AppHeader`와 `AppFooter`가 어떻게 import되는지 확인:
   ```javascript
   import AppHeader from '@/layouts/AppHeader.vue'
   import AppFooter from '@/layouts/AppFooter.vue'
   ```

### 3. 페이지 이동 테스트하기
1. 브라우저에서 다음 URL들을 직접 입력해보세요:
   - `http://localhost:3000/`
   - `http://localhost:3000/result/test123`
   - `http://localhost:3000/result/data_trend`
2. 각 페이지가 어떻게 다른지 확인해보세요

### 4. 코드 수정해보기
1. `AppHeader.vue`에서 제목을 바꿔보세요:
   ```vue
   <v-app-bar-title>내가 만든 AFM 뷰어</v-app-bar-title>
   ```
2. 저장하고 브라우저에서 변화 확인하기

## 다음 단계

페이지와 컴포넌트를 이해했다면, 다음으로 [라우팅 시스템](./routing-explained.md)을 읽어보세요.

URL과 페이지가 어떻게 연결되는지 알아봅시다!