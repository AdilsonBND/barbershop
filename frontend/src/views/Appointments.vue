<template>
  <div class="appointments">
    <div class="container">
      <div class="header">
        <h1>Appointments</h1>
        <router-link v-if="userStore.user?.user_type === 'client'" to="/appointments/new" class="btn btn-primary">
          New Appointment
        </router-link>
      </div>
      
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
      </div>
      
      <div v-else>
        <div v-if="appointments.length === 0" class="card">
          <p>No appointments found.</p>
        </div>
        
        <div v-for="appointment in appointments" :key="appointment.id" class="card">
          <div class="appointment-header">
            <div>
              <h3>{{ getServiceName(appointment.service) }}</h3>
              <p class="appointment-date">
                📅 {{ formatDate(appointment.appointment_date) }} às {{ formatTime(appointment.appointment_time) }}
              </p>
            </div>
            <span :class="`badge badge-${getStatusColor(appointment.status)}`">
              {{ getStatusLabel(appointment.status) }}
            </span>
          </div>
          
          <div class="appointment-info">
            <p v-if="userStore.user?.user_type === 'client'">
              <strong>Barber:</strong> {{ appointment.barber?.first_name }} {{ appointment.barber?.last_name }}
            </p>
            <p v-if="userStore.user?.user_type === 'barber'">
              <strong>Client:</strong> {{ appointment.client?.first_name }} {{ appointment.client?.last_name }}
            </p>
            <p v-if="appointment.notes">
              <strong>Notes:</strong> {{ appointment.notes }}
            </p>
          </div>
          
          <div class="appointment-actions">
            <button
              v-if="userStore.user?.user_type === 'barber' && appointment.status === 'scheduled'"
              @click="confirmAppointment(appointment.id)"
              class="btn btn-success"
            >
              Confirm
            </button>
            <button
              v-if="userStore.user?.user_type === 'barber' && ['scheduled','confirmed','in_progress'].includes(appointment.status)"
              @click="completeAppointment(appointment.id)"
              class="btn btn-secondary"
            >
              Mark as Completed
            </button>
            <button
              v-if="['scheduled', 'confirmed'].includes(appointment.status)"
              @click="cancelAppointment(appointment.id)"
              class="btn btn-danger"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import api from '../services/api'

const userStore = useUserStore()
const appointments = ref([])
const loading = ref(true)

const fetchAppointments = async () => {
  try {
    const response = await api.get('/appointments/')
    appointments.value = response.data.results || response.data
  } catch (error) {
    console.error('Error fetching appointments:', error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return format(date, "dd 'de' MMMM 'de' yyyy", { locale: ptBR })
}

const formatTime = (timeStr) => {
  return timeStr
}

const getServiceName = (service) => {
  return service?.name || 'Serviço'
}

const getStatusLabel = (status) => {
  const labels = {
    'scheduled': 'Agendado',
    'confirmed': 'Confirmado',
    'in_progress': 'Em Andamento',
    'completed': 'Concluído',
    'cancelled': 'Cancelado',
    'no_show': 'Não Compareceu'
  }
  return labels[status] || status
}

const getStatusColor = (status) => {
  const colors = {
    'scheduled': 'info',
    'confirmed': 'success',
    'in_progress': 'warning',
    'completed': 'success',
    'cancelled': 'danger',
    'no_show': 'danger'
  }
  return colors[status] || 'info'
}

const confirmAppointment = async (id) => {
  try {
    await api.post(`/appointments/${id}/confirm/`)
    await fetchAppointments()
  } catch (error) {
    alert('Error confirming appointment')
  }
}

const cancelAppointment = async (id) => {
  if (!confirm('Are you sure you want to cancel this appointment?')) {
    return
  }
  
  try {
    await api.post(`/appointments/${id}/cancel/`)
    await fetchAppointments()
  } catch (error) {
    alert('Error cancelling appointment')
  }
}

const completeAppointment = async (id) => {
  try {
    await api.post(`/appointments/${id}/complete/`)
    await fetchAppointments()
  } catch (error) {
    alert('Error marking appointment as completed')
  }
}

onMounted(() => {
  fetchAppointments()
})
</script>

<style scoped>
.appointment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.appointment-date {
  color: #6b7280;
  margin-top: 0.5rem;
}

.appointment-info {
  margin-bottom: 1rem;
}

.appointment-info p {
  margin-bottom: 0.5rem;
}

.appointment-actions {
  display: flex;
  gap: 1rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .appointment-header {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>

