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
    <div class="relative min-h-[20rem] sm:h-96 bg-muted">
      <img
        :src="show.image_url || '/placeholder-show.jpg'"
        class="w-full h-full object-cover object-top sm:object-center absolute inset-0"
        alt="Show banner"
      />
      <div class="absolute inset-0 bg-gradient-to-t from-background via-background/60 to-transparent" />
      <div class="container mx-auto px-4 relative pt-8 sm:pt-32 h-full flex flex-col justify-end">
        <div class="max-w-3xl mt-20" >
          <h1 class="text-2xl sm:text-4xl lg:text-5xl font-bold text-white mb-3 sm:mb-4 drop-shadow-lg ">
            {{ show.name }}
          </h1>
          <p class="text-sm sm:text-lg text-white mb-4 sm:mb-6 line-clamp-3 sm:line-clamp-none">
            {{ show.description }}
          </p>
          <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 mb-6 sm:mb-8">
            <Button @click="startRandomEpisode" size="sm" class="sm:size-lg gap-2">
              <PlayIcon class="h-5 w-5 sm:h-6 sm:w-6" />
              Play Random Episode
            </Button>
            <Button @click="createEpisode" variant="outline" size="sm" class="sm:size-lg gap-2">
              <PlusIcon class="h-5 w-5 sm:h-6 sm:w-6" />
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
          <h2 class="text-2xl sm:text-3xl font-bold">Episodes</h2>
        </div>
        <div v-if="episodes.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          <Card
            v-for="episode in episodes"
            :key="episode.id"
            class="group relative overflow-hidden hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-0 bg-muted/10"
          >
            <CardHeader class="relative">
              <!-- Top accent bar -->
              <div class="absolute top-0 left-0 right-0 h-1 bg-primary/50"></div>

              <CardTitle class="text-lg mt-3 font-semibold text-foreground">
                {{ episode.name }}
              </CardTitle>
              
              <!-- Expandable Description -->
              <div class="relative">
                <div 
                  class="text-sm text-muted-foreground transition-all duration-300"
                  :class="expandedDescriptions[episode.id] ? 'line-clamp-none' : 'line-clamp-3'"
                >
                  {{ episode.description || 'No description available' }}
                </div>
                <button
                  v-if="showReadMore(episode.description)"
                  @click.stop="toggleDescription(episode.id)"
                  class="text-primary font-medium hover:underline mt-1 text-sm"
                >
                  {{ expandedDescriptions[episode.id] ? 'Show less' : 'Read more' }}
                </button>
              </div>

              <!-- Stats Row -->
              <div class="flex gap-4 mt-4 text-sm">
                <div class="flex items-center gap-1.5 text-muted-foreground">
                  <StarIcon class="h-4 w-4 text-amber-500" />
                  <span>{{ episode.average_ratings?.toFixed(1) || '0.0' }}</span>
                </div>
                <div class="flex items-center gap-1.5 text-muted-foreground">
                  <ClockIcon class="h-4 w-4 text-emerald-500" />
                  <span>{{ calculateDuration(episode) }}m</span>
                </div>
                <div class="flex items-center gap-1.5 text-muted-foreground">
                  <EyeIcon class="h-4 w-4 text-blue-500" />
                  <span>{{ episode.views?.toLocaleString() || 0 }}</span>
                </div>
              </div>
            </CardHeader>

            <CardContent class="pb-4">
              <Button 
                @click="startEpisode(episode)" 
                class="w-full gap-2 hover:scale-[1.02] transition-transform"
              >
                <PlayIcon class="h-4 w-4" />
                Start Episode
              </Button>
            </CardContent>
          </Card>
        </div>
        <div v-else class="text-center py-12 text-muted-foreground">
          No episodes yet. Click "Add Episode" to create one.
        </div>
      </section>
      
      <!-- Characters Section -->
      <section class="mb-12">
        <h2 class="text-2xl sm:text-3xl font-bold mb-6">Characters</h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <div
            v-for="character in parsedCharacters"
            :key="character.name"
            class="text-center space-y-2"
          >
            <div class="relative w-full aspect-square rounded-full overflow-hidden bg-muted mx-auto">
              <img :src="character.image_url" alt="Character Image" class="object-cover w-full h-full" />
            </div>
            <h3 class="font-medium text-foreground">{{ character.name }}</h3>
          </div>
          <div v-if="parsedCharacters.length === 0" class="col-span-full text-center py-8 text-muted-foreground">
            No characters defined for this show yet.
          </div>
        </div>
      </section>
      
      <!-- Details Section -->
      <section class="mb-12">
        <h2 class="text-2xl sm:text-3xl font-bold mb-6">Details</h2>
        <div class="grid grid-cols-1 gap-8">
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
              <div>
                <div class="text-sm font-medium text-muted-foreground mb-1">Total Views</div>
                <p class="text-foreground">{{ episodes.reduce((sum, ep) => sum + (ep.views || 0), 0).toLocaleString() }}</p>
              </div>
              <div>
                <div class="text-sm font-medium text-muted-foreground mb-1">Average Rating</div>
                <p class="text-foreground">{{ (episodes.reduce((sum, ep) => sum + (ep.average_ratings || 0), 0) / (episodes.length || 1)).toFixed(1) }}</p>
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
    <DialogContent class="max-w-[95vw] sm:max-w-[650px] mx-2">
      <DialogHeader>
        <DialogTitle class="text-xl sm:text-2xl flex items-center gap-2 break-words dark:text-white">
          <PlayIcon class="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
          <span>{{ selectedEpisode?.name }}</span>
        </DialogTitle>
      </DialogHeader>

      <div class="space-y-4 sm:space-y-6">
        <!-- Player Info Grid -->
        <div class="grid grid-cols-1 xs:grid-cols-2 gap-3 sm:gap-4 p-3 sm:p-4 bg-muted/30 rounded-lg">
          <!-- Username Input -->
          <div class="space-y-1">
            <Label class="text-xs sm:text-sm font-medium text-muted-foreground dark:text-white">Your Name</Label>
            <Input 
              v-model="tempUserName" 
              class="text-sm sm:text-base text-foreground font-semibold"
              placeholder="Enter your name"
            />
          </div>
          
          <!-- Role Display -->
          <div class="space-y-1">
            <Label class="text-xs sm:text-sm font-medium text-muted-foreground dark:text-white">Your Role</Label>
            <p class="text-sm sm:text-base text-foreground font-semibold dark:text-white">
              {{ selectedEpisode?.player_role || 'Adventurer' }}
            </p>
          </div>

          <!-- Chat Speed Slider -->
          <div class="col-span-1 xs:col-span-2 space-y-4">
            <div class="space-y-1">
              <Label class="text-xs sm:text-sm font-medium text-muted-foreground dark:text-white">
                Chat Speed ({{ chatSpeed }}x)
              </Label>
              <div class="flex items-center gap-4">
                <input
                  type="range"
                  v-model="chatSpeed"
                  min="1"
                  max="5"
                  step="0.25"
                  class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                />
              </div>
              <p class="text-xs text-muted-foreground">
                Adjust how fast the AI generates responses
              </p>
            </div>
          </div>
        </div>
      </div>

      <DialogFooter class="mt-4 flex flex-col sm:flex-row gap-2 sm:gap-4">
        <Button @click="closePlayerDialog" variant="outline" class="w-full sm:w-auto px-4 sm:px-6 dark:bg-white">
          Cancel
        </Button>
        <Button 
          @click="startPlaying(selectedEpisode?.id)" 
          :disabled="isStarting" 
          class="w-full sm:w-auto px-4 sm:px-8"
        >
          <Loader2Icon v-if="isStarting" class="h-4 w-4 mr-2 animate-spin" />
          <span v-else>Begin Adventure</span>
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>


