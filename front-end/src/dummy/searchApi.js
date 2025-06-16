import { searchMeasurementHistory } from './identifierData.js'

export function searchMeasurements(query) {
  return searchMeasurementHistory(query)
}

export async function searchMeasurementsAsync(query) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const results = searchMeasurementHistory(query)
      
      const groupedResults = results.reduce((acc, measurement) => {
        const existing = acc.find(item => item.group_key === measurement.group_key)
        if (existing) {
          existing.points.push({
            point: measurement.point,
            x_axis: measurement.x_axis,
            y_axis: measurement.y_axis,
            parameter: measurement.parameter,
            value: measurement.value
          })
          if (new Date(measurement.event_time) > new Date(existing.event_time)) {
            existing.event_time = measurement.event_time
          }
        } else {
          acc.push({
            fab: measurement.fab,
            lot_id: measurement.lot_id,
            wf_id: measurement.wf_id,
            lot_wf: measurement.lot_wf,
            group_key: measurement.group_key,
            rcp_id: measurement.rcp_id,
            event_time: measurement.event_time,
            points: [{
              point: measurement.point,
              x_axis: measurement.x_axis,
              y_axis: measurement.y_axis,
              parameter: measurement.parameter,
              value: measurement.value
            }]
          })
        }
        return acc
      }, [])
      
      resolve({
        success: true,
        data: groupedResults.sort((a, b) => new Date(b.event_time) - new Date(a.event_time)),
        total: groupedResults.length,
        query: query
      })
    }, Math.random() * 400 + 100)
  })
}