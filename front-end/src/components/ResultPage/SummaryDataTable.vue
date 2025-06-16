<template>
  <v-card class="mb-4" v-if="summaryData.length > 0">
    <v-card-title>
      <v-icon start>mdi-table</v-icon>
      Summary Statistics
    </v-card-title>
    <v-card-text>
      <v-data-table
        :headers="headers"
        :items="summaryData"
        density="compact"
        hide-default-footer
        disable-pagination
      />
    </v-card-text>
  </v-card>
</template>

<script setup>
// Props
defineProps({
  summaryData: {
    type: Array,
    default: () => []
  }
})

// Data
const headers = [
  { title: 'Point', key: 'point' },
  { title: 'X Coordinate', key: 'no_x' },
  { title: 'Y Coordinate', key: 'no_y' },
  { title: 'ID', key: 'id' },
  { title: 'State', key: 'state' },
  { title: 'Left H', key: 'left_h' },
  { title: 'Right H', key: 'right_h' }
]
</script>