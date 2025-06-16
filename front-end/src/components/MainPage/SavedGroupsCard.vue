<template>
  <v-card elevation="3">
    <v-card-title>
      <v-icon start>mdi-folder-multiple</v-icon>
      Saved Groups ({{ groupHistoryCount }})
      <v-spacer />
      <v-btn v-if="groupHistoryCount > 0" variant="text" size="small" @click="clearGroupHistory">
        Clear All
      </v-btn>
    </v-card-title>
    <v-divider />
    
    <v-list v-if="groupHistoryCount > 0" density="compact">
      <v-list-item v-for="(group, index) in groupHistory" :key="index" @click="loadSavedGroup(group.id)" class="cursor-pointer">
        <v-list-item-title class="text-body-2">{{ group.name }}</v-list-item-title>
        <v-list-item-subtitle class="text-caption">
          <div v-if="group.description" class="mb-1 text-medium-emphasis">{{ group.description }}</div>
          {{ group.itemCount }} items • {{ new Date(group.createdAt).toLocaleDateString() }}
        </v-list-item-subtitle>
        
        <template v-slot:append>
          <v-btn variant="text" size="small" @click.stop="removeFromGroupHistory(group.id)">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </template>
      </v-list-item>
    </v-list>
    
    <v-card-text v-else class="text-center text-medium-emphasis">
      No saved groups yet
    </v-card-text>
  </v-card>
</template>

<script setup>
// Props
defineProps({
  groupHistory: {
    type: Array,
    default: () => []
  },
  groupHistoryCount: {
    type: Number,
    default: 0
  }
})

// Emits
const emit = defineEmits(['load-saved-group', 'remove-from-group-history', 'clear-group-history'])

// Functions
function loadSavedGroup(groupId) {
  emit('load-saved-group', groupId)
}

function removeFromGroupHistory(groupId) {
  emit('remove-from-group-history', groupId)
}

function clearGroupHistory() {
  emit('clear-group-history')
}
</script>