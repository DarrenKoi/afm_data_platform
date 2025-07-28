<template>
  <v-card elevation="3">
    <v-card-title class="py-2">
      <v-icon start size="small">mdi-image-multiple</v-icon>
      <span class="text-subtitle-1">Additional Analysis Images</span>
      <v-spacer />
      <v-chip v-if="selectedPoint" size="x-small" color="primary" variant="outlined">
        Point {{ selectedPoint }}
      </v-chip>
    </v-card-title>
    <v-card-text class="pa-3">
      <v-row dense>
        <!-- Measure Profile Analysis Image -->
        <v-col cols="12" md="4">
          <v-card class="analysis-image-card" height="400">
            <v-card-title class="py-2">
              <v-icon start size="small">mdi-chart-line-variant</v-icon>
              <span class="text-caption">Measure Profile Analysis</span>
            </v-card-title>
            <v-card-text class="pa-2">
              <div v-if="isLoadingMeasureProfileImage" class="text-center pa-4">
                <v-progress-circular indeterminate color="primary" size="small" />
                <p class="mt-2 text-caption">Loading analysis image...</p>
              </div>
              <div v-else-if="measureProfileImageUrl" class="image-container"
                style="height: 340px; display: flex; align-items: center; justify-content: center;">
                <img :src="measureProfileImageUrl" alt="Measure Profile Analysis" class="analysis-image"
                  style="max-height: 100%; max-width: 100%; object-fit: contain;" />
              </div>
              <div v-else class="text-center pa-4">
                <v-icon size="48" color="grey-lighten-1">mdi-chart-bell-curve-cumulative</v-icon>
                <p class="text-caption mt-2 text-medium-emphasis">From /Capture folder</p>
                <p class="text-caption text-grey">No analysis image available</p>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Align Image -->
        <v-col cols="12" md="4">
          <v-card class="analysis-image-card" height="400">
            <v-card-title class="py-2">
              <v-icon start size="small">mdi-align-horizontal-center</v-icon>
              <span class="text-caption">Sample Alignment</span>
            </v-card-title>
            <v-card-text class="pa-2">
              <div v-if="isLoadingAlignImage" class="text-center pa-4">
                <v-progress-circular indeterminate color="primary" size="small" />
                <p class="mt-2 text-caption">Loading align image...</p>
              </div>
              <div v-else-if="alignImageUrl" class="image-container"
                style="height: 340px; display: flex; align-items: center; justify-content: center;">
                <img :src="alignImageUrl" alt="Sample Alignment" class="analysis-image"
                  style="max-height: 100%; max-width: 100%; object-fit: contain;" />
              </div>
              <div v-else class="text-center pa-4">
                <v-icon size="48" color="grey-lighten-1">mdi-crosshairs-gps</v-icon>
                <p class="text-caption mt-2 text-medium-emphasis">From /Debug/SampleAlign</p>
                <p class="text-caption text-grey">No alignment image available</p>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Tip Image -->
        <v-col cols="12" md="4">
          <v-card class="analysis-image-card" height="400">
            <v-card-title class="py-2">
              <v-icon start size="small">mdi-needle</v-icon>
              <span class="text-caption">Tip Condition</span>
            </v-card-title>
            <v-card-text class="pa-2">
              <div v-if="isLoadingTipImage" class="text-center pa-4">
                <v-progress-circular indeterminate color="primary" size="small" />
                <p class="mt-2 text-caption">Loading tip image...</p>
              </div>
              <div v-else-if="tipImageUrl" class="image-container"
                style="height: 340px; display: flex; align-items: center; justify-content: center;">
                <img :src="tipImageUrl" alt="Tip Condition" class="analysis-image"
                  style="max-height: 100%; max-width: 100%; object-fit: contain;" />
              </div>
              <div v-else class="text-center pa-4">
                <v-icon size="48" color="grey-lighten-1">mdi-circle-slice-8</v-icon>
                <p class="text-caption mt-2 text-medium-emphasis">From /Debug/Image</p>
                <p class="text-caption text-grey">No tip image available</p>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

// Props
const props = defineProps({
  selectedPoint: {
    type: [String, Number],
    default: null
  },
  filename: {
    type: String,
    required: true
  }
})

// Image states
const measureProfileImageUrl = ref(null)
const isLoadingMeasureProfileImage = ref(false)
const alignImageUrl = ref(null)
const isLoadingAlignImage = ref(false)
const tipImageUrl = ref(null)
const isLoadingTipImage = ref(false)

// Load images function
function loadImages() {
  // Using placeholder images for development
  // These will be replaced with actual API calls when backend is ready
  
  // Measure Profile Analysis - Using a scientific chart placeholder
  measureProfileImageUrl.value = 'https://via.placeholder.com/600x450/4A90E2/FFFFFF?text=Measure+Profile+Analysis'
  
  // Align Image - Using an alignment grid placeholder
  alignImageUrl.value = 'https://via.placeholder.com/600x450/50C878/FFFFFF?text=Sample+Alignment'
  
  // Tip Image - Using a microscopy-style placeholder
  tipImageUrl.value = 'https://via.placeholder.com/600x450/FF6B6B/FFFFFF?text=Tip+Condition'
  
  console.log('🖼️ Dummy images set for development')
}

// Watch for point changes to potentially reload images
watch(() => props.selectedPoint, (newPoint) => {
  if (newPoint) {
    console.log('Selected point changed to:', newPoint)
    // In the future, reload images for the new point
    // For now, we're using static placeholders
  }
})

// Initialize images on mount
onMounted(() => {
  loadImages()
})
</script>

<style scoped>
/* Analysis image card styles */
.analysis-image-card {
  border: 1px solid rgba(var(--v-theme-outline), 0.12);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.analysis-image-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.analysis-image-card .v-card-title {
  border-bottom: 1px solid rgba(var(--v-theme-outline), 0.12);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 6px 10px;
}

.analysis-image-card .v-card-text {
  padding: 6px;
  height: calc(100% - 36px);
  overflow: hidden;
}

.analysis-image {
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease;
}

.analysis-image:hover {
  transform: scale(1.05);
  cursor: pointer;
}

.image-container {
  background: #f5f5f5;
  border-radius: 4px;
}
</style>