<template>
    <div class="container mx-auto px-4 py-8 max-w-4xl">
      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold tracking-tight">
          {{ isEditMode ? 'Edit Episode' : 'Create New Episode' }}
        </h1>
        <p class="text-muted-foreground text-sm mt-2">
          {{ isEditMode ? 'Update your episode details' : 'Add a new episode to your show' }}
        </p>
      </div>
  
      <!-- Loading State -->
      <div v-if="isLoading" class="flex justify-center items-center min-h-[400px]">
        <Loader2Icon class="h-8 w-8 animate-spin" />
      </div>
  
      <!-- Main Form -->
      <form v-else @submit.prevent="saveEpisode" class="space-y-6">
        <!-- Episode Name -->
        <div class="space-y-2">
          <Label for="episode-name">Episode Name</Label>
          <Input
            id="episode-name"
            v-model="episodeForm.name"
            placeholder="e.g. The One With the Reunion"
            required
            class="w-full"
          />
        </div>
  
        <!-- Description -->
        <div class="space-y-2">
          <Label for="episode-description">Description</Label>
          <Textarea
            id="episode-description"
            v-model="episodeForm.description"
            placeholder="Brief description of the episode"
            rows="3"
            class="w-full"
          />
        </div>
  
        <!-- Scene Background -->
        <div class="space-y-2">
          <Label for="episode-background">Scene Background</Label>
          <Textarea
            id="episode-background"
            v-model="episodeForm.background"
            placeholder="The initial scene setup"
            rows="4"
            class="w-full"
          />
        </div>
  
        <!-- Plot Objectives Section -->
        <div class="space-y-2">
          <div class="flex justify-between items-center">
            <Label>Plot Objectives</Label>
            <Button @click="addObjective" type="button" variant="outline" size="sm">
              <PlusIcon class="h-4 w-4 mr-2" />
              Add Objective
            </Button>
          </div>
  
          <!-- Objective Cards -->
          <div
            v-for="(objective, index) in episodeForm.plot_objectives"
            :key="index"
            class="p-4 border rounded-lg relative space-y-2 mt-2"
          >
          <Button
                type="button"
                variant="destructive"
                size="icon"
                class="absolute right-2 top-2"
                @click="removeObjective(index)"
                :disabled="episodeForm.plot_objectives.length <= 1"
              >
              <XIcon class="h-4 w-4" />
              <span class="sr-only">Remove</span>
            </Button>
            <div class="space-y-2">
              <Label :for="`objective-${index}`">Objective {{ index + 1 }}</Label>
              <Textarea
                :id="`objective-${index}`"
                v-model="episodeForm.plot_objectives[index]"
                placeholder="Describe what needs to happen in this stage"
                rows="2"
                class="w-full"
              />
            </div>
          </div>
        </div>
  
        <!-- Form Actions -->
        <div class="flex flex-col-reverse sm:flex-row sm:justify-end gap-3 pt-6">
          <Button @click="cancel" type="button" variant="outline" class="w-full sm:w-auto">
            Cancel
          </Button>
          <Button type="submit" :disabled="isSaving || !isFormValid" class="w-full sm:w-auto">
            <Loader2Icon v-if="isSaving" class="h-4 w-4 mr-2 animate-spin" />
            {{ isSaving ? 'Saving...' : 'Save Episode' }}
          </Button>
        </div>
      </form>
    </div>
  </template>
  
  <script>
  import { Button } from '@/components/ui/button'
  import { Input } from '@/components/ui/input'
  import { Label } from '@/components/ui/label'
  import { Textarea } from '@/components/ui/textarea'
  import { Loader2Icon, PlusIcon, XIcon } from 'lucide-vue-next'
  import { useToast } from 'vue-toastification'
  import { useRouter } from 'vue-router'
  import { fetchApi } from '@/lib/utils'
  
  export default {
    name: 'CreateEpisode',
    components: {
      Button,
      Input,
      Label,
      Textarea,
      Loader2Icon,
      PlusIcon,
      XIcon
    },
    
    setup() {
      const router = useRouter()
      const toast = useToast()
      return { router, toast }
    },
  
    data() {
      return {
        episodeForm: {
          name: '',
          description: '',
          background: '',
          plot_objectives: ['']
        },
        isSaving: false,
        isLoading: false,
        API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
        // No longer storing session_token directly
        // fetchApi will handle authentication
        currentUserId: null // Will be populated after fetching user data
      }
    },
  
    computed: {
      isEditMode() {
        return !!this.$route.params.episodeId
      },
      
      showId() {
        return this.$route.params.showId || this.$route.params.id
      },
  
      episodeId() {
        return this.$route.params.episodeId
      },
  
      isFormValid() {
        return (
          this.episodeForm?.name?.trim() !== '' &&
          Array.isArray(this.episodeForm?.plot_objectives) &&
          this.episodeForm.plot_objectives.length > 0 &&
          this.episodeForm.plot_objectives.every(obj => obj && obj.trim() !== '')
        )
      }
    },
  
    async created() {
      if (this.isEditMode) {
        await this.fetchEpisodeData()
      }
    },
  
    methods: {
      async fetchEpisodeData() {
        this.isLoading = true
        try {
          const episodeData = await fetchApi(
            `api/show/${this.showId}/episodes/${this.episodeId}`
          )
          
          const episode = episodeData.episode || episodeData
          let plotObjectives = []

          try {
            if (typeof episode.plot_objectives === 'string') {
              plotObjectives = JSON.parse(episode.plot_objectives)
            } else if (Array.isArray(episode.plot_objectives)) {
              plotObjectives = episode.plot_objectives
            }
          } catch (e) {
            console.error('Error parsing plot objectives:', e)
            this.toast.error('Error parsing episode objectives')
          }

          // Ensure we have at least one objective
          if (plotObjectives.length === 0) {
            plotObjectives = ['']
          }

          this.episodeForm = {
            name: episode.name || '',
            description: episode.description || '',
            background: episode.background || '',
            plot_objectives: plotObjectives
          }
        } catch (error) {
          this.toast.error('Failed to load episode data')
          console.error('Fetch episode error:', error)
        } finally {
          this.isLoading = false
        }
      },
  
      addObjective() {
        this.episodeForm.plot_objectives.push('')
      },
  
      removeObjective(index) {
        // Don't allow removing the last objective
        if (this.episodeForm.plot_objectives.length > 1) {
          this.episodeForm.plot_objectives.splice(index, 1)
        }
      },
  
      async saveEpisode() {
        if (!this.isFormValid) return
        
        this.isSaving = true
        const url = this.isEditMode
          ? `api/show/${this.showId}/episodes/${this.episodeId}`
          : `api/show/${this.showId}/episodes`
  
        try {
          await fetchApi(url, {
            method: this.isEditMode ? 'PUT' : 'POST',
            body: JSON.stringify({
              ...this.episodeForm
            })
          })
  
          this.toast.success(`Episode ${this.isEditMode ? 'updated' : 'created'} successfully!`)
          this.router.push(`/show/${this.showId}`)
        } catch (error) {
          this.toast.error(error.message || 'An error occurred while saving')
        } finally {
          this.isSaving = false
        }
      },
  
      cancel() {
        this.router.go(-1)
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