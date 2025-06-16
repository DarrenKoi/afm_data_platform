# 웹 개발 기초 이해하기

## 웹 애플리케이션이란?

웹 애플리케이션은 인터넷 브라우저에서 실행되는 프로그램입니다. 예를 들어:
- 네이버, 구글 (검색 사이트)
- 유튜브 (동영상 사이트)
- 온라인 쇼핑몰
- 우리가 만드는 AFM 데이터 뷰어

## 웹의 3가지 핵심 기술

### 1. HTML (HyperText Markup Language)
**역할**: 웹페이지의 구조와 내용을 정의

```html
<!-- 이런 식으로 생겼습니다 -->
<h1>제목입니다</h1>
<p>이것은 문단입니다</p>
<button>버튼입니다</button>
```

**비유**: 집의 뼈대나 기둥 같은 역할
- 어디에 제목이 올지
- 어디에 버튼이 있을지
- 어디에 이미지가 들어갈지

### 2. CSS (Cascading Style Sheets)
**역할**: 웹페이지의 디자인과 레이아웃을 담당

```css
/* 이런 식으로 생겼습니다 */
h1 {
  color: blue;
  font-size: 24px;
}

button {
  background-color: green;
  border-radius: 5px;
}
```

**비유**: 집의 인테리어나 페인트 같은 역할
- 글자 색깔과 크기
- 버튼의 색깔과 모양
- 레이아웃 배치

### 3. JavaScript
**역할**: 웹페이지에 동작과 상호작용을 추가

```javascript
// 이런 식으로 생겼습니다
function searchData() {
  console.log('검색 버튼을 클릭했습니다!')
}

const searchResults = []
```

**비유**: 집의 전기, 수도, 엘리베이터 같은 역할
- 버튼을 클릭했을 때 무엇을 할지
- 데이터를 어떻게 처리할지
- 사용자와 어떻게 상호작용할지

## 우리 AFM 프로젝트에서 확인해보기

### 1. HTML 구조 찾아보기
`src/pages/MainPage.vue` 파일의 `<template>` 부분을 보면:

```html
<v-container>
  <v-card>
    <v-text-field label="Search AFM measurements..." />
    <v-btn>Search</v-btn>
  </v-card>
</v-container>
```

- `v-container`: 전체 영역을 감싸는 컨테이너
- `v-card`: 카드 모양의 박스
- `v-text-field`: 텍스트 입력 필드
- `v-btn`: 버튼

### 2. CSS 스타일 찾아보기
같은 파일에서 `style` 부분이나 `class` 속성들:

```html
<div class="text-center mb-6">
<v-card class="pa-6 mb-4" elevation="3">
```

- `text-center`: 텍스트를 가운데 정렬
- `mb-6`: 아래쪽 여백 6단위
- `pa-6`: 내부 패딩 6단위
- `elevation="3"`: 그림자 효과

### 3. JavaScript 로직 찾아보기
`<script setup>` 부분을 보면:

```javascript
const searchQuery = ref('')
const searchResults = ref([])

function performSearch() {
  // 검색 기능 실행
}
```

- `searchQuery`: 사용자가 입력한 검색어를 저장
- `searchResults`: 검색 결과를 저장
- `performSearch()`: 검색 버튼을 눌렀을 때 실행되는 함수

## 직접 해보기 🎯

1. `src/pages/MainPage.vue` 파일을 열어보세요
2. `<template>` 섹션에서 HTML 구조를 찾아보세요
3. `<script setup>` 섹션에서 JavaScript 코드를 찾아보세요
4. 브라우저에서 개발자 도구(F12)를 열고 Elements 탭에서 실제 HTML을 확인해보세요

## 다음 단계

HTML, CSS, JavaScript의 기본 개념을 이해했다면, 다음으로 [Vue.js 소개](./vue-introduction.md)를 읽어보세요.

Vue.js는 이 3가지 기술을 더 쉽고 효율적으로 사용할 수 있게 도와주는 도구입니다.