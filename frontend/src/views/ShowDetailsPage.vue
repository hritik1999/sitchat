<template>
    <div class="container mx-auto py-8 px-4">
      <!-- Loading state -->
      <div v-if="loading" class="space-y-6">
        <div class="flex items-center gap-4">
          <Skeleton class="h-12 w-64" />
          <Skeleton class="h-8 w-24 ml-auto" />
        </div>
        <Skeleton class="h-[200px] w-full" />
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Skeleton v-for="i in 4" :key="i" class="h-[140px]" />
        </div>
      </div>
  
      <!-- Show details -->
      <div v-else-if="show" class="space-y-6">
        <div class="flex justify-between items-start">
          <div>
            <h1 class="text-3xl font-bold tracking-tight">{{ show.name }}</h1>
            <p class="text-muted-foreground">
              Created by {{ getCreatorName(show) }}
            </p>
          </div>
  
          <div class="flex items-center gap-2">
            <Button v-if="canEditShow" @click="editShow" variant="outline">
              <EditIcon class="h-4 w-4 mr-2" />
              Edit Show
            </Button>
            <Button @click="goBack" variant="outline">
              <ArrowLeftIcon class="h-4 w-4 mr-2" />
              Back
            </Button>
          </div>
        </div>
  
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- Show information -->
          <div class="md:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Description</CardTitle>
              </CardHeader>
              <CardContent>
                <p>{{ show.description || 'No description provided.' }}</p>
              </CardContent>
            </Card>
  
            <Card>
              <CardHeader>
                <CardTitle>Characters</CardTitle>
              </CardHeader>
              <CardContent>
                <div v-if="characters.length === 0" class="text-muted-foreground">
                  No characters defined.
                </div>
                <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div v-for="character in characters" :key="character.name" class="p-4 bg-muted rounded-lg">
                    <h3 class="font-semibold">{{ character.name }}</h3>
                    <p class="text-sm">{{ character.description }}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
  
            <Card>
              <CardHeader>
                <CardTitle>Relationships</CardTitle>
              </CardHeader>
              <CardContent>
                <p>{{ show.relations || 'No relationship information provided.' }}</p>
              </CardContent>
            </Card>
          </div>
  
          <!-- Image and actions -->
          <div>
            <Card class="mb-6">
              <CardHeader class="pb-2">
                <CardTitle>Show Image</CardTitle>
              </CardHeader>
              <CardContent>
                <div v-if="show.image_url" class="h-48 w-full rounded-md overflow-hidden">
                  <img :src="show.image_url" alt="Show thumbnail" class="h-full w-full object-cover" />
                </div>
                <div v-else class="h-48 w-full bg-muted rounded-md flex items-center justify-center">
                  <ImageIcon class="h-12 w-12 text-muted-foreground/40" />
                </div>
              </CardContent>
            </Card>
  
            <Card v-if="canEditShow" class="mb-6">
              <CardHeader>
                <CardTitle>Actions</CardTitle>
              </CardHeader>
              <CardContent class="space-y-2">
                <Button @click="createEpisode" variant="default" class="w-full">
                  <PlusIcon class="h-4 w-4 mr-2" />
                  Create Episode
                </Button>
                <Button @click="confirmDeleteShow" variant="destructive" class="w-full">
                  <TrashIcon class="h-4 w-4 mr-2" />
                  Delete Show
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
  
        <!-- Episodes section -->
        <div class="space-y-4">
          <h2 class="text-2xl font-bold tracking-tight">Episodes</h2>
          
          <div v-if="loadingEpisodes" class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Skeleton v-for="i in 4" :key="i" class="h-[140px]" />
          </div>
          
          <div v-else-if="episodes.length === 0" class="text-center py-12">
            <FolderIcon class="h-16 w-16 mx-auto text-muted-foreground/40 mb-4" />
            <h3 class="text-lg font-medium">No Episodes Yet</h3>
            <p class="text-muted-foreground mb-4">
              This show doesn't have any episodes yet.
            </p>
            <Button v-if="canEditShow" @click="createEpisode" variant="default">
              <PlusIcon class="h-4 w-4 mr-2" />
              Create First Episode
            </Button>
          </div>
          
          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card v-for="episode in episodes" :key="episode.id" class="cursor-pointer hover:bg-accent/10" @click="startEpisode(episode)">
              <CardHeader>
                <CardTitle>{{ episode.name }}</CardTitle>
                <CardDescription class="line-clamp-2">{{ episode.description || 'No description' }}</CardDescription>
              </CardHeader>
              <CardContent class="space-y-2">
                <div>
                  <span class="font-medium">Background:</span>
                  <p class="text-sm line-clamp-2">{{ episode.background || 'No background information' }}</p>
                </div>
                <div>
                  <span class="font-medium">Objectives:</span>
                  <p class="text-sm">{{ getObjectivesCount(episode.plot_objectives) }}</p>
                </div>
              </CardContent>
              <CardFooter>
                <div class="flex items-center justify-between w-full">
                  <Button @click.stop="startEpisode(episode)" variant="default">
                    <PlayIcon class="h-4 w-4 mr-2" />
                    Play Episode
                  </Button>
                  <div class="flex items-center gap-2">
                    <Button v-if="canEditShow" @click.stop="editEpisode(episode)" variant="outline" size="icon">
                      <EditIcon class="h-4 w-4" />
                    </Button>
                    <Button v-if="canEditShow" @click.stop="confirmDeleteEpisode(episode)" variant="outline" size="icon">
                      <TrashIcon class="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardFooter>
            </Card>
          </div>
        </div>
      </div>
  
      <!-- Not found state -->
      <div v-else class="text-center py-12">
        <AlertTriangleIcon class="h-16 w-16 mx-auto text-muted-foreground/40 mb-4" />
        <h2 class="text-2xl font-bold mb-2">Show Not Found</h2>
        <p class="text-muted-foreground mb-6">The show you're looking for doesn't exist or has been removed.</p>
        <Button @click="goBack" variant="default">
          <ArrowLeftIcon class="h-4 w-4 mr-2" />
          Go Back
        </Button>
      </div>
  
      <!-- Create/Edit Episode Dialog -->
      <Dialog :open="episodeDialog" @update:open="closeEpisodeDialog">
        <DialogContent class="sm:max-w-[600px] h-[90vh] max-h-[90vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle>{{ editingEpisode ? 'Edit Episode' : 'Create New Episode' }}</DialogTitle>
            <DialogDescription>
              {{ editingEpisode ? 'Update episode details' : 'Add a new episode to your show' }}
            </DialogDescription>
          </DialogHeader>
          
          <form @submit.prevent="saveEpisode" class="space-y-4 flex-1 overflow-y-auto pr-1 -mr-1 pb-4">
            <div class="space-y-2">
              <Label for="episode-name">Episode Name</Label>
              <Input id="episode-name" v-model="episodeForm.name" placeholder="e.g. The One With the Reunion" required />
            </div>
            
            <div class="space-y-2">
              <Label for="episode-description">Description</Label>
              <Textarea id="episode-description" v-model="episodeForm.description" placeholder="Brief description of the episode" />
            </div>
            
            <div class="space-y-2">
              <Label for="episode-background">Scene Background</Label>
              <Textarea id="episode-background" v-model="episodeForm.background" placeholder="The initial scene setup" />
            </div>
            
            <div class="space-y-2">
              <div class="flex justify-between items-center">
                <Label>Plot Objectives</Label>
                <Button @click="addObjective" type="button" variant="outline" size="sm">
                  <PlusIcon class="h-4 w-4 mr-2" />
                  Add Objective
                </Button>
              </div>
              
              <div v-for="(objective, index) in episodeForm.plot_objectives" :key="index" class="p-4 border rounded-lg relative mt-2">
                <Button type="button" variant="destructive" size="icon" class="absolute right-2 top-2" @click="removeObjective(index)">
                  <XIcon class="h-4 w-4" />
                  <span class="sr-only">Remove</span>
                </Button>
                
                <div class="space-y-2">
                  <Label :for="`objective-${index}`">Objective {{ index + 1 }}</Label>
                  <Textarea :id="`objective-${index}`" v-model="episodeForm.plot_objectives[index]" placeholder="Describe what needs to happen in this stage" />
                </div>
              </div>
            </div>
          </form>
          
          <DialogFooter>
            <Button @click="closeEpisodeDialog" variant="outline">Cancel</Button>
            <Button @click="saveEpisode" :disabled="isSaving">
              <Loader2Icon v-if="isSaving" class="h-4 w-4 mr-2 animate-spin" />
              {{ isSaving ? 'Saving...' : 'Save Episode' }}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
  
      <!-- Player Dialog -->
      <Dialog :open="playerDialog" @update:open="closePlayerDialog">
        <DialogContent class="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Start Episode</DialogTitle>
            <DialogDescription>
              Enter your character details to begin "{{ selectedEpisode?.name }}"
            </DialogDescription>
          </DialogHeader>
          
          <form @submit.prevent="startPlaying" class="space-y-4">
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
            <Button @click="startPlaying" :disabled="isStarting">
              <Loader2Icon v-if="isStarting" class="h-4 w-4 mr-2 animate-spin" />
              {{ isStarting ? 'Starting...' : 'Start Episode' }}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
  
      <!-- Delete Confirmation Dialog -->
      <AlertDialog :open="deleteDialog" @update:open="deleteDialog = false">
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              {{ deleteType === 'show' 
                ? 'This will permanently delete this show and all its episodes.' 
                : 'This will permanently delete this episode and all associated chat history.' }}
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction @click="confirmDelete" class="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              <Loader2Icon v-if="isDeleting" class="h-4 w-4 mr-2 animate-spin" />
              {{ isDeleting ? 'Deleting...' : 'Delete' }}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  </template>
  

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSupabase } from '@/composables/useSupabase'
import { useToast } from 'vue-toastification'
import { 
  ArrowLeftIcon, EditIcon, PlusIcon, XIcon, ImageIcon, 
  TrashIcon, PlayIcon, FolderIcon, AlertTriangleIcon, Loader2Icon 
} from 'lucide-vue-next'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { 
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'

const route = useRoute()
const router = useRouter()
const { supabase } = useSupabase()
const toast = useToast()

// State
const show = ref(null)
const episodes = ref([])
const loading = ref(true)
const loadingEpisodes = ref(false)
const characters = ref([])
const userSession = ref(null) // Changed from computed to ref

// Dialog states
const episodeDialog = ref(false)
const playerDialog = ref(false)
const deleteDialog = ref(false)
const deleteType = ref('') // 'show' or 'episode'
const itemToDelete = ref(null)

// Form states
const editingEpisode = ref(null)
const selectedEpisode = ref(null)
const isSaving = ref(false)
const isStarting = ref(false)
const isDeleting = ref(false)

const episodeForm = ref({
  name: '',
  description: '',
  background: '',
  plot_objectives: []
})

const playerForm = ref({
  player_name: '',
  player_description: ''
})

// Check if user can edit this show
const canEditShow = computed(() => {
  if (!userSession.value || !show.value) return false
  return show.value.creator_id === userSession.value.user.id
})

// Fetch show data on component mount
onMounted(async () => {
  const showId = route.params.id
  if (!showId) {
    router.push('/shows')
    return
  }
  
  // Properly get the user session
  const { data } = await supabase.auth.getSession()
  userSession.value = data.session
  
  // Set up listener for auth state changes
  supabase.auth.onAuthStateChange((event, session) => {
    userSession.value = session
  })
  
  await fetchShow(showId)
  await fetchEpisodes(showId)
})

// Methods
async function fetchShow(showId) {
  loading.value = true
  
  try {
    const { data, error } = await supabase
      .from('shows')
      .select('*, users:creator_id(username)')
      .eq('id', showId)
      .single()
    
    if (error) throw error
    
    show.value = data
    
    // Process characters
    if (show.value.characters) {
      const chars = typeof show.value.characters === 'string' 
        ? JSON.parse(show.value.characters) 
        : show.value.characters
      
      characters.value = Object.entries(chars).map(([name, description]) => ({
        name,
        description
      }))
    }
    
  } catch (error) {
    console.error('Error fetching show:', error)
    toast.error('Failed to load show details')
    show.value = null
  } finally {
    loading.value = false
  }
}

async function fetchEpisodes(showId) {
  loadingEpisodes.value = true
  
  try {
    const { data, error } = await supabase
      .from('episodes')
      .select('*')
      .eq('show_id', showId)
      .order('created_at', { ascending: false })
    
    if (error) throw error
    
    episodes.value = data || []
  } catch (error) {
    console.error('Error fetching episodes:', error)
    toast.error('Failed to load episodes')
  } finally {
    loadingEpisodes.value = false
  }
}

function createEpisode() {
  if (!userSession.value) {
    toast.error('You must be signed in to add episodes')
    router.push('/auth')
    return
  }
  
  if (!canEditShow.value) {
    toast.error('You must be the creator of this show to add episodes')
    return
  }
  
  editingEpisode.value = null
  episodeForm.value = {
    name: `Episode ${episodes.value.length + 1}`,
    description: '',
    background: '',
    plot_objectives: ['First objective']
  }
  
  episodeDialog.value = true
}

function editEpisode(episode) {
  if (!userSession.value) {
    toast.error('You must be signed in to edit episodes')
    router.push('/auth')
    return
  }
  
  if (!canEditShow.value) return
  
  editingEpisode.value = episode
  
  // Parse plot objectives if needed
  const objectives = typeof episode.plot_objectives === 'string'
    ? JSON.parse(episode.plot_objectives)
    : episode.plot_objectives || []
  
  episodeForm.value = {
    name: episode.name,
    description: episode.description || '',
    background: episode.background || '',
    plot_objectives: objectives
  }
  
  episodeDialog.value = true
}

async function saveEpisode() {
  if (!userSession.value) {
    toast.error('You must be signed in to create an episode')
    router.push('/auth')
    return
  }
  
  // Validate form
  if (!episodeForm.value.name.trim()) {
    toast.error('Episode name is required')
    return
  }
  
  if (episodeForm.value.plot_objectives.length === 0) {
    toast.error('You must add at least one plot objective')
    return
  }
  
  isSaving.value = true
  
  try {
    const formData = {
      show_id: show.value.id,
      creator_id: userSession.value.user.id,
      name: episodeForm.value.name,
      description: episodeForm.value.description,
      background: episodeForm.value.background,
      plot_objectives: episodeForm.value.plot_objectives
    }
    
    let result
    
    if (editingEpisode.value) {
      // Update existing episode
      const { data, error } = await supabase
        .from('episodes')
        .update(formData)
        .eq('id', editingEpisode.value.id)
        .select()
      
      if (error) throw error
      result = data[0]
      toast.success('Episode updated successfully')
    } else {
      // Create new episode
      const { data, error } = await supabase
        .from('episodes')
        .insert([formData])
        .select()
      
      if (error) throw error
      result = data[0]
      toast.success('Episode created successfully')
    }
    
    // Refresh episodes list
    await fetchEpisodes(show.value.id)
    closeEpisodeDialog()
    
  } catch (error) {
    console.error('Error saving episode:', error)
    toast.error(error.message || 'Failed to save episode')
  } finally {
    isSaving.value = false
  }
}

function startEpisode(episode) {
  selectedEpisode.value = episode
  playerDialog.value = true
}

async function startPlaying() {
  if (!userSession.value) {
    toast.error('You must be signed in to play episodes')
    router.push('/auth')
    return
  }
  
  if (!selectedEpisode.value) return
  
  if (!playerForm.value.player_name.trim()) {
    toast.error('Character name is required')
    return
  }
  
  isStarting.value = true
  
  try {
    // Create a chat/session in the database
    const response = await fetch('http://localhost:5001/api/chats', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userSession.value?.access_token || ''}`
      },
      body: JSON.stringify({
        episode_id: selectedEpisode.value.id,
        player_name: playerForm.value.player_name,
        player_description: playerForm.value.player_description
      })
    })
    
    const data = await response.json()
    
    if (!response.ok) throw new Error(data.error || 'Failed to start episode')
    
    // Navigate to the chat session
    router.push(`/chat/${data.chat_id}`)
    
  } catch (error) {
    console.error('Error starting episode:', error)
    toast.error(error.message || 'Failed to start episode')
  } finally {
    isStarting.value = false
    closePlayerDialog()
  }
}

function confirmDeleteShow() {
  if (!userSession.value) {
    toast.error('You must be signed in to delete this show')
    router.push('/auth')
    return
  }
  
  if (!canEditShow.value) return
  
  deleteType.value = 'show'
  itemToDelete.value = show.value
  deleteDialog.value = true
}

function confirmDeleteEpisode(episode) {
  if (!userSession.value) {
    toast.error('You must be signed in to delete episodes')
    router.push('/auth')
    return
  }
  
  if (!canEditShow.value) return
  
  deleteType.value = 'episode'
  itemToDelete.value = episode
  deleteDialog.value = true
}

async function confirmDelete() {
  if (!itemToDelete.value) return
  
  isDeleting.value = true
  
  try {
    if (deleteType.value === 'show') {
      // Delete show
      const { error } = await supabase
        .from('shows')
        .delete()
        .eq('id', itemToDelete.value.id)
      
      if (error) throw error
      
      toast.success('Show deleted successfully')
      router.push('/shows')
      
    } else if (deleteType.value === 'episode') {
      // Delete episode
      const { error } = await supabase
        .from('episodes')
        .delete()
        .eq('id', itemToDelete.value.id)
      
      if (error) throw error
      
      toast.success('Episode deleted successfully')
      await fetchEpisodes(show.value.id)
    }
    
    deleteDialog.value = false
    
  } catch (error) {
    console.error('Error deleting:', error)
    toast.error(error.message || `Failed to delete ${deleteType.value}`)
  } finally {
    isDeleting.value = false
  }
}

function editShow() {
  router.push(`/edit-show/${show.value.id}`)
}

function goBack() {
  router.go(-1)
}

function closeEpisodeDialog() {
  episodeDialog.value = false
  editingEpisode.value = null
}

function closePlayerDialog() {
  playerDialog.value = false
  selectedEpisode.value = null
}

function addObjective() {
  episodeForm.value.plot_objectives.push('')
}

function removeObjective(index) {
  if (episodeForm.value.plot_objectives.length === 1) {
    toast.error('You must have at least one objective')
    return
  }
  episodeForm.value.plot_objectives.splice(index, 1)
}

// Utility functions
function getCreatorName(show) {
  return show.users?.username || 'Unknown'
}

function getObjectivesCount(objectives) {
  if (!objectives) return 'No objectives'
  
  try {
    const objs = typeof objectives === 'string' ? JSON.parse(objectives) : objectives
    return `${objs.length} objective${objs.length !== 1 ? 's' : ''}`
  } catch (e) {
    return 'Error parsing objectives'
  }
}
</script>