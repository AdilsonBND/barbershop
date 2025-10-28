<template>
  <div v-if="showWelcomeModal" class="modal-overlay" @click="closeModal">
    <div class="modal welcome-modal" @click.stop>
      <div class="modal-header">
        <h2>🎉 Welcome to Barbershop!</h2>
        <button @click="closeModal" class="close-btn">×</button>
      </div>
      
      <div class="modal-content">
        <div class="welcome-icon">
          <i class="icon">💈</i>
        </div>
        
        <h3>Your account has been created successfully!</h3>
        
        <div class="info-box">
          <h4>Next Steps:</h4>
          <ol>
            <li><strong>Complete your profile</strong> - Add your specialization, bio, and working hours</li>
            <li><strong>Request authorization</strong> - Contact the administrator to activate your account</li>
            <li><strong>Start receiving appointments</strong> - Once authorized, clients can book with you</li>
          </ol>
        </div>
        
        <div class="contact-info">
          <p><strong>Need help?</strong></p>
          <p>Contact the administrator to get your account authorized and start receiving appointments.</p>
        </div>
        
        <div class="modal-actions">
          <button @click="goToProfile" class="btn btn-primary">
            Complete My Profile
          </button>
          <button @click="closeModal" class="btn btn-secondary">
            Continue to Dashboard
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const showWelcomeModal = ref(false)

const closeModal = () => {
  showWelcomeModal.value = false
  localStorage.setItem('barber_welcome_shown', 'true')
}

const goToProfile = () => {
  closeModal()
  router.push('/barber-profile')
}

onMounted(() => {
  // Check if this is a new barber registration
  const welcomeShown = localStorage.getItem('barber_welcome_shown')
  const isNewBarber = sessionStorage.getItem('new_barber_registration')
  
  if (!welcomeShown && isNewBarber) {
    showWelcomeModal.value = true
    sessionStorage.removeItem('new_barber_registration')
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.welcome-modal {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-header h2 {
  margin: 0;
  color: #2563eb;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
}

.welcome-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.modal-content h3 {
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.info-box {
  background: #f3f4f6;
  border-radius: 8px;
  padding: 1.5rem;
  margin: 1.5rem 0;
  text-align: left;
}

.info-box h4 {
  margin-top: 0;
  color: #1f2937;
}

.info-box ol {
  margin: 0;
  padding-left: 1.5rem;
}

.info-box li {
  margin-bottom: 0.5rem;
  color: #374151;
}

.contact-info {
  background: #eff6ff;
  border-radius: 8px;
  padding: 1rem;
  margin: 1.5rem 0;
  border-left: 4px solid #2563eb;
}

.contact-info p {
  margin: 0.5rem 0;
  color: #1e40af;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

@media (max-width: 768px) {
  .welcome-modal {
    padding: 1.5rem;
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .modal-actions .btn {
    width: 100%;
  }
}
</style>
