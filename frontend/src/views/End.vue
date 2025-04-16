<template>
  <div class="h-screen flex flex-col">
    <!-- Header Section -->
    <div class="bg-background border-b p-4">
      <div class="container mx-auto flex justify-between items-center">
        <div>
          <h1 class="text-xl font-bold">{{ showName }}</h1>
          <p class="text-sm text-muted-foreground">{{ episodeName }}</p>
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
        <p class="text-sm text-green-700 dark:text-green-300 mt-1">
          You've reached the end of this episode. Rate your experience below!
        </p>
      </div>
    </div>

    <!-- Chat History -->
    <div class="flex-1 overflow-hidden container mx-auto p-4">
      <div class="h-full flex flex-col border rounded-lg bg-background dark:bg-gray-900">
        <!-- Messages Area -->
        <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
          <!-- Messages -->
          <div v-for="(msg, index) in messages" :key="index" class="flex gap-3">
            <div 
              class="flex-1" 
              :class="{
                'flex justify-end': msg.role === 'Player'
              }"
            >
              <div class="max-w-[90%]">
                <!-- Role Label -->
                <div class="flex items-center gap-2 mb-1" :class="{ 'justify-end': msg.role === 'Player' }">
                  <span class="font-semibold text-sm" :class="getRoleColor(msg.role || '')">
                    {{ msg.role === 'Player' ? player_name : msg.role }}
                  </span>
                </div>
                
                <!-- Message Bubble -->
                <div 
                  class="p-3 rounded-lg"
                  :class="[
                    getMessageStyle(msg.type || '', msg.role || ''),
                    {
                      'ml-auto': msg.role === 'Player',
                      'whitespace-pre-wrap break-words': true
                    }
                  ]"
                >
                  {{ msg.content }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Rating Section -->
        <div class="border-t p-8">
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
import { useToast } from 'vue-toastification';

export default {
  name: 'EndPage',
  
  components: {
    Button,
    ArrowLeftIcon,
    StarIcon,
    LoaderIcon
  },

  data() {
    return {
      showId: null,
      episodeId: this.$route.params.episode_id,
      chatId: this.$route.params.chat_id,
      showName: 'Loading...',
      episodeName: 'Loading...',
      messages: [],
      rating: 0,
      isSubmitting: false,
      ratingSubmitted: false,
      toast: useToast(),
      player_name: 'Player',
      characterColors: {},
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

        // Fetch chat details
        const chatData = await fetchApi(`api/chats/${this.chatId}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        if (!chatData?.chat) throw new Error('Invalid chat data')
        this.player_name = chatData.chat.player_name || 'Player' 
        this.episodeId = chatData.chat.episode_id
        this.episodeName = chatData.chat.episodes?.name || 'Unknown Episode'
        this.messages = chatData.messages?.sort((a, b) => a.sequence - b.sequence) || []
        this.showId = chatData.chat.episodes?.show_id

        // Fetch show details
        if (chatData.chat.episodes?.show_id) {
          const showData = await fetchApi(`api/shows/${chatData.chat.episodes.show_id}`, {
            headers: { Authorization: `Bearer ${token}` }
          })
          
          if (showData?.show) {
            this.showName = showData.show.name || 'Unknown Show'
            
            // Handle characters based on type
            if (showData.show.characters) {
              let charactersArray;
              
              // Check if characters is a string and try to parse it
              if (typeof showData.show.characters === 'string') {
                try {
                  charactersArray = JSON.parse(showData.show.characters);
                  console.log('Successfully parsed characters string to array');
                } catch (parseError) {
                  console.error('Failed to parse characters string:', parseError);
                  charactersArray = [];
                }
              } 
              // Check if it's already an array
              else if (Array.isArray(showData.show.characters)) {
                charactersArray = showData.show.characters;
              } 
              // Handle object case (if characters is an object with character entries)
              else if (typeof showData.show.characters === 'object' && showData.show.characters !== null) {
                charactersArray = Object.values(showData.show.characters);
              }
              else {
                console.warn('Characters has unexpected type:', typeof showData.show.characters);
                charactersArray = [];
              }
              
              // Now assign colors to characters
              charactersArray.forEach((character, index) => {
                if (character && character.name) {
                  this.characterColors[character.name.toLowerCase()] = 
                    this.colorPalette[index % this.colorPalette.length];
                }
              });
            } else {
              console.warn('No characters data available');
            }
          }
        }

        // Fetch rating - Make this a separate request
        await this.fetchExistingRating();

      } catch (error) {
        console.error('Error fetching chat details:', error, 'Current state:', {
          chatId: this.chatId,
          episodeId: this.episodeId
        });
        this.toast.error('Failed to load chat history. Please try refreshing the page.');
      }
    },

    async fetchExistingRating() {
      try {
        const ratingData = await fetchApi(`api/ratings/${this.episodeId}`, {
          method: 'GET',
        });
        
        if (ratingData?.rating) {
          // Ensure it's treated as a number
          this.rating = Number(ratingData.rating.rating);
          this.ratingSubmitted = true;
        }
      } catch (error) {
        console.warn('No existing rating found:', error);
        // No existing rating, which is fine
      }
    },

    setRating(value) {
      if (!this.ratingSubmitted) {
        this.rating = value;
      }
    },

    async submitRating() {
      if (!this.rating || this.ratingSubmitted || this.isSubmitting) return;
      
      this.isSubmitting = true;
      
      try {
        await fetchApi(`api/ratings/${this.episodeId}`, {
          method: 'POST',
          body: JSON.stringify({
            show_id: this.showId,
            episode_id: this.episodeId,
            rating: this.rating
          })
        });

        this.ratingSubmitted = true;
        this.toast.success('Rating submitted successfully!');

      } catch (error) {
        console.error('Rating submission failed:', error);
        this.toast.error('Failed to submit rating. Please try again.');
      } finally {
        this.isSubmitting = false;
      }
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    },

    goBack() {
      this.$router.push('/shows');
    },

    getRoleColor(role) {
      const lowerRole = role.toLowerCase();
      // Check lowercase version
      if (this.characterColors[lowerRole]) {
        return this.characterColors[lowerRole];
      }
        
      // Default colors for system roles
      const colorMap = {
        'Narration': 'text-purple-600 dark:text-purple-400',
        'Player': 'text-blue-600 dark:text-blue-400',
        'system': 'text-gray-600 dark:text-gray-400'
      };
        
      return colorMap[role] || 'text-gray-600 dark:text-gray-400';
    },

    getMessageStyle(type, role) {
      const styleMap = {
        'narration': 'bg-purple-100 dark:bg-purple-900/30 italic',
        'player_input': 'bg-blue-100 dark:bg-blue-900/30',
        'system': 'bg-gray-100 dark:bg-gray-800/50 text-sm'
      };

      if (type === 'actor_dialogue') {
        const lowerRole = role.toLowerCase();
        if (this.characterColors[lowerRole]) {
          const baseColor = this.characterColors[lowerRole].split(' ')[0];
          return `${baseColor.replace('text', 'bg')}/20 dark:${baseColor.replace('text', 'bg')}/30`;
        }
      }

      return styleMap[type] || 'bg-gray-100 dark:bg-gray-800/30';
    }
  }
}
</script>

<style scoped>
/* Consistent scrollbar styling with chat page */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 4px;
}

.dark .overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.3);
}

/* Rating animation */
button:hover .star-icon {
  transform: scale(1.2);
}
</style>