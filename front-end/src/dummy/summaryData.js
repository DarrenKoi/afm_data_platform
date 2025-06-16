function generateSummaryData(groupKey, point) {
  const seed = groupKey.split('').reduce((a, b) => a + b.charCodeAt(0), 0) + point
  const random = (multiplier = 1) => {
    const x = Math.sin(seed * multiplier) * 10000
    return Math.abs(x - Math.floor(x))
  }
  
  const baseX = random(1) * 10000 + 1000
  const baseY = random(2) * 100000 - 50000
  
  return {
    point: point,
    no_x: baseX.toFixed(2),
    no_y: baseY.toFixed(2),
    id: point,
    state: random(3) > 0.1 ? "TRUE" : "FALSE",
    left_h: (random(4) * 5 + 2).toFixed(3),
    right_h: (random(5) * 5 + 2).toFixed(3)
  }
}

const summaryCache = new Map()

export function getSummaryData(groupKey) {
  if (summaryCache.has(groupKey)) {
    return summaryCache.get(groupKey)
  }
  
  const maxPoints = Math.floor(Math.random() * 8) + 3
  const summaryData = []
  
  for (let point = 1; point <= maxPoints; point++) {
    summaryData.push(generateSummaryData(groupKey, point))
  }
  
  summaryCache.set(groupKey, summaryData)
  return summaryData
}

export async function fetchSummaryData(groupKey) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const data = getSummaryData(groupKey)
      resolve({
        success: true,
        data: data,
        metadata: {
          groupKey,
          totalPoints: data.length,
          columns: ["Point", "No X", "No Y", "ID", "State", "Left_H", "Right_H"]
        }
      })
    }, Math.random() * 600 + 100)
  })
}