# AFM Data Platform Nuxt UI 이식 분석 리포트

## 1. 목적과 결론

이 문서는 현재 `afm_data_platform` 앱을 `DarrenKoi/skewnono_v3_nuxt` 프로젝트로 이식하기 위한 분석 리포트다. 목표는 단순히 Vue 파일을 옮기는 것이 아니라, 대상 프로젝트의 Nuxt 4, Nuxt UI, Tailwind CSS, Flask 백엔드 구조에 맞게 기능을 재배치하는 것이다.

핵심 결론은 다음과 같다.

- AFM 프론트엔드는 대상 프로젝트의 `front-dev-home/app/` 아래에 새 도메인 `afm`으로 추가하는 것이 가장 안전하다.
- 기존 Vue Router의 `/`, `/result/:recipeId/:filename`, `/result/data_trend` 라우트는 대상 프로젝트의 허브 `/`와 충돌하므로 `/afm`, `/afm/result`, `/afm/trend`로 재설계한다.
- Vuetify, Vue Router, axios, Pinia, Vue Query를 그대로 가져오지 말고 Nuxt 내장 라우팅, `$fetch`, `useAsyncData`, `useState`, Nuxt UI 컴포넌트로 치환한다.
- ECharts는 유지해도 된다. 다만 대상 프로젝트에는 아직 의존성이 없으므로 `front-dev-home/package.json`에 추가하고 차트 컴포넌트는 client-only 패턴으로 이식한다.
- AFM 백엔드는 대상 프로젝트의 `back_dev_home/` 아래에 `afm` 블루프린트 패키지로 합류시키는 것이 맞다.
- 대상 저장소는 문서상 Nuxt mock server 구조를 설명하지만, 현재 코드 기준으로는 `front-dev-home/server/`가 없고 `nuxt.config.ts`가 `/api`를 Flask로 프록시한다. 따라서 1차 이식은 Flask 엔드포인트를 먼저 합치는 방식이 현실적이다.

검토 기준:

- 현재 앱: 로컬 저장소 `afm_data_platform`, commit `b09bee9`
- 대상 앱: `https://github.com/DarrenKoi/skewnono_v3_nuxt`, 확인 commit `befb052`

## 2. 현재 AFM 앱 구조

현재 앱은 Flask 백엔드와 Vue 3/Vite/Vuetify 프론트엔드가 분리된 구조다.

```text
afm_data_platform/
├── index.py
├── api/
│   ├── __init__.py
│   ├── routes.py
│   ├── afm_routes.py
│   ├── image_routes.py
│   ├── activity_routes.py
│   └── utils/
│       ├── file_parser.py
│       ├── app_logger_standard.py
│       └── standard_logger.py
└── front-end/
    ├── src/
    │   ├── App.vue
    │   ├── main.js
    │   ├── router/index.js
    │   ├── pages/
    │   ├── components/
    │   ├── composables/
    │   ├── services/
    │   ├── stores/
    │   ├── plugins/
    │   ├── styles/
    │   └── utils/
    ├── package.json
    └── vite.config.mjs
```

주요 프론트엔드 의존성:

| 영역 | 현재 사용 |
| --- | --- |
| 앱 프레임워크 | Vue 3 + Vite |
| UI | Vuetify 3, MDI font |
| 라우팅 | vue-router |
| 상태 | Pinia + localStorage |
| 서버 상태 | `@tanstack/vue-query` |
| HTTP | axios |
| 차트 | ECharts |
| 빌드 설정 | Vite plugin, Vuetify plugin, auto-import |

주요 화면:

| 현재 파일 | 역할 |
| --- | --- |
| `front-end/src/pages/MainPage.vue` | AFM 검색, 툴 선택, 조회 이력, 그룹 관리 |
| `front-end/src/pages/ResultPage.vue` | 측정 상세, 이미지, 포인트 테이블, 히트맵, 히스토그램, 다운로드 |
| `front-end/src/pages/DataTrendPage.vue` | 그룹 데이터 트렌드 분석, 시계열 차트 |
| `front-end/src/pages/AboutPage.vue` | 앱 소개와 버전 정보 |

주요 API:

| Endpoint | 역할 |
| --- | --- |
| `GET /api/health` | API 상태 |
| `GET /api/afm-files?tool=MAP608` | AFM 파일 목록 |
| `GET /api/afm-files/detail/<filename>?tool=...` | 측정 상세 pickle 로드 |
| `GET /api/afm-files/profile/<filename>/<point>?tool=...` | 포인트별 profile x/y/z 데이터 |
| `GET /api/afm-files/image/<filename>/<point>?tool=...` | 이미지 메타 조회 |
| `GET /api/afm-files/image-file/<filename>/<point>?tool=...` | 이미지 파일 서빙 |
| `GET /api/afm-files/images/<image_type>?tool=...` | 타입별 이미지 목록 |
| `GET /api/afm-files/download-raw-image/<filename>/<point>?tool=...` | 원본 이미지 다운로드 |
| `GET /api/user-activities` | 활동 로그 조회 |
| `GET /api/current-user` | 쿠키 기반 사용자 조회 |

