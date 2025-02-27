<template>
    <div>
      <!-- Hero section -->
      <section class="w-full py-12 md:py-24 lg:py-32 bg-gradient-to-b from-background to-muted">
        <div class="container px-4 md:px-6 flex flex-col items-center space-y-4 text-center">
          <div class="space-y-2">
            <h1 class="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl">
              Interactive Storytelling with AI
            </h1>
            <p class="mx-auto max-w-[700px] text-muted-foreground md:text-xl">
              Create, share, and experience dynamic stories where you become part of the narrative.
            </p>
          </div>
          <div class="flex flex-col sm:flex-row gap-4 mt-6">
            <Button @click="router.push('/shows')" size="lg">
              <PlayIcon class="mr-2 h-5 w-5" />
              Browse Shows
            </Button>
            <Button @click="router.push('/auth')" variant="outline" size="lg" v-if="!isLoggedIn">
              <UserPlusIcon class="mr-2 h-5 w-5" />
              Sign Up
            </Button>
            <Button @click="router.push('/my-shows')" variant="outline" size="lg" v-else>
              <FolderIcon class="mr-2 h-5 w-5" />
              My Shows
            </Button>
          </div>
        </div>
      </section>
  
      <!-- Features section -->
      <section class="w-full py-12 md:py-24 lg:py-32">
        <div class="container px-4 md:px-6">
          <div class="flex flex-col items-center justify-center space-y-4 text-center">
            <div class="space-y-2">
              <h2 class="text-3xl font-bold tracking-tighter md:text-4xl">How It Works</h2>
              <p class="mx-auto max-w-[700px] text-muted-foreground md:text-xl">
                SitChat brings your favorite shows to life with AI-powered interactive experiences
              </p>
            </div>
          </div>
          <div class="mx-auto grid max-w-5xl grid-cols-1 gap-6 md:grid-cols-3 lg:gap-12 mt-8">
            <div class="flex flex-col items-center space-y-4 text-center">
              <div class="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                <BookOpenIcon class="h-8 w-8 text-primary" />
              </div>
              <div class="space-y-2">
                <h3 class="text-xl font-bold">Create Stories</h3>
                <p class="text-muted-foreground">
                  Design your shows with detailed characters, relationships, and plot objectives.
                </p>
              </div>
            </div>
            <div class="flex flex-col items-center space-y-4 text-center">
              <div class="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                <MessageSquareIcon class="h-8 w-8 text-primary" />
              </div>
              <div class="space-y-2">
                <h3 class="text-xl font-bold">Participate</h3>
                <p class="text-muted-foreground">
                  Join the conversation as an interactive character, influencing the story's direction.
                </p>
              </div>
            </div>
            <div class="flex flex-col items-center space-y-4 text-center">
              <div class="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                <ShareIcon class="h-8 w-8 text-primary" />
              </div>
              <div class="space-y-2">
                <h3 class="text-xl font-bold">Share</h3>
                <p class="text-muted-foreground">
                  Publish your stories for others to experience and enjoy.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
  
      <!-- Popular Shows Section -->
      <section class="w-full py-12 md:py-24 lg:py-32 bg-muted">
        <div class="container px-4 md:px-6">
          <div class="flex flex-col items-center justify-center space-y-4 text-center">
            <div class="space-y-2">
              <h2 class="text-3xl font-bold tracking-tighter md:text-4xl">Popular Shows</h2>
              <p class="mx-auto max-w-[700px] text-muted-foreground md:text-xl">
                Discover interactive stories created by our community
              </p>
            </div>
          </div>
  
          <div v-if="loading" class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <Skeleton v-for="i in 3" :key="i" class="h-[300px] rounded-lg" />
          </div>
  
          <div v-else-if="popularShows.length > 0" class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <Card v-for="show in popularShows" :key="show.id" class="overflow-hidden flex flex-col">
              <CardHeader>
                <CardTitle>{{ show.name }}</CardTitle>
                <CardDescription class="line-clamp-2">{{ show.description }}</CardDescription>
              </CardHeader>
              <CardContent class="flex-grow">
                <div v-if="show.image_url" class="w-full h-40 bg-muted rounded-md mb-4 overflow-hidden">
                  <img :src="show.image_url" alt="Show thumbnail" class="w-full h-full object-cover" />
                </div>
                <div v-else class="w-full h-40 bg-background rounded-md mb-4 flex items-center justify-center">
                  <ImageIcon class="h-8 w-8 text-muted-foreground/40" />
                </div>
                <p class="text-sm text-muted-foreground">Created by {{ show.users?.username || 'Unknown' }}</p>
              </CardContent>
              <CardFooter>
                <Button @click="router.push(`/shows/${show.id}`)" variant="default" class="w-full">
                  View Show
                </Button>
              </CardFooter>
            </Card>
          </div>
  
          <div v-else class="mx-auto max-w-md p-8 mt-8 rounded-lg bg-background text-center">
            <FolderIcon class="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 class="text-xl font-bold mb-2">No Shows Yet</h3>
            <p class="text-muted-foreground mb-4">Be the first to create an interactive show!</p>
            <Button @click="router.push('/auth')" variant="default">
              Get Started
            </Button>
          </div>
  
          <div class="flex justify-center mt-8">
            <Button variant="outline" @click="router.push('/shows')">
              View All Shows
              <ArrowRightIcon class="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </section>
  
      <!-- Getting Started -->
      <section class="w-full py-12 md:py-24 lg:py-32">
        <div class="container px-4 md:px-6">
          <div class="grid gap-6 lg:grid-cols-[1fr_400px] lg:gap-12 xl:grid-cols-[1fr_600px]">
            <div class="flex flex-col justify-center space-y-4">
              <div class="space-y-2">
                <h2 class="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
                  Start Creating Your Own Stories
                </h2>
                <p class="max-w-[600px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                  It's easy to create your own interactive stories. Just sign up, create a show, define your characters,
                  and set your plot objectives.
                </p>
              </div>
              <div class="flex flex-col gap-2 min-[400px]:flex-row">
                <Button @click="router.push('/auth')" size="lg">
                  Get Started
                </Button>
                <Button @click="router.push('/shows')" variant="outline" size="lg">
                  Explore Shows
                </Button>
              </div>
            </div>
            <div class="mx-auto w-full max-w-[400px] lg:max-w-none bg-muted p-6 rounded-lg">
              <div class="space-y-4">
                <div class="space-y-2">
                  <h3 class="text-xl font-bold">Create a Show</h3>
                  <p class="text-muted-foreground">Define your show's setting and characters</p>
                </div>
                <div class="space-y-2">
                  <h3 class="text-xl font-bold">Create Episodes</h3>
                  <p class="text-muted-foreground">Define plot objectives and story progression</p>
                </div>
                <div class="space-y-2">
                  <h3 class="text-xl font-bold">Share & Play</h3>
                  <p class="text-muted-foreground">Invite others to experience your interactive narratives</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue'
  import { useRouter } from 'vue-router'
  import { useSupabase } from '@/composables/useSupabase'
  import { useToast } from 'vue-toastification'
  import { 
    ArrowRightIcon, BookOpenIcon, FolderIcon, ImageIcon, 
    MessageSquareIcon, PlayIcon, ShareIcon, UserPlusIcon
  } from 'lucide-vue-next'
  import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
  import { Button } from '@/components/ui/button'
  import { Skeleton } from '@/components/ui/skeleton'
  
  const router = useRouter()
  const { supabase } = useSupabase()
  const toast = useToast()
  
  // State
  const loading = ref(true)
  const popularShows = ref([])
  
  // Computed
  const isLoggedIn = computed(() => {
    return !!supabase.auth.getSession()?.data?.session
  })
  
  // Lifecycle
  onMounted(async () => {
    await fetchPopularShows()
  })
  
  // Methods
  async function fetchPopularShows() {
    loading.value = true
    
    try {
      // Fetch a few popular shows (for this demo, just getting the most recent)
      const { data, error } = await supabase
        .from('shows')
        .select('*, users:creator_id(username)')
        .order('created_at', { ascending: false })
        .limit(3)
      
      if (error) throw error
      
      popularShows.value = data || []
    } catch (error) {
      console.error('Error fetching popular shows:', error)
      toast.error('Failed to load shows')
    } finally {
      loading.value = false
    }
  }
  </script>