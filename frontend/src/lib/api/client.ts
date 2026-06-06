import axios from 'axios'

const getApiKey = () => {
  if (typeof window !== 'undefined' && (window as any).API_KEY) {
    return (window as any).API_KEY
  }
  return import.meta.env.VITE_API_KEY
}

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  timeout: 120_000,
  headers: {
    'X-API-KEY': getApiKey(),
  },
})
