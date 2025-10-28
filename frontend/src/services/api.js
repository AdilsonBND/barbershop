import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add token to each request dynamically
api.interceptors.request.use(
  (config) => {
    // List of endpoints that don't require authentication
    const publicEndpoints = ['/login/', '/register/']
    const isPublicEndpoint = publicEndpoints.some(endpoint => 
      config.url.endsWith(endpoint)
    )
    
    // Only add token if it's not a public endpoint
    if (!isPublicEndpoint) {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Token ${token}`
      } else {
        // Remove Authorization header if no token
        delete config.headers.Authorization
      }
    } else {
      // Explicitly remove Authorization header for public endpoints
      delete config.headers.Authorization
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

export default api

