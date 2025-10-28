<template>
  <div class="admin-services">
    <div class="container">
      <div class="header">
        <h1>Manage Services</h1>
        <button @click="showCreateModal = true" class="btn btn-primary">
          Add Service
        </button>
      </div>
      
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
      </div>
      
      <div v-else>
        <div v-if="services.length === 0" class="card">
          <p>No services found.</p>
        </div>
        
        <div v-for="service in services" :key="service.id" class="card">
          <div class="service-header">
            <h2>{{ service.name }}</h2>
            <div class="service-actions">
              <button @click="editService(service)" class="btn btn-secondary">
                Edit
              </button>
              <button @click="deleteService(service.id)" class="btn btn-danger">
                Delete
              </button>
            </div>
          </div>
          
          <div class="service-info">
            <p><strong>Price:</strong> {{ formatPrice(service.price) }}</p>
            <p><strong>Duration:</strong> {{ service.duration }} minutes</p>
            <p v-if="service.description"><strong>Description:</strong> {{ service.description }}</p>
            <p><strong>Status:</strong> {{ service.is_active ? 'Active' : 'Inactive' }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ showEditModal ? 'Edit Service' : 'Add Service' }}</h3>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>Service Name</label>
            <input v-model="form.name" type="text" required placeholder="e.g., Men's Haircut" />
          </div>
          
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="form.description" placeholder="Describe the service..."></textarea>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Duration (minutes)</label>
              <input v-model="form.duration" type="number" min="1" required />
            </div>
            
            <div class="form-group">
              <label>Price</label>
              <input v-model="form.price" type="number" step="0.01" min="0" required />
            </div>
          </div>
          
          <div class="form-group">
            <label>
              <input v-model="form.is_active" type="checkbox" />
              Active service
            </label>
          </div>
          
          <div v-if="error" class="message message-error">{{ error }}</div>
          
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Saving...' : (showEditModal ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const services = ref([])
const loading = ref(true)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingService = ref(null)
const error = ref('')

const form = ref({
  name: '',
  description: '',
  duration: 30,
  price: 0,
  is_active: true
})

const formatPrice = (price) => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(price)
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

const editService = (service) => {
  editingService.value = service
  form.value = {
    name: service.name,
    description: service.description || '',
    duration: service.duration,
    price: service.price,
    is_active: service.is_active
  }
  showEditModal.value = true
}

const deleteService = async (id) => {
  if (!confirm('Are you sure you want to delete this service?')) {
    return
  }
  
  try {
    await api.delete(`/services/${id}/`)
    await fetchServices()
  } catch (error) {
    alert('Error deleting service')
  }
}

const handleSubmit = async () => {
  error.value = ''
  loading.value = true
  
  try {
    if (showEditModal.value) {
      await api.put(`/services/${editingService.value.id}/`, form.value)
    } else {
      await api.post('/services/', form.value)
    }
    
    closeModal()
    await fetchServices()
  } catch (err) {
    console.error('Error saving service:', err)
    if (err.response?.data) {
      error.value = JSON.stringify(err.response.data)
    } else {
      error.value = 'Error saving service'
    }
  } finally {
    loading.value = false
  }
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  editingService.value = null
  error.value = ''
  form.value = {
    name: '',
    description: '',
    duration: 30,
    price: 0,
    is_active: true
  }
}

onMounted(() => {
  fetchServices()
})
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.service-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.service-actions {
  display: flex;
  gap: 0.5rem;
}

.service-info {
  margin-bottom: 1rem;
}

.service-info p {
  margin-bottom: 0.5rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .service-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .modal {
    padding: 1rem;
  }
}
</style>
