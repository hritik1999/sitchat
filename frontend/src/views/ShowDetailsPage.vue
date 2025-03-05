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
            class="group relative overflow-hidden cursor-pointer hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
            @click="startEpisode(episode)"
          >
            <div class="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            
            <!-- Play Button Overlay -->
            <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <div class="bg-background/90 p-4 rounded-full shadow-lg">
                <PlayIcon class="h-8 w-8 text-primary translate-x-[1px]" />
              </div>
            </div>

            <CardHeader class="relative">
              <div class="absolute top-2 right-2 bg-primary/80 text-primary-foreground rounded-full p-2">
                <PlayIcon class="h-4 w-4" />
              </div>
              <CardTitle class="line-clamp-1 text-lg">{{ episode.name }}</CardTitle>
              <CardDescription class="line-clamp-2 text-sm mt-2">{{ episode.description }}</CardDescription>
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
      
    </div>
  </div>
  <!-- Player Dialog -->
  <Dialog :open="playerDialog" @update:open="closePlayerDialog">
    <DialogContent class="sm:max-w-[600px]">
      <DialogHeader>
        <DialogTitle>Start Episode</DialogTitle>
        <DialogDescription>
          Enter your character details to begin "{{ selectedEpisode?.name }}"
        </DialogDescription>
      </DialogHeader>
      
      <form @submit.prevent="startPlaying(selectedEpisode?.id)" class="space-y-4">
        <div class="space-y-2">
          <Label for="player-name">Your Character Name</Label>
          <Input id="player-name" v-model="playerForm.player_name" placeholder="Your character's name" required />
        </div>
        
        <div class="space-y-2">
          <Label for="player-description">Character Description</Label>
          <Textarea id="player-description" v-model="playerForm.player_description" placeholder="Brief description of your character" />
        </div>
      </form>
      
      <DialogFooter>
        <Button @click="closePlayerDialog" variant="outline">Cancel</Button>
        <Button @click="startPlaying(selectedEpisode?.id)" :disabled="isStarting">
          <Loader2Icon v-if="isStarting" class="h-4 w-4 mr-2 animate-spin" />
          {{ isStarting ? 'Starting...' : 'Start Episode' }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<script>
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { PlayIcon, PlusIcon, ChevronRightIcon, Loader2Icon } from 'lucide-vue-next'
import { useToast } from 'vue-toastification'
import { fetchApi } from '@/lib/utils'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'

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
    ChevronRightIcon,
    Loader2Icon,
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
    Label,
    Input,
    Textarea
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
      playerDialog: false,
      selectedEpisode: null,
      playerForm: {
        player_name: '',
        player_description: ''
      },
      isStarting: false,
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
    createEpisode() {
      // Redirect to create episode page or show modal
      this.$router.push('/create/episode/' + this.show_id)
    },
    closePlayerDialog() {
      this.playerDialog = false
    },
    startEpisode(episode) {
      this.selectedEpisode = episode
      this.playerDialog = true
    },
    async startPlaying(episodeId) {
      this.isStarting = true
      const toast = useToast()
      
      try {
        console.log('Episode ID:', episodeId)
        console.log('Player Data:', this.playerForm)
        
        // Your episode starting logic
        // Use imported fetchApi utility function for consistent authentication
        const data = await fetchApi(`api/episodes/${episodeId}/chats`, {
          method: 'POST', 
          body: JSON.stringify(this.playerForm)
        });
        
        if (data.error) {
          toast.error(`Error starting episode: ${data.error}`)
        } else {
          this.$router.push(`/show/${this.show_id}/chat/${data.chat.id}`)
        }
      } catch (error) {
        toast.error(`Error starting episode: ${error.message}`)
      } finally {
        this.isStarting = false
      }
    },
    startRandomEpisode() {
      if (this.episodes.length === 0) {
        alert('No episodes available')
        return
      }
      const randomEpisode = this.episodes[Math.floor(Math.random() * this.episodes.length)]
      this.startEpisode(randomEpisode)
    },
    // Using imported fetchApi from utils.js
    async getShow() {
      const toast = useToast(); // Get the toast instance
      
      try {
        this.loading = true
        this.error = null
        
        // Using imported fetchApi which manages auth state properly
        const data = await fetchApi(`api/shows/${this.show_id}`)
        
        // Replace the entire show object to ensure reactivity
        this.show = { ...data.show }
        
        // Now fetch episodes
        await this.getEpisodes()
        
      } catch (error) {
        console.error('Error fetching show:', error)
        this.error = `Failed to load show: ${error.message}`
        toast.error(`Failed to load show: ${error.message}`)
      } finally {
        this.loading = false
      }
    },
    async getEpisodes() {
      try {
        const data = await fetchApi(`api/show/${this.show_id}/episodes`)
        this.episodes = data.episodes
      } catch (error) {
        console.error('Error fetching episodes:', error)
        this.episodes = []
      }
    }
  },
  mounted() {
    // Don't check for session token directly
    // The imported fetchApi will handle auth properly and redirect if needed
    this.getShow()
  }
}
</script>

<style>
/* Custom gradient overlay */
.bg-gradient-to-t {
  background-image: linear-gradient(to top, var(--tw-gradient-from), var(--tw-gradient-via), var(--tw-gradient-to));
}
</style>