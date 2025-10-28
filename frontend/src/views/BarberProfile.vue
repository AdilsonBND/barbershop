<template>
  <div class="barber-profile">
    <div class="container">
      <h1>My Profile</h1>
      
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
      </div>
      
      <div v-else-if="profile" class="profile-form">
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>Specialization</label>
            <input v-model="form.specialization" type="text" placeholder="e.g., Haircuts, Beard trimming" />
          </div>
          
          <div class="form-group">
            <label>Bio</label>
            <textarea v-model="form.bio" placeholder="Tell clients about yourself..."></textarea>
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
          <div v-if="success" class="message message-success">{{ success }}</div>
          
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Saving...' : 'Update Profile' }}
          </button>
        </form>
      </div>
      
      <div v-else class="no-profile">
        <div class="card">
          <h2>Create Your Profile</h2>
          <p>Complete your profile to start receiving appointments from clients.</p>
          
          <form @submit.prevent="handleCreate">
            <div class="form-group">
              <label>Specialization</label>
              <input v-model="form.specialization" type="text" placeholder="e.g., Haircuts, Beard trimming" />
            </div>
            
            <div class="form-group">
              <label>Bio</label>
              <textarea v-model="form.bio" placeholder="Tell clients about yourself..."></textarea>
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
            
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Creating...' : 'Create Profile' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const profile = ref(null)
const loading = ref(true)
const error = ref('')
const success = ref('')

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

const fetchProfile = async () => {
  try {
    const response = await api.get('/barbers/my_profile/')
    profile.value = response.data
    // Populate form with existing data
    form.value = {
      specialization: profile.value.specialization || '',
      bio: profile.value.bio || '',
      is_available: profile.value.is_available,
      monday_start: profile.value.monday_start || '',
      monday_end: profile.value.monday_end || '',
      tuesday_start: profile.value.tuesday_start || '',
      tuesday_end: profile.value.tuesday_end || '',
      wednesday_start: profile.value.wednesday_start || '',
      wednesday_end: profile.value.wednesday_end || '',
      thursday_start: profile.value.thursday_start || '',
      thursday_end: profile.value.thursday_end || '',
      friday_start: profile.value.friday_start || '',
      friday_end: profile.value.friday_end || '',
      saturday_start: profile.value.saturday_start || '',
      saturday_end: profile.value.saturday_end || '',
      sunday_start: profile.value.sunday_start || '',
      sunday_end: profile.value.sunday_end || ''
    }
  } catch (error) {
    if (error.response?.status === 404) {
      // Profile doesn't exist yet
      profile.value = null
    } else {
      console.error('Error fetching profile:', error)
    }
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  error.value = ''
  success.value = ''
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
    
    await api.patch(`/barbers/${profile.value.id}/`, cleanedForm)
    success.value = 'Profile updated successfully!'
    await fetchProfile()
  } catch (err) {
    console.error('Error updating profile:', err)
    if (err.response?.data) {
      error.value = JSON.stringify(err.response.data)
    } else {
      error.value = 'Error updating profile'
    }
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
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
    
    await api.post('/barbers/', cleanedForm)
    await fetchProfile()
  } catch (err) {
    console.error('Error creating profile:', err)
    if (err.response?.data) {
      error.value = JSON.stringify(err.response.data)
    } else {
      error.value = 'Error creating profile'
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.profile-form, .no-profile {
  max-width: 800px;
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

@media (max-width: 768px) {
  .hours-grid {
    grid-template-columns: 1fr;
  }
}
</style>
