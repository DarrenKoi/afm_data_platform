<template>
  <div>
    <div v-if="isLoading" class="text-center pa-4">
      <v-progress-circular indeterminate color="primary" size="small" />
      <p class="mt-2 text-caption">Loading...</p>
    </div>
    <div v-else-if="profileData.length > 0">
      <ScatterChart 
        v-if="chartType === 'scatter'"
        :profile-data="profileData"
        :selected-point="selectedPoint"
        :chart-height="chartHeight"
        :compact="compact"
      />
      <HeatmapChart 
        v-else-if="chartType === 'heatmap'"
        :profile-data="profileData"
        :selected-point="selectedPoint"
        :chart-height="chartHeight"
        :compact="compact"
      />
      <HistogramChart 
        v-else-if="chartType === 'histogram'"
        :profile-data="profileData"
        :selected-point="selectedPoint"
        :chart-height="chartHeight"
        :compact="compact"
      />
      <div v-if="!compact" class="mt-2">
        <v-row dense>
          <v-col cols="12" md="4">
            <v-card variant="outlined" class="pa-2">
              <div class="text-caption text-medium-emphasis">Data Points</div>
              <div class="text-subtitle-2">{{ profileData.length.toLocaleString() }}</div>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card variant="outlined" class="pa-2">
              <div class="text-caption text-medium-emphasis">Surface Size</div>
              <div class="text-subtitle-2">{{ surfaceSize.x }} × {{ surfaceSize.y }} µm</div>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card variant="outlined" class="pa-2">
              <div class="text-caption text-medium-emphasis">Z Range</div>
              <div class="text-subtitle-2">{{ zRange.min.toFixed(3) }} to {{ zRange.max.toFixed(3) }} nm</div>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </div>
    <div v-else class="text-center pa-4">
      <v-icon size="32" color="grey">mdi-chart-scatter-plot</v-icon>
      <p class="text-body-2 mt-2 text-medium-emphasis">No data available</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import ScatterChart from './charts/ScatterChart.vue'
import HeatmapChart from './charts/HeatmapChart.vue'
import HistogramChart from './charts/HistogramChart.vue'

const props = defineProps({
  selectedPoint: {
    type: [Number, String],
    default: null
  },
  profileData: {
    type: Array,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  chartHeight: {
    type: Number,
    default: 500
  },
  compact: {
    type: Boolean,
    default: false
  },
  chartType: {
    type: String,
    default: 'scatter'
  }
})

const surfaceSize = computed(() => {
  if (props.profileData.length === 0) return { x: 0, y: 0 }
  const maxX = Math.max(...props.profileData.map(p => p.x))
  const maxY = Math.max(...props.profileData.map(p => p.y))
  return { x: maxX.toFixed(1), y: maxY.toFixed(1) }
})

const zRange = computed(() => {
  if (props.profileData.length === 0) return { min: 0, max: 0 }
  const zValues = props.profileData.map(p => p.z)
  return {
    min: Math.min(...zValues),
    max: Math.max(...zValues)
  }
})

</script>