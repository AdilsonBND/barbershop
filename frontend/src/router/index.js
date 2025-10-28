import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/appointments',
    name: 'Appointments',
    component: () => import('../views/Appointments.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/appointments/new',
    name: 'NewAppointment',
    component: () => import('../views/NewAppointment.vue'),
    meta: { requiresAuth: true, requiresClient: true }
  },
  {
    path: '/barbers',
    name: 'Barbers',
    component: () => import('../views/Barbers.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/services',
    name: 'Services',
    component: () => import('../views/Services.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/barber-profile',
    name: 'BarberProfile',
    component: () => import('../views/BarberProfile.vue'),
    meta: { requiresAuth: true, requiresBarber: true }
  },
  {
    path: '/admin/barbers',
    name: 'AdminBarbers',
    component: () => import('../views/AdminBarbers.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/services',
    name: 'AdminServices',
    component: () => import('../views/AdminServices.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresGuest && userStore.isAuthenticated) {
    next('/dashboard')
  } else if (to.meta.requiresClient && userStore.user?.user_type !== 'client') {
    next('/dashboard')
  } else if (to.meta.requiresBarber && userStore.user?.user_type !== 'barber') {
    next('/dashboard')
  } else if (to.meta.requiresAdmin && userStore.user?.user_type !== 'admin') {
    next('/dashboard')
  } else {
    next()
  }
})

export default router

