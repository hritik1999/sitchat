<template>
    <div class="container mx-auto px-4 py-8 max-w-4xl">
      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold tracking-tight">
          {{ editingEpisode ? 'Edit Episode' : 'Create New Episode' }}
        </h1>
        <p class="text-muted-foreground text-sm mt-2">
          {{ editingEpisode ? 'Update your episode details' : 'Add a new episode to your show' }}
        </p>
      </div>
  
      <!-- Main Form -->
      <form @submit.prevent="saveEpisode" class="space-y-6">
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
    props: {
      editingEpisode: {
        type: Boolean,
        default: false
      },
      initialData: {
        type: Object,
        default: () => ({
          name: '',
          description: '',
          background: '',
          plot_objectives: ['']
        })
      }
    },
    setup() {
      // Initialize router here for use throughout the component
      const router = useRouter()
      const toast = useToast()
      
      return { router, toast }
    },
    data() {
      return {
        episodeForm: { ...this.initialData },
        isSaving: false,
        API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
        session_token: localStorage.getItem('supabase_session') 
          ? JSON.parse(localStorage.getItem('supabase_session')).access_token 
          : null,
        currentUserId: localStorage.getItem('supabase_session') 
          ? JSON.parse(localStorage.getItem('supabase_session')).user?.id 
          : null,
        show_id: this.$route.params.id
      }
    },
    computed: {
      isFormValid() {
        return (
          this.episodeForm.name.trim() !== '' &&
          this.episodeForm.plot_objectives.length > 0 &&
          this.episodeForm.plot_objectives.every(obj => obj.trim() !== '')
        )
      }
    },
    methods: {
      addObjective() {
        this.episodeForm.plot_objectives.push('')
      },
      removeObjective(index) {
        this.episodeForm.plot_objectives.splice(index, 1)
      },
      async saveEpisode() {
        if (!this.isFormValid) return
        
        this.isSaving = true
        
        try {
          // Replace with your actual API endpoint
          const response = await fetch(`${this.API_BASE_URL}/api/show/${this.show_id}/episodes`, {
            method: this.editingEpisode ? 'PUT' : 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${this.session_token}`
            },
            body: JSON.stringify(this.episodeForm)
          })
  
          if (!response.ok) throw new Error('Failed to save episode')
          
          this.toast.success('Episode saved successfully!')
          // Use the router instance from setup()
          this.router.push(`/show/${this.show_id}`)
        } catch (error) {
          this.toast.error(error.message || 'An error occurred while saving')
        } finally {
          this.isSaving = false
        }
      },
      cancel() {
        // Use the router instance from setup()
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