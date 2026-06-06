import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  timeout: 120_000,
  headers: {
    'X-API-KEY': import.meta.env.VITE_API_KEY,
  },
})
