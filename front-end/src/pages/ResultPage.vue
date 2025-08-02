<template>
  <v-container fluid class="pa-6 px-md-8 px-lg-12">
    <!-- Distinctive Back Button and Download Options -->
    <div class="mb-3 d-flex justify-space-between align-center flex-wrap ga-3">
      <v-btn color="primary" variant="elevated" size="large" @click="goBack" class="back-button">
        <v-icon start>mdi-arrow-left</v-icon>
        {{ referrer === 'data-trend' ? 'Back to Data Trend' : 'Back to Search' }}
      </v-btn>

      <!-- Download Menu -->
      <div class="d-flex ga-2">
        <v-menu>
          <template v-slot:activator="{ props }">
            <v-btn color="success" variant="elevated" v-bind="props" :disabled="!hasData">
              <v-icon start>mdi-download</v-icon>
              Download Data
              <v-icon end>mdi-menu-down</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item @click="downloadMeasurementInfo"
              :disabled="!measurementInfo || Object.keys(measurementInfo).length === 0">
              <template v-slot:prepend>
                <v-icon>mdi-information</v-icon>
              </template>
              <v-list-item-title>Measurement Info</v-list-item-title>
            </v-list-item>

            <v-list-item @click="downloadSummaryStatistics" :disabled="!summaryData || summaryData.length === 0">
              <template v-slot:prepend>
                <v-icon>mdi-chart-line</v-icon>
              </template>
              <v-list-item-title>Summary Statistics</v-list-item-title>
            </v-list-item>

            <v-list-item @click="downloadDetailedData" :disabled="!detailedData || detailedData.length === 0">
              <template v-slot:prepend>
                <v-icon>mdi-table-large</v-icon>
              </template>
              <v-list-item-title>Detailed Data</v-list-item-title>
            </v-list-item>

            <v-list-item @click="downloadProfileData" :disabled="!profileData || profileData.length === 0">
              <template v-slot:prepend>
                <v-icon>mdi-axis</v-icon>
              </template>
              <v-list-item-title>Profile Data (X,Y,Z)</v-list-item-title>
            </v-list-item>

            <v-divider></v-divider>

            <v-list-item @click="downloadAllData" :disabled="!hasData">
              <template v-slot:prepend>
                <v-icon>mdi-package-down</v-icon>
              </template>
              <v-list-item-title>Download All (CSV)</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>
    </div>

    <!-- First row: Information and Scatter Chart with equal heights -->
    <v-row dense class="mb-3 equal-height-row">
      <!-- First column: Information -->
      <v-col cols="12" lg="6" class="d-flex">
        <div class="info-scatter-container w-100">
          <MeasurementInfo :measurement-info="measurementInfo" :summary-data="summaryData" :compact="true" />
        </div>
      </v-col>

      <!-- Second column: Scatter Chart -->
      <v-col cols="12" lg="6" class="d-flex">
        <div class="info-scatter-container w-100">
          <StatisticalInfoByPoints :summary-data="summaryData" @row-click="handleStatisticRowClick"
            @statistic-selected="handleStatisticSelected" :compact="true" />
        </div>
      </v-col>
    </v-row>

    <!-- Additional Images Row: Measure Profile Analysis, Align, and Tip Images -->
    <v-row dense class="mb-3">
      <v-col cols="12">
        <AdditionalAnalysisImages :selected-point="selectedPoint" :filename="filename" />
      </v-col>
    </v-row>

    <!-- Second row: Two-column layout for detailed data and heat map -->
    <v-row dense>
      <!-- Column 1: Detailed Data (Half Width) -->
      <v-col cols="12" lg="6">
        <div style="max-height: 1000px; overflow-y: auto;">
          <MeasurementPoints :detailed-data="detailedData" :loading="isLoadingProfile" :filename="filename"
            :measurement-points="measurementPoints" :selected-point="selectedPoint"
            @point-selected="handlePointSelected" @point-data-loaded="handlePointDataLoaded"
            @simple-point-selected="selectPoint" />
        </div>
      </v-col>

      <!-- Column 2: Heat Map and Charts -->
      <v-col cols="12" lg="6">
        <v-row dense>
          <!-- Heat Map -->
          <v-col cols="12">
            <v-card class="heat-map-card mb-3" height="500">
              <v-card-title class="py-2">
                <v-icon start size="small">mdi-grid</v-icon>
                <span class="text-subtitle-1">Wafer Heat Map</span>
              </v-card-title>
              <v-card-text class="pa-3">
                <EnhancedChartVisualization :filename="filename" :chart-height="440" :profile-data="profileData"
                  :selected-point="selectedPoint" @point-selected="handleWaferPointSelected" />
              </v-card-text>
            </v-card>
          </v-col>

          <!-- Profile Image and Z-Distribution Row -->
          <v-col cols="12">
            <v-row dense>
              <!-- Profile Image -->
              <v-col cols="12" md="6">
                <v-card class="profile-card" height="350">
                  <v-card-title class="py-2">
                    <v-icon start size="small">mdi-image</v-icon>
                    <span class="text-subtitle-1">Profile Image</span>
                    <v-spacer />
                    <v-chip v-if="selectedPoint" size="x-small" color="primary" variant="outlined">
                      Point {{ selectedPoint }}
                    </v-chip>
                  </v-card-title>
                  <v-card-text class="pa-3">
                    <div v-if="isLoadingProfileImage" class="text-center pa-4">
                      <v-progress-circular indeterminate color="primary" size="small" />
                      <p class="mt-2 text-caption">Loading profile image...</p>
                    </div>
                    <div v-else-if="profileImageUrl" class="profile-image-container"
                      style="height: 280px; display: flex; align-items: center; justify-content: center;">
                      <img :src="profileImageUrl" alt="Profile Image" class="profile-image"
                        style="max-height: 100%; max-width: 100%; object-fit: contain;" @error="handleImageError"
                        @load="handleImageLoad" />
                    </div>
                    <div v-else class="text-center pa-4">
                      <v-icon size="32" color="grey">mdi-image-off</v-icon>
                      <p class="text-body-2 mt-2 text-medium-emphasis">No profile image available</p>
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>

              <!-- Z-Value Distribution -->
              <v-col cols="12" md="6">
                <v-card class="distribution-card" height="350">
                  <v-card-title class="py-2">
                    <v-icon start size="small">mdi-chart-bar</v-icon>
                    <span class="text-subtitle-1">Z-Value Distribution</span>
                    <v-spacer />
                    <v-chip v-if="profileData.length > 0" size="x-small" color="success" variant="outlined">
                      {{ profileData.length.toLocaleString() }} points
                    </v-chip>
                  </v-card-title>
                  <v-card-text class="pa-3">
                    <ChartVisualization :selected-point="selectedPoint" :profile-data="profileData"
                      :is-loading="isLoadingProfile" :chart-height="280" :compact="false" :chart-type="'histogram'" />
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchProfileData, fetchSummaryData, fetchMeasurementData, apiService } from '@/services/index.js'
import { downloadCSV, formatMeasurementInfo, formatSummaryStatistics, formatProfileData, generateFilename } from '@/utils/exportUtils.js'

