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
      <DialogContent class="sm:max-w-[600px] h-[90vh] max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>{{ editingShow ? 'Edit Show' : 'Create New Show' }}</DialogTitle>
          <DialogDescription>
            {{ editingShow ? 'Update your show details' : 'Fill in the details to create a new show' }}
          </DialogDescription>
        </DialogHeader>
        
        <div class="flex-1 overflow-y-auto pr-1 -mr-1 pb-4">
          <form @submit.prevent="saveShow" class="space-y-4">
            <div class="space-y-2">
              <Label for="show-name">Show Name</Label>
              <Input id="show-name" v-model="showForm.name" placeholder="e.g. Friends" required />
            </div>
            
            <div class="space-y-2">
              <Label for="show-description">Description</Label>
              <Textarea id="show-description" v-model="showForm.description" placeholder="Brief description of the show" rows="3" />
            </div>
            
            <div class="space-y-2">
              <Label>Show Image</Label>
              <div class="grid grid-cols-1 gap-4">
                <!-- Image preview -->
                <div v-if="imagePreview" class="relative aspect-video bg-muted rounded-md overflow-hidden">
                  <img :src="imagePreview" alt="Preview" class="object-cover w-full h-full" />
                  <Button 
                    type="button" 
                    variant="destructive" 
                    size="icon" 
                    class="absolute top-2 right-2 h-8 w-8 rounded-full"
                    @click="clearImage"
                  >
                    <XIcon class="h-4 w-4" />
                  </Button>
                </div>
                <!-- Upload button -->
                <div v-else class="border border-dashed rounded-md p-4 flex flex-col items-center justify-center">
                  <input 
                    ref="fileInput" 
                    type="file" 
                    accept="image/*" 
                    class="hidden" 
                    @change="handleImageChange" 
                  />
                  <ImageIcon class="h-8 w-8 text-muted-foreground mb-2" />
                  <Button type="button" variant="outline" @click="triggerFileInput">
                    <UploadIcon class="h-4 w-4 mr-2" />
                    Upload Image
                  </Button>
                  <p class="text-xs text-muted-foreground mt-2">PNG, JPG or GIF, max 2MB</p>
                </div>
              </div>
            </div>
            
            <div class="space-y-2">
              <Label for="show-relations">Character Relationships</Label>
              <Textarea id="show-relations" v-model="showForm.relations" placeholder="Describe relationships between characters" rows="3" />
            </div>
            
            <div class="space-y-2">
              <div class="flex justify-between items-center">
                <Label>Characters</Label>
                <Button @click="addCharacter" type="button" variant="outline" size="sm">
                  <PlusIcon class="h-4 w-4 mr-2" />
                  Add Character
                </Button>
              </div>
              
              <div v-for="(character, index) in showForm.characters" :key="character.id || index" class="p-4 border rounded-lg relative space-y-2 mt-2">
                <Button type="button" variant="destructive" size="icon" class="absolute right-2 top-2" @click="removeCharacter(index)">
                  <XIcon class="h-4 w-4" />
                  <span class="sr-only">Remove</span>
                </Button>
                
                <div class="space-y-2">
                  <Label :for="`character-name-${index}`">Character Name</Label>
                  <Input 
                    :id="`character-name-${index}`" 
                    v-model="character.name" 
                    placeholder="Character name" 
                  />
                </div>
                
                <div class="space-y-2">
                  <Label :for="`character-desc-${index}`">Description</Label>
                  <Textarea 
                    :id="`character-desc-${index}`" 
                    v-model="character.description" 
                    placeholder="Character description and personality" 
                    rows="2" 
                  />
                </div>
              </div>
            </div>
          </form>
        </div>
        
        <DialogFooter class="pt-4 border-t mt-4">
          <div class="flex gap-2 justify-end w-full">
            <Button @click="closeShowDialog" variant="outline">Cancel</Button>
            <Button @click="saveShow" :disabled="isSaving || !isFormValid">
              <Loader2Icon v-if="isSaving" class="h-4 w-4 mr-2 animate-spin" />
              {{ isSaving ? 'Saving...' : 'Save Show' }}
            </Button>
          </div>
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
import { fetchApi } from '@/lib/utils'
import { 
  PlusIcon, XIcon, ImageIcon, UploadIcon, 
  Loader2Icon, EditIcon, TrashIcon 
} from 'lucide-vue-next'
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

// Form state
const showForm = ref({
  name: '',
  description: '',
  image_url: '',
  relations: '',
  characters: [] // Use array of objects instead of object
})

// Image upload state
const fileInput = ref(null)
const selectedFile = ref(null)
const imagePreview = ref(null)

// API Base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001'

// State for the current user session
const userSession = ref(null)

// Function to get the current user session
async function getCurrentSession() {
  try {
    const { data } = await supabase.auth.getSession()
    userSession.value = data.session
  } catch (error) {
    console.error('Error getting session:', error)
  }
}