데이터 경로는 현재 코드에 상대 경로로 박혀 있다.

```text
itc-afm-data-platform-pjt-shared/AFM_DB/{tool}/
├── data_dir_list.txt
├── data_dir_list_parsed.pkl
├── data_dir_pickle/
├── profile_dir/
├── tiff_dir/
├── align_dir/
├── tip_dir/
└── capture_dir/
```

이 경로는 이식 시 환경 변수화해야 한다.

## 3. 대상 skewnono 프로젝트 구조

대상 프로젝트는 루트에 문서와 Python 엔트리포인트를 두고, 실제 Nuxt 앱은 `front-dev-home/`, Flask 백엔드는 `back_dev_home/`에 있다.

```text
skewnono_v3_nuxt/
├── index.py
├── back_dev_home/
│   ├── __init__.py
│   ├── _core/
│   ├── sem_list/
│   ├── storage/
│   └── device_statistics/
├── front-dev-home/
│   ├── nuxt.config.ts
│   ├── package.json
│   ├── public/
│   └── app/
│       ├── app.vue
│       ├── app.config.ts
│       ├── assets/css/main.css
│       ├── components/
│       ├── composables/
│       ├── layouts/
│       ├── pages/
│       ├── plugins/
│       └── stores/
└── docs/
    └── api-contracts/
```

대상 프론트엔드 핵심:

| 항목 | 대상 프로젝트 방식 |
| --- | --- |
| Nuxt | `nuxt ^4.4.2` |
| UI | `@nuxt/ui ^4.6.1`, Tailwind CSS v4 |
| 렌더링 | `ssr: false` |
| 전역 래퍼 | `app/app.vue`의 `<UApp><NuxtLayout><NuxtPage /></NuxtLayout></UApp>` |
| 데이터 호출 | composable 안에서 `$fetch` + `useRuntimeConfig().public.apiBase` |
| 캐싱 | `useAsyncData` |
| 상태 | Pinia가 아니라 `useState` 기반 store |
| API 프록시 | Nuxt dev server가 `/api`를 Flask `NUXT_API_TARGET`으로 프록시 |
| 시각 스타일 | `dashboard-surface`, Tailwind utility, Nuxt UI `U*` 컴포넌트 |

대상 백엔드 핵심:

```text
back_dev_home/
├── __init__.py             # Flask app factory, blueprint 등록
├── _core/routes.py         # /api/health
├── sem_list/routes.py      # /api/sem-list
├── storage/routes.py       # /api/storage, /api/storage-unavailable
└── device_statistics/
```

대상 API 응답은 대부분 bare array다. AFM 기존 API는 `{ success, data, message }` envelope를 사용하므로, 1차 이식에서는 기존 shape를 유지하고 `docs/api-contracts/afm.yaml`에 명확히 기록하는 것이 좋다. 프론트 리팩터까지 한 번에 하면서 응답 shape를 바꾸면 검증 범위가 커진다.

## 4. 권장 통합 방향

AFM은 E-Beam 하위 feature가 아니라 별도 계측 도메인으로 두는 것이 좋다. 이유는 다음과 같다.

- 대상의 E-Beam 네비게이션은 `cd-sem`, `hv-sem`, `verity-sem`, `provision` 도구 타입과 FAB 사이드바를 전제로 한다.
- AFM은 `MAP608`, `MAPC01` 툴 선택이 핵심이고 FAB 사이드바와 직접 맞지 않는다.
- AFM의 주요 UX는 파일 검색, 측정 상세, 포인트/이미지/차트, 그룹 트렌드 분석이다. 기존 E-Beam feature tab과 데이터 모델이 다르다.

권장 URL:

| 현재 URL | 대상 URL |
| --- | --- |
| `/` | `/afm` |
| `/result/:recipeId/:filename?tool=...` | `/afm/result?recipeId=...&filename=...&tool=...` |
| `/result/data_trend` | `/afm/trend` |
| `/about` | `/information`에 일부 병합 또는 `/afm/about` |

`filename`에는 `#` 같은 문자가 포함되므로 path param보다 query param이 더 안전하다. 기존 path 구조를 꼭 유지해야 한다면 `/afm/result/[recipeId]/[filename].vue`로 만들고 모든 이동에서 `encodeURIComponent`를 엄격히 적용해야 한다.

