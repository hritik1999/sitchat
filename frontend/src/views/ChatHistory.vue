<template>
  <div class="bg-background min-h-screen">
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center min-h-screen">
      <div class="animate-spin h-12 w-12 border-4 border-primary border-t-transparent rounded-full"></div>
    </div>
    
    <!-- Error State -->
    <div v-else-if="error" class="p-4 bg-red-50 dark:bg-red-900/30 text-red-800 dark:text-red-300 rounded-md m-4">
      Error: {{ error }}
    </div>
    
    <!-- Content when loaded -->
    <div v-else class="container mx-auto px-4 py-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold mb-2">Your Chat History</h1>
        <p class="text-muted-foreground">Continue your adventures</p>
      </div>
      
      <!-- Empty state -->
      <div v-if="chatHistory.length === 0" class="text-center py-16">
        <div class="mb-4">
          <MessageSquareIcon class="h-12 w-12 mx-auto text-muted-foreground/50" />
        </div>
        <h2 class="text-xl font-semibold mb-2">No chats yet</h2>
        <p class="text-muted-foreground mb-6">Start an episode to begin your storytelling journey</p>
        <Button @click="$router.push('/')" size="lg" class="gap-2">
          <PlayIcon class="h-5 w-5" />
          Browse Shows
        </Button>
      </div>
      
      <!-- Chat History -->
      <div v-else class="space-y-8">
        <div v-for="(showData, index) in chatHistory" :key="index" class="space-y-4">
          <!-- Show Header -->
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="h-10 w-10 rounded-md bg-primary/10 flex items-center justify-center text-primary font-bold overflow-hidden">
                <img v-if="showData.show_image" :src="showData.show_image" alt="Show image" class="h-full w-full object-cover">
                <span v-else>{{ showData.show_name.charAt(0) }}</span>
              </div>
              <h2 class="text-xl font-bold">{{ showData.show_name }}</h2>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              @click="$router.push(`/show/${showData.show_id}`)"
              class="gap-1"
            >
              View Show
              <ChevronRightIcon class="h-4 w-4" />
            </Button>
          </div>
          
          <!-- Episodes Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card
              v-for="chat in showData.chats"
              :key="chat.id"
              class="overflow-hidden border border-gray-200 dark:border-gray-800 rounded-lg hover:shadow-md transition-all duration-200 cursor-pointer bg-white dark:bg-gray-900"
              @click="continueChat(chat.id)"
            >
              <CardHeader class="py-2 px-3">
                <CardTitle class="flex justify-between items-center text-base">
                  <span class="truncate">{{ chat.episode_name }}</span>
                  <Badge
                    :class="chat.completed ? 
                      'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 px-1.5 py-0.5 text-xs rounded-full' : 
                      'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 px-1.5 py-0.5 text-xs rounded-full'"
                  >
                    {{ chat.completed ? 'Completed' : 'In Progress' }}
                  </Badge>
                </CardTitle>
                <CardDescription class="text-xs text-gray-500 dark:text-gray-400">
                  Last played: {{ formatDate(chat.last_activity) }}
                </CardDescription>
              </CardHeader>
              
              <CardContent class="space-y-3 py-2 px-3">
                <!-- Compact Recap with Preview -->
                <div class="space-y-1">
                  <div class="text-xs text-gray-600 dark:text-gray-300">
                    <span class="font-medium text-gray-700 dark:text-gray-300 mr-1">Recap:</span>
                    <span>
                      {{ chat.expandRecap ? 
                        chat.chat_summary : 
                        (chat.chat_summary.length > 60 ? chat.chat_summary.substring(0, 60) + '...' : chat.chat_summary) }}
                    </span>
                    <span 
                      v-if="chat.chat_summary.length > 60"
                      @click.stop="toggleRecap(chat)" 
                      class="text-blue-600 dark:text-blue-400 font-medium text-xs ml-1 cursor-pointer hover:underline inline-flex items-center"
                    >
                      {{ chat.expandRecap ? 'less' : 'more' }}
                      <ChevronDownIcon 
                        class="h-3 w-3 transition-transform duration-200"
                        :class="{ 'transform rotate-180': chat.expandRecap }"
                      />
                    </span>
                  </div>
                </div>
                
                <!-- Progress Bar -->
                <div class="space-y-1">
                  <div class="flex justify-between items-center text-xs text-gray-500 dark:text-gray-400">
                    <span>Progress</span>
                    <span>{{ chat.current_objective_index }}/{{ chat.total_objectives }}</span>
                  </div>
                  <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                    <div
                      class="bg-blue-600 dark:bg-blue-500 h-2 rounded-full transition-all duration-300"
                      :style="{ width: `${calculateProgress(chat.current_objective_index, chat.total_objectives)}%` }"
                    ></div>
                  </div>
                </div>
                
                <div class="flex justify-between items-center pt-1 text-xs">
                  <span class="text-gray-600 dark:text-gray-400">Playing as: {{ chat.player_name }}</span>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    @click.stop="continueChat(chat.id)" 
                    :class="chat.completed ? 
                      'gap-1 bg-gray-50 hover:bg-gray-100 text-gray-700 dark:bg-gray-900/20 dark:hover:bg-gray-900/30 dark:text-gray-300 border border-gray-200 dark:border-gray-800 rounded-md px-2 py-0.5 text-xs' :
                      'gap-1 bg-blue-50 hover:bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:hover:bg-blue-900/30 dark:text-blue-300 border border-blue-200 dark:border-blue-800 rounded-md px-2 py-0.5 text-xs'"
                  >
                    <div v-if="chat.completed" class="flex items-center gap-1">
                      <MessageCircleIcon class="h-4 w-4" />
                      View
                    </div>
                    <div v-else class="flex items-center gap-1">
                      <MessageSquareIcon class="h-4 w-4" />
                      Continue
                    </div>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { 
  ChevronRightIcon, 
  PlayIcon, 
  MessageSquareIcon, 
  MessageCircleIcon,
  ChevronDownIcon
} from 'lucide-vue-next'
import { fetchApi } from '@/lib/utils'
import { useToast } from 'vue-toastification'

