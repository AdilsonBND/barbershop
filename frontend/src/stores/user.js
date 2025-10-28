import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const isAuthenticated = ref(false)
  
  // Load user from localStorage on init
  const userFromStorage = localStorage.getItem('user')
  if (userFromStorage) {
    try {
      user.value = JSON.parse(userFromStorage)
      isAuthenticated.value = !!token.value
    } catch (e) {
      console.error('Error loading user from storage:', e)
    }
  }
  
  const login = async (username, password) => {
    try {
      const response = await api.post('/login/', {
        username,
        password
      })
      
      token.value = response.data.token
      user.value = response.data.user
      isAuthenticated.value = true
      
      localStorage.setItem('token', token.value)
      localStorage.setItem('user', JSON.stringify(user.value))
      
      api.defaults.headers.common['Authorization'] = `Token ${token.value}`
      
      return response.data
    } catch (error) {
      console.error('Login error:', error)
      
      // Handle different types of errors
      if (error.response?.status === 401) {
        throw {
          message: 'Invalid credentials. Check your username and password.',
          type: 'auth'
        }
      } else if (error.response?.status === 400) {
        const errors = error.response.data
        
        // If the backend returned a simple error with the 'error' property
        if ('error' in errors && typeof errors.error === 'string') {
          throw {
            message: errors.error,
            type: 'validation',
            details: errors
          }
        }
        
        let errorMessages = []
        
        for (const [field, messages] of Object.entries(errors)) {
          if (Array.isArray(messages)) {
            errorMessages.push(`${field}: ${messages.join(', ')}`)
          } else if (typeof messages === 'string') {
            errorMessages.push(`${field}: ${messages}`)
          }
        }
        
        throw {
          message: errorMessages.join('\n'),
          type: 'validation',
          details: errors
        }
      } else if (error.response?.status >= 500) {
        throw {
          message: 'Server error. Please try again later.',
          type: 'server'
        }
      } else if (error.message === 'Network Error' || !error.response) {
        throw {
          message: 'Unable to connect to server. Check if backend is running.',
          type: 'network'
        }
      } else {
        throw {
          message: error.response?.data?.non_field_errors || 
                   error.response?.data || 
                   error.message || 
                   'Unknown error logging in',
          type: 'unknown'
        }
      }
    }
  }
  
  const register = async (userData) => {
    try {
      const response = await api.post('/register/', userData)
      
      token.value = response.data.token
      user.value = response.data.user
      isAuthenticated.value = true
      
      // Mark as new barber registration if user type is barber
      if (userData.user_type === 'barber') {
        sessionStorage.setItem('new_barber_registration', 'true')
      }
      
      localStorage.setItem('token', token.value)
      localStorage.setItem('user', JSON.stringify(user.value))
      
      api.defaults.headers.common['Authorization'] = `Token ${token.value}`
      
      return response.data
    } catch (error) {
      console.error('Registration error:', error)
      
      // Handle different types of errors
      if (error.response?.status === 401) {
        throw {
          message: 'Unauthorized. Check your credentials or if the server is running.',
          type: 'auth'
        }
      } else if (error.response?.status === 400) {
        // Parse validation errors from Django
        const errors = error.response.data
        let errorMessages = []
        
        for (const [field, messages] of Object.entries(errors)) {
          if (Array.isArray(messages)) {
            errorMessages.push(`${field}: ${messages.join(', ')}`)
          } else if (typeof messages === 'string') {
            errorMessages.push(`${field}: ${messages}`)
          } else {
            errorMessages.push(`${field}: ${JSON.stringify(messages)}`)
          }
        }
        
        throw {
          message: errorMessages.join('\n'),
          type: 'validation',
          details: errors
        }
      } else if (error.response?.status >= 500) {
        throw {
          message: 'Server error. Please try again later.',
          type: 'server'
        }
      } else if (error.message === 'Network Error' || !error.response) {
        throw {
          message: 'Unable to connect to server. Check if backend is running.',
          type: 'network'
        }
      } else {
        throw {
          message: error.response?.data || error.message || 'Unknown error registering',
          type: 'unknown'
        }
      }
    }
  }
  
  const logout = async () => {
    try {
      await api.post('/logout/')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      token.value = null
      user.value = null
      isAuthenticated.value = false
      
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      delete api.defaults.headers.common['Authorization']
    }
  }
  
  const updateUser = async (userData) => {
    try {
      const response = await api.patch(`/users/me/`, userData)
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(user.value))
      return response.data
    } catch (error) {
      throw error.response?.data || error.message
    }
  }
  
  return {
    user,
    token,
    isAuthenticated,
    login,
    register,
    logout,
    updateUser
  }
})

