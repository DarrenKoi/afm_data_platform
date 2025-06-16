<template>
  <v-container fluid class="pa-4">
    <!-- Compact Header -->
    <div class="d-flex align-center mb-3">
      <v-btn
        variant="outlined" 
        size="small"
        @click="goBack"
        class="mr-3"
      >
        <v-icon start size="small">mdi-arrow-left</v-icon>
        Back
      </v-btn>
      
      <div>
        <h1 class="text-h5 mb-0">AFM Measurement Details</h1>
        <p class="text-caption text-medium-emphasis">{{ groupKey }}</p>
      </div>
    </div>

    <!-- Compact Information Row -->
    <v-row dense class="mb-3">
      <v-col cols="12" md="6">
        <MeasurementInfo :measurement-info="measurementInfo" :compact="true" />
      </v-col>
      <v-col cols="12" md="6">
        <StatisticalInfo :profile-data="profileData" :compact="true" />
      </v-col>
    </v-row>

    <!-- Compact Summary Data -->
    <SummaryDataTable :summary-data="summaryData" :compact="true" class="mb-3" />

    <!-- Compact Measurement Points Selection -->
    <MeasurementPointsSelector 
      :measurement-points="measurementPoints"
      :selected-point="selectedPoint"
      :compact="true"
      @point-selected="selectPoint"
      class="mb-3"
    />

    <!-- Professional Two-Column Layout -->
    <v-row dense class="main-content-row">
      <!-- Column 1: Heat Map and Controls -->
      <v-col cols="12" lg="7" xl="6">
        <v-card class="heat-map-card" :height="chartHeight">
          <v-card-title class="py-2">
            <v-icon start size="small">mdi-grid</v-icon>
            <span class="text-subtitle-1">Wafer Heat Map</span>
          </v-card-title>
          <v-card-text class="pa-2">
            <EnhancedChartVisualization 
              :group-key="groupKey" 
              :chart-height="chartHeight - 80"
              @point-selected="handleWaferPointSelected"
            />
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Column 2: Profile Data and Z-Distribution -->
      <v-col cols="12" lg="5" xl="6">
        <v-row dense>
          <!-- Profile Data Chart -->
          <v-col cols="12">
            <v-card class="profile-card mb-2" :height="(chartHeight / 2) - 6">
              <v-card-title class="py-2">
                <v-icon start size="small">mdi-chart-scatter-plot</v-icon>
                <span class="text-subtitle-1">Profile Data</span>
                <v-spacer />
                <v-chip v-if="selectedPoint" size="x-small" color="primary" variant="outlined">
                  Point {{ selectedPoint }}
                </v-chip>
              </v-card-title>
              <v-card-text class="pa-2">
                <ChartVisualization 
                  :selected-point="selectedPoint"
                  :profile-data="profileData"
                  :is-loading="isLoadingProfile"
                  :chart-height="(chartHeight / 2) - 90"
                  :compact="true"
                  :chart-type="'scatter'"
                  @chart-type-changed="handleChartTypeChanged"
                />
              </v-card-text>
            </v-card>
          </v-col>

          <!-- Z-Value Distribution -->
          <v-col cols="12">
            <v-card class="distribution-card" :height="(chartHeight / 2) - 6">
              <v-card-title class="py-2">
                <v-icon start size="small">mdi-chart-bar</v-icon>
                <span class="text-subtitle-1">Z-Value Distribution</span>
                <v-spacer />
                <v-chip v-if="profileData.length > 0" size="x-small" color="success" variant="outlined">
                  {{ profileData.length.toLocaleString() }} points
                </v-chip>
              </v-card-title>
              <v-card-text class="pa-2">
                <ChartVisualization 
                  :selected-point="selectedPoint"
                  :profile-data="profileData"
                  :is-loading="isLoadingProfile"
                  :chart-height="(chartHeight / 2) - 90"
                  :compact="true"
                  :chart-type="'histogram'"
                  @chart-type-changed="handleChartTypeChanged"
                />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { identifierData, fetchProfileData, fetchSummaryData } from '@/services/api.js'

// Import components
import MeasurementInfo from '@/components/ResultPage/MeasurementInfo.vue'
import SummaryDataTable from '@/components/ResultPage/SummaryDataTable.vue'
import MeasurementPointsSelector from '@/components/ResultPage/MeasurementPointsSelector.vue'
import ChartVisualization from '@/components/ResultPage/ChartVisualization.vue'
import StatisticalInfo from '@/components/ResultPage/StatisticalInfo.vue'
import EnhancedChartVisualization from '@/components/ResultPage/EnhancedChartVisualization.vue'

