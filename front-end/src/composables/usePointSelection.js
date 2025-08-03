import { ref, watch } from 'vue'
import { useQueryClient } from '@tanstack/vue-query'

/**
 * Composable for handling point selection in ResultPage
 */
export function usePointSelection() {
  const selectedPoint = ref(null)
  const queryClient = useQueryClient()

  // Simple point selection function
  function selectPoint(pointNumber) {
    console.log(`📍 Selecting point: ${pointNumber}`)
    selectedPoint.value = pointNumber
  }

  // Handle point selection from MeasurementPoints component
  function handlePointSelected(pointData) {
    const { measurementPoint, pointNumber, filename: pointFilename, siteInfo } = pointData

    if (pointNumber && pointFilename) {
      console.log(`📍 Point selected:`, pointData)
      
      // Update selected point with site info for API calls
      selectedPoint.value = {
        value: pointNumber,
        measurementPoint,
        siteInfo,
        filename: pointFilename
      }
      
      // Prefetch profile data and image for better UX
      const cleanFilename = pointFilename.replace('.csv', '')
      
      // Extract tool name from URL or use default
      const toolName = new URLSearchParams(window.location.search).get('tool') || 'MAP608'
      
      // Prefetch profile data
      queryClient.prefetchQuery({
        queryKey: ['profile-data', cleanFilename, pointNumber, toolName, siteInfo],
        staleTime: 5 * 60 * 1000
      })
      
      // Prefetch profile image
      queryClient.prefetchQuery({
        queryKey: ['profile-image', cleanFilename, pointNumber, toolName, siteInfo],
        staleTime: 10 * 60 * 1000
      })
    }
  }

  // Handle wafer point selection from heatmap
  function handleWaferPointSelected(point) {
    console.log(`📍 Wafer point selected:`, point)
    
    if (point && point.point) {
      selectPoint(point.point)
    } else if (point && measurementPoints.value.length > 0) {
      const firstPoint = measurementPoints.value[0]
      selectPoint(firstPoint.point)
    }
  }


  // Handle point data loaded event (for compatibility)
  function handlePointDataLoaded(data) {
    console.log(`📊 Point data loaded:`, data)
    // Could be used to update UI state or trigger other actions
  }

  return {
    selectedPoint,
    selectPoint,
    handlePointSelected,
    handleWaferPointSelected,
    handlePointDataLoaded
  }
}