# API 통신 - Axios 라이브러리 사용하기

## REST API 기초

### REST API란 무엇인가?

REST(Representational State Transfer) API는 웹 서비스 간 데이터를 주고받는 표준화된 방법입니다. 레스토랑에서 주문하는 과정을 생각해보면 이해하기 쉽습니다. 고객(프론트엔드)이 웨이터(API)에게 주문(요청)을 하면, 주방(백엔드)에서 요리(데이터)를 만들어 다시 고객에게 전달하는 것과 같은 원리입니다.

### HTTP 메서드 이해하기

REST API는 HTTP 프로토콜의 메서드를 사용하여 다양한 작업을 수행합니다:

| 메서드 | 용도             | 예시                          |
| ------ | ---------------- | ----------------------------- |
| GET    | 데이터 조회      | AFM 측정 데이터 목록 가져오기 |
| POST   | 새 데이터 생성   | 새로운 측정 결과 저장하기     |
| PUT    | 전체 데이터 수정 | 장비 정보 전체 업데이트       |
| PATCH  | 일부 데이터 수정 | 장비 상태만 변경하기          |
| DELETE | 데이터 삭제      | 오래된 측정 데이터 삭제       |

### API 엔드포인트 구조 예시

```
https://api주소.skhynix.com/afm/v1/equipments/AFM-001/measurements
```

이 URL을 분해해보면:

- `https://api주소.skhynix.com` - API 서버 주소
- `/afm/v1` - API 버전
- `/equipments` - 리소스 타입 (장비)
- `/AFM-001` - 특정 장비 ID
- `/measurements` - 하위 리소스 (측정 데이터)

### 상태 코드 이해하기

서버는 요청 처리 결과를 상태 코드로 알려줍니다:

**200번대: 성공**

- `200 OK` - 요청 성공
- `201 Created` - 생성 성공
- `204 No Content` - 삭제 성공

**400번대: 클라이언트 오류**

- `400 Bad Request` - 잘못된 요청
- `401 Unauthorized` - 인증 필요
- `404 Not Found` - 리소스 없음

**500번대: 서버 오류**

- `500 Internal Server Error` - 서버 내부 오류
- `503 Service Unavailable` - 서비스 이용 불가

## Axios 라이브러리 소개

### Axios란?

Axios는 브라우저와 Node.js에서 사용할 수 있는 Promise 기반 HTTP 클라이언트입니다. Vue.js 커뮤니티에서 가장 널리 사용되는 HTTP 라이브러리로, 간단하고 직관적인 API를 제공합니다.

### Axios의 주요 특징

- **Promise 기반**: async/await 문법과 완벽하게 호환됩니다.
- **요청/응답 인터셉터**: 모든 요청과 응답을 가로채어 전처리할 수 있습니다.
- **자동 JSON 변환**: JSON 데이터를 자동으로 파싱하고 문자열로 변환합니다.
- **에러 처리**: HTTP 에러를 자동으로 감지하고 처리합니다.
- **요청 취소**: 진행 중인 요청을 취소할 수 있습니다.
- **XSRF 보호**: 크로스 사이트 요청 위조 공격을 방지합니다.

### Axios 설치하기

```bash
# npm을 사용한 설치
npm install axios
```

### 기본 설정

```javascript
// src/api/index.js
import axios from "axios";

// Axios 기본 인스턴스 생성
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:5000/api",
  timeout: 10000, // 10초 타임아웃
  headers: {
    "Content-Type": "application/json",
  },
});

export default apiClient;
```

## HTTP 요청 보내기

### GET 요청 - 데이터 조회

```javascript
// src/api/equipment.js
import apiClient from "./index";

// 모든 장비 목록 조회
export const getEquipments = async () => {
  try {
    const response = await apiClient.get("/equipments");
    return response.data;
  } catch (error) {
    console.error("장비 목록 조회 실패:", error);
    throw error;
  }
};

// 특정 장비 상세 정보 조회
export const getEquipmentById = async (id) => {
  try {
    const response = await apiClient.get(`/equipments/${id}`);
    return response.data;
  } catch (error) {
    console.error(`장비 ${id} 조회 실패:`, error);
    throw error;
  }
};

// 쿼리 파라미터를 사용한 필터링
export const getEquipmentsByStatus = async (status) => {
  try {
    const response = await apiClient.get("/equipments", {
      params: {
        status: status,
        sort: "name",
        limit: 50,
      },
    });
    return response.data;
  } catch (error) {
    console.error("장비 상태별 조회 실패:", error);
    throw error;
  }
};
```

