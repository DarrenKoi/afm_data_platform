# Vue3 좀 더 다지기

이 장에서는 Vue 3의 더 고급 개념들을 배워보겠습니다. 이전 장에서 배운 기초 개념들을 바탕으로, 실제 개발에서 자주 사용되는 중요한 기능들을 살펴보겠습니다.

## 1. Watchers (감시자)

Watchers는 데이터의 변화를 감시하고, 변화가 일어났을 때 특정 작업을 수행하는 Vue의 기능입니다.

### 1.1 기본 Watcher 사용법

```js
<template>
  <div>
    <h3>AFM 측정 조건 설정</h3>
    <input v-model="scanSpeed" placeholder="스캔 속도 입력" />
    <p>현재 스캔 속도: {{ scanSpeed }}</p>
    <p v-if="speedWarning" style="color: red;">
      {{ speedWarning }}
    </p>
  </div>
</template>;

import { ref, watch } from "vue";

const scanSpeed = ref(0);
const speedWarning = ref("");

// scanSpeed 값을 감시하여 경고 메시지 표시
watch(scanSpeed, (newSpeed, oldSpeed) => {
  console.log(`스캔 속도가 ${oldSpeed}에서 ${newSpeed}로 변경되었습니다`);

  if (newSpeed > 100) {
    speedWarning.value = "스캔 속도가 너무 높습니다! 100 이하로 설정해주세요.";
  } else if (newSpeed < 0) {
    speedWarning.value = "스캔 속도는 음수일 수 없습니다.";
  } else {
    speedWarning.value = "";
  }
});
```

### 1.2 여러 값을 동시에 감시하기

```js
import { ref, watch } from "vue";

const width = ref(0);
const height = ref(0);
const area = ref(0);

// 여러 값을 동시에 감시
watch([width, height], ([newWidth, newHeight]) => {
  area.value = newWidth * newHeight;
  console.log(`스캔 영역: ${area.value}`);
});
```

### 1.3 Deep Watcher (깊은 감시)

객체의 내부 속성 변화도 감시할 수 있습니다:

```js
import { ref, watch } from "vue";

const measurementSettings = ref({
  speed: 50,
  resolution: 256,
  force: 1.5,
});

// 객체 내부 변화도 감시
watch(
  measurementSettings,
  (newSettings) => {
    console.log("측정 설정이 변경되었습니다:", newSettings);
  },
  { deep: true }
);
```

## 2. Props와 Emits (부모-자식 컴포넌트 통신)

Vue에서 컴포넌트 간 데이터를 주고받는 핵심 메커니즘입니다.

### 2.1 Props (부모 → 자식 데이터 전달)

**자식 컴포넌트 (MeasurementCard.vue) 템플릿:**

```html
<template>
  <div class="measurement-card">
    <h3>{{ title }}</h3>
    <p>측정 값: {{ value }} {{ unit }}</p>
    <p>상태: {{ status }}</p>
  </div>
</template>
```

**자식 컴포넌트 스크립트:**

```js
// Props 정의 - 부모로부터 받을 데이터
const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  value: {
    type: Number,
    default: 0,
  },
  unit: {
    type: String,
    default: "nm",
  },
  status: {
    type: String,
    default: "대기중",
    validator: (value) => {
      return ["대기중", "측정중", "완료", "오류"].includes(value);
    },
  },
});

// props 사용하기
console.log("받은 제목:", props.title);
```

**부모 컴포넌트 템플릿:**

```html
<template>
  <div>
    <h2>AFM 측정 대시보드</h2>

    <!-- 자식 컴포넌트에 데이터 전달 -->
    <MeasurementCard
      title="표면 거칠기"
      :value="roughness"
      unit="nm"
      status="측정중"
    />

    <MeasurementCard
      title="높이 측정"
      :value="height"
      unit="μm"
      status="완료"
    />
  </div>
</template>
```

**부모 컴포넌트 스크립트:**

