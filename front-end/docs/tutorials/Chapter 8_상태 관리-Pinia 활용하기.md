# 상태 관리 - Pinia 활용하기

## 상태 관리 필요성

Vue 애플리케이션이 성장하면서 컴포넌트 간 데이터 공유가 복잡해집니다. 부모-자식 관계가 아닌 컴포넌트들이 같은 데이터를 사용해야 하거나, 여러 컴포넌트에서 동일한 상태를 변경해야 할 때 상태 관리가 필요합니다.

**상태 관리가 필요한 시나리오**

- 사용자 로그인 정보를 여러 컴포넌트에서 사용
- AFM 장비 목록을 대시보드, 분석 페이지, 설정 페이지에서 공유
- 실시간 알림을 여러 화면에서 동시에 표시
- 필터링된 데이터를 페이지 이동 후에도 유지

## Pinia 설치 및 설정

Pinia는 Vue 3를 위한 공식 상태 관리 라이브러리입니다. Vuex의 후속 버전으로, 더 간단하고 TypeScript 친화적인 API를 제공합니다.

**읽을 거리 (TypeScript = 타입을 가진 JavaScript + 더 나은 개발 경험)**

TypeScript는 JavaScript에 **정적 타입(type)**을 추가한 **프로그래밍 언어**입니다.  
JavaScript의 상위 집합(Superset)으로, JavaScript 코드에 타입을 명시할 수 있게 해 주어 **코드 오류를 사전에 방지**하고 **더 안전하고 유지보수하기 쉬운 코드**를 작성할 수 있게 합니다. TypeScript 코드는 브라우저에서 실행될 수 있도록 **JavaScript로 컴파일**됩니다. 코드가 방대해지고 협업이 진행될 때 TypeScript를 주로 사용하게 됩니다. JavaScript가 익숙해지면 TypeScript를 공부해봅시다.

**설치**

```bash
npm install pinia
```

**main.js 설정**

```javascript
import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);

app.mount("#app");
```

## Store 만들기

Pinia에서는 `defineStore` 함수를 사용하여 스토어를 정의합니다. Composition API 스타일로 작성하면 더 직관적입니다.

**src/stores/equipment.js**

```javascript
import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useEquipmentStore = defineStore("equipment", () => {
  // State
  const equipments = ref([]);
  const loading = ref(false);
  const selectedEquipmentId = ref(null);

  // Getters
  const activeEquipments = computed(() => {
    return equipments.value.filter((eq) => eq.status === "active");
  });

  const selectedEquipment = computed(() => {
    return equipments.value.find((eq) => eq.id === selectedEquipmentId.value);
  });

  const equipmentCount = computed(() => equipments.value.length);

  // Actions
  async function fetchEquipments() {
    loading.value = true;
    try {
      const response = await fetch("/api/equipments");
      equipments.value = await response.json();
    } catch (error) {
      console.error("장비 목록 로드 실패:", error);
    } finally {
      loading.value = false;
    }
  }

  function addEquipment(equipment) {
    equipments.value.push({
      id: Date.now(),
      ...equipment,
      createdAt: new Date().toISOString(),
    });
  }

  function updateEquipment(id, updates) {
    const index = equipments.value.findIndex((eq) => eq.id === id);
    if (index !== -1) {
      equipments.value[index] = { ...equipments.value[index], ...updates };
    }
  }

  function deleteEquipment(id) {
    equipments.value = equipments.value.filter((eq) => eq.id !== id);
  }

  function selectEquipment(id) {
    selectedEquipmentId.value = id;
  }

  return {
    // State
    equipments,
    loading,
    selectedEquipmentId,

    // Getters
    activeEquipments,
    selectedEquipment,
    equipmentCount,

    // Actions
    fetchEquipments,
    addEquipment,
    updateEquipment,
    deleteEquipment,
    selectEquipment,
  };
});
```

## State, Getters, Actions 설명

### State (상태)

애플리케이션의 중앙 데이터 저장소입니다. Composition API에서는 `ref()`나 `reactive()`를 사용하여 반응형 상태를 정의합니다.

```javascript
const equipments = ref([]); // 장비 목록
const loading = ref(false); // 로딩 상태
const filters = reactive({
  // 필터 옵션
  status: "all",
  type: null,
});
```

### Getters (계산된 속성)

State를 기반으로 파생된 값을 반환합니다. `computed()`를 사용하여 정의하며, 종속된 상태가 변경될 때만 재계산됩니다.

```javascript
const activeCount = computed(() => {
  return equipments.value.filter((eq) => eq.status === "active").length;
});

const filteredEquipments = computed(() => {
  return equipments.value.filter((eq) => {
    if (filters.status !== "all" && eq.status !== filters.status) return false;
    if (filters.type && eq.type !== filters.type) return false;
    return true;
  });
});
```

