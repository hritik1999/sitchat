<!-- src/views/ShowPage.vue -->
<template>
  <div class="py-8">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold tracking-tight">Browse Shows</h1>
        <p class="text-muted-foreground">Discover interactive shows created by the community</p>
      </div>
      <Button v-if="user" @click="navigateToCreate" variant="default">
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
</template>

<script>
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { PlusIcon } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { supabase } from '@/composables/useSupabase'

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
      router.push('/create')
    }

    return {
      navigateToCreate
    }
  },
  data() {
    return {
      user: null,
      shows: [...Array(8)].map((_, i) => ({
        id: i + 1,
        name: `Show ${i + 1}`,
        description: 'An amazing interactive show with multiple characters and storylines',
        imageUrl: `https://picsum.photos/300/200?random=${i}`,
      })),
    }
  },
  async mounted() {
    // Get current user
    const { data } = await supabase.auth.getSession()
    this.user = data.session?.user || null
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