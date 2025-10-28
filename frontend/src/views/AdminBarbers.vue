<template>
  <div class="admin-barbers">
    <div class="container">
      <div class="header">
        <h1>Manage Barbers</h1>
        <button @click="showCreateModal = true" class="btn btn-primary">
          Add Barber Profile
        </button>
      </div>
      
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
      </div>
      
      <div v-else>
        <div v-if="barberProfiles.length === 0" class="card">
          <p>No barber profiles found.</p>
        </div>
        
        <div v-for="profile in barberProfiles" :key="profile.id" class="card">
          <div class="profile-header">
            <h2>{{ profile.user?.first_name }} {{ profile.user?.last_name }}</h2>
            <div class="profile-actions">
              <span class="badge" :class="profile.is_approved ? 'badge-success' : 'badge-warning'">
                {{ profile.is_approved ? 'Approved' : 'Pending approval' }}
              </span>
              <button @click="editProfile(profile)" class="btn btn-secondary">
                Edit
              </button>
              <button v-if="!profile.is_approved" @click="approveProfile(profile.id)" class="btn btn-success">
                Approve
              </button>
              <button @click="deleteProfile(profile.id)" class="btn btn-danger">
                Delete
              </button>
            </div>
          </div>
          
          <div class="profile-info">
            <p><strong>Email:</strong> {{ profile.user?.email }}</p>
            <p><strong>Phone:</strong> {{ profile.user?.phone || 'Not provided' }}</p>
            <p v-if="profile.specialization"><strong>Specialization:</strong> {{ profile.specialization }}</p>
            <p v-if="profile.bio"><strong>Bio:</strong> {{ profile.bio }}</p>
            <p><strong>Available:</strong> {{ profile.is_available ? 'Yes' : 'No' }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ showEditModal ? 'Edit Barber Profile' : 'Add Barber Profile' }}</h3>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>Barber User</label>
            <select v-model="form.user_id" required>
              <option value="">Select a barber user</option>
              <option v-for="user in barberUsers" :key="user.id" :value="user.id">
                {{ user.first_name }} {{ user.last_name }} ({{ user.username }})
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Specialization</label>
            <input v-model="form.specialization" type="text" placeholder="e.g., Haircuts, Beard trimming" />
          </div>
          
          <div class="form-group">
            <label>Bio</label>
            <textarea v-model="form.bio" placeholder="Tell us about yourself..."></textarea>
          </div>
          
          <div class="form-group">
            <label>Working Hours <span class="optional">(Optional - leave empty for days you don't work)</span></label>
            <div class="hours-grid">
              <div v-for="day in days" :key="day.key" class="day-hours">
                <label>{{ day.label }}</label>
                <div class="time-inputs">
                  <input 
                    v-model="form[day.start]" 
                    type="time" 
                    :placeholder="day.start"
                  />
                  <span>to</span>
                  <input 
                    v-model="form[day.end]" 
                    type="time" 
                    :placeholder="day.end"
                  />
                </div>
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <label>
              <input v-model="form.is_available" type="checkbox" />
              Available for appointments
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

const barberProfiles = ref([])
const barberUsers = ref([])
const loading = ref(true)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingProfile = ref(null)
const error = ref('')

const days = [
  { key: 'monday', label: 'Monday', start: 'monday_start', end: 'monday_end' },
  { key: 'tuesday', label: 'Tuesday', start: 'tuesday_start', end: 'tuesday_end' },
  { key: 'wednesday', label: 'Wednesday', start: 'wednesday_start', end: 'wednesday_end' },
  { key: 'thursday', label: 'Thursday', start: 'thursday_start', end: 'thursday_end' },
  { key: 'friday', label: 'Friday', start: 'friday_start', end: 'friday_end' },
  { key: 'saturday', label: 'Saturday', start: 'saturday_start', end: 'saturday_end' },
  { key: 'sunday', label: 'Sunday', start: 'sunday_start', end: 'sunday_end' }
]

const form = ref({
  user_id: '',
  specialization: '',
  bio: '',
  is_available: true,
  monday_start: '',
  monday_end: '',
  tuesday_start: '',
  tuesday_end: '',
  wednesday_start: '',
  wednesday_end: '',
  thursday_start: '',
  thursday_end: '',
  friday_start: '',
  friday_end: '',
  saturday_start: '',
  saturday_end: '',
  sunday_start: '',
  sunday_end: ''
})

const fetchBarberProfiles = async () => {
  try {
    const response = await api.get('/barbers/')
    barberProfiles.value = response.data.results || response.data
  } catch (error) {
    console.error('Error fetching barber profiles:', error)
  } finally {
    loading.value = false
  }
}

const fetchBarberUsers = async () => {
  try {
    const response = await api.get('/users/?user_type=barber')
    barberUsers.value = response.data.results || response.data
  } catch (error) {
    console.error('Error fetching barber users:', error)
  }
}

const editProfile = (profile) => {
  editingProfile.value = profile
  form.value = {
    user_id: profile.user?.id || '',
    specialization: profile.specialization || '',
    bio: profile.bio || '',
    is_available: profile.is_available,
    monday_start: profile.monday_start || '',
    monday_end: profile.monday_end || '',
    tuesday_start: profile.tuesday_start || '',
    tuesday_end: profile.tuesday_end || '',
    wednesday_start: profile.wednesday_start || '',
    wednesday_end: profile.wednesday_end || '',
    thursday_start: profile.thursday_start || '',
    thursday_end: profile.thursday_end || '',
    friday_start: profile.friday_start || '',
    friday_end: profile.friday_end || '',
    saturday_start: profile.saturday_start || '',
    saturday_end: profile.saturday_end || '',
    sunday_start: profile.sunday_start || '',
    sunday_end: profile.sunday_end || ''
  }
  showEditModal.value = true
}

const deleteProfile = async (id) => {
  if (!confirm('Are you sure you want to delete this barber profile?')) {
    return
  }
  
  try {
    await api.delete(`/barbers/${id}/`)
    await fetchBarberProfiles()
  } catch (error) {
    alert('Error deleting barber profile')
  }
}

const approveProfile = async (id) => {
  try {
    await api.post(`/barbers/${id}/approve/`)
    await fetchBarberProfiles()
  } catch (error) {
    alert('Error approving barber profile')
  }
}

const handleSubmit = async () => {
  error.value = ''
  loading.value = true
  
  try {
    // Clean up empty time fields - convert empty strings to null
    const cleanedForm = { ...form.value }
    const timeFields = [
      'monday_start', 'monday_end', 'tuesday_start', 'tuesday_end',
      'wednesday_start', 'wednesday_end', 'thursday_start', 'thursday_end',
      'friday_start', 'friday_end', 'saturday_start', 'saturday_end',
      'sunday_start', 'sunday_end'
    ]
    
    timeFields.forEach(field => {
      if (cleanedForm[field] === '') {
        cleanedForm[field] = null
      }
    })
    
    if (showEditModal.value) {
      await api.put(`/barbers/${editingProfile.value.id}/`, cleanedForm)
    } else {
      await api.post('/barbers/', cleanedForm)
    }
    
    closeModal()
    await fetchBarberProfiles()
  } catch (err) {
    console.error('Error saving barber profile:', err)
    if (err.response?.data) {
      error.value = JSON.stringify(err.response.data)
    } else {
      error.value = 'Error saving barber profile'
    }
  } finally {
    loading.value = false
  }
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  editingProfile.value = null
  error.value = ''
  form.value = {
    user_id: '',
    specialization: '',
    bio: '',
    is_available: true,
    monday_start: '',
    monday_end: '',
    tuesday_start: '',
    tuesday_end: '',
    wednesday_start: '',
    wednesday_end: '',
    thursday_start: '',
    thursday_end: '',
    friday_start: '',
    friday_end: '',
    saturday_start: '',
    saturday_end: '',
    sunday_start: '',
    sunday_end: ''
  }
}

onMounted(() => {
  fetchBarberProfiles()
  fetchBarberUsers()
})
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.profile-actions {
  display: flex;
  gap: 0.5rem;
}

.profile-info {
  margin-bottom: 1rem;
}

.profile-info p {
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
  max-width: 600px;
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

.hours-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.day-hours {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.time-inputs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.time-inputs input {
  flex: 1;
}

.optional {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: normal;
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
  
  .profile-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .modal {
    padding: 1rem;
  }
}
</style>