### Actions (액션)

상태를 변경하는 함수들입니다. 비동기 작업도 처리할 수 있으며, 일반 함수로 정의합니다.

```javascript
async function fetchMeasurementData(equipmentId) {
  try {
    const response = await fetch(`/api/equipments/${equipmentId}/measurements`);
    const data = await response.json();

    // 상태 업데이트
    const equipment = equipments.value.find((eq) => eq.id === equipmentId);
    if (equipment) {
      equipment.measurements = data;
    }
  } catch (error) {
    console.error("측정 데이터 로드 실패:", error);
  }
}
```

## Composition API 도입과 어떻게 변했는지 설명

### Options API vs Composition API

**기존 Options API 방식 (Vuex/Pinia)**

```javascript
export const useEquipmentStore = defineStore("equipment", {
  state: () => ({
    equipments: [],
    loading: false,
  }),

  getters: {
    activeEquipments: (state) => {
      return state.equipments.filter((eq) => eq.status === "active");
    },
  },

  actions: {
    async fetchEquipments() {
      this.loading = true;
      // ...
    },
  },
});
```

**Composition API 방식**

```javascript
export const useEquipmentStore = defineStore("equipment", () => {
  // 모든 로직을 하나의 setup 함수 안에 작성
  const equipments = ref([]);
  const loading = ref(false);

  const activeEquipments = computed(() => {
    return equipments.value.filter((eq) => eq.status === "active");
  });

  async function fetchEquipments() {
    loading.value = true;
    // ...
  }

  return { equipments, loading, activeEquipments, fetchEquipments };
});
```

### Composition API의 장점

1. **타입 추론 향상**: TypeScript와 함께 사용할 때 더 정확한 타입 추론
2. **코드 재사용**: Composable 함수로 로직을 쉽게 추출하고 재사용
3. **더 나은 구조화**: 관련된 로직을 함께 그룹화
4. **IDE 지원**: 자동 완성과 리팩토링이 더 효과적

Composable 함수란, **다른 함수들과 조합(조합 가능, composition)**하여 더 복잡한 동작을 만들어낼 수 있는 함수입니다.

보통 입력과 출력을 명확히 하고, 부작용이 없는 순수 함수인 경우가 많습니다.

## 컴포넌트에서 Store 사용 예시

### 대시보드 컴포넌트

```javascript
<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1>장비 현황</h1>
        <p>총 {{ equipmentCount }}대 중 {{ activeEquipments.length }}대 운영 중</p>
      </v-col>
    </v-row>

    <v-row>
      <v-col v-for="equipment in activeEquipments" :key="equipment.id" cols="12" md="4">
        <v-card @click="selectEquipment(equipment.id)">
          <v-card-title>{{ equipment.name }}</v-card-title>
          <v-card-text>
            <p>상태: {{ equipment.status }}</p>
            <p>마지막 측정: {{ equipment.lastMeasurement }}</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-progress-linear v-if="loading" indeterminate></v-progress-linear>
  </v-container>
</template>

<script setup>
import { onMounted } from 'vue'
import { useEquipmentStore } from '@/stores/equipment'
import { storeToRefs } from 'pinia'

// Store 사용
const equipmentStore = useEquipmentStore()

// 반응형 상태 추출 (storeToRefs 사용)
const { activeEquipments, loading, equipmentCount } = storeToRefs(equipmentStore)

// Actions는 직접 구조 분해
const { fetchEquipments, selectEquipment } = equipmentStore

// 컴포넌트 마운트 시 데이터 로드
onMounted(() => {
  fetchEquipments()
})
</script>
```

### 장비 추가 폼 컴포넌트

```javascript
<template>
  <v-dialog v-model="dialog" max-width="600">
    <v-card>
      <v-card-title>새 장비 추가</v-card-title>
      <v-card-text>
        <v-form @submit.prevent="handleSubmit">
          <v-text-field
            v-model="formData.name"
            label="장비명"
            required
          ></v-text-field>

          <v-select
            v-model="formData.type"
            :items="equipmentTypes"
            label="장비 타입"
          ></v-select>

          <v-select
            v-model="formData.status"
            :items="['active', 'maintenance', 'inactive']"
            label="상태"
          ></v-select>
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn @click="dialog = false">취소</v-btn>
        <v-btn color="primary" @click="handleSubmit">추가</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useEquipmentStore } from '@/stores/equipment'

const equipmentStore = useEquipmentStore()
const dialog = ref(false)

const formData = reactive({
  name: '',
  type: '',
  status: 'active'
})

const equipmentTypes = ['AFM', 'SEM', 'TEM', 'XRD']

function handleSubmit() {
  // Store의 action 호출
  equipmentStore.addEquipment(formData)

  // 폼 초기화
  Object.assign(formData, {
    name: '',
    type: '',
    status: 'active'
  })

  dialog.value = false
}
</script>
```

