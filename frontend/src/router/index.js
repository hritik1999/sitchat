import { createRouter, createWebHistory } from 'vue-router';
import AuthPage from '@/views/AuthPage.vue';
import AuthCallback from '@/views/AuthCallback.vue';
import ChatPage from '@/views/ChatPage.vue';

const routes = [
  {
    path: '/login',
    component: AuthPage
  },
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: AuthCallback,
  },
  {
    path: '/',
    component: ChatPage
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