```js
import { ref } from "vue";
import MeasurementCard from "./MeasurementCard.vue";

const roughness = ref(23.5);
const height = ref(1.2);
```

### 2.2 Emits (자식 → 부모 이벤트 전달)

**자식 컴포넌트 템플릿:**

```html
<template>
  <div class="control-panel">
    <h3>측정 제어</h3>
    <button @click="startMeasurement">측정 시작</button>
    <button @click="stopMeasurement">측정 중지</button>
    <button @click="resetMeasurement">초기화</button>
  </div>
</template>
```

**자식 컴포넌트 스크립트:**

```js
// 부모에게 보낼 이벤트 정의
const emit = defineEmits(["start", "stop", "reset", "statusChange"]);

function startMeasurement() {
  // 부모에게 'start' 이벤트 전달
  emit("start", {
    timestamp: new Date(),
    message: "측정을 시작합니다",
  });

  // 상태 변경도 알림
  emit("statusChange", "측정중");
}

function stopMeasurement() {
  emit("stop", {
    timestamp: new Date(),
    message: "측정을 중지합니다",
  });
  emit("statusChange", "중지됨");
}

function resetMeasurement() {
  emit("reset");
  emit("statusChange", "대기중");
}
```

**부모 컴포넌트 템플릿:**

```html
<template>
  <div>
    <h2>AFM 제어 시스템</h2>
    <p>현재 상태: {{ currentStatus }}</p>

    <!-- 자식 컴포넌트의 이벤트 수신 -->
    <ControlPanel
      @start="handleStart"
      @stop="handleStop"
      @reset="handleReset"
      @status-change="handleStatusChange"
    />

    <div v-if="logs.length > 0">
      <h3>로그</h3>
      <ul>
        <li v-for="log in logs" :key="log.id">
          {{ log.time }}: {{ log.message }}
        </li>
      </ul>
    </div>
  </div>
</template>
```

**부모 컴포넌트 스크립트:**

```js
import { ref } from "vue";
import ControlPanel from "./ControlPanel.vue";

const currentStatus = ref("대기중");
const logs = ref([]);

function handleStart(data) {
  console.log("측정 시작:", data);
  addLog(data.message);
}

function handleStop(data) {
  console.log("측정 중지:", data);
  addLog(data.message);
}

function handleReset() {
  console.log("초기화됨");
  addLog("시스템이 초기화되었습니다");
  logs.value = []; // 로그도 초기화
}

function handleStatusChange(newStatus) {
  currentStatus.value = newStatus;
}

function addLog(message) {
  logs.value.push({
    id: Date.now(),
    time: new Date().toLocaleTimeString(),
    message: message,
  });
}
```

## 3. 생명주기 (Lifecycle)

Vue 컴포넌트는 생성부터 소멸까지 여러 단계를 거칩니다. 각 단계에서 특별한 작업을 수행할 수 있습니다.

### 3.1 주요 생명주기 훅들