<script>
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { PlayIcon, PlusIcon, ChevronRightIcon, Loader2Icon,StarIcon, EyeIcon, ClockIcon,ChevronDownIcon, ScrollTextIcon  } from 'lucide-vue-next'
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
    Textarea,
    StarIcon,
    EyeIcon, 
    ClockIcon,
    ChevronDownIcon,
    ScrollTextIcon
  },
  name: 'ShowDetailsPage',
  data() {
    return {
      loading: true, // Start with loading state
      error: null,   // Add error state
      show_id: this.$route.params.id,
      API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
      user_name : localStorage.getItem('username').split(' ')[0] || 'player',
      tempUserName: '',
      chatSpeed : parseFloat(localStorage.getItem('chatSpeed')) || 2.5,
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
      isStarting: false,
      expandedDescriptions: {},
    }
  },
  computed: {
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
    this.tempUserName = this.user_name // Initialize with current username
    this.playerDialog = true
  },
  async startPlaying(episodeId) {
    this.isStarting = true
    const toast = useToast()
    
    try {
      // Save chat speed to localStorage
      localStorage.setItem('chatSpeed', this.chatSpeed.toString())
      
      // Update username in localStorage if changed
      if (this.tempUserName !== this.user_name) {
        localStorage.setItem('username', this.tempUserName)
        this.user_name = this.tempUserName
      }

      const data = await fetchApi(`api/episodes/${episodeId}/chats`, {
        method: 'POST', 
        body: JSON.stringify({
          player_name: this.tempUserName,
          player_description: this.selectedEpisode?.player_role || '',
          chat_speed: this.chatSpeed
        })
      })
      
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
    },
    calculateDuration(episode) {
    try {
      const objectives = typeof episode.plot_objectives === 'string' 
        ? JSON.parse(episode.plot_objectives || '[]')
        : episode.plot_objectives || [];
      return objectives.length * 2;
    } catch (e) {
      console.error('Error parsing plot objectives:', e);
      return 0;
    }
  },
  toggleDescription(episodeId) {
    // Fixed the $set error by using direct property access
    this.expandedDescriptions = {
      ...this.expandedDescriptions,
      [episodeId]: !this.expandedDescriptions[episodeId]
    };
  },
  showReadMore(description) {
    return description?.length > 100;
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

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
</style>