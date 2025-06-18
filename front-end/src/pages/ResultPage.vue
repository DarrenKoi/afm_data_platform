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
      <StatisticalInfoByPoints 
        :summary-data="summaryData" 
        @row-click="handleStatisticRowClick"
        @statistic-selected="handleStatisticSelected"
      />
    </div>

    <!-- Detailed Measurement Points Data -->
    <div class="mb-4">
      <MeasurementPoints 
        :detailed-data="detailedData"
        :loading="isLoadingProfile"
        :filename="filename"
        @point-selected="handlePointSelected"
        @point-data-loaded="handlePointDataLoaded"
      />
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
              :filename="filename" 
              :chart-height="chartHeight - 80"
              :profile-data="profileData"
              :selected-point="selectedPoint"
              @point-selected="handleWaferPointSelected"
            />
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Column 2: Profile Image and Z-Distribution -->
      <v-col cols="12" lg="5" xl="6">
        <v-row dense>
          <!-- Profile Image -->
          <v-col cols="12">
            <v-card class="profile-card mb-2" :height="(chartHeight / 2) - 6">
              <v-card-title class="py-2">
                <v-icon start size="small">mdi-image</v-icon>
                <span class="text-subtitle-1">Profile Image</span>
                <v-spacer />
                <v-chip v-if="selectedPoint" size="x-small" color="primary" variant="outlined">
                  Point {{ selectedPoint }}
                </v-chip>
              </v-card-title>
              <v-card-text class="pa-2">
                <div v-if="isLoadingProfileImage" class="text-center pa-4">
                  <v-progress-circular indeterminate color="primary" size="small" />
                  <p class="mt-2 text-caption">Loading profile image...</p>
                </div>
                <div v-else-if="profileImageUrl" class="profile-image-container">
                  <img 
                    :src="profileImageUrl" 
                    alt="Profile Image"
                    class="profile-image"
                    @error="handleImageError"
                    @load="handleImageLoad"
                  />
                </div>
                <div v-else class="text-center pa-4">
                  <v-icon size="32" color="grey">mdi-image-off</v-icon>
                  <p class="text-body-2 mt-2 text-medium-emphasis">No profile image available</p>
                </div>
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
import { fetchProfileData, fetchSummaryData, fetchMeasurementData, apiService } from '@/services/api.js'

// Import components
import MeasurementInfo from '@/components/ResultPage/MeasurementInfo.vue'
import SummaryDataTable from '@/components/ResultPage/SummaryDataTable.vue'
import MeasurementPointsSelector from '@/components/ResultPage/MeasurementPointsSelector.vue'
import ChartVisualization from '@/components/ResultPage/ChartVisualization.vue'
import StatisticalInfo from '@/components/ResultPage/StatisticalInfo.vue'
import StatisticalInfoByPoints from '@/components/ResultPage/StatisticalInfoByPoints.vue'
import MeasurementPoints from '@/components/ResultPage/MeasurementPoints.vue'
import EnhancedChartVisualization from '@/components/ResultPage/EnhancedChartVisualization.vue'

const route = useRoute()
const router = useRouter()