```js
<template>
  <div>
    <h3>AFM 데이터 분석기</h3>
    <div v-if="loading">데이터 로딩 중...</div>
    <div v-else>
      <p>분석된 데이터 포인트: {{ dataPoints.length }}개</p>
      <button @click="refreshData">데이터 새로고침</button>
    </div>
  </div>
</template>

import { ref, onMounted, onBeforeUnmount, onUpdated } from "vue";

const loading = ref(true);
const dataPoints = ref([]);
let dataUpdateTimer = null;

// 컴포넌트가 DOM에 마운트된 후 실행
onMounted(() => {
  console.log("AFM 분석기가 마운트되었습니다");

  // 초기 데이터 로드
  loadInitialData();

  // 주기적 데이터 업데이트 시작
  startDataUpdate();
});

// 컴포넌트가 업데이트될 때마다 실행
onUpdated(() => {
  console.log("컴포넌트가 업데이트되었습니다");
  console.log("현재 데이터 포인트 수:", dataPoints.value.length);
});

// 컴포넌트가 언마운트되기 전 실행 (정리 작업)
onBeforeUnmount(() => {
  console.log("AFM 분석기가 언마운트됩니다");

  // 타이머 정리
  if (dataUpdateTimer) {
    clearInterval(dataUpdateTimer);
    console.log("데이터 업데이트 타이머가 정리되었습니다");
  }

  // 기타 정리 작업
  cleanup();
});

// 초기 데이터 로드
async function loadInitialData() {
  try {
    loading.value = true;

    // 가상의 AFM 데이터 로드
    await new Promise((resolve) => setTimeout(resolve, 2000)); // 2초 대기

    dataPoints.value = generateSampleData(100);
    console.log("초기 데이터 로드 완료");
  } catch (error) {
    console.error("데이터 로드 실패:", error);
  } finally {
    loading.value = false;
  }
}

// 주기적 데이터 업데이트
function startDataUpdate() {
  dataUpdateTimer = setInterval(() => {
    // 새로운 데이터 포인트 추가
    const newPoint = {
      x: Math.random() * 100,
      y: Math.random() * 100,
      z: Math.random() * 10,
      timestamp: new Date(),
    };

    dataPoints.value.push(newPoint);
    console.log("새 데이터 포인트 추가:", newPoint);

    // 데이터가 너무 많아지면 오래된 것 제거
    if (dataPoints.value.length > 1000) {
      dataPoints.value.shift();
    }
  }, 5000); // 5초마다 업데이트
}

// 데이터 새로고침
async function refreshData() {
  dataPoints.value = [];
  await loadInitialData();
}

// 샘플 데이터 생성
function generateSampleData(count) {
  const data = [];
  for (let i = 0; i < count; i++) {
    data.push({
      x: Math.random() * 100,
      y: Math.random() * 100,
      z: Math.random() * 10,
      timestamp: new Date(Date.now() - Math.random() * 86400000), // 24시간 내 랜덤
    });
  }
  return data;
}

// 정리 작업
function cleanup() {
  // WebSocket 연결 종료, 이벤트 리스너 제거 등
  console.log("정리 작업 완료");
}
```

### 3.2 생명주기 순서 이해하기

```js
import {
  ref,
  onBeforeMount,
  onMounted,
  onBeforeUpdate,
  onUpdated,
  onBeforeUnmount,
  onUnmounted,
} from "vue";

const count = ref(0);

// 1. 마운트 전 (DOM 생성 전)
onBeforeMount(() => {
  console.log("1. onBeforeMount: DOM이 생성되기 전");
});

// 2. 마운트 후 (DOM 생성 후)
onMounted(() => {
  console.log("2. onMounted: DOM이 생성된 후");
  // DOM 요소에 접근 가능
  // 외부 라이브러리 초기화
  // API 호출 등
});

// 3. 업데이트 전 (데이터 변경으로 인한 재렌더링 전)
onBeforeUpdate(() => {
  console.log("3. onBeforeUpdate: 업데이트 전");
});

// 4. 업데이트 후 (재렌더링 후)
onUpdated(() => {
  console.log("4. onUpdated: 업데이트 후");
  // 업데이트된 DOM에 접근 가능
});

// 5. 언마운트 전 (컴포넌트 제거 전)
onBeforeUnmount(() => {
  console.log("5. onBeforeUnmount: 언마운트 전");
  // 정리 작업 수행
});

// 6. 언마운트 후 (컴포넌트 제거 후)
onUnmounted(() => {
  console.log("6. onUnmounted: 언마운트 후");
});
```

## 4. 실제 AFM 프로젝트에서의 활용 예시

### 4.1 측정 데이터 모니터링 컴포넌트 - 완전한 예시

**템플릿:**

