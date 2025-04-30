<template>
  <div class="h-screen flex flex-col">
    <!-- Header Section -->
    <div class="bg-background border-b p-4">
      <div class="container mx-auto flex justify-between items-center">
        <div class="flex items-center">
          <!-- Show Thumbnail -->
          <img
            v-if="showImageUrl"
            :src="showImageUrl"
            alt="Show Thumbnail"
            class="h-10 w-10 mr-4 rounded"
          />
          <div>
            <h1 class="text-xl font-bold inline-block">{{ showName }}</h1>
            <p class="text-sm text-muted-foreground">{{ episodeName }}</p>
          </div>
        </div>
        <Button variant="outline" @click="goBack" size="sm">
          <ArrowLeftIcon class="h-4 w-4 mr-2" />
          Back to Shows
        </Button>
      </div>
    </div>

    <!-- Completion Message -->
    <div class="bg-green-100 dark:bg-green-900/30 border-b p-4">
      <div class="container mx-auto text-center">
        <h2 class="text-lg font-semibold text-green-800 dark:text-green-200">
          🎉 Story Completed!
        </h2>
        <p class="text-sm text-green-700 dark:text-green-300">
          You've reached the end of this episode. Rate your experience below!
        </p>
      </div>
    </div>

    <!-- Chat History -->
    <div class="flex-1 overflow-hidden">
      <div class="h-full flex flex-col border rounded-lg bg-background dark:bg-gray-900">
        <!-- Messages Area -->
        <div ref="messagesContainer" class="flex-[5] overflow-y-auto p-4 space-y-4"> 
          <div
            v-for="(msg, index) in messages"
            :key="index"
            class="flex items-start gap-3"
            :class="{ 'justify-start flex-row-reverse': msg.role === 'Player' }"
          >
            <!-- Avatar -->
            <img
              v-if="(msg.role === 'Player' && playerImageUrl) || (msg.role !== 'Player' && getCharacterImageUrl(msg.role))"
              :src="msg.role === 'Player' ? playerImageUrl : getCharacterImageUrl(msg.role)"
              alt="Avatar"
              class="h-14 w-14 rounded-full flex-shrink-0"
            />

            <!-- Content -->
            <div class="flex-1 max-w-[90%]" :class="{ 'text-right ml-auto': msg.role === 'Player' }">
              <div class="flex items-center" :class="{ 'justify-end': msg.role === 'Player' }">
                <span class="font-semibold text-sm" :class="getRoleColor(msg.role)">
                  {{ msg.role === 'Player' ? player_name : msg.role }}
                </span>
              </div>
              <div
                class="p-2 rounded-lg whitespace-pre-wrap break-words"
                :class="getMessageStyle(msg.type, msg.role)"
              >
                {{ msg.content }}
              </div>
            </div>
          </div>
        </div>

        <!-- Rating Section -->
        <div class="flex-[1] border-t p-2"> 
          <div class="max-w-md mx-auto text-center">
            <h3 class="text-lg font-semibold mb-4">Rate This Experience</h3>
            <div class="flex justify-center gap-2 mb-4">
              <button
                v-for="star in 5"
                :key="star"
                @click="!ratingSubmitted && setRating(star)"
                :disabled="ratingSubmitted"
                class="p-2 transition-all duration-150"
                :class="[
                  rating >= star
                    ? 'text-yellow-400 dark:text-yellow-300 scale-110'
                    : 'text-gray-300 dark:text-gray-600',
                  !ratingSubmitted ? 'hover:text-yellow-300 hover:scale-125' : ''
                ]"
              >
                <StarIcon class="w-8 h-8 fill-current" />
              </button>
            </div>
             <!-- Add Feedback Section Here -->
            <div class="mt-4 text-left">
              <label class="block text-sm font-medium text-foreground mb-2">
                Additional Feedback (optional)
              </label>
              <textarea
                v-model="feedback"
                :disabled="ratingSubmitted"
                rows="3"
                class="w-full p-2 border rounded-md bg-background transition-colors focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50"
                placeholder="What did you think of this episode? Any Suggestions to improve the overall experience?"></textarea>
            </div>
            <Button
              @click="submitRating"
              :disabled="!rating || ratingSubmitted || isSubmitting"
              class="w-full max-w-xs mx-auto"
            >
              <template v-if="isSubmitting">
                <LoaderIcon class="h-4 w-4 mr-2 animate-spin" />
                Submitting...
              </template>
              <template v-else>
                {{ ratingSubmitted ? 'Rating Submitted' : 'Submit Rating' }}
              </template>
            </Button>
            <p v-if="ratingSubmitted" class="text-sm text-green-600 dark:text-green-400 mt-2">
              Thank you for your rating!
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ArrowLeftIcon, StarIcon, LoaderIcon } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { fetchApi } from '@/lib/utils'
import { supabase } from '@/composables/useSupabase'
import { useToast } from 'vue-toastification'