// Form validation
const isFormValid = computed(() => {
  return (
    showForm.value.name.trim() !== '' && 
    showForm.value.characters.length > 0 &&
    showForm.value.characters.every(char => 
      char.name?.trim() !== '' && char.description?.trim() !== ''
    )
  )
})

// Fetch shows and session on component mount
onMounted(async () => {
  await getCurrentSession()
  await fetchShows()
})

// Methods
async function fetchShows() {
  loading.value = true
  
  try {
    const data = await fetchApi('api/shows')
    shows.value = data.shows || []
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
    characters: [] // Initialize as empty array
  }
  
  // Add a default character with proper structure
  addCharacter()
  
  clearImage()
  showDialog.value = true
}

// Image handling functions
function triggerFileInput() {
  fileInput.value.click()
}

function handleImageChange(event) {
  const file = event.target.files[0]
  if (!file) return
  
  // Validate file size (max 2MB)
  if (file.size > 2 * 1024 * 1024) {
    toast.error('Image size should not exceed 2MB')
    return
  }
  
  selectedFile.value = file
  
  // Create preview URL
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

function clearImage() {
  selectedFile.value = null
  imagePreview.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function uploadImage() {
  if (!selectedFile.value) return null
  
  try {
    // Generate a unique filename
    const fileExt = selectedFile.value.name.split('.').pop()
    const fileName = `${Date.now()}.${fileExt}`
    
    // Upload to Supabase Storage
    const { data, error } = await supabase.storage
      .from('show-images')
      .upload(fileName, selectedFile.value, {
        cacheControl: '3600',
        upsert: false
      })
    
    if (error) throw error
    
    // Get public URL
    const { data: urlData } = supabase.storage
      .from('show-images')
      .getPublicUrl(data.path)
    
    return urlData.publicUrl
  } catch (error) {
    console.error('Error uploading image:', error)
    toast.error(error.message || 'Failed to upload image')
    return null
  }
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
  
  if (showForm.value.characters.length === 0) {
    toast.error('You must add at least one character')
    return
  }
  
  isSaving.value = true
  
  try {
    // Upload image if selected
    let imageUrl = showForm.value.image_url
    if (selectedFile.value) {
      imageUrl = await uploadImage()
      if (!imageUrl && !editingShow.value) {
        // Only fail if we're creating a new show and image upload failed
        throw new Error('Failed to upload image')
      }
    }
    
    // Get authorization token
    const session = await supabase.auth.getSession()
    const token = session?.data?.session?.access_token
    
    // Convert characters array to object format expected by the backend
    const formattedCharacters = {}
    showForm.value.characters.forEach(char => {
      if (char.name && char.description) {
        formattedCharacters[char.name] = char.description
      }
    })
    
    // Prepare form data
    const formData = {
      name: showForm.value.name,
      description: showForm.value.description,
      image_url: imageUrl,
      relations: showForm.value.relations,
      characters: formattedCharacters
    }
    
    let result
    
    if (editingShow.value) {
      // Update existing show
      const { data, error } = await supabase
        .from('shows')
        .update(formData)
        .eq('id', editingShow.value.id)
        .select()
      
      if (error) throw error
      result = data[0]
      toast.success('Show updated successfully')
    } else {
      // Create new show
      const { data, error } = await supabase
        .from('shows')
        .insert([{
          ...formData,
          creator_id: userSession.value.user.id
        }])
        .select()
      
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
  clearImage()
}

function addCharacter() {
  // Add a new character object to the array
  showForm.value.characters.push({
    id: Date.now().toString(), // Unique ID for React keys
    name: `Character ${showForm.value.characters.length + 1}`,
    description: ''
  })
}

function removeCharacter(index) {
  // Remove character at the specified index
  if (showForm.value.characters.length <= 1) {
    toast.error('You must have at least one character')
    return
  }
  showForm.value.characters.splice(index, 1)
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

// For editing a show - not implemented in the current view
function editShow(show) {
  if (!userSession.value) {
    router.push('/auth')
    return
  }
  
  editingShow.value = show
  
  // Parse characters object to array format for the form
  let charactersArray = []
  try {
    const chars = typeof show.characters === 'string' 
      ? JSON.parse(show.characters) 
      : show.characters
    
    charactersArray = Object.entries(chars).map(([name, description]) => ({
      id: `char_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name,
      description
    }))
  } catch (e) {
    console.error('Error parsing characters:', e)
    charactersArray = []
  }
  
  showForm.value = {
    name: show.name || '',
    description: show.description || '',
    image_url: show.image_url || '',
    relations: show.relations || '',
    characters: charactersArray.length > 0 ? charactersArray : [{ id: Date.now().toString(), name: 'Character 1', description: '' }]
  }
  
  // Set image preview if there's an image URL
  if (show.image_url) {
    imagePreview.value = show.image_url
  } else {
    clearImage()
  }
  
  showDialog.value = true
}
</script>