## 5. 대상 파일 구조 변경안

### 5.1 프론트엔드 추가 구조

```text
front-dev-home/app/
├── pages/
│   └── afm/
│       ├── index.vue             # 검색/그룹/히스토리
│       ├── result.vue            # 측정 상세, query 기반
│       ├── trend.vue             # 그룹 트렌드 분석
│       └── about.vue             # 선택 사항
│
├── components/
│   └── afm/
│       ├── common/
│       │   ├── AfmBreadcrumb.vue
│       │   └── AfmLoadingModal.vue
│       ├── search/
│       │   ├── AfmSearchSection.vue
│       │   ├── AfmToolSelector.vue
│       │   ├── AfmViewHistoryCard.vue
│       │   ├── AfmDataGroupingCard.vue
│       │   └── AfmSavedGroupsCard.vue
│       ├── result/
│       │   ├── AfmMeasurementInfo.vue
│       │   ├── AfmMeasurementPoints.vue
│       │   ├── AfmAdditionalAnalysisImages.vue
│       │   ├── AfmStatisticalInfoByPoints.vue
│       │   └── charts/
│       │       ├── AfmHeatmapChart.client.vue
│       │       ├── AfmHistogramChart.client.vue
│       │       ├── AfmDataScatterChart.client.vue
│       │       ├── AfmStatisticalScatterChart.client.vue
│       │       └── AfmScatterDataSelector.vue
│       └── trend/
│           ├── AfmSimplifiedMeasurementCard.vue
│           └── AfmTimeSeriesChart.client.vue
│
├── composables/
│   ├── useAfmApi.ts
│   ├── useAfmSearch.ts
│   ├── useAfmResultData.ts
│   ├── useAfmPointSelection.ts
│   ├── useAfmDataDownload.ts
│   └── useAfmToolSelection.ts
│
├── stores/
│   └── afm.ts
│
├── plugins/
│   └── persist-afm.client.ts
│
└── utils/
    ├── afmExport.ts
    └── afmImageDownload.ts
```

정적 자산:

```text
front-dev-home/public/images/afm/
├── afm_logo.png
└── afm_logo2.png
```

대상 프로젝트는 이미 `public/fonts`와 `app/assets/css/main.css`를 관리한다. 기존 `front-end/src/styles/fonts.css`, `settings.scss`, Vuetify 스타일은 가져오지 않는다.

### 5.2 백엔드 추가 구조

```text
back_dev_home/
├── afm/
│   ├── __init__.py
│   ├── routes.py          # /api/afm-files, /api/afm-files/detail, profile
│   ├── image_routes.py    # image-file, raw download, typed images
│   ├── activity_routes.py # 필요 시 활동 로그
│   ├── file_parser.py
│   └── data_paths.py      # AFM_DB_ROOT 환경 변수 처리
└── __init__.py            # afm blueprint 등록 추가
```

`back_dev_home/__init__.py`에 추가:

```python
from back_dev_home.afm import bp as afm_bp

app.register_blueprint(afm_bp, url_prefix="/api")
```

이미지 라우트를 별도 blueprint로 둘 경우:

```python
from back_dev_home.afm.image_routes import bp as afm_image_bp

app.register_blueprint(afm_image_bp, url_prefix="/api")
```

백엔드 환경 변수:

```text
AFM_DB_ROOT=/path/to/itc-afm-data-platform-pjt-shared/AFM_DB
```

`data_paths.py` 예시:

```python
from pathlib import Path
import os


def get_afm_tool_root(tool_name: str) -> Path:
    root = Path(os.environ.get("AFM_DB_ROOT", "itc-afm-data-platform-pjt-shared/AFM_DB"))
    return root / tool_name
```

대상 `back_dev_home/requirements.txt`에는 현재 `Flask`, `flask-cors`만 있다. AFM pickle 내부가 pandas/numpy 객체를 포함할 수 있으므로 최소 다음 의존성을 추가해야 한다.

```text
numpy
pandas
pyarrow
```

`APScheduler`, `requests`는 현재 AFM 런타임에 꼭 필요한지 다시 확인하고 필요할 때만 추가한다.

## 6. 현재 파일별 이식 매핑

### 6.1 페이지

| 현재 파일 | 대상 파일 | 처리 |
| --- | --- | --- |
| `front-end/src/pages/MainPage.vue` | `front-dev-home/app/pages/afm/index.vue` | Vuetify 레이아웃을 Tailwind/Nuxt UI로 재작성 |
| `front-end/src/pages/ResultPage.vue` | `front-dev-home/app/pages/afm/result.vue` | route param을 query 기반으로 변경 권장 |
| `front-end/src/pages/DataTrendPage.vue` | `front-dev-home/app/pages/afm/trend.vue` | sessionStorage 의존 축소, `useState` fallback reload |
| `front-end/src/pages/AboutPage.vue` | `front-dev-home/app/pages/afm/about.vue` 또는 `information.vue` 병합 | 앱 소개만 선별 반영 |

