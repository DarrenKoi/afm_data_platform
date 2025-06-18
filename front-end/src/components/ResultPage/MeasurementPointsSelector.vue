<template>
  <v-card class="mb-4" v-if="measurementPoints.length > 0">
    <v-card-title>
      <v-icon start>mdi-target</v-icon>
      Measurement Points ({{ measurementPoints.length }})
    </v-card-title>
    <v-card-text>
      <div class="d-flex flex-wrap gap-2 mb-4">
        <v-btn
          v-for="point in measurementPoints"
          :key="point.point"
          :color="selectedPoint === point.point ? 'primary' : 'default'"
          :variant="selectedPoint === point.point ? 'flat' : 'outlined'"
          size="small"
          @click="selectPoint(point.point)"
        >
          Point {{ point.point }}
          <v-chip size="x-small" class="ml-2" :color="getParameterColor(point.parameter)">
            {{ point.parameter }}
          </v-chip>
        </v-btn>
      </div>
      
      <v-row v-if="selectedPointData">
        <v-col cols="12" md="6">
          <v-list density="compact">
            <v-list-item>
              <v-list-item-title>X Coordinate</v-list-item-title>
              <v-list-item-subtitle>{{ selectedPointData.x_axis }} µm</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Y Coordinate</v-list-item-title>
              <v-list-item-subtitle>{{ selectedPointData.y_axis }} µm</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-col>
        <v-col cols="12" md="6">
          <v-list density="compact">
            <v-list-item>
              <v-list-item-title>Parameter</v-list-item-title>
              <v-list-item-subtitle>{{ selectedPointData.parameter }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Value</v-list-item-title>
              <v-list-item-subtitle>{{ selectedPointData.value }} nm</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

// Props
const props = defineProps({
  measurementPoints: {
    type: Array,
    default: () => []
  },
  selectedPoint: {
    type: [Number, String],
    default: null
  }
})

// Emits
const emit = defineEmits(['point-selected'])

// Computed properties
const selectedPointData = computed(() => {
  return props.measurementPoints.find(p => p.point === props.selectedPoint)
})

// Functions
function getParameterColor(parameter) {
  const colors = {
    'RQ_value': 'blue',
    'RA_value': 'green', 
    'RMAX_value': 'orange'
  }
  return colors[parameter] || 'grey'
}

function selectPoint(pointNumber) {
  emit('point-selected', pointNumber)
}
</script>