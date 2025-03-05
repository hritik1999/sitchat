// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import { supabase } from '@/composables/useSupabase';
import AuthPage from '@/views/AuthPage.vue';
import AuthCallback from '@/views/AuthCallback.vue';
import ChatPage from '@/views/ChatPage.vue';
import ShowPage from '@/views/ShowPage.vue';
import CreateShow from '@/views/CreateShow.vue';
import ShowDetailsPage from '@/views/ShowDetailsPage.vue';
import CreateEpisode from '@/views/CreateEpisode.vue';
import Profile from '@/views/Profile.vue';
import EditProfile from '@/views/EditProfile.vue';
// Define routes with meta for layout and auth requirements
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: AuthPage,
    meta: { requiresAuth: false, layout: 'none' }
  },
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: AuthCallback,
    meta: { requiresAuth: false, layout: 'none' }
  },
  {
    path: '/',
    name: 'Home',
    component: ShowPage,
    meta: { requiresAuth: true, layout: 'main' }
  },
  {
    path: '/shows',
    name: 'Shows',
    component: ShowPage,
    meta: { requiresAuth: true, layout: 'main' }
  },
  {
    path: '/show/:show_id/chat/:chat_id',
    name: 'Chat',
    component: ChatPage,
    meta: { requiresAuth: true, layout: 'none' }
  },
  {
    path: '/create/show',
    name: 'CreateShow',
    component: CreateShow,
    meta: { requiresAuth: true, layout: 'main' }
  },
  {
    path: '/show/:id',
    name:'ShowDetails',
    component:ShowDetailsPage,
    meta: {requiresAuth:true,layout:'main'}
  },
  {
    path: '/create/episode/:id',
    name:'CreateEpisode',
    component:CreateEpisode,
    meta: {requiresAuth:true,layout:'main'}
  },
  {
    path: '/edit/episode/:showId/:episodeId',
    name: 'EditEpisode',
    component: CreateEpisode,
    meta: { requiresAuth: true, layout: 'main' }
  },
  {
    path: '/edit/show/:showId',
    name: 'EditShow',
    component: CreateShow,
    meta: { requiresAuth: true, layout: 'main' }
  },
  {
    path: '/edit/profile',
    name:'EditProfile',
    component:EditProfile,
    meta: {requiresAuth:true,layout:'main'}
  },
  {
    path: '/profile',
    name:'Profile',
    component:Profile,
    meta: {requiresAuth:true,layout:'main'}
  }
  // Add more routes as needed
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Global navigation guard for authentication
router.beforeEach(async (to, from, next) => {
  // Check if the route requires authentication
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  
  // Get current session
  const { data, error } = await supabase.auth.getSession();
  const session = data?.session;
  
  // For debugging
  console.log('Route:', to.path, 'Auth required:', requiresAuth, 'Session exists:', !!session);
  
  if (requiresAuth && !session) {
    // Redirect to login if authentication is required but user is not logged in
    console.log('Redirecting to login, auth required but no session');
    return next('/login');
  } else if (to.path === '/login' && session) {
    // Redirect to home if user is already logged in and tries to access login page
    console.log('Redirecting to home, user is logged in but trying to access login');
    return next('/');
  } else {
    // Proceed as normal
    console.log('Proceeding to route:', to.path);
    return next();
  }
});

export default router;