### 여러 Store 함께 사용하기

```javascript
<script setup>
import { useEquipmentStore } from '@/stores/equipment'
import { useUserStore } from '@/stores/user'
import { useMeasurementStore } from '@/stores/measurement'

const equipmentStore = useEquipmentStore()
const userStore = useUserStore()
const measurementStore = useMeasurementStore()

// 각 Store의 상태와 액션 사용
const { currentUser } = storeToRefs(userStore)
const { selectedEquipment } = storeToRefs(equipmentStore)

async function loadMeasurements() {
  if (selectedEquipment.value && currentUser.value) {
    await measurementStore.fetchMeasurements({
      equipmentId: selectedEquipment.value.id,
      userId: currentUser.value.id
    })
  }
}
</script>
```

이러한 방식으로 Pinia를 사용하면 애플리케이션의 상태를 체계적으로 관리할 수 있으며, 컴포넌트 간 데이터 공유가 매우 간단해집니다. 특히 Composition API 스타일로 작성하면 더 직관적이고 유지보수가 용이한 코드를 작성할 수 있습니다.

## Vue의 컴포넌트 통신 방법과 Pinia의 역할

### Vue의 기본 컴포넌트 통신

Vue에서 컴포넌트 간 데이터 전달은 계층 구조에 따라 다릅니다.

**Props - 부모에서 자식으로**

```javascript
<!-- 부모 컴포넌트 -->
<template>
  <EquipmentCard
    :equipment="equipmentData"
    :status="activeStatus"
    @update="handleUpdate"
  />
</template>

<!-- 자식 컴포넌트 (EquipmentCard.vue) -->
<template>
  <div>
    <h3>{{ equipment.name }}</h3>
    <p>상태: {{ status }}</p>
  </div>
</template>

<script setup>
defineProps({
  equipment: Object,
  status: String
})
</script>
```

**Emit - 자식에서 부모로**

```javascript
<!-- 자식 컴포넌트 -->
<script setup>
const emit = defineEmits(['update', 'delete'])

function updateEquipment() {
  emit('update', { id: 1, name: '새 이름' })
}
</script>
```

### Props Drilling 문제

여러 단계를 거쳐 데이터를 전달해야 할 때 발생하는 문제입니다.

```javascript
<!-- App.vue → Dashboard.vue → EquipmentList.vue → EquipmentCard.vue -->
<!-- 4단계를 거쳐 userData를 전달해야 함 -->
```

### Provide/Inject - 깊은 계층 구조 해결

```javascript
<!-- 최상위 컴포넌트 -->
<script setup>
import { provide, ref } from 'vue'

const userData = ref({ name: '홍길동', role: 'engineer' })
provide('user', userData)
</script>

<!-- 깊은 하위 컴포넌트 -->
<script setup>
import { inject } from 'vue'

const user = inject('user')
// 중간 컴포넌트를 거치지 않고 직접 접근
</script>
```

### Pinia가 해결하는 문제

**1. 형제 컴포넌트 간 통신**

```javascript
<!-- Header.vue -->
<script setup>
import { useUserStore } from '@/stores/user'
const userStore = useUserStore()
</script>

<!-- Sidebar.vue -->
<script setup>
import { useUserStore } from '@/stores/user'
const userStore = useUserStore()
// 동일한 상태 공유
</script>
```

**2. 전역 상태 관리**

```javascript
// stores/notification.js
export const useNotificationStore = defineStore("notification", () => {
  const notifications = ref([]);

  function addNotification(message) {
    notifications.value.push({
      id: Date.now(),
      message,
      timestamp: new Date(),
    });
  }

  return { notifications, addNotification };
});
```

모든 컴포넌트에서 알림 상태에 접근 가능합니다.

### 언제 무엇을 사용해야 하나

**Props/Emit 사용**

- 부모-자식 관계가 명확한 경우
- 컴포넌트가 재사용 가능해야 하는 경우
- 데이터 흐름이 단순한 경우

**Provide/Inject 사용**

- 깊은 계층 구조에서 특정 데이터 공유
- 플러그인이나 라이브러리 설정 주입
- 컴포넌트 트리의 일부분에만 필요한 데이터

**Pinia 사용**

