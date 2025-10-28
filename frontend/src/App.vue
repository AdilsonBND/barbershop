<template>
  <div id="app">
    <nav class="navbar" v-if="userStore.isAuthenticated" :class="{ 'is-mobile-menu': isMobileMenu }" ref="navbarRef">
      <div class="navbar-brand" ref="brandRef">
        <h1>💈 Barbershop</h1>
      </div>
      
      <!-- Hamburger menu for mobile -->
      <button class="menu-toggle" @click="toggleMobileMenu" aria-label="Toggle menu">
        <i class="icon">☰</i>
      </button>
      
      <!-- Navigation links -->
      <div class="navbar-links" :class="{ 'mobile-open': mobileMenuOpen }" ref="linksRef">
        <button class="close-menu" @click="toggleMobileMenu" aria-label="Close menu">
          ✕
        </button>
        <router-link to="/dashboard" @click="closeMobileMenu">
          <i class="icon">📊</i> Dashboard
        </router-link>
        <router-link to="/appointments" @click="closeMobileMenu">
          <i class="icon">📅</i> Appointments
        </router-link>
        <router-link to="/barbers" @click="closeMobileMenu">
          <i class="icon">👨‍💼</i> Barbers
        </router-link>
        <router-link to="/services" @click="closeMobileMenu">
          <i class="icon">✂️</i> Services
        </router-link>
        <router-link v-if="userStore.user?.user_type === 'barber'" to="/barber-profile" @click="closeMobileMenu">
          <i class="icon">👤</i> My Profile
        </router-link>
        <router-link v-if="userStore.user?.user_type === 'admin'" to="/admin/barbers" @click="closeMobileMenu">
          <i class="icon">👨‍💼</i> Manage Barbers
        </router-link>
        <router-link v-if="userStore.user?.user_type === 'admin'" to="/admin/services" @click="closeMobileMenu">
          <i class="icon">⚙️</i> Manage Services
        </router-link>
        <button @click="handleLogout" class="btn-logout">
          <i class="icon">🚪</i> Logout
        </button>
      </div>
      
      <!-- Overlay for mobile -->
      <div v-if="mobileMenuOpen" class="navbar-overlay" @click="closeMobileMenu"></div>
    </nav>
    <router-view />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from './stores/user'

const router = useRouter()
const userStore = useUserStore()
const mobileMenuOpen = ref(false)
const isMobileMenu = ref(false)
const navbarRef = ref(null)
const brandRef = ref(null)
const linksRef = ref(null)

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

const handleLogout = async () => {
  await userStore.logout()
  closeMobileMenu()
  router.push('/login')
}

const checkOverflow = () => {
  const navbar = navbarRef.value
  const brand = brandRef.value
  const links = linksRef.value
  if (!navbar || !brand || !links) return
  const available = navbar.clientWidth - brand.clientWidth - 32 /* safety gap */
  isMobileMenu.value = links.scrollWidth > available
}

const onResize = () => {
  // Delay until DOM lays out
  nextTick(() => checkOverflow())
}

onMounted(() => {
  window.addEventListener('resize', onResize)
  nextTick(() => checkOverflow())
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
})
</script>

<style scoped>
.navbar {
  background-color: #1a1a1a;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: relative;
}

.navbar-brand h1 {
  margin: 0;
  font-size: 1.5rem;
}

/* Menu toggle button - hidden on desktop */
.menu-toggle {
  display: none;
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
}

.navbar-links {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.navbar-links a {
  color: white;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.navbar-links a:hover {
  background-color: rgba(255,255,255,0.1);
}

.btn-logout {
  background-color: #ff4444;
  border: none;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-logout:hover {
  background-color: #cc0000;
}

.close-menu {
  display: none;
}

.navbar-overlay {
  display: none;
}

/* Styles for medium screens - ensure logo and navigation stay side by side */
.navbar.is-mobile-menu {
  /* when overflowing, force hamburger mode regardless of width */
}

.navbar.is-mobile-menu .menu-toggle {
  display: block;
}

.navbar.is-mobile-menu .navbar-links {
  position: fixed;
  top: 0;
  right: 0;
  transform: translateX(100%);
  width: 280px;
  height: 100vh;
  background-color: #1a1a1a;
  flex-direction: column;
  align-items: flex-start;
  padding: 2rem 1.5rem;
  transition: transform 0.3s ease;
  z-index: 1000;
  box-shadow: -2px 0 8px rgba(0,0,0,0.2);
  gap: 0.5rem;
}

.navbar.is-mobile-menu .navbar-links.mobile-open {
  transform: translateX(0);
}

.navbar.is-mobile-menu .close-menu {
  display: block;
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
}

.navbar.is-mobile-menu .navbar-overlay {
  display: block;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.5);
  z-index: 999;
}

@media (max-width: 1024px) and (min-width: 769px) {
  .navbar {
    padding: 1rem 1.5rem;
  }
  
  .navbar-brand h1 {
    font-size: 1.3rem;
    white-space: nowrap;
  }
  
  .navbar-links {
    gap: 1rem;
    flex-wrap: nowrap;
  }
  
  .navbar-links a {
    padding: 0.5rem 0.75rem;
    font-size: 0.9rem;
    white-space: nowrap;
  }
  
  .btn-logout {
    padding: 0.5rem 0.75rem;
    font-size: 0.9rem;
    white-space: nowrap;
  }
}

/* Styles for mobile */
@media (max-width: 768px) {
  .menu-toggle {
    display: block;
  }
  
  .navbar-links {
    position: fixed;
    top: 0;
    right: 0;
    transform: translateX(100%);
    width: 280px;
    height: 100vh;
    background-color: #1a1a1a;
    flex-direction: column;
    align-items: flex-start;
    padding: 2rem 1.5rem;
    transition: transform 0.3s ease;
    z-index: 1000;
    box-shadow: -2px 0 8px rgba(0,0,0,0.2);
    gap: 0.5rem;
  }
  
  .navbar-links.mobile-open {
    transform: translateX(0);
  }
  
  .navbar-links a,
  .navbar-links .btn-logout {
    width: 100%;
    padding: 1rem;
  }
  
  .close-menu {
    display: block;
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0.5rem;
  }
  
  .navbar-overlay {
    display: block;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.5);
    z-index: 999;
  }
}

@media (max-width: 480px) {
  .navbar {
    padding: 1rem;
  }
  
  .navbar-brand h1 {
    font-size: 1.2rem;
  }
  
  .navbar-links {
    width: 250px;
  }
}

/* Global (non-scoped) fixes to avoid horizontal scroll white gap */
</style>
<style>
html, body {
  overflow-x: hidden;
  background-color: #f8f9fa;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
  background-color: #f8f9fa;
}
</style>
