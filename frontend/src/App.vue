<!-- App.vue -->
<template>
  <MainLayout v-if="$route.meta.layout === 'main'">
    <RouterView />
  </MainLayout>
  <RouterView v-else />
</template>

<script>
import MainLayout from '@/layouts/MainLayout.vue';

export default {
  name: 'App',
  components: {
    MainLayout
  },
  mounted() {
    // Check for dark mode preference on app initialization
    const savedTheme = localStorage.getItem('theme')
    
    if (savedTheme === 'dark') {
      document.documentElement.classList.add('dark')
    } else if (savedTheme === 'light') {
      document.documentElement.classList.remove('dark')
    } else {
      // If no saved preference, check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      if (prefersDark) {
        document.documentElement.classList.add('dark')
      }
    }
  }
};
</script>