// Reactive data
const filename = ref(decodeURIComponent(route.params.groupKey || '')) // groupKey param contains filename now
const recipeId = ref(route.params.recipeId)
const measurementInfo = ref({})
const summaryData = ref([])
const detailedData = ref([])
const measurementPoints = ref([])
const selectedPoint = ref(null)
const profileData = ref([])
const isLoadingProfile = ref(false)
const selectedStatistic = ref(null)
const profileImageUrl = ref(null)
const isLoadingProfileImage = ref(false)


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
    const response = await fetchProfileData(filename.value, pointNumber)
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
  console.log(`🚀 [ResultPage] Loading data for recipe: ${recipeId.value}, filename: ${filename.value}`)
  
  try {
    // Load real measurement data from pickle file
    console.log(`🔍 [ResultPage] Calling fetchMeasurementData...`)
    const measurementResponse = await fetchMeasurementData(filename.value)
    
    console.log(`📦 [ResultPage] measurementResponse:`, measurementResponse)
    console.log(`📦 [ResultPage] measurementResponse.success:`, measurementResponse.success)
    console.log(`📦 [ResultPage] measurementResponse.data:`, measurementResponse.data)
    
    if (measurementResponse.success && measurementResponse.data) {
      const data = measurementResponse.data
      console.log(`🎯 [ResultPage] Processing data with keys:`, Object.keys(data))
      
      // Set measurement info from information dict
      console.log(`🔍 [ResultPage] Checking information data:`, data.information)
      if (data.information && Object.keys(data.information).length > 0) {
        measurementInfo.value = data.information
        console.log(`✅ [ResultPage] Set measurement information:`, measurementInfo.value)
      } else {
        // Fallback measurement info
        measurementInfo.value = {
          'Group Key': filename.value,
          'Recipe ID': recipeId.value || 'Unknown',
          'Lot ID': extractLotIdFromGroupKey(filename.value),
          'Fab': 'SK_Hynix_ITC',
          'Loading Status': 'No Information Available'
        }
        console.log(`⚠️ [ResultPage] Using fallback measurement info:`, measurementInfo.value)
      }
      
      // Set summary data from DataFrame
      console.log(`🔍 [ResultPage] Checking summary data:`, data.summary)
      console.log(`🔍 [ResultPage] Summary is array:`, Array.isArray(data.summary))
      console.log(`🔍 [ResultPage] Summary length:`, data.summary ? data.summary.length : 'null/undefined')
      
      if (data.summary && Array.isArray(data.summary) && data.summary.length > 0) {
        summaryData.value = data.summary
        console.log(`✅ [ResultPage] Set summary data:`, summaryData.value)
        console.log(`✅ [ResultPage] Summary data length:`, summaryData.value.length)
        console.log(`✅ [ResultPage] First summary record:`, summaryData.value[0])
      } else {
        // Generate dummy summary data for demonstration
        summaryData.value = generateDummySummaryData(filename.value)
        console.log(`⚠️ [ResultPage] Using dummy summary data:`, summaryData.value)
      }
      
      // Set detailed data from DataFrame  
      if (data.data && Array.isArray(data.data) && data.data.length > 0) {
        detailedData.value = data.data
        console.log(`✅ Loaded ${data.data.length} detailed data records`)
      } else {
        detailedData.value = []
        console.log('⚠️ No detailed data available')
      }
      
      // Set available measurement points
      if (data.available_points && data.available_points.length > 0) {
        measurementPoints.value = data.available_points.map(point => ({
          point: point,
          filename: filename.value
        }))
        
        // Auto-select first point and load its data
        selectPoint(data.available_points[0])
      } else {
        // Generate default measurement points from filename
        // Try to parse slot and measured info from filename
        const parsed = filename.value.match(/#(\d+)_(\w+)#/)
        if (parsed) {
          const [, slot, measuredInfo] = parsed
          measurementPoints.value = [{
            point: `${slot}_${measuredInfo}`,
            filename: filename.value
          }]
          selectPoint(`${slot}_${measuredInfo}`)
        }
      }
      
      // Set profile data if available
      if (data.profile_data && Array.isArray(data.profile_data)) {
        profileData.value = data.profile_data
        console.log(`✅ Loaded ${data.profile_data.length} profile data points`)
      }
      
      console.log('✅ Measurement data loaded successfully')
    } else {
      console.warn('⚠️ Failed to load measurement data, using fallback')
      createFallbackData()
    }
  } catch (error) {
    console.error('❌ Error loading measurement data:', error)
    createFallbackData()
  }
}

// Helper function to extract lot ID from group key
function extractLotIdFromGroupKey(groupKey) {
  const parts = groupKey.split('_')
  return parts.length > 0 ? parts[0] : 'Unknown'
}

