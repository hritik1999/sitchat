<template>
    <div class="min-h-screen transition-colors duration-300">
      <header class="flex items-center justify-between p-6 bg-background/90 backdrop-blur-sm border-b border-foreground/10">
        <h1 class="text-2xl font-bold tracking-tight bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text">
          Sitchat Blog
        </h1>
      </header>
  
      <main class="container mx-auto px-4 py-12 space-y-8 max-w-3xl">
        <Card 
          v-for="post in posts" 
          :key="post.title" 
          class="group transition-all hover:shadow-md hover:-translate-y-0.5 border border-foreground/5 hover:border-foreground/10"
        >
          <CardContent class="p-6">
            <div class="space-y-3">
              <h2 class="text-xl font-semibold tracking-tight bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text">
                {{ post.title }}
              </h2>
              <p class="text-sm text-foreground/60 flex items-center space-x-2">
                <span>{{ post.date }}</span>
                <span class="w-1 h-1 rounded-full bg-foreground/30"></span>
                <span>{{ post.readTime }}</span>
              </p>
              <p class="text-foreground/80 leading-relaxed">
                {{ post.excerpt }}
              </p>
              <Button 
                variant="ghost" 
                size="sm" 
                class="mt-4 text-foreground/60 hover:text-foreground/90 transition-colors pl-0"
                @click="$router.push(post.link)"
              >
                Read more
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"/>
                </svg>
              </Button>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { Card, CardContent } from '@/components/ui/card'
  import { Button } from '@/components/ui/button'
  
  const posts = ref([
    { 
      title: 'Creating Shows in Sitchat', 
      date: 'May 13, 2025', 
      readTime: '4 min', 
      excerpt: 'Learn how to build and launch your own fan-powered show with ease.', 
      link: '/blog/create-show' 
    },
    { 
      title: 'Creating Episodes in Sitchat', 
      date: 'May 13, 2025', 
      readTime: '5 min', 
      excerpt: 'Step into the writer’s seat—design episodes that feel like the real thing.', 
      link: '/blog/create-episode' 
    }
  ])
  </script>