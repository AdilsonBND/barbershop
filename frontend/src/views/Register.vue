<template>
  <div class="register-container">
    <div class="form">
      <h2>Registration</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-grid">
          <div class="form-group">
            <label>Username</label>
            <input v-model="form.username" type="text" required />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="form.email" type="email" required />
          </div>
          <div class="form-group">
            <label>First Name</label>
            <input v-model="form.first_name" type="text" required />
          </div>
          <div class="form-group">
            <label>Last Name</label>
            <input v-model="form.last_name" type="text" required />
          </div>
          <div class="form-group">
            <label>Phone</label>
            <input v-model="form.phone" type="tel" />
          </div>
          <div class="form-group">
            <label>User Type</label>
            <select v-model="form.user_type" required>
              <option value="client">Client</option>
              <option value="barber">Barber</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>Password</label>
          <input v-model="form.password" type="password" required />
        </div>
        <div class="form-group">
          <label>Confirm Password</label>
          <input v-model="form.password2" type="password" required />
        </div>
        <div v-if="error" class="message message-error">{{ error }}</div>
        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? 'Registering...' : 'Register' }}
        </button>
      </form>
      <p class="login-link">
        Already have an account? <router-link to="/login">Login</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const form = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  user_type: 'client',
  password: '',
  password2: ''
})

const error = ref('')
const loading = ref(false)

const handleRegister = async () => {
  error.value = ''
  
  // Local validation
  if (form.value.password !== form.value.password2) {
    error.value = 'Passwords do not match'
    return
  }
  
  if (form.value.password.length < 3) {
    error.value = 'Password must be at least 3 characters long'
    return
  }
  
  loading.value = true
  
  try {
    await userStore.register(form.value)
    router.push('/dashboard')
  } catch (err) {
    console.error('Registration error:', err)
    
    // Handle structured Django errors
    if (typeof err === 'object' && err !== null) {
      // Create a friendly message based on errors
      const errorMessages = []
      
      if ('username' in err) {
        const msg = Array.isArray(err.username) ? err.username.join(', ') : err.username
        errorMessages.push(`Username: ${msg}`)
      }
      if ('email' in err) {
        const msg = Array.isArray(err.email) ? err.email.join(', ') : err.email
        errorMessages.push(`Email: ${msg}`)
      }
      if ('password' in err) {
        const msg = Array.isArray(err.password) ? err.password.join(', ') : err.password
        errorMessages.push(`Password: ${msg}`)
      }
      if ('phone' in err) {
        const msg = Array.isArray(err.phone) ? err.phone.join(', ') : err.phone
        errorMessages.push(`Phone: ${msg}`)
      }
      if ('non_field_errors' in err) {
        const msg = Array.isArray(err.non_field_errors) ? err.non_field_errors.join(', ') : err.non_field_errors
        errorMessages.push(msg)
      }
      
      // If no specific errors found, use generic message
      if (errorMessages.length === 0) {
        if ('detail' in err) {
          error.value = typeof err.detail === 'string' ? err.detail : 'Error registering.'
        } else if ('message' in err) {
          error.value = err.message
        } else {
          error.value = 'Error registering. Please check your data and try again.'
        }
      } else {
        error.value = errorMessages.join(' ')
      }
    } else if (typeof err === 'string') {
      error.value = err
    } else {
      error.value = 'Unknown error registering.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.form {
  max-width: 800px;
  width: 100%;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.login-link {
  margin-top: 1rem;
  text-align: center;
  color: #6b7280;
}

.login-link a {
  color: #2563eb;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>

