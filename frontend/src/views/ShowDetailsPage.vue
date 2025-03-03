<template>
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center min-h-screen">
      <div class="animate-spin h-12 w-12 border-4 border-primary border-t-transparent rounded-full"></div>
    </div>
    
    <!-- Error State -->
    <div v-else-if="error" class="p-4 bg-red-50 text-red-800 rounded-md m-4">
      Error: {{ error }}
    </div>
    
    <!-- Content when loaded -->
    <div v-else class="bg-background min-h-screen">
      <!-- Hero Section -->
      <div class="relative h-96 bg-muted">
        <img
          :src="show.image_url || '/placeholder-show.jpg'"
          class="w-full h-full object-cover absolute inset-0"
          alt="Show banner"
        >
        <div class="absolute inset-0 bg-gradient-to-t from-background via-background/60 to-transparent" />
        <div class="container mx-auto px-4 relative pt-32 h-full flex flex-col justify-end">
          <div class="max-w-3xl">
            <h1 class="text-5xl font-bold text-foreground mb-4 drop-shadow-lg text-white">{{ show.name }}</h1>
            <p class="text-lg text-muted-foreground mb-6 text-white">{{ show.description }}</p>
            <div class="flex gap-4 mb-8">
              <Button @click="startRandomEpisode" size="lg" class="gap-2">
                <PlayIcon class="h-6 w-6" />
                Play Random Episode
              </Button>
              <Button @click="createEpisode" variant="outline" size="lg" class="gap-2">
                <PlusIcon class="h-6 w-6" />
                Add Episode
              </Button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Content Container -->
      <div class="container mx-auto px-4 py-8">
        <!-- Episodes Section -->
        <section class="mb-12">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-3xl font-bold">Episodes</h2>
            <Button v-if="canEditShow" @click="createEpisode" variant="ghost" class="gap-2">
              View All
              <ChevronRightIcon class="h-4 w-4" />
            </Button>
          </div>
          <div v-if="episodes.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            <Card
              v-for="episode in episodes"
              :key="episode.id"
              class="group relative overflow-hidden cursor-pointer hover:bg-accent/10 transition-all"
              @click="startEpisode(episode)"
            >
              <CardHeader>
                <CardTitle class="line-clamp-1">{{ episode.name }}</CardTitle>
                <CardDescription class="line-clamp-2">{{ episode.description }}</CardDescription>
              </CardHeader>
            </Card>
          </div>
          <div v-else class="text-center py-12 text-muted-foreground">
            No episodes yet. Click "Add Episode" to create one.
          </div>
        </section>
        
        <!-- Characters Section -->
        <section class="mb-12">
          <h2 class="text-3xl font-bold mb-6">Characters</h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <div
              v-for="character in parsedCharacters"
              :key="character.name"
              class="text-center space-y-2"
            >
              <div class="relative w-full aspect-square rounded-full overflow-hidden bg-muted mx-auto">
                <!-- Character image placeholder -->
                <div class="flex items-center justify-center h-full bg-primary/10 text-primary text-2xl font-bold">
                  {{ character.name.charAt(0) }}
                </div>
              </div>
              <h3 class="font-medium">{{ character.name }}</h3>
            </div>
            <div v-if="parsedCharacters.length === 0" class="col-span-full text-center py-8 text-muted-foreground">
              No characters defined for this show yet.
            </div>
          </div>
        </section>
        
        <!-- Details Section -->
        <section class="mb-12">
          <h2 class="text-3xl font-bold mb-6">Details</h2>
          <div class="grid md:grid-cols-2 gap-8">
            <Card>
              <CardHeader>
                <CardTitle>About the Show</CardTitle>
              </CardHeader>
              <CardContent class="space-y-4">
                <div>
                  <div class="text-sm font-medium text-muted-foreground mb-1">Created By</div>
                  <p class="text-foreground">{{ getCreatorName() }}</p>
                </div>
                <div>
                  <div class="text-sm font-medium text-muted-foreground mb-1">Total Episodes</div>
                  <p class="text-foreground">{{ episodes.length }}</p>
                </div>
                <div v-if="show.relations">
                  <div class="text-sm font-medium text-muted-foreground mb-1">Relations</div>
                  <p class="text-foreground">{{ show.relations }}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>
        
        <!-- Debug Info (comment out in production) -->
        <!-- <div class="mt-8 p-4 bg-gray-100 rounded">
          <h3 class="text-lg font-semibold mb-2">Debug Info:</h3>
          <div>Show Name: {{ show.name || 'Not loaded' }}</div>
          <div>Characters Count: {{ parsedCharacters.length }}</div>
          <pre class="text-xs mt-2 bg-gray-200 p-2 rounded overflow-auto max-h-40">{{ JSON.stringify(show, null, 2) }}</pre>
        </div> -->
      </div>
    </div>
  </template>
  
  <script>
  import { Button } from '@/components/ui/button'
  import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
  import { Badge } from '@/components/ui/badge'
  import { PlayIcon, PlusIcon, ChevronRightIcon } from 'lucide-vue-next'
  
  export default {
    components: {
      Button,
      Card,
      CardHeader,
      CardTitle,
      CardDescription,
      CardContent,
      Badge,
      PlayIcon,
      PlusIcon,
      ChevronRightIcon
    },
    name: 'ShowDetailsPage',
    data() {
      return {
        loading: true, // Start with loading state
        error: null,   // Add error state
        show_id: this.$route.params.id,
        API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
        session_token: localStorage.getItem('supabase_session') 
          ? JSON.parse(localStorage.getItem('supabase_session')).access_token 
          : null,
        currentUserId: localStorage.getItem('supabase_session') 
          ? JSON.parse(localStorage.getItem('supabase_session')).user?.id 
          : null,
        show: {
          id: '',
          name: '',
          image_url: '',
          description: '',
          creator_id: '',
          users: { username: '' },
          characters: '[]',
          relations: ''
        },
        episodes: [],
      }
    },
    computed: {
      canEditShow() {
        // Check if current user is the creator of the show
        return this.currentUserId && this.currentUserId === this.show.creator_id
      },
      parsedCharacters() {
        try {
          if (!this.show.characters) return [];
          
          if (typeof this.show.characters === 'string') {
            return JSON.parse(this.show.characters);
          } else if (Array.isArray(this.show.characters)) {
            return this.show.characters;
          } else {
            console.error('Characters in unexpected format:', this.show.characters);
            return [];
          }
        } catch (error) {
          console.error('Error parsing characters:', error, this.show.characters);
          return [];
        }
      }
    },
    methods: {
      getCreatorName() {
        return this.show.users?.username || 'Unknown creator'
      },
      startEpisode(episode) {
        alert(`Starting episode: ${episode.name}`)
      },
      startRandomEpisode() {
        if (this.episodes.length === 0) {
          alert('No episodes available')
          return
        }
        const randomEpisode = this.episodes[Math.floor(Math.random() * this.episodes.length)]
        this.startEpisode(randomEpisode)
      },
      createEpisode() {
        // Redirect to create episode page or show modal
        alert('Redirect to create episode page')
      },
      async getShow() {
        try {
          this.loading = true
          this.error = null
          
          // Check if we have a session token
          if (!this.session_token) {
            throw new Error('No authentication token available')
          }
          
          const response = await fetch(`${this.API_BASE_URL}/api/shows/${this.show_id}`, {
            headers: {
              'Authorization': `Bearer ${this.session_token}`
            }
          })
          
          if (!response.ok) {
            throw new Error(`API responded with status: ${response.status}`)
          }
          
          const data = await response.json()
          console.log('Show data:', data.show)
          
          // Replace the entire show object to ensure reactivity
          this.show = { ...data.show }
          
          // Now fetch episodes
          await this.getEpisodes()
          
          this.loading = false
        } catch (error) {
          console.error('Error fetching show:', error)
          this.error = `Failed to load show: ${error.message}`
          this.loading = false
        }
      },
      async getEpisodes() {
        try {
          const response = await fetch(`${this.API_BASE_URL}/api/shows/${this.show_id}/episodes`, {
            headers: {
              'Authorization': `Bearer ${this.session_token}`
            }
          })
          
          if (response.ok) {
            const data = await response.json()
            this.episodes = data
          } else {
            console.warn(`Could not fetch episodes: ${response.status}`)
            this.episodes = []
          }
        } catch (error) {
          console.error('Error fetching episodes:', error)
          this.episodes = []
        }
      }
    },
    mounted() {
      if (!this.session_token) {
        this.error = 'Authentication required'
        this.loading = false
        // Optionally redirect to login
        // this.$router.push('/auth')
      } else {
        this.getShow()
      }
    }
  }
  </script>
  
  <style>
  /* Custom gradient overlay */
  .bg-gradient-to-t {
    background-image: linear-gradient(to top, var(--tw-gradient-from), var(--tw-gradient-via), var(--tw-gradient-to));
  }
  </style>