### 6.2 컴포넌트

| 현재 디렉터리 | 대상 디렉터리 |
| --- | --- |
| `components/MainPage/*` | `components/afm/search/*` |
| `components/ResultPage/*` | `components/afm/result/*` |
| `components/ResultPage/charts/*` | `components/afm/result/charts/*.client.vue` |
| `components/DataTrend/*` | `components/afm/trend/*` |
| `components/common/*` | `components/afm/common/*` |
| `components/Settings/*` | 필요 시 `components/afm/settings/*` |

Nuxt는 `app/components`를 자동 import한다. 예를 들어 `app/components/afm/search/AfmSearchSection.vue`는 `<AfmSearchSection />`로 사용한다. 폴더명을 컴포넌트명에 중복시키지 않는 방향으로 파일명을 명확히 둔다.

### 6.3 서비스와 composable

| 현재 파일 | 대상 파일 | 변경 |
| --- | --- | --- |
| `services/api.js` | `composables/useAfmApi.ts` | axios 제거, `$fetch` 사용 |
| `services/afmService.js` | `composables/useAfmApi.ts` | endpoint 함수 typed export |
| `services/imageService.js` | `composables/useAfmApi.ts` 또는 `useAfmImageApi.ts` | 이미지 URL 생성은 `runtimeConfig.public.apiBase` 사용 |
| `services/activityService.js` | `composables/useAfmActivityApi.ts` | 필요 시 분리 |
| `services/dataService.js` | `utils/afmDataTransform.ts` | 순수 변환 함수로 분리 |
| `composables/useSearch.js` | `composables/useAfmSearch.ts` | `useAsyncData` + local filter |
| `composables/useResultPageQueries.js` | `composables/useAfmResultData.ts` | Vue Query 제거 |
| `stores/dataStore.js` | `stores/afm.ts` + `plugins/persist-afm.client.ts` | Pinia 제거, `useState` 패턴 |

### 6.4 제거하거나 가져오지 않을 것

| 현재 항목 | 이유 |
| --- | --- |
| `front-end/src/main.js` | Nuxt가 앱 부트스트랩을 담당 |
| `front-end/src/router/index.js` | Nuxt file-based routing 사용 |
| `front-end/src/plugins/vuetify.js` | Nuxt UI로 치환 |
| `front-end/src/plugins/vue-query.js` | 대상은 `useAsyncData` 패턴 |
| `front-end/vite.config.mjs` | Nuxt 설정은 `nuxt.config.ts`에서 관리 |
| `@mdi/font`, `vuetify`, `vite-plugin-vuetify` | 대상 디자인 시스템과 충돌 |
| `axios` | `$fetch`로 대체 |
| `pinia` | 대상 프로젝트의 `useState` store와 통일 |

## 7. Nuxt UI 치환 가이드

| Vuetify | Nuxt/Nuxt UI 대상 |
| --- | --- |
| `<v-app>` | 이미 `app.vue`의 `<UApp>` 존재 |
| `<v-main>` | Nuxt layout의 `<main>` |
| `<v-container>` | `div` + Tailwind max-width/padding 또는 필요 시 `UContainer` |
| `<v-row>`, `<v-col>` | CSS grid/flex (`grid`, `md:grid-cols-*`, `gap-*`) |
| `<v-card>` | `<UCard class="dashboard-surface rounded-2xl">` |
| `<v-card-title>` | `#header` slot 또는 내부 heading |
| `<v-card-text>` | UCard body 또는 plain div |
| `<v-btn>` | `<UButton>` |
| `<v-icon>` | `<UIcon name="i-lucide-...">` |
| `<v-chip>` | `<UBadge>`, pill-style `<UButton>`, 또는 custom span |
| `<v-dialog>` | `<UModal>` |
| `<v-menu>` | `<UDropdownMenu>` |
| `<v-list>` | `UDropdownMenu` items 또는 semantic list |
| `<v-alert>` | `<UAlert>` |
| `<v-progress-linear>` | `<UProgress>` |
| `<v-progress-circular>` | `UIcon i-lucide-loader-circle animate-spin` 또는 custom spinner |
| `<v-tooltip>` | `<UTooltip>` |
| `<v-tabs>` + `<v-window>` | `<UTabs>` 또는 대상 프로젝트의 custom pill nav |
| `<v-data-table>` | `<UTable>` |
| `<v-select>` | `<USelect>` 또는 `<USelectMenu>` |
| `<v-text-field>` | `<UInput>` |
| `<v-textarea>` | `<UTextarea>` |
| `<v-checkbox>` | `<UCheckbox>` |
| `<v-breadcrumbs>` | `<UBreadcrumb>` |

