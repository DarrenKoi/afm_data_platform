<template>
  <v-card class="h-100" elevation="2">
    <v-card-title class="bg-primary text-white">
      <v-icon start>mdi-information</v-icon>
      Measurement Information
    </v-card-title>
    <v-card-text class="pa-6">
      <v-row>
        <v-col cols="12" md="4">
          <div class="info-item">
            <div class="info-label">Fab ID</div>
            <div class="info-value text-h6 text-primary">{{ measurementInfo.fab || 'N/A' }}</div>
          </div>
        </v-col>
        <v-col cols="12" md="4">
          <div class="info-item">
            <div class="info-label">Lot ID</div>
            <div class="info-value text-h6 text-success">{{ measurementInfo.lot_id || 'N/A' }}</div>
          </div>
        </v-col>
        <v-col cols="12" md="4">
          <div class="info-item">
            <div class="info-label">Workflow ID</div>
            <div class="info-value text-h6 text-info">{{ measurementInfo.wf_id || 'N/A' }}</div>
          </div>
        </v-col>
      </v-row>
      <v-row class="mt-2">
        <v-col cols="12" md="4">
          <div class="info-item">
            <div class="info-label">Recipe ID</div>
            <div class="info-value text-h6 text-warning">{{ measurementInfo.rcp_id || 'N/A' }}</div>
          </div>
        </v-col>
        <v-col cols="12" md="4">
          <div class="info-item">
            <div class="info-label">Event Time</div>
            <div class="info-value text-body-1 text-medium-emphasis">{{ formatEventTime(measurementInfo.event_time) }}</div>
          </div>
        </v-col>
        <v-col cols="12" md="4">
          <div class="info-item">
            <div class="info-label">Group Key</div>
            <div class="info-value text-body-2 text-medium-emphasis">{{ measurementInfo.group_key || 'N/A' }}</div>
          </div>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup>
// Props
defineProps({
  measurementInfo: {
    type: Object,
    default: () => ({})
  }
})

// Functions
function formatEventTime(eventTime) {
  if (!eventTime) return 'N/A'
  try {
    return new Date(eventTime).toLocaleString()
  } catch (error) {
    return 'Invalid Date'
  }
}
</script>

<style scoped>
.info-item {
  margin-bottom: 8px;
}

.info-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: rgba(var(--v-theme-on-surface), 0.8);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-weight: 600;
  word-break: break-word;
}
</style>