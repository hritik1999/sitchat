<template>
  <div class="container mx-auto px-4 py-8 max-w-4xl">
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold tracking-tight">
        {{ isEditMode ? 'Edit Show' : 'Create New Show' }}
      </h1>
      <p class="text-muted-foreground text-sm mt-2">
        {{ isEditMode ? 'Update your show details' : 'Fill in the details to create a new show' }}
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex justify-center items-center min-h-[400px]">
      <Loader2Icon class="h-8 w-8 animate-spin" />
    </div>

    <!-- Main Form -->
    <form v-else @submit.prevent="saveShow" class="space-y-6">
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
          :key="index"
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
          <div class="space-y-2">
            <Label>Character Image</Label>
            <div class="grid grid-cols-1 gap-4">
              <div
                v-if="character.imagePreview"
                class="relative aspect-square bg-muted rounded-md overflow-hidden"
              >
                <img :src="character.imagePreview" alt="Preview" class="object-cover w-full h-full" />
                <Button
                  type="button"
                  variant="destructive"
                  size="icon"
                  class="absolute top-2 right-2 h-8 w-8 rounded-full"
                  @click="clearCharacterImage(index)"
                >
                  <XIcon class="h-4 w-4" />
                </Button>
              </div>
              <div
                v-else
                class="border border-dashed rounded-md p-4 flex flex-col items-center justify-center"
              >
                <input
                  type="file"
                  accept="image/*"
                  :ref="el => characterFileInputs[index] = el"
                  class="hidden"
                  @change="e => handleCharacterImageChange(e, index)"
                />

                <Button 
                  type="button" 
                  variant="outline" 
                  @click="triggerCharacterFileInput(index)"
                >
                  <UploadIcon class="h-4 w-4 mr-2" />
                  Upload Image
                </Button>
                <p class="text-xs text-muted-foreground mt-2">PNG, JPG or GIF, max 2MB</p>
              </div>
            </div>
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
        <Button @click="cancel" type="button" variant="outline" class="w-full sm:w-auto">
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
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { ImageIcon, Loader2Icon, PlusIcon, UploadIcon, XIcon } from 'lucide-vue-next'
import { fetchApi } from '@/lib/utils'

export default {
  name: 'CreateShow',
  components: { Button, Input, Label, Textarea, ImageIcon, Loader2Icon, PlusIcon, UploadIcon, XIcon },

  setup() {
    const router = useRouter()
    const toast = useToast()

    const showForm = reactive({
      name: '',
      description: '',
      relations: '',
      characters: []
    })
    // Initialize with a default character
    showForm.characters.push({ name: '', description: '', imagePreview: null, imageFile: null })

    const imagePreview = ref(null)
    const selectedFile = ref(null)
    const isSaving = ref(false)
    const isLoading = ref(false)
    const fileInput = ref(null)
    const characterFileInputs = ref([null])

    const isEditMode = computed(() => !!router.currentRoute.value.params.showId)
    const showId = computed(() => router.currentRoute.value.params.showId)

    const isFormValid = computed(() => {
      return (
        showForm.name.trim() !== '' &&
        showForm.characters.length > 0 &&
        showForm.characters.every(char =>
          char.name.trim() !== '' &&
          (isEditMode.value ? true : char.imageFile)
        )
      )
    })

    const fetchShowData = async () => {
      if (!isEditMode.value) return
      isLoading.value = true
      try {
        const data = await fetchApi(`api/shows/${showId.value}`)
        const show = data.show || data

        showForm.name = show.name || ''
        showForm.description = show.description || ''
        showForm.relations = show.relations || ''

        let chars = []
        if (typeof show.characters === 'string') {
          try { chars = JSON.parse(show.characters) } catch {} 
        } else if (Array.isArray(show.characters)) {
          chars = show.characters
        }

        if (chars.length) {
          showForm.characters = chars.map(c => ({
            name: c.name || '',
            description: c.description || '',
            imagePreview: c.image_url || null,
            imageFile: null
          }))
          characterFileInputs.value = chars.map(() => null)
        }

        if (show.image_url) imagePreview.value = show.image_url
      } catch {
        toast.error('Failed to load show data')
      } finally {
        isLoading.value = false
      }
    }

    if (isEditMode.value) fetchShowData()

    const addCharacter = () => {
      showForm.characters.push({ name: '', description: '', imagePreview: null, imageFile: null })
      characterFileInputs.value.push(null)
    }

    const removeCharacter = index => {
      showForm.characters.splice(index, 1)
      characterFileInputs.value.splice(index, 1)
    }

    const triggerFileInput = () => fileInput.value.click()

    const handleImageChange = e => {
      const file = e.target.files[0]
      if (file && file.size <= 2 * 1024 * 1024) {
        selectedFile.value = file
        imagePreview.value = URL.createObjectURL(file)
      } else {
        toast.error('Image size should be less than 2MB')
      }
    }

    const clearImage = () => {
      imagePreview.value = null
      selectedFile.value = null
      if (fileInput.value) fileInput.value.value = ''
    }

    const handleCharacterImageChange = (e, index) => {
      const file = e.target.files[0]
      if (file && file.size <= 2 * 1024 * 1024) {
        const reader = new FileReader()
        reader.onload = ev => showForm.characters[index].imagePreview = ev.target.result
        reader.readAsDataURL(file)
        showForm.characters[index].imageFile = file
      } else {
        toast.error('Image size should be less than 2MB')
      }
    }

    const triggerCharacterFileInput = index => {
      const inp = characterFileInputs.value[index]
      if (inp) inp.click()
    }

    const clearCharacterImage = index => {
      showForm.characters[index].imagePreview = null
      showForm.characters[index].imageFile = null
      const inp = characterFileInputs.value[index]
      if (inp) inp.value = ''
    }

    const saveShow = async () => {
      if (!isFormValid.value) return
      if (!isEditMode.value && !selectedFile.value) {
        toast.error('Please select an image for the show')
        return
      }
      isSaving.value = true
      try {
        const formData = new FormData()
        formData.append('data', JSON.stringify({
          name: showForm.name,
          description: showForm.description,
          characters: showForm.characters.map(char => ({
            name: char.name,
            description: char.description,
            ...(isEditMode.value && !char.imageFile && { image_url: char.imagePreview })
          })),
          relations: showForm.relations
        }))
        if (selectedFile.value) formData.append('image', selectedFile.value)
        showForm.characters.forEach((char, idx) => {
          if (char.imageFile) formData.append(`characters[${idx}].image`, char.imageFile)
        })
        const endpoint = isEditMode.value ? `api/shows/${showId.value}` : `api/shows`
        await fetchApi(endpoint, {
          method: isEditMode.value ? 'PUT' : 'POST',
          body: formData
        })
        toast.success(`Show ${isEditMode.value ? 'updated' : 'created'} successfully!`)
        router.push('/shows')
      } catch (err) {
        toast.error(err.message || 'An error occurred while saving')
      } finally {
        isSaving.value = false
      }
    }

    const cancel = () => router.go(-1)

    return {
      showForm,
      imagePreview,
      selectedFile,
      isSaving,
      isLoading,
      isEditMode,
      isFormValid,
      fileInput,
      characterFileInputs,
      addCharacter,
      removeCharacter,
      triggerFileInput,
      handleImageChange,
      clearImage,
      handleCharacterImageChange,
      triggerCharacterFileInput,
      clearCharacterImage,
      saveShow,
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