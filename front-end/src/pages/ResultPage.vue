<template>
  <v-container fluid class="pa-4">
    <!-- Distinctive Back Button -->
    <div class="mb-4">
      <v-btn
        color="primary"
        variant="elevated"
        size="large"
        @click="goBack"
        class="back-button"
      >
        <v-icon start>mdi-arrow-left</v-icon>
        Back to Search
      </v-btn>
    </div>

    <!-- Measurement Information at Top -->
    <div class="mb-4">
      <MeasurementInfo :measurement-info="measurementInfo" :compact="false" />
    </div>

    <!-- Statistical Information by UL Points -->
    <div class="mb-4">
      <StatisticalInfoByPoints :statistics-data="statisticsData" />
    </div>

    <!-- Measurement Points Selection -->
    <div class="mb-4">
      <MeasurementPointsSelector 
        :measurement-points="measurementPoints"
        :selected-point="selectedPoint"
        :compact="false"
        @point-selected="selectPoint"
      />
    </div>

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
import { identifierData, fetchProfileData, fetchSummaryData, fetchMeasurementData } from '@/services/api.js'

// Import components
import MeasurementInfo from '@/components/ResultPage/MeasurementInfo.vue'
import SummaryDataTable from '@/components/ResultPage/SummaryDataTable.vue'
import MeasurementPointsSelector from '@/components/ResultPage/MeasurementPointsSelector.vue'
import ChartVisualization from '@/components/ResultPage/ChartVisualization.vue'
import StatisticalInfo from '@/components/ResultPage/StatisticalInfo.vue'
import StatisticalInfoByPoints from '@/components/ResultPage/StatisticalInfoByPoints.vue'
import EnhancedChartVisualization from '@/components/ResultPage/EnhancedChartVisualization.vue'

const route = useRoute()
const router = useRouter()

// Reactive data
const groupKey = ref(route.params.groupKey)
const recipeId = ref(route.params.recipeId)
const measurementInfo = ref({})
const statisticsData = ref({})
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
  console.log(`🚀 Loading data for recipe: ${recipeId.value}, group_key: ${groupKey.value}`)
  
  try {
    // Load real measurement data from pickle file
    const measurementResponse = await fetchMeasurementData(groupKey.value)
    
    if (measurementResponse.success && measurementResponse.data) {
      const data = measurementResponse.data
      
      // Set measurement info from pickle data
      measurementInfo.value = {
        fab: 'SK_Hynix_ITC',
        lot_id: data.measurement_info['Lot ID'] || 'Unknown',
        wf_id: 'W01',
        group_key: groupKey.value,
        rcp_id: data.measurement_info['Recipe ID'] || 'Unknown',
        event_time: data.measurement_info['Start Time'] || new Date().toISOString(),
        tool: data.measurement_info['Tool'] || 'Unknown',
        operator: data.measurement_info['Operator'] || 'Unknown',
        sample_id: data.measurement_info['Sample ID'] || 'Unknown',
        carrier_id: data.measurement_info['Carrier ID'] || 'Unknown'
      }
      
      // Set available measurement points
      if (data.available_points && data.available_points.length > 0) {
        measurementPoints.value = data.available_points.map(point => ({
          point: point,
          group_key: groupKey.value
        }))
        
        // Auto-select first point and load its data
        selectPoint(data.available_points[0])
      }
      
      // Set statistics data by UL points
      if (data.data_status) {
        statisticsData.value = data.data_status
        console.log(`✅ Loaded statistics for points: ${Object.keys(data.data_status).join(', ')}`)
      }
      
      // Load summary/statistics data for backward compatibility
      try {
        const summaryResponse = await fetchSummaryData(groupKey.value)
        if (summaryResponse.success && summaryResponse.data) {
          summaryData.value = summaryResponse.data
          console.log(`✅ Loaded ${summaryResponse.data.length} statistics rows`)
        }
      } catch (error) {
        console.error('Error loading summary data:', error)
      }
      
      console.log('✅ Measurement data loaded successfully')
    } else {
      console.warn('⚠️ Failed to load measurement data, using fallback')
      
      // Fallback: parse group key
      const parts = groupKey.value.split('_')
      if (parts.length >= 3) {
        measurementInfo.value = {
          fab: 'SK_Hynix_ITC',
          lot_id: parts[0],
          wf_id: 'W01',
          group_key: groupKey.value,
          rcp_id: "UNKNOWN_RECIPE",
          event_time: new Date().toISOString()
        }
      }
    }
  } catch (error) {
    console.error('❌ Error loading measurement data:', error)
    
    // Fallback in case of error
    const parts = groupKey.value.split('_')
    if (parts.length >= 3) {
      measurementInfo.value = {
        fab: 'SK_Hynix_ITC',
        lot_id: parts[0],
        wf_id: 'W01',
        group_key: groupKey.value,
        rcp_id: "ERROR_LOADING",
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
/* Distinctive back button */
.back-button {
  border-radius: 12px;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 12px rgba(var(--v-theme-primary), 0.3);
  transition: all 0.3s ease;
}

.back-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(var(--v-theme-primary), 0.4);
}

/* Professional layout */
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

/* Responsive adjustments */
@media (max-width: 1280px) {
  .main-content-row {
    height: auto;
  }
  
  .heat-map-card {
    margin-bottom: 16px;
  }
}

/* Card spacing */
.v-card {
  margin-bottom: 16px;
}

.v-chip.v-chip--size-x-small {
  font-size: 0.625rem;
  height: 20px;
}
</style>