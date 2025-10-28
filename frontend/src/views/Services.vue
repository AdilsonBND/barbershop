<template>
  <div class="services">
    <div class="container">
      <h1>Services</h1>
      
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
      </div>
      
      <div v-else>
        <div v-if="services.length === 0" class="card">
          <p>No services available.</p>
        </div>
        
        <div v-for="service in services" :key="service.id" class="card">
          <div class="service-header">
            <h2>{{ service.name }}</h2>
            <span class="price">{{ formatPrice(service.price) }}</span>
          </div>
          
          <div class="service-info">
            <p><strong>Duration:</strong> {{ service.duration }} minutes</p>
            <p v-if="service.description"><strong>Description:</strong> {{ service.description }}</p>
          </div>
          
          <div class="service-actions">
            <router-link to="/appointments/new" class="btn btn-primary">
              Book This Service
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const services = ref([])
const loading = ref(true)

const formatPrice = (price) => {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(price)
}

const fetchServices = async () => {
  try {
    const response = await api.get('/services/')
    services.value = response.data.results || response.data
  } catch (error) {
    console.error('Error fetching services:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchServices()
})
</script>

<style scoped>
.service-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.price {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2563eb;
}

.service-info {
  margin-bottom: 1rem;
}

.service-actions {
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .service-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>