export default {
  name: 'ChatHistoryPage',
  components: {
    Button,
    Badge,
    Card,
    CardHeader,
    CardTitle,
    CardDescription,
    CardContent,
    ChevronRightIcon,
    PlayIcon,
    MessageSquareIcon,
    MessageCircleIcon,
    ChevronDownIcon
  },
  
  data() {
    return {
      loading: true,
      error: null,
      chatHistory: [],
      API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
      showCache: new Map(),
      episodeCache: new Map()
    }
  },
  
  methods: {
    async fetchChatHistory() {
      const toast = useToast()
      
      try {
        this.loading = true
        this.error = null
        
        // Get all chats
        const chatData = await fetchApi('api/chats')
        
        if (!chatData || !chatData.chats) {
          throw new Error('Invalid response format')
        }
        
        if (chatData.chats.length === 0) {
          this.chatHistory = []
          this.loading = false
          return
        }
        
        // Extract unique show IDs and episode IDs for batch fetching
        const chatsByShowAndEpisode = this.groupChatsByShowAndEpisode(chatData.chats)
        
        // Batch fetch all shows and episodes in parallel
        await this.batchFetchShowsAndEpisodes(chatsByShowAndEpisode)
        
        // Process chats with cached data
        this.processChatHistory(chatData.chats)
        
      } catch (error) {
        console.error('Error fetching chat history:', error)
        this.error = `Failed to load chat history: ${error.message}`
        toast.error(`Failed to load chat history: ${error.message}`)
      } finally {
        this.loading = false
      }
    },
    
    groupChatsByShowAndEpisode(chats) {
      const showMap = new Map()
      
      chats.forEach(chat => {
        if (!chat.show_id) return
        
        if (!showMap.has(chat.show_id)) {
          showMap.set(chat.show_id, new Set())
        }
        
        if (chat.episode_id) {
          showMap.get(chat.show_id).add(chat.episode_id)
        }
      })
      
      return showMap
    },
    
    async batchFetchShowsAndEpisodes(chatsByShowAndEpisode) {
      const showPromises = []
      const episodePromises = []
      
      // Create all promises for shows
      chatsByShowAndEpisode.forEach((episodeIds, showId) => {
        // Fetch show data
        showPromises.push(
          fetchApi(`api/shows/${showId}`)
            .then(show => {
              // Important: Match original code structure - the show data needs to be accessed correctly
              this.showCache.set(showId, show.show || show)
            })
            .catch(err => {
              console.error(`Error fetching show ${showId}:`, err)
              // Store empty object to prevent repeated failed requests
              this.showCache.set(showId, { name: 'Unknown Show' })
            })
        )
        
        // Create all promises for episodes
        episodeIds.forEach(epId => {
          episodePromises.push(
            fetchApi(`api/show/${showId}/episodes/${epId}`)
              .then(episode => {
                this.episodeCache.set(`${showId}-${epId}`, episode)
              })
              .catch(err => {
                console.error(`Error fetching episode ${epId} for show ${showId}:`, err)
                // Store empty object to prevent repeated failed requests
                this.episodeCache.set(`${showId}-${epId}`, { 
                  episode: { name: 'Unknown Episode', plot_objectives: '[]' } 
                })
              })
          )
        })
      })
      
      // Wait for all fetch operations to complete
      await Promise.all([
        Promise.all(showPromises),
        Promise.all(episodePromises)
      ])
    },
    
    processChatHistory(chats) {
      // Group chats by show
      const showMap = new Map()
      
      for (const chat of chats) {
        if (!chat.show_id || !chat.episode_id) continue
        
        const showId = chat.show_id
        const episodeId = chat.episode_id
        const cacheKey = `${showId}-${episodeId}`
        
        // Skip if missing data
        if (!this.episodeCache.has(cacheKey) || !this.showCache.has(showId)) continue
        
        // Get episode from cache
        const episodeData = this.episodeCache.get(cacheKey)
        if (!episodeData || !episodeData.episode) continue
        
        // Get show from cache
        const showData = this.showCache.get(showId)
        if (!showData) continue
        
        // Parse objectives - safely
        let totalObjectives = 5
        try {
          if (episodeData.episode.plot_objectives) {
            const objectives = JSON.parse(episodeData.episode.plot_objectives)
            if (Array.isArray(objectives)) {
              totalObjectives = objectives.length || 5
            }
          }
        } catch (e) {
          console.warn('Error parsing objectives:', e)
        }
        
        // Process chat data with defaults for safety
        const chatData = {
          id: chat.id,
          episode_id: episodeId,
          episode_name: episodeData.episode.name || 'Unknown Episode',
          current_objective_index: typeof chat.current_objective_index === 'number' ? chat.current_objective_index : 0,
          total_objectives: totalObjectives,
          player_name: chat.player_name || 'Player',
          player_description: chat.player_description || '',
          chat_summary: chat.chat_summary || '',
          completed: Boolean(chat.story_completed),
          last_activity: chat.updated_at || chat.created_at || new Date().toISOString(),
          expandRecap: false
        }
        
        // Add to show group or create new group
        if (showMap.has(showId)) {
          showMap.get(showId).chats.push(chatData)
        } else {
          showMap.set(showId, {
            show_id: showId,
            show_name: showData.name || 'Unknown Show',
            show_image: showData.image_url || null,
            chats: [chatData]
          })
        }
      }
      
      // Sort and set chat history
      this.sortAndSetChatHistory(showMap)
    },
    
    sortAndSetChatHistory(showMap) {
      const history = Array.from(showMap.values())
      
      // Sort chats within each show
      history.forEach(show => {
        show.chats.sort((a, b) => new Date(b.last_activity) - new Date(a.last_activity))
      })
      
      // Sort shows by most recent chat
      history.sort((a, b) => {
        const aDate = a.chats[0]?.last_activity || new Date(0)
        const bDate = b.chats[0]?.last_activity || new Date(0)
        return new Date(bDate) - new Date(aDate)
      })
      
      this.chatHistory = history
    },
    
    toggleRecap(chat) {
      chat.expandRecap = !chat.expandRecap
    },
    
    continueChat(chatId) {
      // Find show ID for the chat
      for (const show of this.chatHistory) {
        const chat = show.chats.find(c => c.id === chatId)
        if (chat) {
          this.$router.push(`/show/${show.show_id}/chat/${chatId}`)
          return
        }
      }
      
      // Fallback if show not found
      this.$router.push(`/chat/${chatId}`)
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Unknown'
      
      const date = new Date(dateString)
      const now = new Date()
      const diffMs = now - date
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
      
      if (diffDays === 0) {
        return 'Today'
      } else if (diffDays === 1) {
        return 'Yesterday'
      } else if (diffDays < 7) {
        return `${diffDays} days ago`
      } else {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
      }
    },
    
    calculateProgress(current, total) {
      // Make sure we're working with numbers
      const currentNum = parseInt(current) || 0
      const totalNum = parseInt(total) || 1
      
      if (totalNum <= 0) return 0
      
      // Always show at least 5% progress for visibility if there is any progress
      if (currentNum > 0) {
        return Math.max(5, Math.floor((currentNum / totalNum) * 100))
      }
      
      return 0
    }
  },
  
  mounted() {
    this.fetchChatHistory()
  }
}
</script>