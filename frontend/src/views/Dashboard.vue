<template>
  <div class="dashboard">
    <div class="container">
      <h1>Dashboard</h1>
      
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
      </div>
      
      <div v-else>
        <div class="stats-grid">
          <div class="stat-card" v-for="stat in stats" :key="stat.label">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
        
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Welcome, {{ userStore.user?.first_name || userStore.user?.username }}!</h2>
          </div>
          <p>You are logged in as: <strong>{{ getUserTypeLabel(userStore.user?.user_type) }}</strong></p>
          
          <!-- Barber authorization warning -->
          <div v-if="userStore.user?.user_type === 'barber' && (!barberHasProfile || (barberHasProfile && barberProfile && !barberProfile.is_approved))" class="alert alert-warning">
            <h4>⚠️ Account Authorization Required</h4>
            <p>Your barber account needs to be authorized by an administrator before you can receive appointments.</p>
            <p><strong>Please contact the administrator to activate your account.</strong></p>
            <router-link to="/barber-profile" class="btn btn-primary">
              Complete My Profile
            </router-link>
          </div>
          
          <div class="actions">
            <router-link to="/appointments" class="btn btn-primary">
              View Appointments
            </router-link>
            <router-link v-if="userStore.user?.user_type === 'client'" to="/appointments/new" class="btn btn-success">
              New Appointment
            </router-link>
            <router-link v-if="userStore.user?.user_type === 'barber'" to="/barber-profile" class="btn btn-secondary">
              My Profile
            </router-link>
            <router-link v-if="userStore.user?.user_type === 'admin'" to="/admin/barbers" class="btn btn-secondary">
              Manage Barbers
            </router-link>
            <router-link v-if="userStore.user?.user_type === 'admin'" to="/admin/services" class="btn btn-secondary">
              Manage Services
            </router-link>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Welcome Modal for new barbers -->
    <WelcomeModal />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import api from '../services/api'
import WelcomeModal from '../components/WelcomeModal.vue'

const userStore = useUserStore()
const stats = ref([])
const loading = ref(true)
const barberHasProfile = ref(false)
const barberProfile = ref(null)

const fetchStats = async () => {
  try {
    const response = await api.get('/dashboard/stats/')
    const data = response.data
    
    // Check if barber has profile
    if (userStore.user?.user_type === 'barber') {
      try {
        const res = await api.get('/barbers/my_profile/')
        barberProfile.value = res.data
        barberHasProfile.value = true
      } catch (error) {
        if (error.response?.status === 404) {
          barberHasProfile.value = false
          barberProfile.value = null
        }
      }
    }
    
    if (userStore.user?.user_type === 'admin') {
      stats.value = [
        { label: 'Total Users', value: data.total_users },
        { label: 'Clients', value: data.total_clients },
        { label: 'Barbers', value: data.total_barbers },
        { label: 'Appointments', value: data.total_appointments },
        { label: 'Pending', value: data.pending_appointments }
      ]
    } else if (userStore.user?.user_type === 'barber') {
      stats.value = [
        { label: 'Appointments', value: data.total_appointments },
        { label: 'Today', value: data.today_appointments },
        { label: 'Pending', value: data.pending_appointments },
        { label: 'Completed', value: data.completed_appointments }
      ]
    } else {
      stats.value = [
        { label: 'Appointments', value: data.total_appointments },
        { label: 'Upcoming', value: data.upcoming_appointments },
        { label: 'Past', value: data.past_appointments }
      ]
    }
  } catch (error) {
    console.error('Error fetching stats:', error)
  } finally {
    loading.value = false
  }
}

const getUserTypeLabel = (type) => {
  const labels = {
    'client': 'Client',
    'barber': 'Barber',
    'admin': 'Administrator'
  }
  return labels[type] || type
}

onMounted(() => {
  fetchStats()
})
</script>

<script>
import WelcomeModal from '../components/WelcomeModal.vue'

export default {
  components: {
    WelcomeModal
  }
}
</script>

<style scoped>
.dashboard {
  min-height: calc(100vh - 70px);
  padding-top: 2rem;
}

.actions {
  margin-top: 1rem;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .actions {
    flex-direction: column;
  }
  
  .actions .btn {
    width: 100%;
  }
}

.alert {
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
}

.alert-warning {
  background-color: #fef3cd;
  border: 1px solid #fde68a;
  color: #92400e;
}

.alert h4 {
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.alert p {
  margin-bottom: 0.5rem;
}
</style>

