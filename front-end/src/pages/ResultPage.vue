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
        <AdditionalAnalysisImages :selected-point="selectedPoint?.value || selectedPoint" :filename="filename" />
      </v-col>
    </v-row>

    <!-- Second row: Two-column layout for detailed data and heat map -->
    <v-row dense>
      <!-- Column 1: Detailed Data (Half Width) -->
      <v-col cols="12" lg="6">
        <div style="max-height: 1200px; overflow-y: auto;">
          <MeasurementPoints :detailed-data="detailedData" :loading="isLoadingProfile" :filename="filename"
            :measurement-points="measurementPoints"
            :selected-point="String(selectedPoint?.value || selectedPoint || '')" @point-selected="handlePointSelected"
            @point-data-loaded="handlePointDataLoaded" @simple-point-selected="selectPoint" />
        </div>
      </v-col>

      <!-- Column 2: Heat Map and Charts -->
      <v-col cols="12" lg="6">
        <div style="min-height: 1200px; max-height: 1200px; overflow-y: auto; overflow-x: hidden;">
          <v-row dense>
            <!-- Heat Map -->
            <v-col cols="12">
              <v-card class="heat-map-card mb-3" height="480">
                <v-card-title class="py-2">
                  <v-icon start size="small">mdi-grid</v-icon>
                  <span class="text-subtitle-1">Wafer Heat Map</span>
                  <v-spacer />
                  <v-progress-circular v-if="isLoadingWafer" indeterminate size="16" width="2" />
                </v-card-title>
                <v-card-text class="pa-3">
                  <HeatmapChart :profile-data="waferData" :chart-height="420" :clickable="true"
                    :selected-point="selectedPoint?.value || selectedPoint"
                    @point-selected="handleWaferPointSelected" />
                </v-card-text>
              </v-card>
            </v-col>

            <!-- Profile Image Row -->
            <v-col cols="12">
              <v-card class="profile-card" height="500">
                <v-card-title class="py-2">
                  <v-icon start size="small">mdi-image</v-icon>
                  <span class="text-subtitle-1">Profile Image</span>
                  <v-spacer />
                  <v-chip v-if="selectedPoint?.value || selectedPoint" size="x-small" color="primary"
                    variant="outlined">
                    Point {{ selectedPoint?.value || selectedPoint }}
                  </v-chip>
                </v-card-title>
                <v-card-text class="pa-3">
                  <div v-if="isLoadingProfileImage" class="text-center pa-4">
                    <v-progress-circular indeterminate color="primary" size="small" />
                    <p class="mt-2 text-caption">Loading profile image...</p>
                  </div>
                  <div v-else-if="profileImageUrl" class="profile-image-container"
                    style="height: 430px; display: flex; align-items: center; justify-content: center;">
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

            <!-- Z-Value Distribution Row -->
            <v-col cols="12">
              <v-card class="distribution-card" height="500">
                <v-card-title class="py-2">
                  <v-icon start size="small">mdi-chart-bar</v-icon>
                  <span class="text-subtitle-1">Z-Value Distribution</span>
                  <v-spacer />
                  <v-chip v-if="profileData.length > 0" size="x-small" color="success" variant="outlined">
                    {{ profileData.length.toLocaleString() }} points
                  </v-chip>
                </v-card-title>
                <v-card-text class="pa-3">
                  <div v-if="isLoadingProfile" class="text-center pa-4">
                    <v-progress-circular indeterminate color="primary" size="small" />
                    <p class="mt-2 text-caption">Loading...</p>
                  </div>
                  <HistogramChart v-else :profile-data="profileData" :chart-height="430" :compact="false" />
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useResultPageData } from '@/composables/useResultPageQueries.js'
import { usePointSelection } from '@/composables/usePointSelection.js'
import { useDataDownload } from '@/composables/useDataDownload.js'

// Import components
import MeasurementInfo from '@/components/ResultPage/MeasurementInfo.vue'
import HistogramChart from '@/components/ResultPage/charts/HistogramChart.vue'
import StatisticalInfoByPoints from '@/components/ResultPage/StatisticalInfoByPoints.vue'
import MeasurementPoints from '@/components/ResultPage/MeasurementPoints.vue'
import HeatmapChart from '@/components/ResultPage/charts/HeatmapChart.vue'
import AdditionalAnalysisImages from '@/components/ResultPage/AdditionalAnalysisImages.vue'

const route = useRoute()
const router = useRouter()

// Navigation tracking
const referrer = ref('')

// Basic route data
const filename = ref(decodeURIComponent(route.params.filename || ''))
const toolName = ref(route.query.tool || 'MAP608')
const selectedStatistic = ref(null)

// Point selection logic
const pointSelection = usePointSelection()
const { selectedPoint, selectPoint, handlePointSelected, handleWaferPointSelected, handlePointDataLoaded } = pointSelection

// Vue Query data fetching
const {
  measurementInfo,
  summaryData,
  detailedData,
  measurementPoints,
  profileData,
  profileImageUrl,
  waferData,
  isLoadingProfile,
  isLoadingProfileImage,
  isLoadingWafer,
  hasData
} = useResultPageData(filename.value, selectedPoint, toolName.value)

// Download functionality
const downloadFunctions = useDataDownload(
  measurementInfo,
  summaryData,
  detailedData,
  profileData,
  computed(() => selectedPoint.value?.value || selectedPoint.value)
)

const {
  downloadMeasurementInfo,
  downloadSummaryStatistics,
  downloadDetailedData,
  downloadProfileData,
  downloadAllData
} = downloadFunctions


// Handler for statistical row clicks
function handleStatisticRowClick(rowItem) {
  selectedStatistic.value = rowItem.ITEM
}

// Handler for statistic selection
function handleStatisticSelected(statisticName) {
  selectedStatistic.value = statisticName
}


// Image handling functions
function handleImageError(event) {
  console.warn('Profile image failed to load:', event)
}

function handleImageLoad(event) {
  // Profile image loaded successfully
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


// Lifecycle
onMounted(() => {
  // Check if we have a referrer in the route query
  if (route.query.from) {
    referrer.value = route.query.from
  }
})

// Auto-select first point when measurement points are loaded
watch(measurementPoints, (newPoints) => {
  if (newPoints && newPoints.length > 0 && !selectedPoint.value) {
    console.log(`📍 Auto-selecting first point: ${newPoints[0].point}`)
    selectPoint(newPoints[0].point)
  }
}, { immediate: true })
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

.equal-height-row>.v-col {
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
.info-scatter-container>* {
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

/* Prevent horizontal overflow in Column 2 */
.heat-map-card,
.profile-card,
.distribution-card {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.heat-map-card .v-card-text,
.profile-card .v-card-text,
.distribution-card .v-card-text {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

/* Ensure charts don't exceed container width */
.heat-map-card :deep(.echarts),
.distribution-card :deep(.echarts) {
  max-width: 100% !important;
  width: 100% !important;
}

/* Since mobile/tablet views are not needed, removed responsive adjustments */
</style>