아이콘은 MDI 이름을 그대로 쓸 수 없다. 대상 프로젝트는 Iconify lucide 컬렉션을 사용한다.

| 기존 MDI | 권장 lucide |
| --- | --- |
| `mdi-microscope` | `i-lucide-microscope` |
| `mdi-tools` | `i-lucide-wrench` |
| `mdi-database` | `i-lucide-database` |
| `mdi-download` | `i-lucide-download` |
| `mdi-arrow-left` | `i-lucide-arrow-left` |
| `mdi-chart-line` | `i-lucide-chart-line` |
| `mdi-chart-bar` | `i-lucide-chart-bar` |
| `mdi-grid` | `i-lucide-grid-3x3` |
| `mdi-image` | `i-lucide-image` |
| `mdi-image-off` | `i-lucide-image-off` |
| `mdi-content-save` | `i-lucide-save` |
| `mdi-close` | `i-lucide-x` |

## 8. 데이터 호출과 상태 관리 전환

### 8.1 axios에서 `$fetch`로 전환

현재:

```js
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api"
})
```

대상:

```ts
const joinApiPath = (base: string, path: string) => {
  const normalizedBase = base.endsWith('/') ? base.slice(0, -1) : base
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${normalizedBase}${normalizedPath}`
}

export const useAfmApi = () => {
  const config = useRuntimeConfig()
  const base = config.public.apiBase

  const fetchAfmFiles = async (tool = 'MAP608') => {
    return await $fetch<AfmFileListResponse>(joinApiPath(base, '/afm-files'), {
      query: { tool }
    })
  }

  return { fetchAfmFiles }
}
```

### 8.2 Vue Query에서 `useAsyncData`로 전환

대상 프로젝트는 이미 `useAsyncData`를 표준 패턴으로 사용한다. Vue Query를 새로 들여오면 같은 앱 안에 서버 상태 관리 방식이 두 개가 된다.

권장:

```ts
export const useAfmFiles = (tool: Ref<string>) => {
  const { fetchAfmFiles } = useAfmApi()

  return useAsyncData(
    () => `afm-files:${tool.value}`,
    () => fetchAfmFiles(tool.value),
    { watch: [tool] }
  )
}
```

상세 페이지:

```ts
export const useAfmMeasurement = (filename: Ref<string>, tool: Ref<string>) => {
  const { fetchAfmFileDetail } = useAfmApi()

  return useAsyncData(
    () => `afm-detail:${tool.value}:${filename.value}`,
    () => fetchAfmFileDetail(filename.value, tool.value),
    { watch: [filename, tool] }
  )
}
```

### 8.3 Pinia에서 `useState`로 전환

현재 Pinia store 역할:

- selectedTool
- searchQuery
- viewHistory
- groupedData
- groupHistory
- localStorage persistence
- navigation helper

대상 store 예시:

```ts
export type AfmTool = 'MAP608' | 'MAPC01'

export interface AfmState {
  selectedTool: AfmTool
  searchQuery: string
  viewHistory: AfmMeasurementSummary[]
  groupedData: AfmMeasurementSummary[]
  groupHistory: AfmSavedGroup[]
}