### POST 요청 - 데이터 생성

```javascript
// 새 측정 데이터 생성
export const createMeasurement = async (equipmentId, measurementData) => {
  try {
    const response = await apiClient.post(
      `/equipments/${equipmentId}/measurements`,
      measurementData
    );
    return response.data;
  } catch (error) {
    console.error("측정 데이터 생성 실패:", error);
    throw error;
  }
};

// 파일 업로드 예제
export const uploadMeasurementFile = async (equipmentId, file) => {
  try {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("equipmentId", equipmentId);

    const response = await apiClient.post("/measurements/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  } catch (error) {
    console.error("파일 업로드 실패:", error);
    throw error;
  }
};
```

### PUT/PATCH 요청 - 데이터 수정

```javascript
// 장비 정보 전체 수정 (PUT)
export const updateEquipment = async (id, equipmentData) => {
  try {
    const response = await apiClient.put(`/equipments/${id}`, equipmentData);
    return response.data;
  } catch (error) {
    console.error(`장비 ${id} 수정 실패:`, error);
    throw error;
  }
};

// 장비 상태만 수정 (PATCH)
export const updateEquipmentStatus = async (id, status) => {
  try {
    const response = await apiClient.patch(`/equipments/${id}`, {
      status: status,
    });
    return response.data;
  } catch (error) {
    console.error(`장비 ${id} 상태 변경 실패:`, error);
    throw error;
  }
};
```

### DELETE 요청 - 데이터 삭제

```javascript
// 측정 데이터 삭제
export const deleteMeasurement = async (measurementId) => {
  try {
    const response = await apiClient.delete(`/measurements/${measurementId}`);
    return response.data;
  } catch (error) {
    console.error(`측정 데이터 ${measurementId} 삭제 실패:`, error);
    throw error;
  }
};
```

## 에러 처리

### 전역 에러 처리

```javascript
// src/api/errorHandler.js
export const handleApiError = (error) => {
  if (error.response) {
    // 서버가 응답을 반환한 경우
    switch (error.response.status) {
      case 400:
        return "잘못된 요청입니다. 입력값을 확인해주세요.";
      case 401:
        return "인증이 필요합니다. 다시 로그인해주세요.";
      case 403:
        return "접근 권한이 없습니다.";
      case 404:
        return "요청한 리소스를 찾을 수 없습니다.";
      case 500:
        return "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.";
      default:
        return `오류가 발생했습니다: ${error.response.statusText}`;
    }
  } else if (error.request) {
    // 요청은 보냈지만 응답을 받지 못한 경우
    return "서버에 연결할 수 없습니다. 네트워크를 확인해주세요.";
  } else {
    // 요청 설정 중 오류가 발생한 경우
    return "요청 처리 중 오류가 발생했습니다.";
  }
};
```

### 컴포넌트에서 에러 처리

```javascript
<template>
  <v-container>
    <!-- 로딩 상태 표시 -->
    <v-progress-linear v-if="loading" indeterminate></v-progress-linear>

    <!-- 에러 메시지 표시 -->
    <v-alert v-if="error" type="error" dismissible @click:close="error = null">
      {{ error }}
    </v-alert>

    <!-- 데이터 표시 -->
    <v-row v-if="!loading && !error">
      <v-col v-for="equipment in equipments" :key="equipment.id" cols="12" md="4">
        <equipment-card :equipment="equipment" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getEquipments } from '@/api/equipment'
import { handleApiError } from '@/api/errorHandler'
import EquipmentCard from '@/components/EquipmentCard.vue'

const equipments = ref([])
const loading = ref(false)
const error = ref(null)

const fetchEquipments = async () => {
  loading.value = true
  error.value = null

  try {
    equipments.value = await getEquipments()
  } catch (err) {
    error.value = handleApiError(err)
    console.error('장비 목록 로드 실패:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchEquipments()
})
</script>
```

## 인터셉터 활용하기

### 인터셉터란?

인터셉터는 HTTP 요청이나 응답을 가로채서 처리하는 미들웨어입니다. 모든 API 호출에 공통으로 적용되는 로직을 중앙에서 관리할 수 있게 해줍니다.

### 요청 인터셉터 - 인증 토큰 추가

```javascript
// src/api/interceptors.js
import { useUserStore } from "@/stores/user";

// 요청 인터셉터 설정
apiClient.interceptors.request.use(
  (config) => {
    const userStore = useUserStore();
    const token = userStore.token;

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
```

### 응답 인터셉터 - 에러 처리

