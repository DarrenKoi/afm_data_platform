<template>
  <v-card class="h-100" elevation="2">
    <v-card-title class="bg-success text-white">
      <v-icon start>mdi-chart-line</v-icon>
      Statistical Information
    </v-card-title>
    <v-card-text class="pa-6">
      <v-row>
        <v-col cols="12" sm="6" md="3">
          <div class="stat-card stat-primary">
            <div class="stat-icon">
              <v-icon>mdi-chart-line-variant</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">Average</div>
              <div class="stat-value">{{ statistics.mean?.toFixed(4) || 'N/A' }}</div>
              <div class="stat-unit">nm</div>
            </div>
          </div>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <div class="stat-card stat-warning">
            <div class="stat-icon">
              <v-icon>mdi-chart-bell-curve</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">Standard Deviation</div>
              <div class="stat-value">{{ statistics.std?.toFixed(4) || 'N/A' }}</div>
              <div class="stat-unit">nm</div>
            </div>
          </div>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <div class="stat-card stat-success">
            <div class="stat-icon">
              <v-icon>mdi-arrow-down-bold</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">Minimum</div>
              <div class="stat-value">{{ statistics.min?.toFixed(4) || 'N/A' }}</div>
              <div class="stat-unit">nm</div>
            </div>
          </div>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <div class="stat-card stat-error">
            <div class="stat-icon">
              <v-icon>mdi-arrow-up-bold</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">Maximum</div>
              <div class="stat-value">{{ statistics.max?.toFixed(4) || 'N/A' }}</div>
              <div class="stat-unit">nm</div>
            </div>
          </div>
        </v-col>
      </v-row>
      <v-row class="mt-4">
        <v-col cols="12" sm="6" md="3">
          <div class="stat-card stat-info">
            <div class="stat-icon">
              <v-icon>mdi-database</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">Data Points</div>
              <div class="stat-value">{{ statistics.count?.toLocaleString() || '0' }}</div>
              <div class="stat-unit">points</div>
            </div>
          </div>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <div class="stat-card stat-secondary">
            <div class="stat-icon">
              <v-icon>mdi-arrow-expand-horizontal</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">Range</div>
              <div class="stat-value">{{ statistics.range?.toFixed(4) || 'N/A' }}</div>
              <div class="stat-unit">nm</div>
            </div>
          </div>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <div class="stat-card stat-secondary">
            <div class="stat-icon">
              <v-icon>mdi-chart-median</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">Median</div>
              <div class="stat-value">{{ statistics.median?.toFixed(4) || 'N/A' }}</div>
              <div class="stat-unit">nm</div>
            </div>
          </div>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <div class="stat-card stat-secondary">
            <div class="stat-icon">
              <v-icon>mdi-chart-areaspline</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">RMS</div>
              <div class="stat-value">{{ statistics.rms?.toFixed(4) || 'N/A' }}</div>
              <div class="stat-unit">nm</div>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed, watch } from 'vue'

const props = defineProps({
  profileData: {
    type: Array,
    default: () => []
  }
})

// Debug: Watch for profileData changes
watch(() => props.profileData, (newData) => {
  console.log('StatisticalInfo received profileData:', newData?.length || 0, 'points')
}, { immediate: true })

const statistics = computed(() => {
  if (!props.profileData || props.profileData.length === 0) {
    return {
      mean: null,
      std: null,
      min: null,
      max: null,
      count: 0,
      range: null,
      median: null,
      rms: null
    }
  }

  const zValues = props.profileData.map(point => point.z)
  const count = zValues.length
  
  // Calculate basic statistics
  const min = Math.min(...zValues)
  const max = Math.max(...zValues)
  const range = max - min
  
  // Calculate mean
  const mean = zValues.reduce((sum, val) => sum + val, 0) / count
  
  // Calculate standard deviation
  const variance = zValues.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / count
  const std = Math.sqrt(variance)
  
  // Calculate median
  const sortedValues = [...zValues].sort((a, b) => a - b)
  const median = count % 2 === 0 
    ? (sortedValues[count / 2 - 1] + sortedValues[count / 2]) / 2
    : sortedValues[Math.floor(count / 2)]
  
  // Calculate RMS (Root Mean Square)
  const rms = Math.sqrt(zValues.reduce((sum, val) => sum + val * val, 0) / count)
  
  return {
    mean,
    std,
    min,
    max,
    count,
    range,
    median,
    rms
  }
})
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
  padding: 16px;
  border-radius: 12px;
  background: rgba(var(--v-theme-surface), 1);
  border: 2px solid transparent;
  transition: all 0.3s ease;
  min-height: 80px;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-primary {
  border-color: rgb(var(--v-theme-primary));
  background: rgba(var(--v-theme-primary), 0.05);
}

.stat-warning {
  border-color: rgb(var(--v-theme-warning));
  background: rgba(var(--v-theme-warning), 0.05);
}

.stat-success {
  border-color: rgb(var(--v-theme-success));
  background: rgba(var(--v-theme-success), 0.05);
}

.stat-error {
  border-color: rgb(var(--v-theme-error));
  background: rgba(var(--v-theme-error), 0.05);
}

.stat-info {
  border-color: rgb(var(--v-theme-info));
  background: rgba(var(--v-theme-info), 0.05);
}

.stat-secondary {
  border-color: rgb(var(--v-theme-secondary));
  background: rgba(var(--v-theme-secondary), 0.05);
}

.stat-icon {
  margin-right: 12px;
  opacity: 0.8;
}

.stat-icon .v-icon {
  font-size: 24px;
}

.stat-primary .stat-icon .v-icon {
  color: rgb(var(--v-theme-primary));
}

.stat-warning .stat-icon .v-icon {
  color: rgb(var(--v-theme-warning));
}

.stat-success .stat-icon .v-icon {
  color: rgb(var(--v-theme-success));
}

.stat-error .stat-icon .v-icon {
  color: rgb(var(--v-theme-error));
}

.stat-info .stat-icon .v-icon {
  color: rgb(var(--v-theme-info));
}

.stat-secondary .stat-icon .v-icon {
  color: rgb(var(--v-theme-secondary));
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: rgba(var(--v-theme-on-surface), 0.7);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: rgba(var(--v-theme-on-surface), 0.9);
  line-height: 1.2;
}

.stat-unit {
  font-size: 0.75rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
  font-weight: 500;
  margin-top: 2px;
}
</style>