export const useAfmStore = () => {
  const state = useState<AfmState>('afm', () => ({
    selectedTool: 'MAP608',
    searchQuery: '',
    viewHistory: [],
    groupedData: [],
    groupHistory: []
  }))

  const setSelectedTool = (tool: AfmTool) => {
    state.value.selectedTool = tool
  }

  return {
    state,
    selectedTool: computed(() => state.value.selectedTool),
    groupedData: computed(() => state.value.groupedData),
    setSelectedTool
  }
}
```

localStorage 동기화는 대상의 `persist-fab.client.ts`와 같은 client plugin으로 둔다.

```text
front-dev-home/app/plugins/persist-afm.client.ts
```

이 plugin에서 `window.localStorage`를 읽고 `watch`로 저장한다. SSR이 꺼져 있어도 `window`, `document`, `localStorage` 접근은 `.client.ts` 또는 `import.meta.client` guard 안에서만 두는 편이 유지보수에 안전하다.

## 9. ECharts 이식 전략

현재 차트 컴포넌트는 ECharts를 직접 import하고 `window.resize`, `document.createElement`, canvas 다운로드 등을 사용한다. 대상 프로젝트는 `ssr: false`이지만 Nuxt 구조에서는 다음 원칙을 적용한다.

- 차트 컴포넌트 파일명에 `.client.vue` suffix를 붙인다.
- `echarts.init()`는 `onMounted` 이후에만 실행한다.
- resize listener는 `onBeforeUnmount`에서 제거한다.
- chart download는 `import.meta.client` guard를 둔다.
- target package에 `echarts`를 추가한다.

추가 의존성:

```bash
cd front-dev-home
npm install echarts
```

`@tanstack/vue-query`, `axios`, `pinia`, `vuetify`, `@mdi/font`는 추가하지 않는다.

## 10. Navigation 통합 변경점

대상 `NavAppHeader.vue`는 현재 category를 `E-Beam`, `Thickness`로 고정한다. AFM을 허브와 헤더에 붙이려면 다음 변경이 필요하다.

`front-dev-home/app/stores/navigation.ts`:

```ts
export type Category = 'ebeam' | 'afm' | 'thickness'
```

`useNavigation.ts`:

```ts
const navigateToCategory = (category: Category) => {
  store.setCategory(category)

  if (category === 'afm') {
    return router.push('/afm')
  }

  if (category === 'thickness') {
    return router.push('/thickness')
  }

  return router.push(toolTypeHref(store.toolType.value))
}
```

`NavAppHeader.vue`:

```ts
const categories = [
  { id: 'ebeam' as const, label: 'E-Beam', enabled: true },
  { id: 'afm' as const, label: 'AFM', enabled: true },
  { id: 'thickness' as const, label: 'Thickness', enabled: false }
]
```

`layouts/default.vue`는 현재 `NavFeatureTabs`를 항상 렌더링한다. AFM 페이지에서는 E-Beam feature tab이 의미 없으므로 조건을 바꾼다.

```vue
<template v-if="category === 'ebeam'">
  <NavToolTypeTabs />
</template>

...

<NavFeatureTabs v-if="category === 'ebeam'" />
```

AFM 내부 feature navigation은 `/afm` 페이지 상단에 별도 pill nav로 둔다.

```text
검색 | 상세 결과 | 트렌드
```

단, 상세 결과는 선택된 측정이 있을 때만 이동 가능하게 한다.

## 11. API 계약 문서 추가

대상 프로젝트는 `docs/api-contracts/`를 shared contract로 사용한다. AFM 이식 시 다음 파일을 추가한다.

```text
docs/api-contracts/afm.yaml
```

초기 계약에 포함할 type:

- `AfmMeasurementSummary`
- `AfmMeasurementDetail`
- `AfmMeasurementInfo`
- `AfmSummaryRecord`
- `AfmProfilePoint`
- `AfmImageDescriptor`
- `AfmActivity`

초기 계약에 포함할 endpoint:

```text
GET /api/afm-files
GET /api/afm-files/detail/{filename}
GET /api/afm-files/profile/{filename}/{point}
GET /api/afm-files/image/{filename}/{point}
GET /api/afm-files/image-file/{filename}/{point}
GET /api/afm-files/images/{image_type}
GET /api/afm-files/download-raw-image/{filename}/{point}
GET /api/user-activities
GET /api/my-activities
GET /api/current-user
GET /api/user-analytics
```

1차 이식에서는 기존 AFM response shape를 유지한다.

```yaml
response:
  status: 200
  body:
    success:
      type: boolean
    data:
      type: array
      items: AfmMeasurementSummary
    total:
      type: integer
    tool:
      type: string
    message:
      type: string
