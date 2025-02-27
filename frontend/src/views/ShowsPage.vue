<template>
    <div class="container mx-auto py-8 px-4">
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-3xl font-bold tracking-tight">Browse Shows</h1>
          <p class="text-muted-foreground">Discover interactive shows created by the community</p>
        </div>
        <Button v-if="userSession" @click="createShow" variant="default">
          <PlusIcon class="h-4 w-4 mr-2" />
          Create Show
        </Button>
      </div>
  
      <!-- Loading skeleton -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Skeleton v-for="i in 6" :key="i" class="h-[320px] rounded-lg" />
      </div>
  
      <!-- Shows grid -->
      <div v-else-if="shows.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card v-for="show in shows" :key="show.id" class="overflow-hidden flex flex-col">
          <CardHeader class="pb-2">
            <CardTitle>{{ show.name }}</CardTitle>
            <CardDescription class="line-clamp-2">{{ show.description }}</CardDescription>
          </CardHeader>
          
          <CardContent class="flex-grow">
            <div v-if="show.image_url" class="w-full h-40 bg-muted rounded-md mb-4 overflow-hidden">
              <img :src="show.image_url" alt="Show thumbnail" class="w-full h-full object-cover" />
            </div>
            <div v-else class="w-full h-40 bg-muted rounded-md mb-4 flex items-center justify-center">
              <ImageIcon class="h-12 w-12 text-muted-foreground/40" />
            </div>
            
            <div class="text-sm space-y-1">
              <p><span class="font-medium">Creator:</span> {{ getCreatorName(show) }}</p>
              <p><span class="font-medium">Characters:</span> {{ getCharacterNames(show.characters) }}</p>
            </div>
          </CardContent>
          
          <CardFooter class="pt-0">
            <Button @click="viewShow(show)" class="w-full">View Episodes</Button>
          </CardFooter>
        </Card>
      </div>
  
      <!-- Empty state -->
      <Card v-else>
        <CardHeader>
          <CardTitle>No Shows Found</CardTitle>
          <CardDescription>There are no shows available yet.</CardDescription>
        </CardHeader>
        <CardContent>
          <p>Be the first to create a show! Sign in and click the "Create Show" button above.</p>
        </CardContent>
      </Card>
  
      <!-- Create/Edit Show Dialog -->
      <Dialog :open="showDialog" @update:open="closeShowDialog">
        <DialogContent class="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>{{ editingShow ? 'Edit Show' : 'Create New Show' }}</DialogTitle>
            <DialogDescription>
              {{ editingShow ? 'Update your show details' : 'Fill in the details to create a new show' }}
            </DialogDescription>
          </DialogHeader>
          
          <form @submit.prevent="saveShow" class="space-y-4">
            <div class="space-y-2">
              <Label for="show-name">Show Name</Label>
              <Input id="show-name" v-model="showForm.name" placeholder="e.g. Friends" required />
            </div>
            
            <div class="space-y-2">
              <Label for="show-description">Description</Label>
              <Textarea id="show-description" v-model="showForm.description" placeholder="Brief description of the show" />
            </div>
            
            <div class="space-y-2">
              <Label for="show-image">Image URL (optional)</Label>
              <Input id="show-image" v-model="showForm.image_url" placeholder="https://example.com/image.jpg" />
            </div>
            
            <div class="space-y-2">
              <Label for="show-relations">Character Relationships</Label>
              <Textarea id="show-relations" v-model="showForm.relations" placeholder="Describe relationships between characters" />
            </div>
            
            <div class="space-y-2">
              <div class="flex justify-between items-center">
                <Label>Characters</Label>
                <Button @click="addCharacter" type="button" variant="outline" size="sm">
                  <PlusIcon class="h-4 w-4 mr-2" />
                  Add Character
                </Button>
              </div>
              
              <div v-for="(desc, name) in showForm.characters" :key="name" class="p-4 border rounded-lg relative space-y-2 mt-2">
                <Button type="button" variant="destructive" size="icon" class="absolute right-2 top-2" @click="removeCharacter(name)">
                  <XIcon class="h-4 w-4" />
                  <span class="sr-only">Remove</span>
                </Button>
                
                <div class="space-y-2">
                  <Label :for="`character-name-${name}`">Character Name</Label>
                  <Input :id="`character-name-${name}`" :value="name" @input="updateCharacterName(name, $event)" placeholder="Character name" />
                </div>
                
                <div class="space-y-2">
                  <Label :for="`character-desc-${name}`">Description</Label>
                  <Textarea :id="`character-desc-${name}`" v-model="showForm.characters[name]" placeholder="Character description and personality" />
                </div>
              </div>
            </div>
          </form>
          
          <DialogFooter>
            <Button @click="closeShowDialog" variant="outline">Cancel</Button>
            <Button @click="saveShow" :disabled="isSaving">
              <Loader2Icon v-if="isSaving" class="h-4 w-4 mr-2 animate-spin" />
              {{ isSaving ? 'Saving...' : 'Save Show' }}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue'
  import { useRouter } from 'vue-router'
  import { useSupabase } from '@/composables/useSupabase'
  import { useToast } from 'vue-toastification'
  import { PlusIcon, XIcon, ImageIcon, Loader2Icon } from 'lucide-vue-next'
  import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
  import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
  import { Button } from '@/components/ui/button'
  import { Input } from '@/components/ui/input'
  import { Textarea } from '@/components/ui/textarea'
  import { Label } from '@/components/ui/label'
  import { Skeleton } from '@/components/ui/skeleton'
  
  const router = useRouter()
  const { supabase } = useSupabase()
  const toast = useToast()
  
  // State
  const shows = ref([])
  const loading = ref(true)
  const showDialog = ref(false)
  const editingShow = ref(null)
  const isSaving = ref(false)
  
  const showForm = ref({
    name: '',
    description: '',
    image_url: '',
    relations: '',
    characters: {}
  })
  
  // Get the current user session
  const userSession = computed(() => {
    return supabase.auth.getSession()?.data?.session
  })
  
  // Fetch shows on component mount
  onMounted(async () => {
    await fetchShows()
  })
  
  // Methods
  async function fetchShows() {
    loading.value = true
    
    try {
      // Fetch shows with creators
      const { data, error } = await supabase
        .from('shows')
        .select('*, users:creator_id(username)')
        .order('created_at', { ascending: false })
      
      if (error) throw error
      
      shows.value = data || []
    } catch (error) {
      console.error('Error fetching shows:', error)
      toast.error('Failed to load shows')
    } finally {
      loading.value = false
    }
  }
  
  function createShow() {
    if (!userSession.value) {
      router.push('/auth')
      return
    }
    
    editingShow.value = null
    showForm.value = {
      name: '',
      description: '',
      image_url: '',
      relations: '',
      characters: {
        'Character 1': 'Description of character 1'
      }
    }
    
    showDialog.value = true
  }
  
  async function saveShow() {
    if (!userSession.value) {
      toast.error('You must be signed in to create a show')
      return
    }
    
    // Validate form
    if (!showForm.value.name.trim()) {
      toast.error('Show name is required')
      return
    }
    
    if (Object.keys(showForm.value.characters).length === 0) {
      toast.error('You must add at least one character')
      return
    }
    
    isSaving.value = true
    
    try {
      const formData = {
        name: showForm.value.name,
        description: showForm.value.description,
        image_url: showForm.value.image_url,
        relations: showForm.value.relations,
        characters: showForm.value.characters,
        creator_id: userSession.value.user.id
      }
      
      let result
      
      if (editingShow.value) {
        // Update existing show
        const { data, error } = await supabase
          .from('shows')
          .update(formData)
          .eq('id', editingShow.value.id)
          .select('*')
        
        if (error) throw error
        result = data[0]
        toast.success('Show updated successfully')
      } else {
        // Create new show
        const { data, error } = await supabase
          .from('shows')
          .insert([formData])
          .select('*')
        
        if (error) throw error
        result = data[0]
        toast.success('Show created successfully')
      }
      
      // Refresh the shows list
      await fetchShows()
      closeShowDialog()
      
    } catch (error) {
      console.error('Error saving show:', error)
      toast.error(error.message || 'Failed to save show')
    } finally {
      isSaving.value = false
    }
  }
  
  function viewShow(show) {
    router.push(`/shows/${show.id}`)
  }
  
  function closeShowDialog() {
    showDialog.value = false
    editingShow.value = null
  }
  
  function addCharacter() {
    const newName = `Character ${Object.keys(showForm.value.characters).length + 1}`
    showForm.value.characters[newName] = ''
  }
  
  function removeCharacter(name) {
    const updatedCharacters = { ...showForm.value.characters }
    delete updatedCharacters[name]
    showForm.value.characters = updatedCharacters
  }
  
  function updateCharacterName(oldName, event) {
    const newName = event.target.value
    if (newName === oldName || !newName.trim()) return
    
    // Create a new characters object with the updated key
    const updatedCharacters = {}
    Object.entries(showForm.value.characters).forEach(([name, desc]) => {
      if (name === oldName) {
        updatedCharacters[newName] = desc
      } else {
        updatedCharacters[name] = desc
      }
    })
    
    showForm.value.characters = updatedCharacters
  }
  
  // Utility functions
  function getCreatorName(show) {
    return show.users?.username || 'Unknown'
  }
  
  function getCharacterNames(characters) {
    if (!characters) return 'None'
    
    try {
      const chars = typeof characters === 'string' ? JSON.parse(characters) : characters
      return Object.keys(chars).join(', ')
    } catch (e) {
      return 'Error parsing characters'
    }
  }
  </script>