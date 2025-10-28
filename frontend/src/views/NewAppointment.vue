<template>
  <div class="new-appointment">
    <div class="container">
      <h1>New Appointment</h1>
      
      <div class="form">
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>Service</label>
            <select v-model="form.service_id" required>
              <option value="">Select a service</option>
              <option v-for="service in services" :key="service.id" :value="service.id">
                {{ service.name }} - {{ formatPrice(service.price) }} ({{ service.duration }}min)
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Barber</label>
            <select v-model="form.barber_profile_id" required>
              <option value="">Select a barber</option>
              <option v-for="barber in availableBarbers" :key="barber.id" :value="barber.id" :data-user-id="barber.user?.id">
                {{ barber.user?.first_name }} {{ barber.user?.last_name }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Date</label>
            <input v-model="form.date" type="date" :min="minDate" required />
          </div>
          
          <div class="form-group">
            <label>Time</label>
            <select v-model="form.time" required>
              <option value="">Select a time</option>
              <option v-for="slot in availableSlots" :key="slot" :value="slot">
                {{ slot }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Notes (optional)</label>
            <textarea v-model="form.notes"></textarea>
          </div>
          
          <div v-if="error" class="message message-error">{{ error }}</div>
          
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Booking...' : 'Book' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import api from '../services/api'

const router = useRouter()
const userStore = useUserStore()

const services = ref([])
const barbers = ref([])
const availableSlots = ref([])
const loading = ref(false)
const error = ref('')

// Calculate minimum date (today) in YYYY-MM-DD format
const getMinDate = () => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const minDate = ref(getMinDate())

const form = ref({
  service_id: '',
  barber_profile_id: '', // Barber profile ID (for availability)
  barber_user_id: '',    // Barber user ID (for creating appointment)
  date: '',
  time: '',
  notes: ''
})

// Filter barbers to not show the barber themselves in the list
const availableBarbers = computed(() => {
  const currentUser = userStore.user
  if (!currentUser || currentUser.user_type !== 'barber') {
    return barbers.value
  }
  // If the user is a barber, filter to not show themselves
  return barbers.value.filter(barber => barber.user?.id !== currentUser.id)
})

const fetchServices = async () => {
  try {
    const response = await api.get('/services/')
    services.value = response.data.results || response.data
  } catch (error) {
    console.error('Error fetching services:', error)
  }
}

const fetchBarbers = async () => {
  try {
    const response = await api.get('/barbers/')
    barbers.value = response.data.results || response.data
  } catch (error) {
    console.error('Error fetching barbers:', error)
  }
}

const fetchAvailableSlots = async () => {
  if (!form.value.barber_profile_id || !form.value.date) {
    availableSlots.value = []
    return
  }
  
  try {
    const response = await api.get(`/barbers/${form.value.barber_profile_id}/availability/`, {
      params: { date: form.value.date }
    })
    
    const slots = response.data.available_slots || []
    availableSlots.value = slots.filter(slot => slot.available).map(slot => slot.time)
    
    // Find and store the user_id of the selected barber
    const selectedBarber = availableBarbers.value.find(b => b.id == form.value.barber_profile_id)
    if (selectedBarber) {
      form.value.barber_user_id = selectedBarber.user?.id
    }
  } catch (error) {
    console.error('Error fetching available slots:', error)
  }
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(price)
}

const handleSubmit = async () => {
  error.value = ''
  loading.value = true
  
  try {
    await api.post('/appointments/', {
      barber_id: form.value.barber_user_id,
      service_id: form.value.service_id,
      appointment_date: form.value.date,
      appointment_time: form.value.time,
      notes: form.value.notes
    })
    
    router.push('/appointments')
  } catch (err) {
    console.error('Error creating appointment:', err)
    if (err.response?.data) {
      // Format Django validation errors de forma amigável
      const errorMessages = []
      const data = err.response.data
      
      if ('service_id' in data) {
        errorMessages.push('Service: ' + (Array.isArray(data.service_id) ? data.service_id.join(', ') : data.service_id))
      }
      if ('barber_id' in data) {
        errorMessages.push('Barber: ' + (Array.isArray(data.barber_id) ? data.barber_id.join(', ') : data.barber_id))
      }
      if ('appointment_date' in data) {
        errorMessages.push('Date: ' + (Array.isArray(data.appointment_date) ? data.appointment_date.join(', ') : data.appointment_date))
      }
      if ('appointment_time' in data) {
        errorMessages.push('Time: ' + (Array.isArray(data.appointment_time) ? data.appointment_time.join(', ') : data.appointment_time))
      }
      if ('non_field_errors' in data) {
        const msg = Array.isArray(data.non_field_errors) ? data.non_field_errors.join(', ') : data.non_field_errors
        errorMessages.push(msg)
      }
      if ('detail' in data) {
        errorMessages.push(typeof data.detail === 'string' ? data.detail : 'Error creating appointment')
      }
      
      if (errorMessages.length > 0) {
        error.value = errorMessages.join(' ')
      } else {
        error.value = 'Erro ao criar agendamento. Verifique os dados e tente novamente.'
      }
    } else {
      error.value = 'Erro ao criar agendamento. Tente novamente.'
    }
  } finally {
    loading.value = false
  }
}

watch(() => [form.value.barber_profile_id, form.value.date], () => {
  if (form.value.barber_profile_id && form.value.date) {
    fetchAvailableSlots()
  }
})

onMounted(() => {
  fetchServices()
  fetchBarbers()
})
</script>

<style scoped>
.form {
  max-width: 600px;
}
</style>

