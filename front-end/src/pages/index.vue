<template>
  <v-container class="fill-height d-flex align-center justify-center">
    <v-row justify="center">
      <v-col cols="12" lg="6" md="8">
        <v-card class="pa-6" elevation="3">
          <v-card-title class="text-center mb-4">
            <h2>AFM Data Search</h2>
          </v-card-title>

          <v-card-text>
            <v-text-field
              v-model="searchQuery"
              clearable
              label="Search AFM data files..."
              placeholder="Enter filename, sample name, or keywords"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              @keyup.enter="performSearch"
            />

            <div class="d-flex gap-2 mt-4">
              <v-btn
                color="primary"
                :disabled="!searchQuery"
                size="large"
                @click="performSearch"
              >
                <v-icon left>mdi-magnify</v-icon>
                Search
              </v-btn>

              <v-btn
                size="large"
                variant="outlined"
                @click="advancedSearch = !advancedSearch"
              >
                <v-icon left>mdi-tune</v-icon>
                Advanced
              </v-btn>
            </div>

            <v-expand-transition>
              <v-card v-show="advancedSearch" class="mt-4" variant="outlined">
                <v-card-text>
                  <v-row>
                    <v-col cols="12" md="6">
                      <v-select
                        v-model="fileType"
                        density="compact"
                        :items="fileTypes"
                        label="File Type"
                        variant="outlined"
                      />
                    </v-col>
                    <v-col cols="12" md="6">
                      <v-text-field
                        v-model="dateRange"
                        density="compact"
                        label="Date Range"
                        placeholder="YYYY-MM-DD to YYYY-MM-DD"
                        variant="outlined"
                      />
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-expand-transition>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
  import { ref } from 'vue'

  const searchQuery = ref('')
  const advancedSearch = ref(false)
  const fileType = ref('')
  const dateRange = ref('')

  const fileTypes = [
    'All Types',
    '.afm',
    '.spm',
    '.nanoscope',
    '.jpk',
    '.gwyddion',
  ]

  function performSearch () {
    if (!searchQuery.value) return

    console.log('Searching for:', searchQuery.value)
    console.log('File type:', fileType.value)
    console.log('Date range:', dateRange.value)
  }
</script>