// Helper function to create fallback data when pickle files are not available
function createFallbackData() {
  // Try to parse information from filename
  const parsed = filename.value.match(/#(\d{6})#(.+?)#([^_]+)_.*?#(\d+)_(\w+)#/)
  if (parsed) {
    const [, date, recipe, lotId, slot, measuredInfo] = parsed
    // Create measurement info from filename
    measurementInfo.value = {
      fab: 'SK_Hynix_ITC',
      lot_id: lotId,
      wf_id: 'W01',
      filename: filename.value,
      rcp_id: recipe || recipeId.value || "UNKNOWN_RECIPE",
      event_time: new Date().toISOString(),
      tool: 'AFM_Tool',
      operator: 'System',
      sample_id: filename.value,
      carrier_id: 'Auto'
    }
    
    // Create measurement points
    measurementPoints.value = [{
      point: `${slot}_${measuredInfo}`,
      filename: filename.value
    }]
    
    // Generate dummy statistics
    statisticsData.value = generateDummyStatistics(filename.value)
    
    console.log('✅ Created fallback measurement data')
  }
}

// Helper function to generate dummy summary data in DataFrame format
function generateDummySummaryData(groupKey) {
  const parts = groupKey.split('_')
  const pointName = parts.length >= 3 ? `${parts[1]}_UL` : '1_UL'
  
  return [
    { ITEM: 'MEAN', [pointName]: -4.942, 'Left_H (nm)': -4.942, 'Right_H (nm)': -6.014, 'Ref_H (nm)': 0.0 },
    { ITEM: 'STDEV', [pointName]: 0.234, 'Left_H (nm)': 0.234, 'Right_H (nm)': 0.156, 'Ref_H (nm)': 0.0 },
    { ITEM: 'MIN', [pointName]: -5.890, 'Left_H (nm)': -5.890, 'Right_H (nm)': -6.520, 'Ref_H (nm)': 0.0 },
    { ITEM: 'MAX', [pointName]: -4.120, 'Left_H (nm)': -4.120, 'Right_H (nm)': -5.340, 'Ref_H (nm)': 0.0 },
    { ITEM: 'COUNT', [pointName]: 1000, 'Left_H (nm)': 1000, 'Right_H (nm)': 1000, 'Ref_H (nm)': 1000 },
    { ITEM: 'RANGE', [pointName]: 1.770, 'Left_H (nm)': 1.770, 'Right_H (nm)': 1.180, 'Ref_H (nm)': 0.0 }
  ]
}

// Handler for statistical row clicks
function handleStatisticRowClick(rowItem) {
  console.log('Statistical row clicked:', rowItem)
  selectedStatistic.value = rowItem.ITEM
  
  // Filter detailed data based on the selected statistic
  // This would show detailed measurement data for the selected statistic
  if (detailedData.value.length > 0) {
    console.log(`Filtering detailed data for statistic: ${rowItem.ITEM}`)
    // Here you could filter or highlight specific data in charts
  }
}

// Handler for statistic selection
function handleStatisticSelected(statisticName) {
  console.log('Statistic selected:', statisticName)
  selectedStatistic.value = statisticName
}

// Handler for measurement point selection from MeasurementPoints component
async function handlePointSelected(pointData) {
  console.log('🎯 [ResultPage] Point selected:', pointData)
  
  const { measurementPoint, pointNumber, filename: pointFilename } = pointData
  
  if (pointNumber && pointFilename) {
    try {
      // Fetch profile data and image in parallel
      console.log(`🔄 [ResultPage] Fetching profile data and image for point ${pointNumber}`)
      isLoadingProfile.value = true
      isLoadingProfileImage.value = true
      
      const [profileResponse, imageResponse] = await Promise.allSettled([
        apiService.getProfileData(pointFilename, pointNumber),
        apiService.getProfileImage(pointFilename, pointNumber)
      ])
      
      // Handle profile data response
      if (profileResponse.status === 'fulfilled' && profileResponse.value.success) {
        console.log(`✅ [ResultPage] Loaded ${profileResponse.value.data.length} profile points`)
        profileData.value = profileResponse.value.data
        console.log(`📊 [ResultPage] Profile data sample:`, profileResponse.value.data.slice(0, 3))
      } else {
        console.warn(`⚠️ [ResultPage] Failed to load profile data:`, profileResponse.reason || profileResponse.value?.error)
        profileData.value = []
      }
      
      // Handle image response
      if (imageResponse.status === 'fulfilled' && imageResponse.value.success) {
        console.log(`✅ [ResultPage] Loaded profile image:`, imageResponse.value.data.filename)
        profileImageUrl.value = apiService.getProfileImageUrl(pointFilename, pointNumber)
        console.log(`🖼️ [ResultPage] Profile image URL:`, profileImageUrl.value)
      } else {
        console.warn(`⚠️ [ResultPage] Failed to load profile image:`, imageResponse.reason || imageResponse.value?.error)
        profileImageUrl.value = null
      }
      
      // Update selected point for other components
      selectedPoint.value = measurementPoint
      
    } catch (error) {
      console.error(`❌ [ResultPage] Error loading profile data and image:`, error)
      profileData.value = []
      profileImageUrl.value = null
    } finally {
      isLoadingProfile.value = false
      isLoadingProfileImage.value = false
    }
  }
}

// Handler for point data loaded event
function handlePointDataLoaded(data) {
  console.log('📊 [ResultPage] Point data loaded:', data)
  // Could be used to update UI state or trigger other actions
}

// Image handling functions
function handleImageError(event) {
  console.warn('Profile image failed to load:', event)
  profileImageUrl.value = null
}

function handleImageLoad(event) {
  console.log('Profile image loaded successfully:', event.target.src)
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

/* Profile image styles */
.profile-image-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.profile-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.profile-image:hover {
  transform: scale(1.02);
}
</style>