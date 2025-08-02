<template>
  <v-card elevation="3" min-height="600">
    <v-card-title class="py-2">
      <v-icon start size="small">mdi-image-multiple</v-icon>
      <span class="text-subtitle-1">Additional Images</span>
      <v-spacer />
    </v-card-title>
    <v-card-text class="pa-0">
      <v-tabs v-model="selectedTab" align-tabs="start" color="primary" show-arrows>
        <v-tab v-for="tab in imageTabs" :key="tab.value" :value="tab.value">
          <v-icon start size="small">{{ tab.icon }}</v-icon>
          {{ tab.title }}
          <v-chip v-if="getImagesForTab(tab.value).length > 0" size="x-small" class="ml-2" color="primary">
            {{ getImagesForTab(tab.value).length }}
          </v-chip>
        </v-tab>
      </v-tabs>

      <v-tabs-window v-model="selectedTab">
        <v-tabs-window-item v-for="tab in imageTabs" :key="tab.value" :value="tab.value">
          <v-container>
            <div v-if="isLoading" class="text-center pa-8">
              <v-progress-circular indeterminate color="primary" />
              <p class="mt-4">Loading {{ tab.title }} images...</p>
            </div>

            <div v-else-if="loadError" class="text-center pa-8">
              <v-icon size="64" color="error">mdi-alert-circle</v-icon>
              <p class="mt-4 text-h6">Error loading images</p>
              <p class="text-body-2 text-grey">{{ loadError }}</p>
              <v-btn @click="loadImages" variant="text" color="primary" class="mt-4">
                <v-icon start>mdi-refresh</v-icon>
                Retry
              </v-btn>
            </div>

            <div v-else-if="getImagesForTab(tab.value).length === 0" class="text-center pa-8">
              <v-icon size="64" color="grey-lighten-1">{{ tab.emptyIcon }}</v-icon>
              <p class="mt-4 text-h6 text-grey">No {{ tab.title }} images available</p>
              <p class="text-body-2 text-grey">{{ tab.description }}</p>
            </div>

            <v-row v-else>
              <v-col v-for="(image, index) in getImagesForTab(tab.value)" :key="index" 
                     cols="12" :md="getImagesForTab(tab.value).length === 1 ? 12 : 6" 
                     :lg="getImagesForTab(tab.value).length === 1 ? 12 : 4">
                <v-card class="image-card" @click="openImageDialog(image)">
                  <v-img 
                    :src="image.url" 
                    :alt="image.name"
                    height="300"
                    cover
                    class="image-hover"
                  >
                    <template v-slot:placeholder>
                      <v-row class="fill-height ma-0" align="center" justify="center">
                        <v-progress-circular indeterminate color="grey-lighten-5" />
                      </v-row>
                    </template>
                  </v-img>
                  <v-card-text class="pa-2">
                    <p class="text-caption text-center text-truncate">{{ image.name }}</p>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-container>
        </v-tabs-window-item>
      </v-tabs-window>
    </v-card-text>

    <!-- Image Dialog for Full View -->
    <v-dialog v-model="imageDialog" max-width="90%" max-height="90vh">
      <v-card>
        <v-card-title class="d-flex align-center">
          {{ selectedImage?.name }}
          <v-spacer />
          <v-btn icon variant="plain" @click="imageDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text class="pa-0">
          <v-img 
            v-if="selectedImage" 
            :src="selectedImage.url" 
            :alt="selectedImage.name"
            max-height="80vh"
            contain
          />
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useDataStore } from '@/stores/dataStore'
import { imageService } from '@/services/imageService'

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

// Store
const dataStore = useDataStore()

// State
const selectedTab = ref('profile')
const isLoading = ref(false)
const loadError = ref('')
const imageDialog = ref(false)
const selectedImage = ref(null)

// Images data structure
const imagesData = ref({
  profile: [],
  tiff: [],
  align: [],
  tip: []
})

// Tab configuration
const imageTabs = [
  {
    value: 'profile',
    title: 'Profile Analysis',
    icon: 'mdi-chart-line-variant',
    emptyIcon: 'mdi-chart-bell-curve-cumulative',
    description: 'AFM profile measurement data visualization'
  },
  {
    value: 'tiff',
    title: 'TIFF Images',
    icon: 'mdi-image',
    emptyIcon: 'mdi-image-off',
    description: 'Original TIFF format images from measurement'
  },
  {
    value: 'align',
    title: 'Sample Alignment',
    icon: 'mdi-align-horizontal-center',
    emptyIcon: 'mdi-crosshairs-gps',
    description: 'Sample alignment and positioning images'
  },
  {
    value: 'tip',
    title: 'Tip Condition',
    icon: 'mdi-needle',
    emptyIcon: 'mdi-circle-slice-8',
    description: 'AFM tip condition and quality images'
  }
]

// Computed
const getImagesForTab = computed(() => {
  return (tabValue) => imagesData.value[tabValue] || []
})

// Methods
async function loadImages() {
  isLoading.value = true
  loadError.value = ''
  
  try {
    const tool = dataStore.selectedTool
    const pointId = props.selectedPoint || 'default'
    
    // Fetch images for each directory type
    const imageTypes = ['profile', 'tiff', 'align', 'tip']
    const promises = imageTypes.map(async (type) => {
      try {
        const response = await imageService.getImagesByType(type, props.filename, pointId, tool)
        
        // Transform response data to include full URLs
        if (response.success && response.data && response.data.images) {
          imagesData.value[type] = response.data.images.map(img => ({
            name: img.name || img,
            url: imageService.getImageUrlByType(props.filename, pointId, type, img.name || img, tool)
          }))
        } else {
          imagesData.value[type] = []
        }
      } catch (error) {
        console.warn(`Failed to load ${type} images:`, error)
        imagesData.value[type] = []
      }
    })
    
    await Promise.all(promises)
    
  } catch (error) {
    console.error('Error loading images:', error)
    loadError.value = error.message || 'Failed to load images'
  } finally {
    isLoading.value = false
  }
}

function openImageDialog(image) {
  selectedImage.value = image
  imageDialog.value = true
}

// Watchers
watch(() => props.selectedPoint, (newPoint) => {
  if (newPoint !== undefined) {
    loadImages()
  }
})

watch(() => props.filename, (newFilename) => {
  if (newFilename) {
    loadImages()
  }
})

// Lifecycle
onMounted(() => {
  loadImages()
})
</script>

<style scoped>
.image-card {
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.image-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.image-hover {
  transition: transform 0.3s ease;
}

.image-card:hover .image-hover {
  transform: scale(1.05);
}

:deep(.v-tabs) {
  border-bottom: 1px solid rgba(var(--v-theme-outline), 0.12);
}

:deep(.v-tab) {
  text-transform: none;
  font-weight: 500;
}

:deep(.v-tabs-window) {
  min-height: 500px;
}
</style>