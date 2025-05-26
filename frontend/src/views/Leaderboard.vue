<template>
    <div class="py-8">
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-3xl font-bold tracking-tight">Leaderboard</h1>
          <p class="text-muted-foreground">See where you stand among the community</p>
        </div>
      </div>
  
      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
  
      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12">
        <p class="text-red-500">{{ error }}</p>
        <Button @click="fetchLeaderboard" class="mt-4">Try Again</Button>
      </div>
  
      <!-- Empty State -->
      <div v-else-if="leaderboard.length === 0" class="text-center py-12">
        <p class="text-muted-foreground">No leaderboard entries yet. Participate in shows to get ranked!</p>
      </div>
  
      <!-- Leaderboard List -->
      <div v-else class="space-y-4">
        <Card 
          v-for="(user, index) in sortedLeaderboard" 
          :key="user.id"
          :data-user-id="user.id"
          class="relative transition-colors"
          :class="{ 
            'bg-blue-100 border-2 border-blue-300 dark:bg-blue-900/50': isCurrentUser(user.id),
            'hover:bg-accent/10': !isCurrentUser(user.id)
          }"
        >
          <CardContent class="p-6">
            <div class="flex items-center gap-4">
              <div class="flex-1 flex items-center gap-4">
                <span class="font-bold w-8">{{ index + 1 }}</span>
                <img 
                  v-if="user.avatar_url"
                  :src="user.avatar_url"
                  class="h-10 w-10 rounded-full object-cover"
                  @error="handleImageError"
                  :alt="user.username || 'Anonymous'"
                  loading='lazy'
                />
                <Avatar v-else>
                  <AvatarFallback>{{ user.username.split(/[\s_-]/).map(n => n[0]).join('').toUpperCase() }}</AvatarFallback>
                </Avatar>
                <div>
                  <p class="font-medium">{{ user.full_name || 'Anonymous' }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <span class="font-bold text-primary">{{ user.total_score }}</span>
                <span class="text-muted-foreground text-sm">points</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </template>
  
  <script>
  import { Button } from '@/components/ui/button'
  import { Card, CardContent } from '@/components/ui/card'
  import { fetchApi } from '@/lib/utils'
  import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar'
  
  export default {
    name: 'LeaderboardPage',
    components: {
      Button,
      Card,
      CardContent,
      Avatar,
      AvatarFallback
    },
    data() {
      return {
        leaderboard: [],
        loading: true,
        error: null,
        currentUserId: null
      }
    },
    computed: {
      sortedLeaderboard() {
        return [...this.leaderboard].sort((a, b) => b.total_score - a.total_score)
      }
    },
    methods: {
      async fetchLeaderboard() {
        this.loading = true
        this.error = null
        
        try {
          const data = await fetchApi('api/leaderboard')
          if (!data || !Array.isArray(data.leaderboard)) {
            throw new Error('Invalid leaderboard data format')
          }
          
          this.leaderboard = data.leaderboard.map(user => ({
            id: user.id,
            username: user.username,
            full_name: user.full_name,
            avatar_url: user.avatar_url,
            total_score: user.total_score || 0,
            show_count: user.show_count || 0
          }))
  
        } catch (error) {
          console.error('Error fetching leaderboard:', error)
          this.error = `Failed to load leaderboard: ${error.message}`
        } finally {
          this.loading = false
          // Scroll to current user after data loads
          this.$nextTick(() => {
            if (this.currentUserId) {
              const userCard = document.querySelector(`[data-user-id="${this.currentUserId}"]`)
              if (userCard) {
                userCard.scrollIntoView({ 
                  behavior: 'smooth',
                  block: 'center'
                })
              }
            }
          })
        }
      },
      
      handleImageError(event) {
        event.target.src = '/placeholder-avatar.jpg'
      },
      
      isCurrentUser(userId) {
        return userId === this.currentUserId
      }
    },
    async mounted() {
      this.currentUserId = localStorage.getItem('user_id')
      await this.fetchLeaderboard()
    }
  }
  </script>
  
  <style>
  /* Smooth scroll alignment */
  [data-user-id] {
    scroll-margin-top: 100px;
  }
  </style>