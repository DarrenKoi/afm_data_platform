function generateMeasurementData() {
  const fabs = ["R3", "M14", "M16"]
  const lotPrefixes = ["T7HQK", "COM6", "XP9KL", "BW8HN", "QT5RL", "LM4TX", "NP6ZY", "RK3MQ", "ST8VP", "DH2WX"]
  const recipes = [
    "BSOXCMP_DISHING_9PT", 
    "METAL_PLANAR_12PT", 
    "OXIDE_CMP_FINAL_6PT", 
    "POLY_PLANAR_15PT", 
    "TUNGSTEN_CMP_8PT",
    "NITRIDE_ETCH_16PT",
    "COPPER_CMP_20PT"
  ]
  const parameters = ["RQ_value", "RA_value", "RMAX_value"]
  
  const measurements = []
  
  for (let i = 0; i < 50; i++) {
    const fab = fabs[Math.floor(Math.random() * fabs.length)]
    const lotPrefix = lotPrefixes[Math.floor(Math.random() * lotPrefixes.length)]
    const lotSuffix = Math.random().toString(36).substring(2, 6).toUpperCase()
    const lot_id = lotPrefix + lotSuffix
    const wf_id = Math.floor(Math.random() * 25) + 1
    const lot_wf = `${lot_id}_${wf_id}`
    const group_key = `${fab}_${lot_id}_${wf_id}`
    const rcp_id = recipes[Math.floor(Math.random() * recipes.length)]
    
    const numPoints = Math.floor(Math.random() * 5) + 1
    
    for (let point = 1; point <= numPoints; point++) {
      const parameter = parameters[Math.floor(Math.random() * parameters.length)]
      let value
      switch (parameter) {
        case "RQ_value":
          value = (Math.random() * 0.5 + 0.1).toFixed(3)
          break
        case "RA_value":
          value = (Math.random() * 0.4 + 0.05).toFixed(3)
          break
        case "RMAX_value":
          value = (Math.random() * 3 + 0.5).toFixed(3)
          break
      }
      
      const daysAgo = Math.floor(Math.random() * 30)
      const hoursAgo = Math.floor(Math.random() * 24)
      const minutesAgo = Math.floor(Math.random() * 60)
      const now = new Date()
      const event_time = new Date(now.getTime() - (daysAgo * 24 * 60 * 60 * 1000) - (hoursAgo * 60 * 60 * 1000) - (minutesAgo * 60 * 1000)).toISOString()
      
      measurements.push({
        fab,
        lot_id,
        wf_id,
        lot_wf,
        group_key,
        point,
        x_axis: (Math.random() * 50 + 5).toFixed(2),
        y_axis: (Math.random() * 50 + 5).toFixed(2),
        parameter,
        value: parseFloat(value),
        event_time,
        rcp_id
      })
    }
  }
  
  return measurements.sort((a, b) => new Date(b.event_time) - new Date(a.event_time))
}

export const identifierData = generateMeasurementData()

export function searchMeasurementHistory(query) {
  if (!query) return identifierData.slice(0, 20)
  
  const lowerQuery = query.toLowerCase()
  return identifierData.filter(item => 
    item.fab.toLowerCase().includes(lowerQuery) ||
    item.lot_id.toLowerCase().includes(lowerQuery) ||
    item.group_key.toLowerCase().includes(lowerQuery) ||
    item.rcp_id.toLowerCase().includes(lowerQuery) ||
    item.parameter.toLowerCase().includes(lowerQuery)
  ).slice(0, 20)
}