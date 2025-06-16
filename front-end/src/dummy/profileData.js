function generateProfile(surfaceWidth, surfaceHeight, baseZ) {
  const profile = []
  const targetPoints = 20000
  
  const pointsX = Math.ceil(Math.sqrt(targetPoints * (surfaceWidth / surfaceHeight)))
  const pointsY = Math.ceil(targetPoints / pointsX)
  
  const stepX = surfaceWidth / (pointsX - 1)
  const stepY = surfaceHeight / (pointsY - 1)
  
  for (let i = 0; i < pointsX; i++) {
    for (let j = 0; j < pointsY; j++) {
      const x = (i * stepX).toFixed(4)
      const y = (j * stepY).toFixed(4)
      
      const normalizedX = i / (pointsX - 1)
      const normalizedY = j / (pointsY - 1)
      
      const surfacePattern = Math.sin(normalizedX * Math.PI * 3) * Math.cos(normalizedY * Math.PI * 2) * 0.3
      const edgeEffect = (1 - Math.pow(normalizedX - 0.5, 2) * 4) * (1 - Math.pow(normalizedY - 0.5, 2) * 4) * 0.2
      const randomNoise = (Math.random() - 0.5) * 0.15
      const microStructure = Math.sin(normalizedX * Math.PI * 20) * Math.cos(normalizedY * Math.PI * 25) * 0.05
      
      const z = (baseZ + surfacePattern + edgeEffect + randomNoise + microStructure).toFixed(9)
      
      profile.push({
        x: parseFloat(x),
        y: parseFloat(y),
        z: parseFloat(z)
      })
    }
  }
  
  return profile
}

const profileCache = new Map()

export function getProfileData(groupKey, point) {
  const key = `${groupKey}_${point}`
  
  if (profileCache.has(key)) {
    return profileCache.get(key)
  }
  
  const surfaceConfigs = [
    { width: 55.0, height: 25.0 },
    { width: 40.0, height: 30.0 },
    { width: 60.0, height: 20.0 },
    { width: 50.0, height: 35.0 },
    { width: 45.0, height: 45.0 },
    { width: 70.0, height: 15.0 },
    { width: 35.0, height: 40.0 }
  ]
  
  const configIndex = Math.abs(groupKey.split('').reduce((a, b) => a + b.charCodeAt(0), 0) + point) % surfaceConfigs.length
  const config = surfaceConfigs[configIndex]
  
  const baseZ = (Math.random() * 0.5 + 0.1) * (Math.random() > 0.5 ? 1 : -1)
  
  const profile = generateProfile(config.width, config.height, baseZ)
  profileCache.set(key, profile)
  
  return profile
}

export async function fetchProfileData(groupKey, point) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const data = getProfileData(groupKey, point)
      const surfaceWidth = Math.max(...data.map(p => p.x))
      const surfaceHeight = Math.max(...data.map(p => p.y))
      
      resolve({
        success: data !== null,
        data: data,
        metadata: {
          groupKey,
          point,
          totalPoints: data ? data.length : 0,
          surfaceSize: {
            x: surfaceWidth,
            y: surfaceHeight
          },
          units: {
            x: "micrometers",
            y: "micrometers", 
            z: "nanometers"
          }
        }
      })
    }, Math.random() * 800 + 200)
  })
}