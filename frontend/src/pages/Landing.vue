<template>
    <div class="min-h-screen bg-background text-foreground">
      <!-- Hero Section -->
      <section class="container mx-auto px-4 py-16 md:py-24">
        <div class="text-center space-y-6">
          <Badge variant="outline" class="text-lg py-2 px-4 bg-purple-100 dark:bg-purple-900/20">
            🎬 The Future of Fan-Powered Storytelling
          </Badge>
          <h1 class="text-5xl md:text-6xl font-bold bg-gradient-to-r from-purple-400 to-blue-500 bg-clip-text text-transparent">
            Welcome to Sitchat
          </h1>
          <p class="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto">
            Where you don't just watch - you participate. Dive into immersive group chats with AI versions of your favorite characters!
          </p>
          <Button class="gap-2" size="lg">
            <Sparkles class="w-4 h-4" />
            Start Creating
          </Button>
        </div>
      </section>
  
      <!-- Features Grid -->
      <section class="bg-muted/50 py-16">
        <div class="container mx-auto px-4 grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <Card v-for="(feature, index) in features" :key="index" class="p-6 hover:border-primary transition-all">
            <div class="space-y-4">
              <div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
                <Component :is="feature.icon" class="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
              <h3 class="text-xl font-semibold">{{ feature.title }}</h3>
              <p class="text-muted-foreground">{{ feature.description }}</p>
              <div class="flex flex-wrap gap-2">
                <Badge v-for="(tag, tagIndex) in feature.tags" :key="tagIndex" variant="secondary">
                  {{ tag }}
                </Badge>
              </div>
            </div>
          </Card>
        </div>
      </section>
  
      <!-- Founder Section -->
      <section class="container mx-auto px-4 py-16 md:py-24">
        <Card class="p-8 bg-gradient-to-br from-background to-muted/50 border border-primary/20">
          <div class="flex flex-col md:flex-row gap-8 items-center">
            <Avatar class="w-32 h-32">
              <AvatarImage src="/path-to-hritik-image.jpg" />
              <AvatarFallback>HG</AvatarFallback>
            </Avatar>
            <div class="space-y-4">
              <Badge variant="outline" class="text-sm">👋 Meet the Creator</Badge>
              <h2 class="text-3xl font-bold">Hritik Gupta</h2>
              <p class="text-muted-foreground text-lg">
                "Sitchat was born from pure love for stories and a little bit of post-show sadness. 
                Our vision is to become the Netflix of interactive storytelling!"
              </p>
              <div class="flex gap-4">
                <Button variant="outline" class="gap-2">
                  <Mail class="w-4 h-4" />
                  Contact
                </Button>
                <Button variant="outline" class="gap-2">
                  <Phone class="w-4 h-4" />
                  Call
                </Button>
              </div>
            </div>
          </div>
        </Card>
      </section>
  
      <!-- CTA Section -->
      <section class="border-t bg-muted/50">
        <div class="container mx-auto px-4 py-16 text-center space-y-6">
          <h2 class="text-4xl font-bold">Ready to Direct Your Story?</h2>
          <p class="text-xl text-muted-foreground max-w-2xl mx-auto">
            Create shows, build episodes, earn achievements, and experience being part of the show!
          </p>
          <Button size="lg" class="gap-2">
            <Play class="w-4 h-4" />
            Join the Fun
          </Button>
        </div>
      </section>
    </div>
  </template>
  
  <script setup>
  import { Badge } from '@/components/ui/badge'
  import { Button } from '@/components/ui/button'
  import { Card } from '@/components/ui/card'
  import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar'
  import { 
    Sparkles, 
    Mail, 
    Phone, 
    Play,
    Users,
    Bot,
    LayoutDashboard,
    Trophy,
    GalleryVerticalEnd
  } from 'lucide-vue-next'
  
  const features = [
    {
      icon: Users,
      title: "Group Chat Stories",
      description: "Interact with multiple characters in dynamic group chats",
      tags: ["Multi-character", "Immersive", "Interactive"]
    },
    {
      icon: LayoutDashboard,
      title: "Create Shows",
      description: "Build your own episodes with custom characters and plots",
      tags: ["Customization", "Episodes", "Fan-fiction"]
    },
    {
      icon: Trophy,
      title: "Earn Achievements",
      description: "Unlock hilarious milestones as you interact with characters",
      tags: ["Badges", "Milestones", "Fun"]
    },
    {
      icon: GalleryVerticalEnd,
      title: "Story Progression",
      description: "Structured narratives with real plot development",
      tags: ["Plotlines", "Objectives", "Challenges"]
    },
    {
      icon: Bot,
      title: "AI Characters",
      description: "Authentic character personalities powered by AI",
      tags: ["Personality", "Responsive", "Dynamic"]
    }
  ]
  </script>