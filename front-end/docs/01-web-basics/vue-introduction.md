# Vue.js 소개

## Vue.js가 무엇인가요?

Vue.js는 웹 애플리케이션을 만들기 위한 **프레임워크**입니다.

**프레임워크란?** 🏗️
집을 지을 때 미리 만들어진 기둥, 벽, 지붕 등을 사용하는 것처럼, 웹 개발에 필요한 기본 구조와 도구들을 미리 만들어놓은 것입니다.

## 왜 Vue.js를 사용할까요?

### 1. **순수 HTML/CSS/JavaScript만 사용했다면...**

```html
<!-- index.html -->
<div id="search-results"></div>
<script>
  // 검색 결과를 하나씩 HTML로 만들어야 함
  function showResults(results) {
    let html = ''
    for (let i = 0; i < results.length; i++) {
      html += `
        <div class="result-item">
          <h3>${results[i].title}</h3>
          <p>${results[i].description}</p>
        </div>
      `
    }
    document.getElementById('search-results').innerHTML = html
  }
</script>
```

**문제점:**
- 코드가 복잡하고 반복적
- HTML과 JavaScript가 뒤섞여서 관리하기 어려움
- 버그가 생기기 쉬움

### 2. **Vue.js를 사용하면...**

```vue
<!-- SearchResults.vue -->
<template>
  <div>
    <div v-for="result in results" :key="result.id" class="result-item">
      <h3>{{ result.title }}</h3>
      <p>{{ result.description }}</p>
    </div>
  </div>
</template>

<script setup>
const results = ref([])
</script>
```

**장점:**
- 코드가 깔끔하고 이해하기 쉬움
- HTML, CSS, JavaScript가 하나의 파일에 정리됨
- 자동으로 화면을 업데이트해줌

## Vue.js의 핵심 개념

### 1. **컴포넌트 (Component)**
화면의 한 부분을 담당하는 독립적인 조각

```vue
<!-- SearchBar.vue - 검색창 컴포넌트 -->
<template>
  <v-text-field 
    v-model="query" 
    label="검색어를 입력하세요"
    @keyup.enter="search"
  />
</template>
```

**비유**: 레고 블록처럼 작은 부품들을 조합해서 완전한 애플리케이션을 만드는 것

### 2. **반응성 (Reactivity)**
데이터가 변하면 자동으로 화면이 업데이트됨

```javascript
const count = ref(0)  // count가 변하면
// 화면의 {{ count }}도 자동으로 변함
```

### 3. **디렉티브 (Directives)**
HTML에 특별한 기능을 추가하는 Vue만의 문법

```html
<div v-if="isLoggedIn">로그인되었습니다</div>
<div v-for="item in items">{{ item.name }}</div>
<button v-on:click="handleClick">클릭하세요</button>
```

## 우리 AFM 프로젝트에서 Vue.js 찾아보기

### 1. **컴포넌트 구조**
```
src/
├── pages/
│   ├── MainPage.vue      ← 메인 검색 페이지
│   ├── ResultPage.vue    ← 결과 상세 페이지
│   └── DataTrendPage.vue ← 트렌드 분석 페이지
├── layouts/
│   ├── AppHeader.vue     ← 상단 헤더
│   └── AppFooter.vue     ← 하단 푸터
```

각 `.vue` 파일이 하나의 컴포넌트입니다!

### 2. **Vue 파일 구조**
모든 `.vue` 파일은 3부분으로 구성됩니다:

```vue
<template>
  <!-- HTML 템플릿 (화면에 보이는 부분) -->
</template>

<script setup>
  // JavaScript 로직 (동작 부분)
</script>

<style>
  /* CSS 스타일 (디자인 부분) */
</style>
```

### 3. **실제 예시: MainPage.vue**

```vue
<template>
  <!-- 화면 구조 -->
  <v-text-field 
    v-model="searchQuery"           ← 입력값을 searchQuery와 연결
    @keyup.enter="performSearch"    ← 엔터키를 누르면 performSearch 실행
  />
  
  <v-card v-if="searchResults.length > 0">  ← 검색 결과가 있을 때만 보이기
    <v-list-item v-for="result in searchResults" :key="result.id">
      <!-- 검색 결과를 하나씩 반복해서 보여주기 -->
    </v-list-item>
  </v-card>
</template>

<script setup>
// 반응형 데이터
const searchQuery = ref('')        // 검색어
const searchResults = ref([])      // 검색 결과

// 함수
function performSearch() {
  // 검색 로직
}
</script>
```

## Vue.js vs 다른 프레임워크

| 프레임워크 | 특징 | 난이도 |
|-----------|------|--------|
| **Vue.js** | 배우기 쉬움, 한국어 자료 많음 | ⭐⭐ |
| React | 가장 인기, 취업에 유리 | ⭐⭐⭐ |
| Angular | 대규모 프로젝트에 적합 | ⭐⭐⭐⭐ |

**우리가 Vue.js를 선택한 이유:**
- 배우기 쉬워서 비개발자도 접근 가능
- 문법이 직관적
- 한국에서도 많이 사용됨

## 직접 해보기 🎯

1. `src/pages/MainPage.vue` 파일을 열어보세요
2. `<template>`, `<script setup>`, `<style>` 3개 섹션을 찾아보세요
3. `v-model`, `v-if`, `v-for` 같은 Vue 디렉티브를 찾아보세요
4. `ref()`, `function` 같은 JavaScript 부분을 찾아보세요

## 다음 단계

Vue.js의 기본 개념을 이해했다면, 다음으로 [프로젝트 구조 이해하기](../02-project-structure/folder-organization.md)를 읽어보세요.

우리 프로젝트의 파일들이 어떻게 구성되어 있는지 알아봅시다!