<template>
    <div class="container mx-auto px-4 py-8 max-w-4xl">
     <!-- Page Header -->
     <div class="mb-8">
       <h1 class="text-2xl font-bold tracking-tight">
         {{ editingShow ? 'Edit Show' : 'Create New Show' }}
       </h1>
       <p class="text-muted-foreground text-sm mt-2">
         {{ editingShow ? 'Update your show details' : 'Fill in the details to create a new show' }}
       </p>
     </div>
     <!-- Main Form -->
     <form @submit.prevent="saveShow" class="space-y-6">
       <!-- Show Name -->
       <div class="space-y-2">
         <Label for="show-name">Show Name</Label>
         <Input
           id="show-name"
           v-model="showForm.name"
           placeholder="e.g. Friends"
           required
           class="w-full"
         />
       </div>
       <!-- Description -->
       <div class="space-y-2">
         <Label for="show-description">Description</Label>
         <Textarea
           id="show-description"
           v-model="showForm.description"
           placeholder="Brief description of the show"
           rows="3"
           class="w-full"
         />
       </div>
       <!-- Image Upload Section -->
       <div class="space-y-2">
         <Label>Show Image</Label>
         <div class="grid grid-cols-1 gap-4">
           <div
             v-if="imagePreview"
             class="relative aspect-video bg-muted rounded-md overflow-hidden"
           >
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
           <div
             v-else
             class="border border-dashed rounded-md p-4 flex flex-col items-center justify-center"
           >
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
       <!-- Characters Section -->
       <div class="space-y-2">
         <div class="flex justify-between items-center">
           <Label>Characters</Label>
           <Button @click="addCharacter" type="button" variant="outline" size="sm">
             <PlusIcon class="h-4 w-4 mr-2" />
             Add Character
           </Button>
         </div>
         <!-- Character Cards -->
         <div
           v-for="(character, index) in showForm.characters"
           :key="character.id || index"
           class="p-4 border rounded-lg relative space-y-2 mt-2"
         >
           <Button
             type="button"
             variant="destructive"
             size="icon"
             class="absolute right-2 top-2"
             @click="removeCharacter(index)"
           >
             <XIcon class="h-4 w-4" />
             <span class="sr-only">Remove</span>
           </Button>
           <div class="space-y-2">
             <Label :for="`character-name-${index}`">Character Name</Label>
             <Input
               :id="`character-name-${index}`"
               v-model="character.name"
               placeholder="Character name"
               class="w-full"
             />
           </div>
           <div class="space-y-2">
             <Label :for="`character-desc-${index}`">Description</Label>
             <Textarea
               :id="`character-desc-${index}`"
               v-model="character.description"
               placeholder="Character description and personality"
               rows="2"
               class="w-full"
             />
           </div>
         </div>
       </div>
       <!-- Character Relationships -->
       <div class="space-y-2">
         <Label for="show-relations">Character Relationships</Label>
         <Textarea
           id="show-relations"
           v-model="showForm.relations"
           placeholder="Describe relationships between characters"
           rows="3"
           class="w-full"
         />
       </div>
       <!-- Form Actions -->
       <div class="flex flex-col-reverse sm:flex-row sm:justify-end gap-3 pt-6">
         <Button @click="cancel" variant="outline" class="w-full sm:w-auto">
           Cancel
         </Button>
         <Button type="submit" :disabled="isSaving || !isFormValid" class="w-full sm:w-auto">
           <Loader2Icon v-if="isSaving" class="h-4 w-4 mr-2 animate-spin" />
           {{ isSaving ? 'Saving...' : 'Save Show' }}
         </Button>
       </div>
     </form>
   </div>
   </template>
   
   <script>
   import { ref, reactive, computed, inject } from 'vue'
   import { useRouter } from 'vue-router'
   import { useToast } from 'vue-toastification'
   import {Button} from '@/components/ui/button'
   import {Input} from '@/components/ui/input'
   import {Label} from '@/components/ui/label'
   import {Textarea} from '@/components/ui/textarea'
   import { ImageIcon, Loader2Icon, PlusIcon, UploadIcon, XIcon } from 'lucide-vue-next'
   
   export default {
     components: {
       Button,
       Input,
       Label,
       Textarea,
       ImageIcon,
       Loader2Icon,
       PlusIcon,
       UploadIcon,
       XIcon
     },
     props: {
       editingShow: {
         type: Boolean,
         default: false
       },
       initialData: {
         type: Object,
         default: () => ({})
       }
     },
     name: 'CreateShow',
     setup(props) {
       const router = useRouter()
       const toast = useToast()
   
       const showForm = reactive({
         name: '',
         description: '',
         relations: '',
         characters: [{name:'',description:''}],
         ...props.initialData
       })
   
       const imagePreview = ref(null)
       const selectedFile = ref(null)
       const isSaving = ref(false)
       const fileInput = ref(null)
       
       const isFormValid = computed(() => {
         return showForm.name.trim() !== ''
       })
       
       const addCharacter = () => {
         showForm.characters.push({ name: '', description: '' })
       }
       
       const removeCharacter = (index) => {
         showForm.characters.splice(index, 1)
       }
       
       const triggerFileInput = () => {
         fileInput.value.click()
       }
       
       const handleImageChange = (e) => {
         const file = e.target.files[0]
         if (file) {
           selectedFile.value = file
           imagePreview.value = URL.createObjectURL(file)
         }
       }
       
       const clearImage = () => {
         imagePreview.value = null
         selectedFile.value = null
         if (fileInput.value) {
           fileInput.value.value = ''
         }
       }
   
       const showSuccessToast = () => {
         toast.success('Show added successfully!', {
           timeout: 3000
         })
       }
   
       const showErrorToast = (message) => {
         toast.error(message || 'Failed to save show', {
           timeout: 5000
         })
       }
   
       const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001'
       const session_token = localStorage.getItem('supabase_session')
         ? JSON.parse(localStorage.getItem('supabase_session')).access_token
         : null
   
       const saveShow = async () => {
         if (!isFormValid.value) return
         
         // Validate form
         if (!showForm.name.trim()) {
           showErrorToast('Show name is required')
           return
         }
         
         if (showForm.characters.length === 0) {
           showErrorToast('You must add at least one character')
           return
         }
         
         if (!selectedFile.value) {
           showErrorToast('Please select an image for the show')
           return
         }
         
         isSaving.value = true
         
         try {
           // Create FormData object for multipart/form-data submission
           const formData = new FormData()
           
           // Add the image file
           formData.append('image', selectedFile.value)
           
           // Add other form data as a JSON string in a single field
           formData.append('data', JSON.stringify({
             name: showForm.name,
             description: showForm.description,
             characters: showForm.characters,
             relations: showForm.relations
           }))
           
           // Make the API request
           const response = await fetch(`${API_BASE_URL}/api/shows`, {
             method: 'POST',
             headers: {
               'Authorization': `Bearer ${session_token}`
             },
             body: formData
           })
           
           // Parse the response
           const data = await response.json()
           
           if (response.ok) {
             // Show success toast and navigate
             showSuccessToast()
             setTimeout(() => {
               router.push('/shows')
             }, 500)
           } else {
             // Show error toast with server message if available
             showErrorToast(data.error || 'Failed to save show')
           }
         } catch (error) {
           // Show error toast for unexpected errors
           console.error('Error saving show:', error)
           showErrorToast('An unexpected error occurred')
         } finally {
           isSaving.value = false
         }
       }
   
       const cancel = () => {
         // Navigate back to shows page
         router.push('/shows')
       }
   
       return {
         showForm,
         imagePreview,
         selectedFile,
         isSaving,
         isFormValid,
         fileInput,
         addCharacter,
         removeCharacter,
         triggerFileInput,
         handleImageChange,
         clearImage,
         saveShow,
         cancel,
         showSuccessToast,
         showErrorToast
       }
     }
   }
   </script>
   
   <style scoped>
   /* Add any custom responsive styles if needed */
   .container {
     min-height: 100vh;
   }
   @media (max-width: 640px) {
     .container {
       padding: 1rem;
     }
   }
   </style>