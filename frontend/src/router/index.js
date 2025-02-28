import { createRouter, createWebHistory } from 'vue-router'
import { useSupabase } from '@/composables/useSupabase'

// Lazy load components for better performance
const HomePage = () => import('@/views/HomePage.vue')
const AuthPage = () => import('@/views/AuthPage.vue')
const ShowsPage = () => import('@/views/ShowsPage.vue')
const ShowDetailsPage = () => import('@/views/ShowDetailsPage.vue')
const EpisodePage = () => import('@/views/ShowDetailsPage.vue')
const ChatPage = () => import('@/views/ChatPage.vue')

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage,
    meta: { title: 'Home' }
  },
  {
    path: '/auth',
    name: 'auth',
    component: AuthPage,
    meta: { title: 'Sign In', guestOnly: true }
  },
  {
    path: '/shows',
    name: 'shows',
    component: ShowsPage,
    meta: { title: 'Browse Shows' }
  },
  {
    path: '/shows/:id',
    name: 'show-details',
    component: ShowDetailsPage,
    meta: { title: 'Show Details' },
    props: true
  },
  {
    path: '/episode/:id',
    name: 'episode',
    component: EpisodePage,
    meta: { title: 'Episode Details' },
    props: true
  },
  {
    path: '/chat/:id',
    name: 'chat',
    component: ChatPage,
    meta: { title: 'Interactive Story' },
    props: true
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  // Set page title
  document.title = `${to.meta.title ? to.meta.title + ' | ' : ''}SitChat`
  
  const { supabase } = useSupabase()
  const { data } = await supabase.auth.getSession()
  const isLoggedIn = !!data.session
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !isLoggedIn) {
    return next({ name: 'auth', query: { redirect: to.fullPath } })
  }
  
  // Check if route is for guests only (like login)
  if (to.meta.guestOnly && isLoggedIn) {
    return next({ name: 'home' })
  }
  
  next()
})

export default router