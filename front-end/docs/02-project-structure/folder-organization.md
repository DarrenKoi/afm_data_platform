# 프로젝트 구조 이해하기

## 전체 폴더 구조 한눈에 보기

```
front-end/
├── public/                    # 정적 파일들
│   └── favicon.ico           # 브라우저 탭에 보이는 작은 아이콘
├── src/                      # 소스 코드 (우리가 주로 작업하는 곳)
│   ├── assets/              # 이미지, 로고 등 리소스
│   ├── components/          # 재사용 가능한 UI 조각들
│   ├── layouts/             # 페이지 레이아웃 (헤더, 푸터)
│   ├── pages/               # 각 페이지별 화면
│   ├── router/              # 페이지 간 이동 설정
│   ├── stores/              # 데이터 저장소
│   ├── styles/              # 스타일 설정
│   ├── dummy/               # 테스트용 가짜 데이터
│   └── main.js              # 앱 시작점
├── docs/                    # 개발 가이드 문서 (지금 읽고 있는 곳!)
├── package.json             # 프로젝트 설정과 의존성
└── README.md                # 프로젝트 설명서
```

## 각 폴더의 역할 자세히 알아보기

### 📁 `src/pages/` - 페이지 폴더
**역할**: 사용자가 보는 각 화면을 정의

```
src/pages/
├── MainPage.vue          # 메인 검색 페이지 (/)
├── ResultPage.vue        # 개별 결과 상세 페이지 (/result/:id)
└── DataTrendPage.vue     # 트렌드 분석 페이지 (/result/data_trend)
```

**비유**: 건물의 각 층이나 방
- 1층: 메인 페이지 (MainPage.vue)
- 2층: 결과 페이지 (ResultPage.vue)
- 3층: 분석 페이지 (DataTrendPage.vue)

**실제 예시**:
```vue
<!-- MainPage.vue -->
<template>
  <div>
    <img src="@/assets/afm_logo2.png" alt="AFM Logo">
    <v-text-field v-model="searchQuery" label="검색..." />
    <v-btn @click="performSearch">검색하기</v-btn>
  </div>
</template>
```

### 📁 `src/layouts/` - 레이아웃 폴더
**역할**: 모든 페이지에 공통으로 들어가는 부분

```
src/layouts/
├── AppHeader.vue    # 상단 네비게이션 바
└── AppFooter.vue    # 하단 푸터
```

**비유**: 건물의 로비나 복도
- 어느 층(페이지)에 가더라도 항상 보이는 부분
- 헤더: 회사 로고, 메뉴
- 푸터: 저작권 정보

**실제 예시**:
```vue
<!-- AppHeader.vue -->
<template>
  <v-app-bar color="primary">
    <v-app-bar-title>AFM Data Viewer</v-app-bar-title>
    <v-btn>Home</v-btn>
    <v-btn>About</v-btn>
    <v-btn>Help</v-btn>
  </v-app-bar>
</template>
```

### 📁 `src/components/` - 컴포넌트 폴더
**역할**: 여러 페이지에서 재사용할 수 있는 UI 조각들

```
src/components/
└── README.md    # 현재는 비어있음, 앞으로 여기에 추가 예정
```

**비유**: 레고 블록이나 가구 부품
- 버튼, 카드, 차트 등을 만들어 놓고
- 여러 페이지에서 가져다 사용

**앞으로 추가될 예정**:
```
src/components/
├── SearchCard.vue       # 검색 입력 카드
├── ResultList.vue       # 검색 결과 목록
├── DataChart.vue        # 데이터 차트
└── HistoryPanel.vue     # 검색 기록 패널
```

### 📁 `src/router/` - 라우터 폴더
**역할**: URL과 페이지를 연결하는 설정

```
src/router/
└── index.js    # 라우터 설정 파일
```

**비유**: 건물의 엘리베이터나 안내판
- `/` → MainPage.vue (1층으로 이동)
- `/result/abc123` → ResultPage.vue (2층으로 이동)
- `/result/data_trend` → DataTrendPage.vue (3층으로 이동)

**실제 예시**:
```javascript
// router/index.js
const routes = [
  { path: '/', component: MainPage },
  { path: '/result/:groupKey', component: ResultPage },
  { path: '/result/data_trend', component: DataTrendPage }
]
```

### 📁 `src/stores/` - 상태 관리 폴더
**역할**: 여러 페이지가 공유하는 데이터를 저장

```
src/stores/
├── app.js        # 기본 앱 상태
├── dataStore.js  # 검색 기록, 그룹핑 데이터
└── index.js      # 스토어 설정
```

**비유**: 건물의 중앙 관리실이나 창고
- 검색 기록을 저장해두고
- 어느 페이지에서든 불러와서 사용
- 데이터 그룹핑 정보도 여기서 관리

**실제 예시**:
```javascript
// stores/dataStore.js
export const useDataStore = defineStore('data', {
  state: () => ({
    viewHistory: [],      // 검색 기록
    groupedData: []       // 그룹핑된 데이터
  })
})
```

### 📁 `src/assets/` - 리소스 폴더
**역할**: 이미지, 아이콘, 폰트 등 정적 파일들

```
src/assets/
├── afm_logo2.png    # AFM 로고 이미지
├── favicon.png      # 파비콘
└── logo.svg         # 기본 Vue 로고
```

**비유**: 건물의 장식품이나 간판
- 로고, 아이콘, 배경 이미지 등
- 코드에서 `@/assets/파일명`으로 사용

### 📁 `src/dummy/` - 테스트 데이터 폴더
**역할**: 실제 백엔드 연결 전까지 사용할 가짜 데이터

```
src/dummy/
├── searchApi.js         # 가짜 검색 API
├── identifierData.js    # 샘플 측정 데이터 (사용안함)
└── data_description.txt # 데이터 설명서
```

**비유**: 집을 짓기 전에 만드는 모형집
- 실제 서버가 없어도 개발을 진행할 수 있게 해줌
- 나중에 실제 API로 교체 예정

## 파일 이름 규칙

### Vue 컴포넌트
- **PascalCase**: `MainPage.vue`, `AppHeader.vue`
- 첫 글자와 각 단어의 첫 글자를 대문자로

### JavaScript 파일
- **camelCase**: `dataStore.js`, `searchApi.js`
- 첫 글자는 소문자, 나머지 단어 첫 글자는 대문자

### 폴더
- **kebab-case** 또는 **camelCase**: `pages/`, `components/`

## 직접 해보기 🎯

1. **VS Code**에서 `src/` 폴더를 열어보세요
2. **각 폴더를 하나씩 클릭**해서 어떤 파일들이 있는지 확인해보세요
3. **MainPage.vue**를 열어서 다른 파일들을 어떻게 import하는지 보세요:
   ```javascript
   import { useRouter } from 'vue-router'        // router 폴더에서
   import { useDataStore } from '@/stores/dataStore.js'  // stores 폴더에서
   ```
4. **브라우저**에서 URL을 직접 입력해보세요:
   - `http://localhost:3000/` (MainPage)
   - `http://localhost:3000/result/test123` (ResultPage)

## 다음 단계

프로젝트 구조를 이해했다면, 다음으로 [페이지와 컴포넌트](./pages-and-components.md)를 읽어보세요.

각 페이지가 어떻게 만들어져 있는지 자세히 알아봅시다!