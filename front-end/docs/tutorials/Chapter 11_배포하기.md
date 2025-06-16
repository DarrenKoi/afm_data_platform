# 배포하기

## 프로덕션 빌드

개발이 완료된 Vue 애플리케이션을 실제 사용자에게 제공하기 위해서는 **프로덕션 빌드** 과정이 필요합니다. 개발 환경에서는 개발자 편의를 위한 다양한 기능들이 포함되어 있어 파일 크기가 크고 속도가 느립니다. 프로덕션 빌드는 이러한 개발용 코드를 제거하고 최적화하여 사용자에게 최상의 성능을 제공합니다.

### 프로덕션 빌드란?

프로덕션 빌드는 애플리케이션을 실제 운영 환경에 배포하기 위해 최적화하는 과정입니다. 이 과정에서 다음과 같은 작업들이 수행됩니다:

- **코드 압축(Minification)**: 불필요한 공백, 주석, 긴 변수명을 줄여 파일 크기를 최소화합니다.
- **트리 쉐이킹(Tree Shaking)**: 사용하지 않는 코드를 자동으로 제거합니다.
- **코드 분할(Code Splitting)**: 애플리케이션을 여러 작은 청크로 나누어 필요한 부분만 로드합니다.
- **에셋 최적화**: 이미지, 폰트 등의 정적 파일들을 압축하고 최적화합니다.

---

## Vue 프로젝트 빌드하기

Vue 프로젝트의 루트 디렉토리에서 다음 명령어를 실행합니다:

```bash
# 프로덕션 빌드 실행
npm run build
```

빌드가 완료되면 `dist` 폴더가 생성되며, 이 안에 배포 가능한 파일들이 들어있습니다:

```
dist/
├── assets/           # JS, CSS 파일 (해시값 포함)
│   ├── index-5f3d2a1b.js
│   ├── index-8b4c9f7e.css
│   └── logo-1a2b3c4d.png
├── index.html        # 진입점 HTML 파일
└── favicon.ico       # 파비콘
```

---

## 빌드 결과 분석하기

빌드 크기와 구성을 시각적으로 확인하려면 분석 도구를 사용할 수 있습니다:

```bash
# 빌드 분석 도구 설치
npm install -D rollup-plugin-visualizer
```

`vite.config.js`에 다음을 추가합니다:

```js
import { visualizer } from "rollup-plugin-visualizer";

export default defineConfig({
  plugins: [
    vue(),
    visualizer({
      open: true,
      filename: "dist/stats.html",
    }),
  ],
});
```

---

## 빌드 최적화 팁

### 청크 크기 조정

```js
// vite.config.js
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["vue", "vuetify"],
          charts: ["echarts"],
          utils: ["lodash", "axios"],
        },
      },
    },
    chunkSizeWarningLimit: 1000, // 청크 크기 경고 임계값 (KB)
  },
});
```

---

## 환경 변수 설정

환경 변수를 사용하면 개발, 스테이징, 프로덕션 환경에 따라 다른 설정을 적용할 수 있습니다. API 엔드포인트, 인증 키, 기능 플래그 등을 환경별로 다르게 설정할 때 유용합니다.

### 환경 변수 파일 구성

프로젝트 루트에 다음과 같은 환경 변수 파일들을 생성합니다:

- `.env` (모든 환경 공통)
  ```env
  VITE_APP_TITLE=AFM Data Viewer
  VITE_APP_VERSION=1.0.0
  ```
- `.env.development` (개발 환경)
  ```env
  VITE_API_BASE_URL=http://localhost:5000/api
  VITE_DEBUG_MODE=true
  VITE_MOCK_DATA=true
  ```
- `.env.production` (프로덕션 환경)
  ```env
  VITE_API_BASE_URL=https://afm-api.skhynix.com/api
  VITE_DEBUG_MODE=false
  VITE_MOCK_DATA=false
  ```

### 환경 변수 사용하기

Vue 컴포넌트나 JavaScript 파일에서 환경 변수를 사용하는 방법:

```js
// API 설정
const apiConfig = {
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
};

// 디버그 모드 확인
if (import.meta.env.VITE_DEBUG_MODE === "true") {
  console.log("Debug mode is enabled");
}

// 앱 정보 표시
const appInfo = {
  title: import.meta.env.VITE_APP_TITLE,
  version: import.meta.env.VITE_APP_VERSION,
  mode: import.meta.env.MODE, // 'development' 또는 'production'
};
```

#### 환경 변수 보안 주의사항

- **중요한 정보 노출 금지**: API 키, 비밀번호 등 민감한 정보는 프론트엔드 환경 변수에 포함하면 안 됩니다.
- **Git 제외**: `.env.local` 파일은 `.gitignore`에 추가하여 버전 관리에서 제외합니다.
- **VITE\*** 접두사: Vite에서는 `VITE`로 시작하는 환경 변수만 클라이언트 코드에 노출됩니다.
