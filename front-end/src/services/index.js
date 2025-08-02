/**
 * Services Index
 * Central export point for all services
 */

// Export base API instance
export { default as api } from './api'

// Export specialized services
export { activityService } from './activityService'
export { afmService } from './afmService' 
export { imageService } from './imageService'

// Export data processing functions
export {
  filterMeasurementsLocally,
  searchMeasurementsAsync,
  fetchProfileData,
  fetchMeasurementData,
  fetchSummaryData,
  identifierData
} from './dataService'

// Combined API service object for backward compatibility
import { activityService } from './activityService'
import { afmService } from './afmService'
import { imageService } from './imageService'

export const apiService = {
  ...activityService,
  ...afmService,
  ...imageService
}