export default {
  name: 'EndPage',
  components: { Button, ArrowLeftIcon, StarIcon, LoaderIcon },
  data() {
    return {
      showId: null,
      episodeId: '',
      chatId: this.$route.params.chat_id,
      showName: 'Loading...',
      episodeName: 'Loading...',
      messages: [],
      player_name: 'Player',
      playerImageUrl: '',
      showImageUrl: '',
      rating: 0,
      feedback: '',
      isSubmitting: false,
      ratingSubmitted: false,
      toast: useToast(),
      characterColors: {},
      characterImages: {},
      colorPalette: [
        'text-red-600 dark:text-red-400',
        'text-yellow-600 dark:text-yellow-400',
        'text-blue-600 dark:text-blue-400',
        'text-indigo-600 dark:text-indigo-400',
        'text-purple-600 dark:text-purple-400',
        'text-pink-600 dark:text-pink-400',
        'text-orange-600 dark:text-orange-400',
        'text-teal-600 dark:text-teal-400'
      ],
    }
  },
  async mounted() {
    await this.fetchChatDetails()
    this.scrollToBottom()
  },
  methods: {
    async fetchChatDetails() {
      try {
        const { data } = await supabase.auth.getSession()
        const token = data.session?.access_token
        // Fetch chat
        const chatRes = await fetchApi(`api/chats/${this.chatId}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        const chatData = chatRes.chat
        this.player_name = chatData.player_name
        this.playerImageUrl = chatData.player_image_url || ''
        this.episodeName = chatData.episodes?.name
        this.episodeId = chatData.episode_id
        this.showId = chatData.episodes?.show_id
        this.messages = (chatRes.messages || []).sort((a, b) => a.sequence - b.sequence)
        // Fetch show
        if (this.showId) {
          const showRes = await fetchApi(`api/shows/${this.showId}`, {
            headers: { Authorization: `Bearer ${token}` }
          })
          const show = showRes.show
          this.showName = show.name
          this.showImageUrl = show.image_url || ''
          // Parse characters
          let chars = []
          try {
            chars = typeof show.characters === 'string'
              ? JSON.parse(show.characters)
              : show.characters || []
          } catch {
            chars = []
          }
          chars.forEach((c, idx) => {
            const key = c.name.trim().toLowerCase()
            this.characterColors[key] = this.colorPalette[idx % this.colorPalette.length]
            this.characterImages[key] = c.image_url
          })
        }
        await this.fetchExistingRating()
      } catch (e) {
        console.error(e)
        this.toast.error('Failed to load history.')
      }
    },
    async fetchExistingRating() {
    try {
      const res = await fetchApi(`api/ratings/${this.episodeId}`)
      if (res.rating) {
        this.rating = Number(res.rating.rating)
        this.feedback = res.rating.feedback || '' // Add this line
        this.ratingSubmitted = true
      }
    } catch {}
  },
    setRating(val) { if (!this.ratingSubmitted) this.rating = val },
    async submitRating() {
    if (!this.rating) return
    this.isSubmitting = true
    try {
      await fetchApi(`api/ratings/${this.episodeId}`, {
        method: 'POST',
        body: JSON.stringify({
          show_id: this.showId,
          episode_id: this.episodeId,
          rating: this.rating,
          feedback: this.feedback // Add feedback to payload
        })
      })
      this.ratingSubmitted = true
      this.toast.success('Rating submitted!')
    } catch {
      this.toast.error('Submit failed.')
    } finally {
      this.isSubmitting = false
    }
  },
    scrollToBottom() {
      this.$nextTick(() => {
        const c = this.$refs.messagesContainer
        if (c) c.scrollTop = c.scrollHeight
      })
    },
    goBack() { this.$router.push('/shows') },
    getCharacterImageUrl(role) {
      return this.characterImages[role.trim().toLowerCase()] || ''
    },
    getRoleColor(role) {
      const key = role.trim().toLowerCase()
      return this.characterColors[key]
        || { narration:'text-purple-600 dark:text-purple-400', player:'text-blue-600 dark:text-blue-400', system:'text-gray-600 dark:text-gray-400' }[key]
        || 'text-gray-600 dark:text-gray-400'
    },
    getMessageStyle(type, role) {
      const map = {
        narration: 'bg-purple-100 dark:bg-purple-900/30 italic',
        player_input: 'bg-blue-100 dark:bg-blue-900/30',
        system: 'bg-gray-100 dark:bg-gray-800/50 text-sm'
      }
      if (type === 'actor_dialogue') {
        const key = role.trim().toLowerCase()
        if (this.characterColors[key]) {
          const base = this.characterColors[key].split(' ')[0].replace('text','bg')
          return `${base}/20 dark:${base}/30`
        }
      }
      return map[type] || 'bg-gray-100 dark:bg-gray-800/30'
    }
  }
}
</script>

<style scoped>
/* Scrollbar */
.overflow-y-auto::-webkit-scrollbar { width: 8px; }
.overflow-y-auto::-webkit-scrollbar-track { background: transparent; }
.overflow-y-auto::-webkit-scrollbar-thumb { background-color: rgba(156,163,175,0.5); border-radius:4px; }
.dark .overflow-y-auto::-webkit-scrollbar-thumb { background-color: rgba(156,163,175,0.3); }

/* Star hover */
button:hover .fill-current { transform: scale(1.2); }
textarea {
  min-height: 100px;
  resize: vertical;
}
</style>
