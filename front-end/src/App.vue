<template>
  <v-app>
    <v-app-bar color="primary" elevation="2">
      <v-app-bar-title>AFM Data Platform</v-app-bar-title>

      <v-spacer />

      <div class="d-flex gap-3 align-center justify-center">
        <v-fab
          v-model="selectedMode"
          color="secondary"
          size="default"
          value="R3"
          @click="selectMode('R3')"
        >
          R3
        </v-fab>
        <v-fab
          v-model="selectedMode"
          color="secondary"
          size="default"
          value="M14"
          @click="selectMode('M14')"
        >
          M14
        </v-fab>
        <v-fab
          v-model="selectedMode"
          color="secondary"
          size="default"
          value="M15"
          @click="selectMode('M15')"
        >
          M15
        </v-fab>
      </div>

      <v-spacer />

      <v-btn-toggle v-model="selectedTool" color="white" mandatory variant="outlined">
        <v-btn size="small" value="import">
          <v-icon>mdi-upload</v-icon>
          Import
        </v-btn>
        <v-btn size="small" value="analyze">
          <v-icon>mdi-chart-line</v-icon>
          Analyze
        </v-btn>
        <v-btn size="small" value="export">
          <v-icon>mdi-download</v-icon>
          Export
        </v-btn>
      </v-btn-toggle>
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
  import { ref } from 'vue'

  const selectedTool = ref('import')
  const selectedMode = ref('R3')

  function selectMode(mode) {
    selectedMode.value = mode
    console.log('Selected mode:', mode)
  }
</script>