- 여러 컴포넌트에서 공유하는 상태
- 페이지 이동 후에도 유지되어야 하는 데이터
- 복잡한 상태 로직이 필요한 경우
- 형제 컴포넌트 간 통신

### 실제 예시: AFM 대시보드

```javascript
<!-- Props만 사용 (비효율적) -->
<template>
  <Dashboard :equipments="equipments" @update="updateEquipment">
    <EquipmentList :equipments="equipments" @update="$emit('update', $event)">
      <EquipmentCard
        v-for="eq in equipments"
        :equipment="eq"
        @update="$emit('update', $event)"
      />
    </EquipmentList>
  </Dashboard>
</template>

<!-- Pinia 사용 (효율적) -->
<template>
  <Dashboard /> <!-- 각 컴포넌트가 독립적으로 Store 접근 -->
</template>
```

## Pinia가 Props/Emit을 완전히 대체할 수 없는 이유

Pinia와 Props/Emit은 서로 다른 목적과 사용 사례를 가지고 있어 완전히 대체할 수 없습니다.

### Props/Emit의 고유한 역할

**컴포넌트 재사용성**

```javascript
<!-- 재사용 가능한 컴포넌트 -->
<EquipmentCard
  :title="장비1"
  :status="active"
  @click="handleClick"
/>

<!-- 다른 프로젝트에서도 사용 가능 -->
<EquipmentCard
  :title="다른장비"
  :status="inactive"
  @click="differentHandler"
/>
```

Pinia를 사용하면 특정 스토어에 종속되어 재사용이 어려워집니다.

**명확한 인터페이스**

```javascript
<script setup>
// Props로 컴포넌트가 필요한 데이터가 명확함
defineProps({
  equipment: {
    type: Object,
    required: true
  },
  showDetails: {
    type: Boolean,
    default: false
  }
})
</script>
```

Props는 컴포넌트의 "계약"처럼 작동하여 어떤 데이터가 필요한지 명시합니다.

**단방향 데이터 흐름**

```javascript
<!-- 부모 → 자식 -->
<ChildComponent :data="parentData" />

<!-- 자식 → 부모 -->
<ChildComponent @update="parentData = $event" />
```

데이터 흐름이 예측 가능하고 디버깅이 쉽습니다.

### Pinia의 한계

**과도한 전역 상태**

```javascript
// 모든 것을 Store에 넣으면 안 됨
const useFormStore = defineStore("form", () => {
  const tempInput = ref(""); // ❌ 임시 입력값
  const isModalOpen = ref(false); // ❌ 로컬 UI 상태
});
```

**컴포넌트 간 결합도 증가**

```javascript
<!-- Button.vue - 재사용 불가 -->
<script setup>
import { useAppStore } from '@/stores/app' // 특정 스토어에 종속
const store = useAppStore()
</script>
```

### 올바른 사용 구분

**Props/Emit 사용**

- UI 컴포넌트 (버튼, 카드, 모달)
- 폼 입력 컴포넌트
- 부모-자식 간 직접 통신
- 임시 상태나 로컬 UI 상태

**Pinia 사용**

- 사용자 인증 정보
- 전역 설정
- 여러 페이지가 공유하는 데이터
- 서버에서 가져온 데이터 캐싱

이처럼 각 방법은 고유한 장점이 있어 상황에 맞게 선택해야 합니다.

## 정리

**Props/Emit**: 부모-자식 간 데이터 전달 및 이벤트 처리에 사용됩니다. 단방향 데이터 흐름을 유지하며, 간단한 컴포넌트 통신에 적합합니다. 단점은 깊은 컴포넌트 트리에서 Props Drilling 문제가 발생할 수 있습니다.

**Pinia**: 전역 상태 관리 라이브러리로, 여러 컴포넌트가 공유하는 상태를 중앙에서 관리합니다. 복잡한 앱 구조나 상태 로직에 유용합니다.

**차이점**: Props/Emit은 로컬 통신, Pinia는 전역 상태 관리에 초점을 맞춥니다.

**함께 사용 가능**: Props는 컴포넌트별 로컬 데이터 전달, Pinia는 전역 상태 관리에 사용되며, 역할이 달라 조합 가능합니다.

**사용 전략**: Pinia로 전역 상태를 관리하고, Props로 특정 데이터를 전달하며, Emit으로 이벤트를 처리합니다.

**결론**: Pinia로 공유 상태를 관리하고, Props/Emit으로 컴포넌트 간 명확한 통신을 유지하는 것이 효과적입니다.

## 참고 자료

- [Pinia 공식 문서](https://pinia.vuejs.org/)
- [Vue 3 Composition API 가이드](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Pinia 한국어 문서](https://pinia.vuejs.kr/)
