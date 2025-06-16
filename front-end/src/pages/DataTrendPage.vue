<template>
  <v-container class="pa-6">
    <v-row>
      <v-col cols="12">
        <!-- Header with back button -->
        <div class="d-flex align-center mb-4">
          <v-btn variant="outlined" @click="goBack" class="mr-4">
            <v-icon left>mdi-arrow-left</v-icon>
            Back to Search
          </v-btn>
          
          <div>
            <h1 class="text-h4">AFM Data Trend Analysis</h1>
            <p class="text-subtitle-1 text-medium-emphasis">
              Comparing {{ dataStore.groupedCount }} measurements
            </p>
          </div>
        </div>

        <!-- Grouped Data Overview -->
        <v-card class="mb-4" elevation="3">
          <v-card-title>
            <v-icon left>mdi-group</v-icon>
            Selected Measurements
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col 
                v-for="(item, index) in dataStore.groupedData" 
                :key="index"
                cols="12" sm="6" md="4"
              >
                <v-card variant="outlined" class="pa-3">
                  <v-card-title class="text-body-1 pb-2">
                    {{ item.fab }} - {{ item.lot_id }}
                  </v-card-title>
                  <v-card-subtitle class="text-caption">
                    <v-chip size="x-small" color="primary" class="mr-1">WF: {{ item.wf_id }}</v-chip>
                    <v-chip size="x-small" color="secondary">{{ item.rcp_id }}</v-chip>
                  </v-card-subtitle>
                  <v-card-text class="text-caption pt-2">
                    {{ new Date(item.event_time).toLocaleDateString() }}
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Trend Analysis Tabs -->
        <v-card elevation="3">
          <v-tabs v-model="activeTab" bg-color="primary">
            <v-tab value="time-series">
              <v-icon left>mdi-chart-timeline</v-icon>
              Time Series
            </v-tab>
            <v-tab value="comparison">
              <v-icon left>mdi-chart-bar</v-icon>
              Parameter Comparison
            </v-tab>
            <v-tab value="correlation">
              <v-icon left>mdi-scatter-plot</v-icon>
              Correlation Analysis
            </v-tab>
          </v-tabs>

          <v-window v-model="activeTab">
            <!-- Time Series Tab -->
            <v-window-item value="time-series">
              <v-card-text>
                <div class="text-center pa-8">
                  <v-icon size="64" color="primary">mdi-chart-timeline</v-icon>
                  <h3 class="text-h6 mt-4">Time Series Analysis</h3>
                  <p class="text-body-2 text-medium-emphasis mt-2">
                    Track measurement trends over time across different fabs and lots
                  </p>
                  <v-divider class="my-4" />
                  <div class="text-left">
                    <h4 class="text-subtitle-1 mb-2">Features to be implemented:</h4>
                    <ul class="text-body-2 text-medium-emphasis">
                      <li>Multi-line chart showing parameter values over time</li>
                      <li>Interactive tooltips with measurement details</li>
                      <li>Zoom and pan functionality</li>
                      <li>Export to CSV/PNG options</li>
                    </ul>
                  </div>
                </div>
              </v-card-text>
            </v-window-item>

            <!-- Parameter Comparison Tab -->
            <v-window-item value="comparison">
              <v-card-text>
                <div class="text-center pa-8">
                  <v-icon size="64" color="success">mdi-chart-bar</v-icon>
                  <h3 class="text-h6 mt-4">Parameter Comparison</h3>
                  <p class="text-body-2 text-medium-emphasis mt-2">
                    Compare roughness parameters (RQ, RA, RMAX) across selected measurements
                  </p>
                  <v-divider class="my-4" />
                  <div class="text-left">
                    <h4 class="text-subtitle-1 mb-2">Features to be implemented:</h4>
                    <ul class="text-body-2 text-medium-emphasis">
                      <li>Side-by-side bar charts for each parameter</li>
                      <li>Statistical summary (mean, std, min, max)</li>
                      <li>Outlier detection and highlighting</li>
                      <li>Fab/Recipe grouping options</li>
                    </ul>
                  </div>
                </div>
              </v-card-text>
            </v-window-item>

            <!-- Correlation Analysis Tab -->
            <v-window-item value="correlation">
              <v-card-text>
                <div class="text-center pa-8">
                  <v-icon size="64" color="warning">mdi-scatter-plot</v-icon>
                  <h3 class="text-h6 mt-4">Correlation Analysis</h3>
                  <p class="text-body-2 text-medium-emphasis mt-2">
                    Analyze relationships between different measurement parameters
                  </p>
                  <v-divider class="my-4" />
                  <div class="text-left">
                    <h4 class="text-subtitle-1 mb-2">Features to be implemented:</h4>
                    <ul class="text-body-2 text-medium-emphasis">
                      <li>Scatter plots with correlation coefficients</li>
                      <li>Heatmap of parameter correlations</li>
                      <li>Regression line fitting</li>
                      <li>Statistical significance testing</li>
                    </ul>
                  </div>
                </div>
              </v-card-text>
            </v-window-item>
          </v-window>
        </v-card>

        <!-- Action Buttons -->
        <div class="d-flex justify-end mt-4">
          <v-btn variant="outlined" class="mr-2" @click="exportData">
            <v-icon left>mdi-download</v-icon>
            Export Data
          </v-btn>
          <v-btn color="primary" @click="generateReport">
            <v-icon left>mdi-file-document</v-icon>
            Generate Report
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useDataStore } from '@/stores/dataStore.js'

const router = useRouter()
const dataStore = useDataStore()
const activeTab = ref('time-series')

function goBack() {
  router.push('/')
}

function exportData() {
  console.log('Exporting grouped data:', dataStore.groupedData)
  // Future implementation: export to CSV/Excel
}

function generateReport() {
  console.log('Generating report for grouped data:', dataStore.groupedData)
  // Future implementation: generate PDF report
}
</script>