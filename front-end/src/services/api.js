/**
 * Main API Service
 * Central axios configuration
 */

import axios from "axios";

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Response interceptor to auto-extract data (keeps existing service compatibility)
api.interceptors.response.use(
  (response) => response.data,
  (error) => Promise.reject(error)
);

// Export base API instance for direct axios usage and for other services
export default api