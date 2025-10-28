<template>
  <div class="barbers">
    <div class="container">
      <h1>Barbers</h1>
      
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
      </div>
      
      <div v-else>
        <div v-if="barbers.length === 0" class="card">
          <p>No barbers registered.</p>
        </div>
        
        <div v-for="barber in barbers" :key="barber.id" class="card">
          <div class="barber-header">
            <h2>{{ barber.user?.first_name }} {{ barber.user?.last_name }}</h2>
            <span :class="`badge ${barber.is_available ? 'badge-success' : 'badge-danger'}`">
              {{ barber.is_available ? 'Available' : 'Unavailable' }}
            </span>
          </div>
          
          <div v-if="barber.specialization" class="barber-info">
            <p><strong>Specialization:</strong> {{ barber.specialization }}</p>
          </div>
          
          <div v-if="barber.bio" class="barber-info">
            <p><strong>Bio:</strong> {{ barber.bio }}</p>
          </div>
          
          <div class="barber-actions">
            <router-link :to="`/appointments/new?barber=${barber.user?.id}`" class="btn btn-primary">
              Book
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

const barbers = ref([])
const loading = ref(true)

const fetchBarbers = async () => {
  try {
    const response = await api.get('/barbers/')
    barbers.value = response.data.results || response.data
  } catch (error) {
    console.error('Error fetching barbers:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchBarbers()
})
</script>

<style scoped>
.barber-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.barber-info {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background-color: #f9fafb;
  border-radius: 4px;
}

.barber-actions {
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .barber-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>