```javascript
// 응답 인터셉터 설정
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // 토큰 만료 시 로그인 페이지로 리디렉션
      const userStore = useUserStore();
      userStore.logout();
      router.push("/login");
    }

    return Promise.reject(error);
  }
);
```

## 실제 AFM 프로젝트 API 서비스 예제

### 장비 관리 API

```javascript
// src/api/services/equipment.js
import apiClient from "../index";

export const equipmentAPI = {
  // 모든 장비 조회
  async getAll() {
    const response = await apiClient.get("/equipments");
    return response.data;
  },

  // 장비 상세 조회
  async getById(id) {
    const response = await apiClient.get(`/equipments/${id}`);
    return response.data;
  },

  // 새 장비 등록
  async create(equipment) {
    const response = await apiClient.post("/equipments", equipment);
    return response.data;
  },

  // 장비 정보 수정
  async update(id, equipment) {
    const response = await apiClient.put(`/equipments/${id}`, equipment);
    return response.data;
  },

  // 장비 삭제
  async delete(id) {
    const response = await apiClient.delete(`/equipments/${id}`);
    return response.data;
  },

  // 장비 상태 변경
  async updateStatus(id, status) {
    const response = await apiClient.patch(`/equipments/${id}/status`, {
      status,
    });
    return response.data;
  },
};
```

### 측정 데이터 API

```javascript
// src/api/services/measurement.js
import apiClient from "../index";

export const measurementAPI = {
  // 측정 데이터 목록 조회
  async getByEquipment(equipmentId, params = {}) {
    const response = await apiClient.get(
      `/equipments/${equipmentId}/measurements`,
      {
        params: {
          page: params.page || 1,
          limit: params.limit || 20,
          startDate: params.startDate,
          endDate: params.endDate,
        },
      }
    );
    return response.data;
  },

  // 새 측정 데이터 생성
  async create(equipmentId, data) {
    const response = await apiClient.post(
      `/equipments/${equipmentId}/measurements`,
      data
    );
    return response.data;
  },

  // 측정 데이터 다운로드
  async download(measurementId) {
    const response = await apiClient.get(
      `/measurements/${measurementId}/download`,
      {
        responseType: "blob",
      }
    );
    return response.data;
  },

  // 측정 데이터 분석 요청
  async analyze(measurementId, analysisType) {
    const response = await apiClient.post(
      `/measurements/${measurementId}/analyze`,
      {
        type: analysisType,
      }
    );
    return response.data;
  },
};
```

### 컴포넌트에서 API 사용

```javascript
<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h2>AFM 장비 관리</h2>
        <v-btn @click="refreshData" :loading="loading" color="primary">
          새로고침
        </v-btn>
      </v-col>
    </v-row>

    <v-row>
      <v-col v-for="equipment in equipments" :key="equipment.id" cols="12" md="4">
        <v-card>
          <v-card-title>{{ equipment.name }}</v-card-title>
          <v-card-text>
            <p>상태: {{ equipment.status }}</p>
            <p>위치: {{ equipment.location }}</p>
          </v-card-text>
          <v-card-actions>
            <v-btn @click="viewDetails(equipment.id)" text>상세보기</v-btn>
            <v-btn @click="toggleStatus(equipment)" text>
              {{ equipment.status === 'active' ? '비활성화' : '활성화' }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { equipmentAPI } from '@/api/services/equipment'
import { useNotificationStore } from '@/stores/notification'

const equipments = ref([])
const loading = ref(false)
const notificationStore = useNotificationStore()

const refreshData = async () => {
  loading.value = true
  try {
    equipments.value = await equipmentAPI.getAll()
  } catch (error) {
    notificationStore.showError('장비 목록을 불러오는데 실패했습니다.')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const viewDetails = (equipmentId) => {
  router.push(`/equipments/${equipmentId}`)
}

const toggleStatus = async (equipment) => {
  try {
    const newStatus = equipment.status === 'active' ? 'inactive' : 'active'
    await equipmentAPI.updateStatus(equipment.id, newStatus)

    // 로컬 상태 업데이트
    equipment.status = newStatus

    notificationStore.showSuccess('장비 상태가 변경되었습니다.')
  } catch (error) {
    notificationStore.showError('상태 변경에 실패했습니다.')
    console.error(error)
  }
}

onMounted(() => {
  refreshData()
})
</script>
```

## 고급 기능

### 요청 취소하기

