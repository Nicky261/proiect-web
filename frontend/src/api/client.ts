import axios from 'axios'

// const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost/api'
const baseURL = 'http://localhost:8000'  // Direct, fără variabile de mediu

export const api = axios.create({ baseURL })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