```

이후 대상 프로젝트 전체 API 스타일에 맞춰 bare array 또는 `{ data, total }` envelope로 통일할지 별도 리팩터링한다.

## 12. 백엔드 이식 주의점

### 12.1 경로 하드코딩 제거

현재 `file_parser.py`는 `Path('itc-afm-data-platform-pjt-shared') / 'AFM_DB' / tool_name` 형태를 반복한다. 대상 프로젝트에 합칠 때는 `AFM_DB_ROOT` 환경 변수로 빼고 모든 route/util에서 같은 helper를 사용해야 한다.

### 12.2 pickle 로드 의존성

pickle 내부에 pandas DataFrame이 들어 있으면 `pickle.load()` 시 pandas/numpy가 설치되어 있어야 한다. 대상 백엔드 requirements에 반영한다.

### 12.3 쿠키 이름 정리

현재 코드에는 `LASTUSER`와 `LAST_USER`가 혼재한다.

- `api/__init__.py` production current-user route: `LASTUSER`
- `activity_routes.py`, `afm_routes.py`: `LAST_USER`

대상 프로젝트로 옮길 때 하나로 표준화해야 한다. 기존 사내 쿠키가 정해져 있다면 그 이름을 기준으로 하고, 문서와 route 모두 동일하게 맞춘다.

### 12.4 이미지 응답 MIME

`serve_profile_image()`는 현재 무조건 `image/webp`로 응답한다. 실제 파일 확장자를 기준으로 `mimetypes.guess_type()`를 적용하는 것이 안전하다.

### 12.5 대용량 상세 데이터

`DataTrendPage`는 groupedData의 모든 상세 데이터를 한 번에 로드한다. 이식 후에도 같은 방식이면 네트워크와 메모리 부담이 크다. 1차 이식에서는 유지하되, 2차 개선으로 다음을 검토한다.

- group detail bulk endpoint 추가: `POST /api/afm-files/bulk-detail`
- 클라이언트 동시 요청 제한
- 트렌드 분석에 필요한 summary만 먼저 로드하고 상세 raw data는 지연 로드

## 13. 단계별 변환 플랜

### Phase 0. 준비

1. 대상 저장소에서 AFM 이식 branch를 만든다.
2. `front-dev-home/package.json`에 `echarts`만 먼저 추가한다.
3. `back_dev_home/requirements.txt`에 `numpy`, `pandas`, `pyarrow`를 추가한다.
4. `docs/api-contracts/afm.yaml` 초안을 작성한다.
5. `AFM_DB_ROOT` 환경 변수와 샘플 경로를 문서화한다.

완료 기준:

- `npm run typecheck`가 기존 상태에서 통과한다.
- Flask `/api/health`가 기존처럼 동작한다.

### Phase 1. 백엔드 AFM API 이식

1. `back_dev_home/afm/` 패키지를 만든다.
2. `api/utils/file_parser.py`를 `back_dev_home/afm/file_parser.py`로 이식하고 경로 helper를 적용한다.
3. `api/afm_routes.py`, `api/image_routes.py`를 대상 blueprint로 옮긴다.
4. `back_dev_home/__init__.py`에 blueprint를 등록한다.
5. 기존 endpoint path는 유지한다.
6. 로컬에서 다음을 검증한다.

```text
GET /api/afm-files?tool=MAP608
GET /api/afm-files/detail/{encoded_filename}?tool=MAP608
GET /api/afm-files/profile/{encoded_filename}/{point}?tool=MAP608
GET /api/afm-files/image-file/{encoded_filename}/{point}?tool=MAP608
```

완료 기준:

- AFM 목록과 상세 API가 대상 Flask에서 기존 프론트가 기대하는 shape로 응답한다.
- 데이터 경로를 바꿔도 코드 수정 없이 `AFM_DB_ROOT`만으로 동작한다.

### Phase 2. Nuxt API composable과 타입 작성

1. `useAfmApi.ts`를 작성한다.
2. `AfmMeasurementSummary`, `AfmMeasurementDetail` 등 타입을 정의한다.
3. 기존 `services/*.js`의 console-heavy 로직을 정리해 typed `$fetch` 함수로 치환한다.
4. `useAfmSearch.ts`, `useAfmResultData.ts`를 `useAsyncData` 기반으로 만든다.

완료 기준:

- AFM API 호출 코드가 axios 없이 동작한다.
- `npm run typecheck`에서 endpoint 응답 타입 오류가 없다.

### Phase 3. AFM 상태와 navigation 통합

1. `stores/afm.ts`에 `useState` 기반 AFM 상태를 만든다.
2. `persist-afm.client.ts`로 selectedTool, searchQuery, history, group을 localStorage와 동기화한다.
3. `navigation.ts`, `useNavigation.ts`, `NavAppHeader.vue`, 허브 `index.vue`에 AFM category를 추가한다.
4. `default.vue`에서 E-Beam 전용 nav가 AFM 페이지에 뜨지 않도록 조건을 조정한다.

완료 기준:

- 허브에서 AFM으로 진입 가능하다.
- 새로고침 후 selectedTool, searchQuery, history, group이 복원된다.

### Phase 4. 검색 페이지 이식

1. `app/pages/afm/index.vue`를 만든다.
2. `SearchSection`, `ViewHistoryCard`, `DataGroupingCard`, `SavedGroupsCard`, `LoadingDialog`를 Nuxt UI로 재작성한다.
3. `v-row/v-col` 기반 레이아웃을 CSS grid/flex로 바꾼다.
4. 툴 선택은 `UButton` 또는 custom segmented pill로 구현한다.

완료 기준:

- `/afm`에서 MAP608/MAPC01 전환이 된다.
- 목록 검색, 그룹 추가, 히스토리 추가, 상세 이동이 된다.

### Phase 5. 결과 상세 페이지 이식

1. `app/pages/afm/result.vue`를 만든다.
2. route query에서 `filename`, `recipeId`, `tool`을 읽는다.
3. `MeasurementInfo`, `StatisticalInfoByPoints`, `MeasurementPoints`, `AdditionalAnalysisImages`를 Nuxt UI로 재작성한다.
4. chart 컴포넌트는 `.client.vue`로 이식한다.
5. 다운로드 기능은 `import.meta.client` guard를 적용한다.

완료 기준:

- 상세 데이터, summary, point table, heatmap, histogram, profile image가 표시된다.
- raw image download와 CSV download가 동작한다.

### Phase 6. 트렌드 페이지 이식

1. `app/pages/afm/trend.vue`를 만든다.
2. 그룹 상세 데이터 전달을 `useAfmStore` state 중심으로 바꾼다.
3. 새로고침 fallback으로 groupedData 기준 재로드를 제공한다.
4. `TimeSeriesChart`를 `.client.vue`로 이식한다.

완료 기준:

- 그룹 선택 후 트렌드 페이지 진입이 된다.
- site/item/measurement 선택 후 시계열 차트가 표시된다.

### Phase 7. 디자인 정리와 검증

1. 모든 AFM card에 `dashboard-surface rounded-2xl` 패턴을 적용한다.
2. 기존 Vuetify 색상 class를 Tailwind/Nuxt UI semantic color로 변환한다.
3. 아이콘을 lucide로 통일한다.
4. `npm run lint`, `npm run typecheck`, `npm run build`를 실행한다.
5. Flask + Nuxt devProxy 환경에서 smoke test를 수행한다.

완료 기준:

- AFM 화면이 대상 앱의 SKEWNONO UI와 같은 톤으로 보인다.
- Vue/Vuetify 잔여 의존성이 없다.
- production build가 생성된다.

## 14. 리스크와 우선순위

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| Vuetify UI를 그대로 가져오려는 경우 | 번들 증가, 디자인 시스템 충돌 | Nuxt UI로 전면 치환 |
| filename path param encoding | `#`가 fragment로 해석될 수 있음 | query 기반 result route 권장 |
| localStorage 직접 접근 | hydration/client 오류 가능 | `.client.ts` plugin 또는 `import.meta.client` guard |
| ECharts SSR/window 의존 | 빌드/렌더 오류 가능 | `.client.vue`, `onMounted` |
| 대용량 trend 데이터 | 느린 로딩/메모리 증가 | 1차 유지, 2차 bulk/summary endpoint |
| 백엔드 상대 경로 | 실행 위치에 따라 파일 못 찾음 | `AFM_DB_ROOT` 환경 변수 |
| 쿠키 이름 불일치 | 사용자 식별 실패 | `LAST_USER` 또는 사내 표준으로 통일 |
| API response shape 변경 | 프론트 회귀 | 1차에서는 기존 AFM shape 유지 |

## 15. 최종 권장 작업 순서

가장 실패 확률이 낮은 순서는 다음이다.

1. 대상 Flask에 AFM API를 먼저 이식한다.
2. `docs/api-contracts/afm.yaml`로 실제 응답 shape를 고정한다.
3. Nuxt에서 `useAfmApi.ts`만 만들어 API 호출을 검증한다.
4. `/afm` 검색 페이지를 먼저 이식해 목록/상세 이동 흐름을 만든다.
5. `/afm/result` 상세 페이지와 chart를 이식한다.
6. `/afm/trend`를 마지막에 이식한다.
7. 그 후 UI 밀도, 컴포넌트 분리, bulk endpoint 최적화를 진행한다.

이 순서가 좋은 이유는 검색 목록과 상세 API가 전체 앱의 기반이고, 트렌드 분석은 그 위에 얹힌 고비용 기능이기 때문이다.

## 16. 참고 자료

- 대상 저장소: https://github.com/DarrenKoi/skewnono_v3_nuxt
- Nuxt 4 directory structure: https://nuxt.com/docs/4.x/guide/directory-structure/nuxtrc
- Nuxt pages and file-based routing: https://nuxt.com/docs/4.x/guide/directory-structure/app/pages
- Nuxt components auto-import: https://nuxt.com/docs/4.x/guide/directory-structure/app/components
- Nuxt composables auto-import: https://nuxt.com/docs/4.x/guide/directory-structure/app/composables
- Nuxt runtime config: https://nuxt.com/docs/4.x/api/composables/use-runtime-config
- Nuxt UI installation: https://ui.nuxt.com/docs/getting-started/installation/nuxt
- Nuxt UI design system: https://ui.nuxt.com/docs/getting-started/theme/design-system
- Nuxt UI Table: https://ui.nuxt.com/docs/components/table
- Nuxt UI Tabs: https://ui.nuxt.com/docs/components/tabs