```javascript
// 요청 취소를 위한 AbortController 사용
export const getCancelableEquipments = () => {
  const controller = new AbortController();

  const request = apiClient.get("/equipments", {
    signal: controller.signal,
  });

  // 취소 함수와 함께 반환
  return {
    request,
    cancel: () => controller.abort(),
  };
};

// 컴포넌트에서 사용
const { request, cancel } = getCancelableEquipments();

// 컴포넌트 언마운트 시 요청 취소
onBeforeUnmount(() => {
  cancel();
});
```

## 정리

### API 통신의 핵심 포인트

1. **일관된 에러 처리**: 전역 에러 핸들러와 인터셉터를 활용
2. **로딩 상태 관리**: 사용자 경험 향상을 위한 로딩 표시
3. **타입 안전성**: TypeScript 사용 시 API 응답 타입 정의
4. **재사용성**: 공통 API 로직을 서비스 모듈로 분리
5. **성능 최적화**: 요청 취소, 캐싱, 재시도 로직 구현

### 베스트 프랙티스

- **환경별 설정**: 개발/운영 환경에 맞는 API URL 설정
- **보안**: 인증 토큰 자동 관리 및 HTTPS 사용
- **모니터링**: API 호출 로깅 및 성능 측정
- **사용자 피드백**: 명확한 에러 메시지와 로딩 상태 표시

이러한 방법들을 활용하면 안정적이고 사용자 친화적인 AFM 데이터 플랫폼을 구축할 수 있습니다.

## Axios 대안: Ky 라이브러리

### Ky란?

Ky는 브라우저용 HTTP 클라이언트 라이브러리로, fetch API를 기반으로 구축된 현대적이고 가벼운 대안입니다. Axios보다 작은 번들 크기를 가지며, 더 현대적인 JavaScript 문법을 지원합니다.

### Ky의 주요 특징

- **작은 번들 크기**: Axios보다 약 60% 작은 크기
- **TypeScript 내장 지원**: 별도 설치 없이 완전한 타입 지원
- **현대적 문법**: Promise와 async/await를 기본으로 설계
- **fetch 기반**: 브라우저 네이티브 fetch API 사용
- **자동 재시도**: 설정 가능한 재시도 로직 내장
- **JSON 자동 처리**: JSON 요청/응답 자동 변환

### Ky 설치 및 기본 사용법

```bash
# npm을 사용한 설치
npm install ky
```

```javascript
// src/api/kyClient.js
import ky from "ky";

// Ky 인스턴스 생성
const apiClient = ky.create({
  prefixUrl: import.meta.env.VITE_API_URL || "http://localhost:5000/api",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
  retry: {
    limit: 3,
    methods: ["get", "put", "head", "delete", "options", "trace"],
  },
});

export default apiClient;
```

### Ky vs Axios 비교

| 특징          | Axios             | Ky            |
| ------------- | ----------------- | ------------- |
| 번들 크기     | ~45KB             | ~18KB         |
| TypeScript    | @types/axios 필요 | 내장 지원     |
| 브라우저 지원 | IE11+             | 최신 브라우저 |
| API 스타일    | 전통적            | 현대적        |
| 자동 재시도   | 추가 설정 필요    | 내장 지원     |

### Ky 사용 예제

```javascript
// src/api/services/equipmentKy.js
import apiClient from "../kyClient";

export const equipmentAPI = {
  // GET 요청
  async getAll() {
    return await apiClient.get("equipments").json();
  },

  // POST 요청
  async create(equipment) {
    return await apiClient.post("equipments", { json: equipment }).json();
  },

  // PUT 요청
  async update(id, equipment) {
    return await apiClient.put(`equipments/${id}`, { json: equipment }).json();
  },

  // DELETE 요청
  async delete(id) {
    await apiClient.delete(`equipments/${id}`);
  },

  // 파일 업로드
  async uploadFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    return await apiClient.post("upload", { body: formData }).json();
  },
};
```

### 언제 Ky를 사용할까?

**Ky를 선택하는 경우:**

- 번들 크기가 중요한 프로젝트
- TypeScript 프로젝트
- 최신 브라우저만 지원하는 프로젝트
- 현대적이고 간결한 API를 선호하는 경우

**Axios를 선택하는 경우:**

- 구형 브라우저 지원이 필요한 경우
- 기존 Axios 코드베이스가 있는 경우
- 더 많은 커뮤니티 지원과 자료가 필요한 경우
- 복잡한 인터셉터 로직이 필요한 경우

현재 AFM 프로젝트에서는 Axios를 사용하고 있지만, 번들 크기 최적화가 필요하거나 새로운 프로젝트를 시작할 때는 Ky를 고려해볼 수 있습니다.