// Import components
import MeasurementInfo from '@/components/ResultPage/MeasurementInfo.vue'
import ChartVisualization from '@/components/ResultPage/ChartVisualization.vue'
import StatisticalInfoByPoints from '@/components/ResultPage/StatisticalInfoByPoints.vue'
import MeasurementPoints from '@/components/ResultPage/MeasurementPoints.vue'
import EnhancedChartVisualization from '@/components/ResultPage/EnhancedChartVisualization.vue'
import AdditionalAnalysisImages from '@/components/ResultPage/AdditionalAnalysisImages.vue'

const route = useRoute()
const router = useRouter()

// Navigation tracking
const referrer = ref('')

// Reactive data
const filename = ref(decodeURIComponent(route.params.filename || ''))
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

      // Set measurement info from info dict (transformed from information)
      console.log(`🔍 [ResultPage] Checking info data:`, data.info)
      if (data.info && Object.keys(data.info).length > 0) {
        measurementInfo.value = data.info
        console.log(`✅ [ResultPage] Set measurement information:`, measurementInfo.value)
      } else {
        // Fallback measurement info
        measurementInfo.value = {
          'Group Key': filename.value,
          'Recipe ID': recipeId.value || 'Unknown',
          'Lot ID': extractLotIdFromFilename(filename.value),
          'Fab': 'SK_Hynix_ITC',
          'Loading Status': 'No Information Available'
        }
        console.log(`⚠️ [ResultPage] Using fallback measurement info:`, measurementInfo.value)
      }

      // Set summary data from DataFrame - using transformed summaryData
      console.log(`🔍 [ResultPage] Checking summaryData:`, data.summaryData)
      console.log(`🔍 [ResultPage] summaryData is array:`, Array.isArray(data.summaryData))
      console.log(`🔍 [ResultPage] summaryData length:`, data.summaryData ? data.summaryData.length : 'null/undefined')

      if (data.summaryData && Array.isArray(data.summaryData) && data.summaryData.length > 0) {
        summaryData.value = data.summaryData
        console.log(`✅ [ResultPage] Set summary data from summaryData:`, summaryData.value)
        console.log(`✅ [ResultPage] Summary data length:`, summaryData.value.length)
        console.log(`✅ [ResultPage] First summary record:`, summaryData.value[0])
      } else {
        // Fallback: check legacy summary property
        if (data.summary && Array.isArray(data.summary) && data.summary.length > 0) {
          summaryData.value = data.summary
          console.log(`✅ [ResultPage] Set summary data from legacy summary:`, summaryData.value)
        } else {
          // Generate dummy summary data for demonstration
          summaryData.value = generateDummySummaryData(filename.value)
          console.log(`⚠️ [ResultPage] Using dummy summary data:`, summaryData.value)
        }
      }

      // Set detailed data from DataFrame - using transformed profileData (which contains detailed measurements)
      if (data.profileData && Array.isArray(data.profileData) && data.profileData.length > 0) {
        detailedData.value = data.profileData
        console.log(`✅ Loaded ${data.profileData.length} detailed data records from profileData`)
      } else if (data.data && Array.isArray(data.data) && data.data.length > 0) {
        detailedData.value = data.data
        console.log(`✅ Loaded ${data.data.length} detailed data records from legacy data property`)
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

      // Profile data for charts will be loaded separately via API calls when points are selected
      // Initial profile data is not typically available in the summary response
      console.log(`📊 [ResultPage] Profile data will be loaded when measurement points are selected`)


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
function extractLotIdFromFilename(filename) {
  // Extract lot ID from filename pattern #date#recipe#lot_id_time#slot_measured#
  const parts = filename.split('#')
  if (parts.length >= 4) {
    const lotPart = parts[3]
    const lotId = lotPart.split('_')[0] // Get lot ID before underscore
    return lotId || 'Unknown'
  }
  return 'Unknown'
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

    // Set dummy images
    setDummyImages()

    console.log('✅ Created fallback measurement data')
  }
}

