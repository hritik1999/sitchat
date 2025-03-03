<template>
    <div class="min-h-screen flex flex-col">
      <!-- Desktop Navbar -->
      <nav class="bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b hidden md:block">
        <div class="container mx-auto px-4 py-3 flex items-center justify-between">
          <div class="flex items-center gap-8">
            <router-link to="/" class="flex items-center gap-2">
              <span class="text-2xl font-bold">Sitchat</span>
            </router-link>
            <div class="flex gap-6">
              <router-link to="/shows" class="text-sm font-medium hover:text-primary transition-colors">
                Shows
              </router-link>
              <router-link to="/leaderboards" class="text-sm font-medium hover:text-primary transition-colors">
                Leaderboards
              </router-link>
            </div>
          </div>
  
          <div class="flex items-center gap-4">
            <DropdownMenu v-if="userSession">
              <DropdownMenuTrigger class="flex items-center gap-1 hover:bg-accent rounded-full p-2">
                <div class="h-8 w-8 rounded-full bg-muted flex items-center justify-center">
                  <UserIcon class="h-4 w-4" />
                </div>
                <ChevronDownIcon class="h-4 w-4" />
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem>
                  <UserIcon class="mr-2 h-4 w-4" />
                  Profile
                </DropdownMenuItem>
                <DropdownMenuItem @click="logout">
                  <LogOutIcon class="mr-2 h-4 w-4" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            <Button v-else @click="login">
              Sign In
            </Button>
          </div>
        </div>
      </nav>
  
      <!-- Mobile Bottom Nav -->
    <div class="fixed bottom-0 left-0 right-0 border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 md:hidden z-50">
      <div class="grid grid-cols-3 gap-4 p-2">
        <router-link 
          to="/shows"
          class="flex flex-col items-center gap-1 text-xs font-medium hover:text-primary transition-colors"
        >
          <TvIcon class="h-5 w-5" />
          <span>Shows</span>
        </router-link>
        <router-link 
          to="/leaderboards"
          class="flex flex-col items-center gap-1 text-xs font-medium hover:text-primary transition-colors"
        >
          <TrophyIcon class="h-5 w-5" />
          <span>Leaderboards</span>
        </router-link>
        <router-link 
          to="/profile"
          class="flex flex-col items-center gap-1 text-xs font-medium hover:text-primary transition-colors"
        >
          <UserIcon class="h-5 w-5" />
          <span>Profile</span>
        </router-link>
      </div>
    </div>
  
      <!-- Main Content -->
      <main class="flex-1 container mx-auto px-4 pb-16 md:pb-4">
        <div class="py-8">
          <div class="flex justify-between items-center mb-8">
            <div>
              <h1 class="text-3xl font-bold tracking-tight">Browse Shows</h1>
              <p class="text-muted-foreground">Discover interactive shows created by the community</p>
            </div>
            <Button v-if="userSession" @click="navigateToCreate" variant="default">
              <PlusIcon class="h-4 w-4 mr-2" />
              Create Show
            </Button>
          </div>
  
          <!-- Shows Grid -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            <Card 
              v-for="show in shows" 
              :key="show.id" 
              class="group relative overflow-hidden transition-transform hover:scale-105 hover:shadow-lg"
            >
              <div class="aspect-video bg-muted relative">
                <img 
                  :src="show.imageUrl" 
                  class="w-full h-full object-cover"
                  alt="Show thumbnail"
                >
                <div class="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent" />
              </div>
              <CardHeader>
                <CardTitle class="line-clamp-1">{{ show.name }}</CardTitle>
                <CardDescription class="line-clamp-2">{{ show.description }}</CardDescription>
              </CardHeader>
              <CardContent class="pt-0">
                <Button class="w-full">View Show</Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
  
      <!-- Footer -->
      <footer class="border-t bg-background hidden md:block">
        <div class="container mx-auto px-4 py-8">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 class="text-lg font-semibold mb-4">Sitchat</h3>
              <p class="text-sm text-muted-foreground">
                Bringing stories to life through interactive AI experiences
              </p>
            </div>
            <div>
              <h3 class="text-lg font-semibold mb-4">Legal</h3>
              <ul class="space-y-2 text-sm">
                <li><a href="#" class="hover:text-primary transition-colors">Privacy Policy</a></li>
                <li><a href="#" class="hover:text-primary transition-colors">Terms of Service</a></li>
              </ul>
            </div>
            <div>
              <h3 class="text-lg font-semibold mb-4">Social</h3>
              <div class="flex gap-4">
                <a href="#" class="hover:text-primary transition-colors">
                  <!-- <TwitterIcon class="h-5 w-5" /> -->
                </a>
                <a href="#" class="hover:text-primary transition-colors">
                  <!-- <DiscordIcon class="h-5 w-5" /> -->
                </a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  </template>
  
  <script>
  import { Button } from '@/components/ui/button'
  import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
  import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
  } from '@/components/ui/dropdown-menu'
  import {
    ChevronDownIcon,
    DiscIcon as TrophyIcon,
    ImageIcon,
    PlusIcon,
    UserIcon,
    LogOutIcon,
    TvIcon,
  } from 'lucide-vue-next'
  import { useRouter } from 'vue-router'

export default {
    name: 'ShowPage',
    components: {
      Button,
      Card,
      CardContent,
      CardDescription,
      CardHeader,
      CardTitle,
      ChevronDownIcon,
      TrophyIcon,
      ImageIcon,
      PlusIcon,
      UserIcon,
      LogOutIcon,
      TvIcon,
      DropdownMenu,
      DropdownMenuContent,
      DropdownMenuItem,
      DropdownMenuTrigger,
    },
    setup() {
      const router = useRouter()
  
      const navigateToCreate = () => {
        router.push('/create')
      }
  
      return {
        navigateToCreate
      }
    },
    data() {
      return {
        userSession: null, // Replace with actual auth state
        shows: [...Array(8)].map((_, i) => ({
          id: i + 1,
          name: `Show ${i + 1}`,
          description: 'An amazing interactive show with multiple characters and storylines',
          imageUrl: `https://picsum.photos/300/200?random=${i}`,
        })),
      }
    },
    methods: {
      login() {
        // Implement login logic
      },
      logout() {
        // Implement logout logic
      },
    },
}
</script>
  
  <style>
  /* Add custom transitions */
  .hover\:scale-105 {
    transition: transform 0.2s ease;
  }
  
  .group:hover .group-hover\:opacity-100 {
    opacity: 1;
  }
  </style>