<template>
    <div class="min-h-screen bg-white text-gray-900 dark:bg-gray-900 dark:text-gray-100">
      <header class="flex items-center justify-between p-6 max-w-7xl mx-auto">
        <h1 class="text-3xl font-bold">Sitchat Careers</h1>
      </header>
  
      <main class="space-y-12 p-6 max-w-3xl mx-auto">
        <section class="text-center space-y-4">
          <h2 class="text-2xl font-semibold">Join the journey</h2>
          <p class="text-lg">
            Currently, I am the only employee and founder. If you think you can help in any way possible, please feel free to reach out!
          </p>
          <div class="flex justify-center">
            <Button as="a" :href="`mailto:${email}`" variant="primary" size="lg" class="font-bold text-blue-600">
              Contact Me
            </Button><br>
          </div>
          <p>or email me at {{ email }}</p>
        </section>
  
        <section class="space-y-6">
          <h3 class="text-xl font-semibold">Open Roles</h3>
          <p class="italic text-center">There are no open roles at the moment.</p>
        </section>
  
        <section class="space-y-6">
          <h3 class="text-xl font-semibold">Speculative Applications</h3>
          <p>If you're passionate about making Sitchat better—designers, marketers, engineers, or anyone—I'd love to hear from you.</p>
          <Button as="a" :href="`mailto:${email}`" variant="outline">
            Email Speculative Application
          </Button>
        </section>
      </main>
    </div>
  </template>
  
  <script setup>
  import { Button } from '@/components/ui/button'
  
  const email = 'founder@sitchat.ai'
  </script>
  
  <style scoped>
  /* Add any additional scoped styles here */
  </style>
  