const route = useRoute()
const router = useRouter()

// Reactive data
const groupKey = ref(route.params.groupKey)
const measurementInfo = ref({})
const measurementPoints = ref([])
const summaryData = ref([])
const selectedPoint = ref(null)
const profileData = ref([])
const isLoadingProfile = ref(false)


// Calculate optimal chart height based on viewport
const chartHeight = computed(() => {
  // Use 70% of viewport height, minimum 600px for professional layout
  const viewportHeight = window.innerHeight || 800
  const headerHeight = 200 // approximate header + compact info height
  const availableHeight = viewportHeight - headerHeight
  return Math.max(Math.floor(availableHeight * 0.8), 600)
})

// Functions
async function selectPoint(pointNumber) {
  selectedPoint.value = pointNumber
  isLoadingProfile.value = true
  
  try {
    const response = await fetchProfileData(groupKey.value, pointNumber)
    console.log('Profile data response:', response)
    // fetchProfileData returns the data directly, not an object with success/data
    profileData.value = response || []
    await nextTick()
  } catch (error) {
    console.error('Error fetching profile data:', error)
    profileData.value = []
  } finally {
    isLoadingProfile.value = false
  }
}

function handleChartTypeChanged(type) {
  console.log('Chart type changed to:', type)
}

function handleWaferPointSelected(point) {
  // When a point is selected from the wafer heat map, update the profile data
  console.log('handleWaferPointSelected called with:', point)
  
  if (point && point.point) {
    console.log('Selecting point:', point.point)
    selectPoint(point.point)
  } else if (point) {
    // Fallback: try to find a matching measurement point or use first point
    console.log('Point structure unexpected, trying fallback...') 
    console.log('Available measurement points:', measurementPoints.value)
    
    if (measurementPoints.value.length > 0) {
      // For now, let's just select the first point as a test
      const firstPoint = measurementPoints.value[0]
      console.log('Selecting first available point:', firstPoint.point)
      selectPoint(firstPoint.point)
    }
  }
}


async function loadData() {
  // Find measurement points for this group
  const points = identifierData.filter(item => item.group_key === groupKey.value)
  measurementPoints.value = points
  
  if (points.length > 0) {
    // Set measurement info from first point
    measurementInfo.value = points[0]
    
    // Load summary data
    try {
      const summaryResponse = await fetchSummaryData(groupKey.value)
      if (summaryResponse.success) {
        summaryData.value = summaryResponse.data
      }
    } catch (error) {
      console.error('Error loading summary data:', error)
    }
    
    // Auto-select first point
    if (points.length > 0) {
      selectPoint(points[0].point)
    }
  } else {
    // Fallback: parse group key
    const parts = groupKey.value.split('_')
    if (parts.length >= 3) {
      measurementInfo.value = {
        fab: parts[0],
        lot_id: parts[1],
        wf_id: parts[2],
        group_key: groupKey.value,
        rcp_id: "BSOXCMP_DISHING_9PT",
        event_time: new Date().toISOString()
      }
    }
  }
}

function goBack() {
  router.push('/')
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped>
/* Professional compact layout */
.main-content-row {
  height: calc(100vh - 280px);
  min-height: 600px;
}

.heat-map-card,
.profile-card,
.distribution-card {
  border: 1px solid rgba(var(--v-theme-outline), 0.12);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.heat-map-card .v-card-title,
.profile-card .v-card-title,
.distribution-card .v-card-title {
  border-bottom: 1px solid rgba(var(--v-theme-outline), 0.12);
  font-size: 0.875rem;
  font-weight: 600;
  padding: 8px 12px;
}

.heat-map-card .v-card-text,
.profile-card .v-card-text,
.distribution-card .v-card-text {
  padding: 8px;
  height: calc(100% - 44px);
  overflow: hidden;
}

/* Responsive adjustments for professional layout */
@media (max-width: 1280px) {
  .main-content-row {
    height: auto;
  }
  
  .heat-map-card {
    margin-bottom: 16px;
  }
}

/* Ensure no scrolling on desktop */
@media (min-width: 1280px) {
  .v-container {
    height: 100vh;
    overflow: hidden;
  }
  
  .main-content-row {
    flex: 1;
    overflow: hidden;
  }
}

/* Compact spacing overrides */
.v-row.dense .v-col {
  padding: 6px;
}

.v-chip.v-chip--size-x-small {
  font-size: 0.625rem;
  height: 20px;
}

.text-subtitle-1 {
  font-size: 0.875rem !important;
  line-height: 1.2;
}

.text-caption {
  font-size: 0.75rem !important;
  line-height: 1.2;
}
</style>