# 프로젝트 Configuration 파일 가이드

이 문서는 AFM Data Platform frontend 프로젝트의 주요 설정 파일들의 목적과 구성을 설명합니다.

## 개요

이 프로젝트는 개발 환경, build 과정, 그리고 코드 품질 도구를 설정하기 위해 여러 configuration 파일들을 사용합니다. 이러한 파일들을 이해하면 프로젝트를 필요에 맞게 커스터마이징할 수 있습니다.

## Configuration 파일들

### `.env` 및 `.env.production`
Runtime 변수를 위한 환경별 설정 파일입니다.

**목적**: Vue application에서 접근할 수 있는 환경 변수를 저장
**위치**: front-end 디렉토리의 root
**사용법**: `VITE_` prefix가 붙은 변수들은 client-side 코드에서 사용 가능

```bash
# .env (development)
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=AFM Data Platform (Dev)

# .env.production (production build)
VITE_API_BASE_URL=https://api.afm-platform.com
VITE_APP_TITLE=AFM Data Platform
```

**주의사항**:
- 민감한 데이터(API keys, passwords)는 절대 .env 파일에 commit하지 마세요
- 로컬 전용 민감한 변수는 `.env.local`을 사용하세요 (.gitignore에 추가)
- 변수들은 runtime이 아닌 build time에 포함됩니다

### `eslint.config.js`
JavaScript/Vue 코드 linting 및 formatting을 위한 ESLint 설정입니다.

**목적**: 코드 품질 및 일관된 코딩 표준을 강제
**기능들**:
- Vue 3 전용 rules
- Vuetify component linting
- 저장 시 자동 수정
- VS Code 통합

**주요 설정**:
```javascript
// Vuetify의 권장 ESLint config를 확장
export default [
  ...vuetify,
  {
    files: ['**/*.vue', '**/*.js'],
    rules: {
      // 커스텀 rules를 여기에 추가할 수 있습니다
    }
  }
]
```

**사용법**: `npm run lint`를 실행하여 코드 이슈를 확인하고 자동 수정

### `jsconfig.json`
더 나은 IDE 지원을 위한 JavaScript 프로젝트 설정입니다.

**목적**: IntelliSense, path resolution, 그리고 더 나은 개발 경험 제공
**주요 기능들**:
- Path aliases (`@`는 `src/`를 가리킴)
- Module resolution
- Vue 파일 인식
- 자동 완성 지원

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### `package.json`
프로젝트 metadata 및 dependency 관리입니다.

**목적**: 프로젝트 dependencies, scripts, metadata를 정의
**주요 섹션들**:

**Scripts**:
```json
{
  "scripts": {
    "dev": "vite",           // Development server
    "build": "vite build",   // Production build
    "preview": "vite preview", // Production build 미리보기
    "lint": "eslint . --fix"   // 코드 linting
  }
}
```

**Dependencies vs DevDependencies**:
- **dependencies**: Runtime libraries (Vue, Vuetify, Pinia, Vue Router)
- **devDependencies**: Build tools와 개발 전용 packages (Vite, ESLint 등)

### `package-lock.json`
정확한 dependency 버전 lock 파일입니다.

**목적**: 모든 환경에서 일관된 dependency 버전을 보장
**주요 사항들**:
- npm에 의해 자동 생성
- version control에 commit되어야 함
- 재현 가능한 builds를 보장
- 정확한 버전과 dependency tree를 포함

### `vite.config.mjs`
Vite build tool 설정입니다.

**목적**: Development server, build 과정, bundling을 설정
**주요 기능들**:

**Plugins**:
- Vue 3 지원
- Vuetify 통합
- Auto-imports (components와 composables)
- Font loading
- Layout system

**Build 최적화**:
```javascript
build: {
  rollupOptions: {
    output: {
      manualChunks(id) {
        // 더 나은 성능을 위한 코드 분할
        if (id.includes('vuetify')) return 'vuetify';
        if (id.includes('echarts')) return 'charts';
        // ... 더 많은 chunks
      }
    }
  },
  chunkSizeWarningLimit: 300 // 300KB 이상의 chunks에 대해 경고
}
```

**Development Server**:
- Port: 3000
- Hot module replacement
- Asset 최적화

## 자동 생성 파일들

### `components.d.ts`
자동 import되는 components를 위한 TypeScript 정의입니다.

**목적**: Vuetify와 custom components에 대한 type safety 제공
**생성**: unplugin-vue-components
**Commit 여부**: Yes

### `auto-imports.d.ts`
자동 import되는 Vue APIs와 composables를 위한 TypeScript 정의입니다.

**목적**: Vue composables (ref, computed 등)와 Pinia functions에 대한 type safety 제공
**생성**: unplugin-auto-import
**Commit 여부**: Yes

## Best Practices

1. **Environment Variables**: Client에서 접근 가능한 변수는 `VITE_` prefix를 사용하세요
2. **Dependencies**: Runtime dependencies와 dev dependencies를 분리하세요
3. **Linting**: 코드를 commit하기 전에 `npm run lint`를 실행하세요
4. **Build Testing**: Production builds를 테스트하려면 `npm run preview`를 사용하세요
5. **Version Control**: package-lock.json과 자동 생성된 .d.ts 파일들을 commit하세요

## 문제 해결

**일반적인 문제들**:
- Auto-imports 누락: .d.ts 파일을 재생성하려면 dev server를 재시작하세요
- Build 오류: vite.config.mjs의 syntax 오류를 확인하세요
- Linting 오류: 대부분의 문제를 자동 수정하려면 `npm run lint`를 실행하세요
- Environment variables가 작동하지 않음: `VITE_` prefix가 사용되었는지 확인하세요