```html
<template>
  <div class="afm-monitor">
    <h2>AFM 실시간 모니터링</h2>

    <!-- 측정 상태 표시 -->
    <div class="status-panel">
      <div :class="['status-indicator', statusClass]"></div>
      <span>{{ measurementStatus }}</span>
    </div>

    <!-- 측정 데이터 -->
    <div class="data-display">
      <div v-for="channel in channels" :key="channel.id">
        <DataChannel
          :name="channel.name"
          :value="channel.value"
          :unit="channel.unit"
          :status="channel.status"
          @alert="handleChannelAlert"
        />
      </div>
    </div>

    <!-- 제어 버튼 -->
    <div class="controls">
      <button @click="startMonitoring" :disabled="isMonitoring">시작</button>
      <button @click="stopMonitoring" :disabled="!isMonitoring">중지</button>
    </div>
  </div>
</template>
```

**스크립트:**

```js
import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue";
import DataChannel from "./DataChannel.vue";

// 반응형 데이터
const measurementStatus = ref("대기중");
const isMonitoring = ref(false);
const channels = ref([
  { id: 1, name: "X축 위치", value: 0, unit: "nm", status: "normal" },
  { id: 2, name: "Y축 위치", value: 0, unit: "nm", status: "normal" },
  { id: 3, name: "Z축 높이", value: 0, unit: "nm", status: "normal" },
  { id: 4, name: "캔틸레버 힘", value: 0, unit: "nN", status: "normal" },
]);

let monitoringInterval = null;

// 계산된 속성
const statusClass = computed(() => {
  switch (measurementStatus.value) {
    case "측정중":
      return "status-active";
    case "오류":
      return "status-error";
    case "완료":
      return "status-complete";
    default:
      return "status-idle";
  }
});

// 감시자 - 측정 상태 변화 모니터링
watch(measurementStatus, (newStatus, oldStatus) => {
  console.log(`측정 상태 변경: ${oldStatus} → ${newStatus}`);

  if (newStatus === "오류") {
    // 오류 발생 시 모니터링 중지
    stopMonitoring();
  }
});

// 마운트 시 초기화
onMounted(() => {
  console.log("AFM 모니터 초기화 완료");
});

// 언마운트 전 정리
onBeforeUnmount(() => {
  if (monitoringInterval) {
    clearInterval(monitoringInterval);
  }
});

// 모니터링 시작
function startMonitoring() {
  isMonitoring.value = true;
  measurementStatus.value = "측정중";

  monitoringInterval = setInterval(() => {
    updateChannelData();
  }, 1000);
}

// 모니터링 중지
function stopMonitoring() {
  isMonitoring.value = false;
  measurementStatus.value = "대기중";

  if (monitoringInterval) {
    clearInterval(monitoringInterval);
    monitoringInterval = null;
  }
}

// 채널 데이터 업데이트
function updateChannelData() {
  channels.value.forEach((channel) => {
    // 실제로는 AFM 장비에서 데이터를 받아옴
    channel.value = Math.random() * 100;

    // 임계값 체크
    if (channel.value > 80) {
      channel.status = "warning";
    } else if (channel.value > 95) {
      channel.status = "error";
    } else {
      channel.status = "normal";
    }
  });
}

// 채널 알림 처리
function handleChannelAlert(channelInfo) {
  console.log("채널 알림:", channelInfo);
  if (channelInfo.severity === "critical") {
    measurementStatus.value = "오류";
  }
}
```

**스타일:**

```css
.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 8px;
}

.status-idle {
  background-color: gray;
}
.status-active {
  background-color: #4caf50;
}
.status-error {
  background-color: #f44336;
}
.status-complete {
  background-color: #2196f3;
}
```

## 정리

이 장에서 배운 내용:

1. **Watchers**: 데이터 변화 감시 및 반응
2. **Props**: 부모에서 자식으로 데이터 전달
3. **Emits**: 자식에서 부모로 이벤트 전달
4. **생명주기**: 컴포넌트의 생성부터 소멸까지의 과정

이러한 개념들은 Vue 애플리케이션 개발의 핵심이며, AFM 데이터 플랫폼과 같은 복잡한 시스템에서 컴포넌트 간의 효율적인 데이터 흐름과 상태 관리를 가능하게 합니다.

다음 장에서는 Vuetify를 사용한 UI 구성에 대해 배워보겠습니다.
