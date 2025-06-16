# **라우팅 구현하기**

## **Vue Router 소개 및 설치**

### **Vue Router란 무엇인가?**

Vue Router는 Vue.js의 공식 라우팅 라이브러리 (https://router.vuejs.org) 로, 단일 페이지 애플리케이션(SPA)에서 페이지 간 이동을 관리합니다. 전통적인 웹사이트처럼 서버에서 새로운 HTML 페이지를 받아오지 않고도, JavaScript를 통해 동적으로 컴포넌트를 교체하여 마치 여러 페이지가 있는 것처럼 사용자 경험을 제공합니다.

### **Vue Router의 주요 특징**

1. **Single Page Application (SPA) 지원**
   - 페이지 새로고침 없이 부드러운 화면 전환
   - 빠른 페이지 로딩과 자연스러운 사용자 경험
2. **브라우저 히스토리 관리**
   - 뒤로/앞으로 가기 버튼 지원
   - URL 변경을 통한 직접 페이지 접근 가능
3. **동적 라우팅**
   - URL 매개변수를 통한 유연한 페이지 구성
   - 중첩된 라우트로 복잡한 레이아웃 구현
4. **네비게이션 가드**
   - 페이지 접근 권한 제어
   - 로그인 검증, 데이터 검증 등
5. **지연 로딩 (Lazy Loading)**
   - 필요한 시점에만 컴포넌트 로드
   - 초기 번들 크기 최적화

### **Vue Router 설치하기**

대부분의 Vue 프로젝트 템플릿에는 Vue Router가 이미 포함되어 있지만, 수동으로 추가해야 하는 경우:

**설치 방법**

```bash
# Vue Router 설치
npm install vue-router@4
```

**main.js 파일 설정**

```javascript
// src/main.js
import { createApp } from "vue";
import { createVuetify } from "vuetify";
import App from "./App.vue";
import router from "./router";

// Vuetify 설정
const vuetify = createVuetify();

// 앱 생성 및 플러그인 등록
const app = createApp(App);

app.use(router); // 라우터 등록
app.use(vuetify); // Vuetify 등록

app.mount("#app");
```

**⚠️ 설치 시 주의사항**

- Vue 3 프로젝트에는 Vue Router 4를 사용해야 합니다
- Vue 2 프로젝트에는 Vue Router 3을 사용합니다
- 버전 호환성을 확인하고 설치하세요

## **라우터 설정의 기본 이해**

### **라우터 설정 파일 구조**

Vue Router 설정은 일반적으로 `src/router/index.js` 파일에서 관리합니다:

**src/router/index.js**

```javascript
import { createRouter, createWebHistory } from "vue-router";

// 페이지 컴포넌트 임포트
import MainPage from "@/pages/MainPage.vue";
import ResultPage from "@/pages/ResultPage.vue";
import DataTrendPage from "@/pages/DataTrendPage.vue";

// 라우트 정의
const routes = [
  {
    path: "/",
    name: "Main",
    component: MainPage,
    meta: { title: "AFM 데이터 검색" },
  },
  {
    path: "/result",
    name: "Result",
    component: ResultPage,
    meta: { title: "검색 결과" },
  },
  {
    path: "/trends",
    name: "DataTrend",
    component: DataTrendPage,
    meta: { title: "데이터 트렌드" },
  },
];

// 라우터 생성
const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
```

### **App.vue에서 라우터 뷰 설정**

```javascript
<template>
  <v-app>
    <!-- 상단 네비게이션 바 -->
    <v-app-bar app color="primary" dark>
      <v-toolbar-title>AFM 데이터 플랫폼</v-toolbar-title>
      <v-spacer></v-spacer>

      <!-- 네비게이션 메뉴 -->
      <v-btn to="/" text>
        <v-icon left>mdi-home</v-icon>
        홈
      </v-btn>
      <v-btn to="/result" text>
        <v-icon left>mdi-chart-box</v-icon>
        결과
      </v-btn>
      <v-btn to="/trends" text>
        <v-icon left>mdi-trending-up</v-icon>
        트렌드
      </v-btn>
    </v-app-bar>

    <!-- 메인 콘텐츠 영역 -->
    <v-main>
      <!-- 여기에 각 페이지 컴포넌트가 렌더링됩니다 -->
      <router-view />
    </v-main>

    <!-- 하단 푸터 -->
    <v-footer app color="grey lighten-3">
      <v-spacer></v-spacer>
      <span>&copy; 2024 SK hynix AFM Platform</span>
    </v-footer>
  </v-app>
</template>

<script>
// Note: <script setup> should be used in actual implementation
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 페이지 타이틀 업데이트
router.afterEach((to) => {
  document.title = to.meta.title ?
    `${to.meta.title} - AFM Platform` :
    'AFM Data Platform'
})
</script>
```

### **History 모드 vs Hash 모드**

Vue Router는 두 가지 히스토리 모드를 제공합니다:

**1. History 모드 (createWebHistory) - 권장**

```javascript
const router = createRouter({
  history: createWebHistory(), // 깔끔한 URL
  routes,
});

// URL 예시: https://example.com/result
```

**장점:**

- 깔끔한 URL (# 없음)
- SEO에 유리
- 사용자 친화적

**단점:**

- 서버 설정 필요 (모든 경로를 index.html로 리다이렉트)

**2. Hash 모드 (createWebHashHistory)**

```javascript
const router = createRouter({
  history: createWebHashHistory(), // # 포함 URL
  routes,
});

// URL 예시: https://example.com/#/result
```

**장점:**

- 서버 설정 불필요
- 정적 파일 호스팅에서도 작동

**단점:**

- URL에 # 포함
- SEO에 다소 불리

## **기본 네비게이션 구현**

### **선언적 네비게이션**

템플릿에서 `<router-link>` 또는 Vuetify 컴포넌트의 `to` 속성을 사용:

```javascript
<template>
  <v-container>
    <!-- 기본 router-link -->
    <router-link to="/result">결과 페이지로 이동</router-link>

    <!-- Vuetify 버튼과 함께 -->
    <v-btn to="/result" color="primary">
      <v-icon left>mdi-chart-box</v-icon>
      결과 보기
    </v-btn>

    <!-- 네비게이션 드로어 -->
    <v-navigation-drawer permanent>
      <v-list>
        <v-list-item to="/" link>
          <v-list-item-content>
            <v-list-item-title>메인 페이지</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/result" link>
          <v-list-item-content>
            <v-list-item-title>검색 결과</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/trends" link>
          <v-list-item-content>
            <v-list-item-title>데이터 트렌드</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
  </v-container>
</template>
```

### **프로그래매틱 네비게이션**

JavaScript 코드에서 라우터를 직접 제어:

```javascript
<template>
  <v-container>
    <v-card>
      <v-card-title>데이터 검색</v-card-title>
      <v-card-text>
        <v-form @submit.prevent="searchData">
          <v-text-field
            v-model="searchQuery"
            label="검색어를 입력하세요"
            required
          ></v-text-field>

          <v-btn type="submit" color="primary">
            검색
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
// Note: <script setup> should be used in actual implementation
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchQuery = ref('')

function searchData() {
  if (searchQuery.value.trim()) {
    // 검색 결과 페이지로 이동 (히스토리에 추가)
    router.push({
      path: '/result',
      query: { q: searchQuery.value }
    })
  }
}

function goBack() {
  // 이전 페이지로 돌아가기
  router.go(-1)
}

function goToHome() {
  // 현재 히스토리 항목을 교체 (뒤로 가기 불가)
  router.replace('/')
}
</script>
```

### **현재 라우트 정보 활용**

```javascript
<template>
  <v-container>
    <v-breadcrumbs :items="breadcrumbItems" divider=">">
    </v-breadcrumbs>

    <v-card>
      <v-card-title>
        현재 페이지: {{ currentPageName }}
      </v-card-title>
      <v-card-text>
        <p>경로: {{ $route.path }}</p>
        <p>쿼리: {{ JSON.stringify($route.query) }}</p>
        <p v-if="$route.params.id">ID: {{ $route.params.id }}</p>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
// Note: <script setup> should be used in actual implementation
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const currentPageName = computed(() => route.name || '알 수 없음')

const breadcrumbItems = computed(() => {
  const items = [{ text: '홈', to: '/', disabled: false }]

  if (route.path !== '/') {
    items.push({
      text: currentPageName.value,
      to: route.path,
      disabled: true
    })
  }

  return items
})

// 라우트 변경 감지
watch(() => route.path, (newPath, oldPath) => {
  console.log(`페이지 이동: ${oldPath} → ${newPath}`)
})
</script>
```

## **동적 라우팅과 매개변수**

### **URL 매개변수 사용**

동적인 라우트 패턴으로 유연한 페이지 구성:

```javascript
// src/router/index.js
const routes = [
  // 기본 매개변수
  {
    path: "/measurement/:id",
    name: "MeasurementDetail",
    component: () => import("@/pages/MeasurementDetail.vue"),
    props: true, // props로 매개변수 전달
  },

  // 여러 매개변수
  {
    path: "/sample/:sampleId/measurement/:measurementId",
    name: "SampleMeasurement",
    component: () => import("@/pages/SampleMeasurement.vue"),
    props: true,
  },

  // 선택적 매개변수
  {
    path: "/analysis/:type?",
    name: "Analysis",
    component: () => import("@/pages/Analysis.vue"),
    props: true,
  },

  // 와일드카드 매치
  {
    path: "/files/:pathMatch(.*)*",
    name: "FileViewer",
    component: () => import("@/pages/FileViewer.vue"),
  },
];
```

### **매개변수를 사용하는 컴포넌트**

```javascript
<!-- src/pages/MeasurementDetail.vue -->
<template>
  <v-container>
    <v-card v-if="measurement">
      <v-card-title>측정 데이터 #{{ id }}</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <h3>기본 정보</h3>
            <p>샘플명: {{ measurement.sampleName }}</p>
            <p>측정일: {{ measurement.date }}</p>
            <p>장비: {{ measurement.equipment }}</p>
          </v-col>
          <v-col cols="12" md="6">
            <h3>측정값</h3>
            <p>거칠기: {{ measurement.roughness }} nm</p>
            <p>높이: {{ measurement.height }} nm</p>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="$router.go(-1)">뒤로 가기</v-btn>
        <v-btn :to="`/measurement/${id}/edit`" color="primary">
          수정
        </v-btn>
      </v-card-actions>
    </v-card>

    <v-card v-else>
      <v-card-text>
        <v-progress-circular indeterminate></v-progress-circular>
        데이터 로딩 중...
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
// Note: <script setup> should be used in actual implementation
import { ref, onMounted, watch } from 'vue'

// Props로 라우트 매개변수 받기
const props = defineProps(['id'])

const measurement = ref(null)

async function loadMeasurement() {
  try {
    // API에서 측정 데이터 로드
    const response = await fetch(`/api/measurements/${props.id}`)
    measurement.value = await response.json()
  } catch (error) {
    console.error('측정 데이터 로드 실패:', error)
  }
}

// 컴포넌트 마운트 시 데이터 로드
onMounted(() => {
  loadMeasurement()
})

// ID가 변경되면 데이터 다시 로드
watch(() => props.id, () => {
  loadMeasurement()
})
</script>
```

### **쿼리 매개변수 활용**

검색, 필터링, 페이지네이션에 쿼리 매개변수 사용:

```javascript
<!-- src/pages/SearchResults.vue -->
<template>
  <v-container>
    <!-- 검색 필터 -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="searchQuery"
              label="검색어"
              @input="updateQuery"
              prepend-icon="mdi-magnify"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="filterType"
              :items="typeOptions"
              label="데이터 타입"
              @change="updateQuery"
            ></v-select>
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="sortBy"
              :items="sortOptions"
              label="정렬 기준"
              @change="updateQuery"
            ></v-select>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 검색 결과 -->
    <v-row>
      <v-col
        v-for="result in searchResults"
        :key="result.id"
        cols="12" md="6" lg="4"
      >
        <v-card>
          <v-card-title>{{ result.title }}</v-card-title>
          <v-card-text>{{ result.description }}</v-card-text>
          <v-card-actions>
            <v-btn :to="`/measurement/${result.id}`">
              상세보기
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- 페이지네이션 -->
    <v-pagination
      v-if="totalPages > 1"
      v-model="currentPage"
      :length="totalPages"
      @input="updateQuery"
      class="mt-4"
    ></v-pagination>
  </v-container>
</template>

<script>
// Note: <script setup> should be used in actual implementation
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// 검색 상태
const searchQuery = ref('')
const filterType = ref('all')
const sortBy = ref('date')
const currentPage = ref(1)
const searchResults = ref([])

// 옵션 데이터
const typeOptions = [
  { text: '전체', value: 'all' },
  { text: 'AFM', value: 'afm' },
  { text: 'SEM', value: 'sem' }
]

const sortOptions = [
  { text: '날짜순', value: 'date' },
  { text: '이름순', value: 'name' },
  { text: '크기순', value: 'size' }
]

const totalPages = computed(() => {
  return Math.ceil(searchResults.value.length / 10)
})

// URL 쿼리와 상태 동기화
function syncWithQuery() {
  searchQuery.value = route.query.q || ''
  filterType.value = route.query.type || 'all'
  sortBy.value = route.query.sort || 'date'
  currentPage.value = parseInt(route.query.page) || 1
}

// 상태를 URL 쿼리에 반영
function updateQuery() {
  const query = {}

  if (searchQuery.value) query.q = searchQuery.value
  if (filterType.value !== 'all') query.type = filterType.value
  if (sortBy.value !== 'date') query.sort = sortBy.value
  if (currentPage.value > 1) query.page = currentPage.value

  router.push({ query })
}

// 검색 실행
async function performSearch() {
  try {
    const params = new URLSearchParams({
      q: searchQuery.value,
      type: filterType.value,
      sort: sortBy.value,
      page: currentPage.value
    })

    const response = await fetch(`/api/search?${params}`)
    searchResults.value = await response.json()
  } catch (error) {
    console.error('검색 실패:', error)
  }
}

// 라우트 변경 감지
watch(() => route.query, () => {
  syncWithQuery()
  performSearch()
}, { immediate: true })
</script>
```

## **중첩 라우트와 레이아웃**

### **중첩 라우트 정의**

복잡한 페이지 구조를 위한 중첩 라우트:

```javascript
// src/router/index.js
const routes = [
  {
    path: "/dashboard",
    component: () => import("@/layouts/DashboardLayout.vue"),
    children: [
      {
        path: "", // /dashboard
        name: "DashboardHome",
        component: () => import("@/pages/Dashboard/Home.vue"),
      },
      {
        path: "measurements", // /dashboard/measurements
        name: "Measurements",
        component: () => import("@/pages/Dashboard/Measurements.vue"),
      },
      {
        path: "analysis", // /dashboard/analysis
        name: "Analysis",
        component: () => import("@/pages/Dashboard/Analysis.vue"),
        children: [
          {
            path: "surface", // /dashboard/analysis/surface
            component: () => import("@/pages/Dashboard/SurfaceAnalysis.vue"),
          },
          {
            path: "roughness", // /dashboard/analysis/roughness
            component: () => import("@/pages/Dashboard/RoughnessAnalysis.vue"),
          },
        ],
      },
    ],
  },
];
```

### **레이아웃 컴포넌트 구현**

```javascript
<!-- src/layouts/DashboardLayout.vue -->
<template>
  <v-app>
    <!-- 네비게이션 드로어 -->
    <v-navigation-drawer v-model="drawer" app>
      <v-list>
        <v-list-item to="/dashboard">
          <v-list-item-action>
            <v-icon>mdi-view-dashboard</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>대시보드</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/dashboard/measurements">
          <v-list-item-action>
            <v-icon>mdi-chart-box</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>측정 데이터</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-group>
          <template v-slot:activator>
            <v-list-item-action>
              <v-icon>mdi-chart-line</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>분석</v-list-item-title>
            </v-list-item-content>
          </template>

          <v-list-item to="/dashboard/analysis/surface">
            <v-list-item-title>표면 분석</v-list-item-title>
          </v-list-item>
          <v-list-item to="/dashboard/analysis/roughness">
            <v-list-item-title>거칠기 분석</v-list-item-title>
          </v-list-item>
        </v-list-group>
      </v-list>
    </v-navigation-drawer>

    <!-- 상단 앱 바 -->
    <v-app-bar app color="primary" dark>
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>AFM 데이터 대시보드</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon>
        <v-icon>mdi-account</v-icon>
      </v-btn>
    </v-app-bar>

    <!-- 메인 콘텐츠 -->
    <v-main>
      <v-container fluid>
        <!-- 브레드크럼 -->
        <v-breadcrumbs :items="breadcrumbItems" class="pa-0 mb-4">
        </v-breadcrumbs>

        <!-- 자식 라우트 컴포넌트가 렌더링되는 곳 -->
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
// Note: <script setup> should be used in actual implementation
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const drawer = ref(true)

const breadcrumbItems = computed(() => {
  const items = [{ text: '홈', to: '/', disabled: false }]

  // 현재 경로 기반으로 브레드크럼 생성
  if (route.path.includes('/dashboard')) {
    items.push({ text: '대시보드', to: '/dashboard', disabled: false })

    if (route.path.includes('/measurements')) {
      items.push({ text: '측정 데이터', to: '/dashboard/measurements', disabled: true })
    } else if (route.path.includes('/analysis')) {
      items.push({ text: '분석', to: '/dashboard/analysis', disabled: false })

      if (route.path.includes('/surface')) {
        items.push({ text: '표면 분석', disabled: true })
      } else if (route.path.includes('/roughness')) {
        items.push({ text: '거칠기 분석', disabled: true })
      }
    }
  }

  return items
})
</script>
```

## **라우트 가드와 인증**

### **전역 가드 설정**

모든 라우트 변경에 대한 인증 및 권한 검사:

```javascript
// src/router/index.js
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 전역 Before 가드
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  // 로딩 상태 시작
  const loadingStore = useLoadingStore();
  loadingStore.start();

  // 인증이 필요한 페이지 확인
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // 로그인 페이지로 리다이렉트
    next({
      name: "Login",
      query: { redirect: to.fullPath },
    });
    return;
  }

  // 권한 확인
  if (to.meta.roles && !to.meta.roles.includes(authStore.userRole)) {
    next({ name: "Forbidden" });
    return;
  }

  // 이미 로그인한 사용자가 로그인 페이지 접근 시
  if (to.name === "Login" && authStore.isAuthenticated) {
    next({ name: "Dashboard" });
    return;
  }

  next();
});

// 전역 After 가드
router.afterEach((to) => {
  const loadingStore = useLoadingStore();
  loadingStore.finish();

  // 페이지 타이틀 설정
  document.title = to.meta.title
    ? `${to.meta.title} - AFM Platform`
    : "AFM Data Platform";
});

export default router;
```

### **라우트별 가드**

특정 라우트에만 적용되는 가드:

```javascript
const routes = [
  {
    path: "/admin",
    component: () => import("@/pages/Admin.vue"),
    meta: { requiresAuth: true, roles: ["admin"] },
    beforeEnter: (to, from, next) => {
      const authStore = useAuthStore();

      if (authStore.userRole !== "admin") {
        next({ name: "Forbidden" });
      } else {
        next();
      }
    },
  },
  {
    path: "/measurement/:id",
    component: () => import("@/pages/MeasurementDetail.vue"),
    beforeEnter: async (to, from, next) => {
      // 데이터 존재 여부 확인
      try {
        const response = await fetch(`/api/measurements/${to.params.id}`);
        if (response.status === 404) {
          next({ name: "NotFound" });
        } else {
          next();
        }
      } catch (error) {
        next({ name: "Error" });
      }
    },
  },
];
```

### **컴포넌트 내 가드**

컴포넌트 레벨에서의 가드 구현:

```javascript
<template>
  <v-container>
    <v-card>
      <v-card-title>측정 데이터 편집</v-card-title>
      <v-card-text>
        <v-form v-model="isFormValid">
          <v-text-field
            v-model="measurementData.name"
            label="측정명"
            @input="markAsChanged"
            required
          ></v-text-field>
          <!-- 기타 폼 필드들 -->
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="saveMeasurement" :disabled="!isFormValid">
          저장
        </v-btn>
        <v-btn @click="$router.go(-1)">
          취소
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script>
// Note: <script setup> should be used in actual implementation
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const props = defineProps(['id'])

const measurementData = ref({})
const isFormValid = ref(false)
const hasUnsavedChanges = ref(false)
const originalData = ref(null)

function markAsChanged() {
  hasUnsavedChanges.value = true
}

async function loadMeasurement() {
  try {
    const response = await fetch(`/api/measurements/${props.id}`)
    measurementData.value = await response.json()
    originalData.value = JSON.stringify(measurementData.value)
  } catch (error) {
    console.error('데이터 로드 실패:', error)
  }
}

async function saveMeasurement() {
  // 저장 로직
  hasUnsavedChanges.value = false
  router.push('/dashboard/measurements')
}

onMounted(() => {
  loadMeasurement()
})

// 컴포넌트에서 나가기 전 확인
onBeforeRouteLeave((to, from, next) => {
  if (hasUnsavedChanges.value) {
    const answer = window.confirm(
      '저장되지 않은 변경사항이 있습니다. 정말 나가시겠습니까?'
    )
    next(answer)
  } else {
    next()
  }
})
</script>
```

---

## **💡 Vue Router 효과적으로 활용하기**

### **🎯 실용적인 접근 방법**

Vue Router를 처음 배울 때는 모든 기능을 완벽히 이해하려 하지 마세요. 필요한 기능부터 단계적으로 적용해보는 것이 효과적입니다.

**📚 학습 vs 실무 접근법**

| 구분     | 학습 중심           | **실무 중심 (권장)**        |
| -------- | ------------------- | --------------------------- |
| 방식     | 모든 기능 완벽 숙지 | 기본 라우팅부터 점진적 확장 |
| 시간     | 며칠~몇 주          | 즉시 시작 가능              |
| 효과     | 이론적 완벽함       | 빠른 결과물                 |
| 스트레스 | 높음                | 낮음                        |

### **🔍 단계별 구현 전략**

**1️⃣ 기본 라우팅부터 시작**

```javascript
// 1단계: 가장 단순한 라우팅
const routes = [
  { path: "/", component: Home },
  { path: "/about", component: About },
];
```

**2️⃣ 동적 라우팅 추가**

```javascript
// 2단계: ID 매개변수 추가
const routes = [
  { path: "/", component: Home },
  { path: "/measurement/:id", component: MeasurementDetail },
];
```

**3️⃣ 네비게이션 가드 적용**

```javascript
// 3단계: 인증 가드 추가
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isLoggedIn()) {
    next("/login");
  } else {
    next();
  }
});
```

### **🛠️ 자주 사용하는 핵심 패턴**

AFM 데이터 플랫폼에서 90% 이상 사용하게 될 패턴들:

**기본 네비게이션**

- `router.push()` - 새 페이지로 이동
- `router.go(-1)` - 뒤로 가기
- `<router-link to="/path">` - 선언적 네비게이션

**매개변수 처리**

- `$route.params.id` - URL 매개변수 접근
- `$route.query.search` - 쿼리 매개변수 접근
- `props: true` - 매개변수를 props로 전달

**조건부 네비게이션**

- `v-if="$route.name === 'Home'"` - 현재 페이지 확인
- `meta: { requiresAuth: true }` - 인증 필요 표시

### **🎨 Vuetify와 함께 사용하기**

**1️⃣ 네비게이션 컴포넌트**

```javascript
<!-- 아름다운 네비게이션 바 -->
<v-app-bar app color="primary" dark>
  <v-btn to="/" text>홈</v-btn>
  <v-btn to="/measurements" text>측정 데이터</v-btn>
  <v-btn to="/analysis" text>분석</v-btn>
</v-app-bar>
```

**2️⃣ 드로어 네비게이션**

```javascript
<v-navigation-drawer app>
  <v-list>
    <v-list-item to="/dashboard" link>
      <v-list-item-title>대시보드</v-list-item-title>
    </v-list-item>
  </v-list>
</v-navigation-drawer>
```

### **🚀 개발 워크플로우**

**실제 개발할 때 이렇게 하세요:**

1. **페이지 목록 작성** → "어떤 페이지들이 필요한가?"
2. **라우트 기본 구조 생성** → 간단한 경로부터 시작
3. **네비게이션 추가** → Vuetify 컴포넌트로 예쁘게
4. **동적 기능 확장** → 매개변수, 가드 등 필요시 추가
5. **사용자 경험 개선** → 로딩, 오류 처리 등

**💻 실제 예시: AFM 플랫폼 라우팅 구축**

```javascript
// 1. 기본 구조 (30분)
const routes = [
  { path: '/', component: MainPage },
  { path: '/result', component: ResultPage }
]

// 2. 네비게이션 추가 (20분)
<v-app-bar>
  <v-btn to="/">검색</v-btn>
  <v-btn to="/result">결과</v-btn>
</v-app-bar>

// 3. 동적 기능 추가 (필요시)
{ path: '/measurement/:id', component: Detail }
```

### **🔧 문제 해결 가이드**

**자주 발생하는 문제들:**

1. **"페이지가 안 나와요"**

   ```javascript
   // router-view가 있는지 확인
   <router-view />
   ```

2. **"뒤로 가기가 안 돼요"**

   ```javascript
   // replace 대신 push 사용
   router.push("/path"); // ✅ 히스토리에 추가
   router.replace("/path"); // ❌ 히스토리 교체
   ```

3. **"새로고침하면 404 오류"**
   ```javascript
   // History 모드 사용 시 서버 설정 필요
   // 또는 Hash 모드 사용
   createWebHashHistory(); // /#/ 형태
   ```

### **📖 추천 학습 순서**

**즉시 활용 가능한 순서:**

1. **[Vue Router 기본 가이드](https://router.vuejs.org/guide/)** - 공식 문서 필수 부분만
2. **실제 프로젝트 적용** - 간단한 페이지 2-3개로 시작
3. **Vuetify 네비게이션 컴포넌트** - 예쁜 메뉴 만들기
4. **고급 기능** - 필요할 때마다 하나씩 추가

**🎯 핵심 메시지: "완벽한 라우팅을 처음부터 만들려 하지 마세요!"**

AFM 데이터 플랫폼을 개발하면서 라우팅 기능을 하나씩 추가해 나가는 것이 가장 효율적입니다. 기본 페이지 이동부터 시작해서, 필요에 따라 동적 라우팅, 가드, 중첩 라우트를 점진적으로 도입하세요!
