<template>
    <div class="container mx-auto px-4 py-8 max-w-2xl">
      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold tracking-tight">Edit Profile</h1>
        <p class="text-muted-foreground text-sm mt-2">Update your profile information</p>
      </div>
  
      <!-- Loading State -->
      <div v-if="isLoading" class="flex justify-center items-center min-h-[400px]">
        <Loader2Icon class="h-8 w-8 animate-spin" />
      </div>
  
      <!-- Main Form -->
      <form v-else @submit.prevent="saveProfile" class="space-y-6">
        <!-- Profile Picture Section -->
        <div class="space-y-2">
          <Label>Profile Picture</Label>
          <div class="grid grid-cols-1 gap-4">
            <div class="flex items-center justify-center">
              <div
                v-if="imagePreview || userForm.avatar_url"
                class="relative w-32 h-32 rounded-full overflow-hidden border-2 border-border"
              >
                <img 
                  :src="imagePreview || userForm.avatar_url || '/placeholder-avatar.png'" 
                  alt="Profile" 
                  class="object-cover w-full h-full"
                />
                <Button
                  type="button"
                  variant="destructive"
                  size="icon"
                  class="absolute top-0 right-0 h-8 w-8 rounded-full"
                  @click="clearImage"
                >
                  <XIcon class="h-4 w-4" />
                </Button>
              </div>
              <div
                v-else
                class="w-32 h-32 border-2 border-dashed rounded-full flex flex-col items-center justify-center"
              >
                <input
                  ref="fileInput"
                  type="file"
                  accept="image/*"
                  class="hidden"
                  @change="handleImageChange"
                />
                <UserIcon class="h-8 w-8 text-muted-foreground mb-2" />
                <Button type="button" variant="outline" size="sm" @click="triggerFileInput">
                  <UploadIcon class="h-4 w-4 mr-2" />
                  Upload Photo
                </Button>
              </div>
            </div>
          </div>
        </div>
  
        <!-- Username -->
        <div class="space-y-2">
          <Label for="username">Username</Label>
          <Input
            id="username"
            v-model="userForm.username"
            placeholder="Your username"
            required
            class="w-full"
          />
        </div>
  
        <!-- Email -->
        <div class="space-y-2">
          <Label for="email">Email</Label>
          <Input
            id="email"
            v-model="userForm.email"
            type="email"
            placeholder="Your email address"
            class="w-full"
          />
        </div>
  
        <!-- Form Actions -->
        <div class="flex flex-col-reverse sm:flex-row sm:justify-end gap-3 pt-6">
          <Button @click="cancel" type="button" variant="outline" class="w-full sm:w-auto">
            Cancel
          </Button>
          <Button 
            type="submit" 
            :disabled="isSaving || !isFormValid" 
            class="w-full sm:w-auto"
          >
            <Loader2Icon v-if="isSaving" class="h-4 w-4 mr-2 animate-spin" />
            {{ isSaving ? 'Saving...' : 'Save Changes' }}
          </Button>
        </div>
      </form>
    </div>
  </template>
  
  <script>
  import { ref, reactive, computed } from 'vue'
  import { useRouter } from 'vue-router'
  import { useToast } from 'vue-toastification'
  import { Button } from '@/components/ui/button'
  import { Input } from '@/components/ui/input'
  import { Label } from '@/components/ui/label'
  import { 
    UserIcon,
    Loader2Icon, 
    UploadIcon, 
    XIcon 
  } from 'lucide-vue-next'
  
  export default {
    name: 'EditProfile',
    components: {
      Button,
      Input,
      Label,
      UserIcon,
      Loader2Icon,
      UploadIcon,
      XIcon
    },
    name: 'EditProfile',
    setup() {
      const router = useRouter()
      const toast = useToast()
      const fileInput = ref(null)
      const imagePreview = ref(null)
      const selectedFile = ref(null)
      const isSaving = ref(false)
      const isLoading = ref(true)
  
      const userForm = reactive({
        username: '',
        email: '',
        avatar_url: null
      })
  
      const isFormValid = computed(() => {
        return userForm.username?.trim() !== ''
      })
  
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001'
      const session_token = localStorage.getItem('supabase_session')
        ? JSON.parse(localStorage.getItem('supabase_session')).access_token
        : null
  
      const fetchUserData = async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/api/user`, {
            headers: {
              'Authorization': `Bearer ${session_token}`
            }
          })
  
          if (!response.ok) {
            throw new Error('Failed to fetch user data')
          }
  
          const data = await response.json()
          const userData = data.user || data
  
          // Update form data
          userForm.username = userData.username || ''
          userForm.email = userData.email || ''
          userForm.avatar_url = userData.avatar_url || null
  
        } catch (error) {
          toast.error('Failed to load user data')
        } finally {
          isLoading.value = false
        }
      }
  
      // Fetch user data when component is mounted
      fetchUserData()
  
      const triggerFileInput = () => {
        fileInput.value.click()
      }
  
      const handleImageChange = (e) => {
        const file = e.target.files[0]
        if (file) {
          if (file.size > 2 * 1024 * 1024) {
            toast.error('Image size should be less than 2MB')
            return
          }
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
        userForm.avatar_url = null
      }
  
      const saveProfile = async () => {
        if (!isFormValid.value) return
        
        isSaving.value = true
  
        try {
          const formData = new FormData()
          
          if (selectedFile.value) {
            formData.append('avatar', selectedFile.value)
          }
  
          formData.append('data', JSON.stringify({
            username: userForm.username,
            email: userForm.email
          }))
  
          const response = await fetch(`${API_BASE_URL}/api/user`, {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${session_token}`
            },
            body: formData
          })
  
          if (!response.ok) {
            throw new Error('Failed to update profile')
          }
  
          toast.success('Profile updated successfully!')
          router.push('/profile')
        } catch (error) {
          toast.error(error.message || 'An error occurred while saving')
        } finally {
          isSaving.value = false
        }
      }
  
      const cancel = () => {
        router.go(-1)
      }
  
      return {
        userForm,
        fileInput,
        imagePreview,
        isSaving,
        isLoading,
        isFormValid,
        triggerFileInput,
        handleImageChange,
        clearImage,
        saveProfile,
        cancel
      }
    }
  }
  </script>
  
  <style scoped>
  .container {
    min-height: calc(100vh - 128px);
  }
  
  @media (max-width: 640px) {
    .container {
      padding: 1rem;
    }
  }
  </style>