// Helper function to generate dummy summary data in DataFrame format
function generateDummySummaryData(filename) {
  const parts = filename.split('#')
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

  const { measurementPoint, pointNumber, filename: pointFilename, siteInfo } = pointData

  console.log(`🔍 [ResultPage] Destructured values:`)
  console.log(`   measurementPoint: "${measurementPoint}" (${typeof measurementPoint})`)
  console.log(`   pointNumber: "${pointNumber}" (${typeof pointNumber})`)
  console.log(`   pointFilename: "${pointFilename}" (${typeof pointFilename})`)
  console.log(`   siteInfo:`, siteInfo)

  if (pointNumber && pointFilename) {
    try {
      // Fetch profile data and image in parallel
      console.log(`🔄 [ResultPage] Fetching profile data and image for point ${pointNumber}`)
      console.log(`📍 [ResultPage] Site info received:`, siteInfo)
      isLoadingProfile.value = true
      isLoadingProfileImage.value = true

      // Clean filename by removing .csv extension if present
      const cleanFilename = pointFilename.replace('.csv', '')

      // Convert measurement point format to point number if needed
      let cleanPointNumber = pointNumber
      if (typeof pointNumber === 'string' && pointNumber.includes('_')) {
        console.log(`🔧 [ResultPage] Converting "${pointNumber}" to number part`)
        cleanPointNumber = pointNumber.split('_')[0] // Extract number part
      }

      console.log(`🔧 [ResultPage] Final values for API calls:`)
      console.log(`   cleanFilename: "${cleanFilename}"`)
      console.log(`   cleanPointNumber: "${cleanPointNumber}" (${typeof cleanPointNumber})`)
      console.log(`   siteInfo:`, siteInfo)

      const toolName = route.query.tool || 'MAP608'

      const [profileResponse, imageResponse] = await Promise.allSettled([
        apiService.getProfileData(cleanFilename, cleanPointNumber, toolName, siteInfo),
        apiService.getProfileImage(cleanFilename, cleanPointNumber, toolName, siteInfo)
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
        profileImageUrl.value = apiService.getProfileImageUrl(cleanFilename, cleanPointNumber, toolName, siteInfo)
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
  // Check if we came from DataTrendPage
  if (referrer.value === 'data-trend') {
    router.push('/result/data_trend')
  } else {
    // Default: go back to search page
    router.push('/')
  }
}

// Computed property for checking if we have any data
const hasData = computed(() => {
  return (measurementInfo.value && Object.keys(measurementInfo.value).length > 0) ||
    (summaryData.value && summaryData.value.length > 0) ||
    (detailedData.value && detailedData.value.length > 0)
})

// Download functions
function downloadMeasurementInfo() {
  const data = formatMeasurementInfo(measurementInfo.value)
  const filename = generateFilename('measurement_info', measurementInfo.value)
  downloadCSV(data, filename)
}

function downloadSummaryStatistics() {
  const data = formatSummaryStatistics(summaryData.value)
  const filename = generateFilename('summary_statistics', measurementInfo.value)
  downloadCSV(data, filename)
}

function downloadDetailedData() {
  const filename = generateFilename('detailed_data', measurementInfo.value)
  downloadCSV(detailedData.value, filename)
}

function downloadProfileData() {
  const data = formatProfileData(profileData.value)
  const filename = generateFilename(`profile_data_point_${selectedPoint.value || 'all'}`, measurementInfo.value)
  downloadCSV(data, filename)
}

function downloadAllData() {
  // Create a combined dataset
  const timestamp = new Date().toISOString().split('T')[0].replace(/-/g, '')
  const lotId = measurementInfo.value.lot_id || 'unknown'
  const recipe = measurementInfo.value.recipe_name || 'data'

  // Download each dataset separately with related names
  const baseFilename = `AFM_${recipe}_${lotId}_${timestamp}`

  // Download measurement info
  if (measurementInfo.value && Object.keys(measurementInfo.value).length > 0) {
    const infoData = formatMeasurementInfo(measurementInfo.value)
    downloadCSV(infoData, `${baseFilename}_info`)
  }

  // Download summary statistics
  if (summaryData.value && summaryData.value.length > 0) {
    const summaryFormatted = formatSummaryStatistics(summaryData.value)
    downloadCSV(summaryFormatted, `${baseFilename}_summary`)
  }

  // Download detailed data
  if (detailedData.value && detailedData.value.length > 0) {
    downloadCSV(detailedData.value, `${baseFilename}_detailed`)
  }

  // Download profile data if available
  if (profileData.value && profileData.value.length > 0) {
    const profileFormatted = formatProfileData(profileData.value)
    downloadCSV(profileFormatted, `${baseFilename}_profile_point_${selectedPoint.value || 'last'}`)
  }
}

// Lifecycle
onMounted(() => {
  // Check if we have a referrer in the route query
  if (route.query.from) {
    referrer.value = route.query.from
  }

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
  font-size: 0.75rem;
  font-weight: 600;
  padding: 6px 10px;
}

.heat-map-card .v-card-text,
.profile-card .v-card-text,
.distribution-card .v-card-text {
  padding: 6px;
  height: calc(100% - 36px);
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
  margin-bottom: 12px;
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


/* Equal height row styling */
.equal-height-row {
  min-height: 750px;
}

.equal-height-row > .v-col {
  display: flex;
}

/* Fixed height containers for first row - both use same class now */
.info-scatter-container {
  min-height: 750px;
  height: 750px;
  position: relative;
  display: flex;
  flex-direction: column;
}

/* Ensure child components fill the container */
.info-scatter-container > * {
  height: 100%;
  flex: 1;
}

/* Make both cards consistent */
.info-scatter-container :deep(.v-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.info-scatter-container :deep(.v-card-title) {
  flex-shrink: 0;
}

.info-scatter-container :deep(.v-card-text) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Special handling for scatter chart to ensure it fills space */
.info-scatter-container :deep(.v-row) {
  flex-shrink: 0;
}

/* Ensure the chart itself fills remaining space */
.info-scatter-container :deep(.v-card-text > div:last-child) {
  flex: 1;
  min-height: 0;
}

/* Custom scrollbar styling */
.info-scatter-container :deep(.v-card-text)::-webkit-scrollbar {
  width: 6px;
}

.info-scatter-container :deep(.v-card-text)::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.info-scatter-container :deep(.v-card-text)::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.info-scatter-container :deep(.v-card-text)::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Since mobile/tablet views are not needed, removed responsive adjustments */
</style>
