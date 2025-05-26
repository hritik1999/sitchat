<template>
  <div class="py-8">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold tracking-tight">Browse Shows</h1>
        <p class="text-muted-foreground">Discover interactive shows created by the community</p>
      </div>
      <Button @click="navigateToCreate" variant="default">
        <PlusIcon class="h-4 w-4 mr-2" />
        Create Show
      </Button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-12">
      <p class="text-red-500">{{ error }}</p>
      <Button @click="fetchShows" class="mt-4">Try Again</Button>
    </div>

    <!-- Empty State -->
    <div v-else-if="shows.length === 0" class="text-center py-12">
      <p class="text-muted-foreground">No shows found. Be the first to create one!</p>
      <Button v-if="user" @click="navigateToCreate" class="mt-4">Create Show</Button>
    </div>

    <!-- Shows Grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <Card
        v-for="show in shows"
        :key="show.id"
        class="group relative overflow-hidden transition-transform hover:scale-105 hover:shadow-lg"
      >
      <div class="relative w-full pb-[56.25%] bg-muted overflow-hidden">
          <img
            :src="show.imageUrl || '@/assets/og_default.jpg'"
            class="absolute inset-0 w-full h-full object-contain"
            loading='lazy'
            :alt="`${show.name} thumbnail`"
            @error="handleImageError"
            @click="viewShowDetails(show.id)"
          />
          <!-- optional gradient overlay—if you still want it -->
          <div class="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent pointer-events-none" />
        </div>
        <CardHeader>
          <CardTitle class="line-clamp-1">{{ show.name || 'Untitled Show' }}</CardTitle>
          <CardDescription>
            <p 
              :class="{ 'line-clamp-2': !show.isExpanded }" 
              class="transition-all duration-300"
            >
              {{ show.description || 'No description available' }}
            </p>
            <button
              v-if="show.description"
              @click="toggleDescription(show)"
              class="text-primary underline hover:text-primary/80 text-md mt-1 font-bold text-blue-500"
            >
              {{ show.isExpanded ? 'Show less' : 'Read more' }}
            </button>
          </CardDescription>
        </CardHeader>
        <CardContent class="pt-0">
          <Button class="w-full" @click="viewShowDetails(show.id)">View Show</Button>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script>
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { PlusIcon } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { supabase } from '@/composables/useSupabase'
import { fetchApi } from '@/lib/utils'

export default {
  name: 'ShowPage',
  components: {
    Button,
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
    PlusIcon
  },
  setup() {
    const router = useRouter()
    
    const navigateToCreate = () => {
      router.push('/create/show')
    }
    
    const viewShowDetails = (showId) => {
      router.push(`/show/${showId}`)
    }
    
    return {
      navigateToCreate,
      viewShowDetails,
      router
    }
  },
  data() {
    return {
      user: null,
      API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
      shows: [],
      loading: true,
      error: null
    }
  },
  methods: {
    async fetchShows() {
      this.loading = true
      this.error = null
      
      try {
        console.log('Fetching shows')
        const data = await fetchApi('api/shows')
        
        // Validate the received data
        if (!data || !data.shows || !Array.isArray(data.shows)) {
          throw new Error('Received invalid data format from API')
        }
        
        this.shows = data.shows.map(show => ({
          id: show.id || '',
          name: show.name || '',
          description: show.description || '',
          imageUrl: show.image_url || '' // Note: API returns image_url, not imageUrl
        }))
        
        console.log('Fetched shows:', this.shows)
      } catch (error) {
        console.error('Error fetching shows:', error)
        this.error = `Failed to load shows: ${error.message}`
      } finally {
        this.loading = false
      }
    },
    
    handleImageError(event) {
      // Replace broken image with placeholder
      event.target.src = '@/assets/og_default.jpg'
    },
    toggleDescription(show) {
      show.isExpanded = !show.isExpanded;
    },
    
    async getCurrentUser() {
      try {
        const { data } = await supabase.auth.getSession()
        this.user = data.session?.user || null
      } catch (error) {
        console.error('Error getting current user:', error)
      }
    }
  },
  async mounted() {
    await this.getCurrentUser()
    await this.fetchShows()
  }
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