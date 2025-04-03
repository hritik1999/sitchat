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
          Back
        </Button>
      </div>
    </div>

    <!-- Progress Bar -->
    <div class="bg-background border-b p-4">
      <div class="container mx-auto">
        <div class="flex justify-between items-center mb-2">
          <span class="text-sm">Objective Progress</span>
          <span class="text-sm">{{ objectiveProgress }}</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
          <div 
            class="bg-blue-600 h-2 rounded-full transition-all duration-300" 
            :style="{ width: `${progress}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Director Directing Message - with loading bar -->
<div v-if="directorDirecting" class="container mx-auto px-4 pt-2">
  <div class="text-center text-sm text-white py-2 bg-indigo-600 dark:bg-indigo-800 rounded-md p-2 animate-pulse">
    <span class="font-medium">{{ this.director_message }}</span>
  </div>
  <!-- Loading Bar -->
  <div class="mt-2 h-1 bg-gray-200 dark:bg-gray-700 rounded-full">
    <div class="h-full bg-indigo-500 dark:bg-indigo-400 rounded-full animate-director-progress"></div>
  </div>
</div>

    <!-- Chat Container -->
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
          <!-- Typing Indicators - Inside chat window -->
          <div v-if="hasActiveTypingIndicators" class="my-2">
            <div v-for="(status, role) in typingIndicators" :key="role">
              <div 
                v-if="status === 'typing'"
                class="flex items-start gap-3"
              >
                <div class="flex-1 max-w-[90%]">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="font-semibold text-sm" :class="getRoleColor(role)">
                      {{ role === 'Player' ? player_name : role }}
                    </span>
                  </div>
                  <div class="p-3 rounded-lg bg-gray-100 dark:bg-gray-800 inline-flex items-center">
                    <div class="flex space-x-1">
                      <div class="h-2 w-2 bg-current rounded-full animate-bounce" style="animation-delay: 0ms" />
                      <div class="h-2 w-2 bg-current rounded-full animate-bounce" style="animation-delay: 150ms" />
                      <div class="h-2 w-2 bg-current rounded-full animate-bounce" style="animation-delay: 300ms" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="bg-red-100 dark:bg-red-900/30 p-3 rounded-lg text-red-700 dark:text-red-300 text-sm">
            {{ errorMessage }}
          </div>
        </div>

        <!-- Input Area -->
        <div class="border-t p-4">
          <div class="space-y-4">
            <Textarea
              ref="messageInput"
              v-model="input"
              placeholder="Type your response..."
              class="resize-none"
              rows="2"
              :disabled="isSending || storyCompleted"
              maxlength="500"
              @keydown.enter.exact.prevent="sendMessage"
              @keydown="handleTyping"
            />
            <div class="flex justify-between items-center">
              <span class="text-sm text-muted-foreground">
                {{ input.length }}/500
              </span>
              <Button @click="sendMessage" :disabled="!input.trim() || isSending || storyCompleted">
                Send
                <SendIcon class="h-4 w-4 ml-2" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ArrowLeftIcon, SendIcon } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Textarea } from '@/components/ui/textarea'
import { fetchApi } from '@/lib/utils'
import { supabase } from '@/composables/useSupabase'
import io from 'socket.io-client'
import { useToast } from 'vue-toastification';

export default {
  name: 'ChatPage',
  
  components: {
    Button,
    Progress,
    Textarea,
    ArrowLeftIcon,
    SendIcon
  },

  data() {
    return {
      progress: 0,
      objectiveIndex: 0,
      totalObjectives: 1,
      objectiveProgress: '0/1',
      isTyping: false,
      API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
      SOCKET_URL: import.meta.env.VITE_SOCKET_URL || 'http://localhost:5001',
      showId: this.$route.params.show_id,
      episodeId:'',
      chatId: this.$route.params.chat_id,
      showName: 'Loading...',
      episodeName: 'Loading...',
      input: '',
      toast: null,
      characters: [],
      player_name:'',
      isSending: false,
      directorDirecting: false,
      typingIndicators: {},
      messages: [],
      statusMessage: '',
      director_message: '',
      errorMessage: '',
      socket: null,
      isConnected: false,
      isChatStarted: false,
      storyCompleted: false,
      typingTimeout: null,
      player_name: 'Player',
      characterColors: {}, // New property to store character colors
      colorPalette: [ // Predefined color classes for characters
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
  
  created() {
    this.toast = useToast()
  },

  mounted() {
    // Initialize Socket.io connection
    this.connectToSocket()
    
    // Fetch show and episode details
    this.fetchChatDetails()
  },

  beforeUnmount() {
    this.disconnectSocket()
  },

  computed: {
    hasActiveTypingIndicators() {
      // Check if any indicator has 'typing' status
      return Object.values(this.typingIndicators).some(status => status === 'typing');
    }
  },
  
  methods: {
    async fetchChatDetails() {
      try {
        // Get chat details
        const data = await fetchApi(`api/chats/${this.chatId}`)
        
        if (!data || !data.chat) {
          throw new Error('Invalid chat data received')
        }
        
        const chatData = data.chat
        this.player_name = chatData.player_name || 'Player' 
        this.episodeId = chatData.episode_id || this.episodeId
        this.episodeName = chatData.episodes?.name || 'Unknown Episode'
        this.objectiveIndex = chatData.current_objective_index
        this.totalObjectives = JSON.parse(chatData.episodes.plot_objectives).length
        this.storyCompleted = chatData.story_completed || false
        
        // If we have a show ID from the episode
        if (chatData.episodes?.show_id) {
          const showData = await fetchApi(`api/shows/${chatData.episodes.show_id}`)
          if (showData && showData.show) {
            this.showId = showData.show.id
            this.showName = showData.show.name || 'Unknown Show'
            const characters = showData.show.characters
            for (const character of characters) {
              this.characters.push({
                name: character.name,
                description: character.description
              })
            }
            // Assign colors to characters
            showData.show.characters.forEach((character, index) => {
              this.characterColors[character.name.toLowerCase()] = 
                  this.colorPalette[index % this.colorPalette.length]
            })
          }
        }
        const messages = data.messages
        
        for (const message of messages) {
          this.messages.push({
            role: message.role,
            content: message.content,
            type: message.type,
            sequence: message.sequence
          })
          this.messages.sort((a, b) => a.sequence - b.sequence)
        }
      } catch (error) {
        console.error('Error fetching chat details:', error)
        this.errorMessage = 'Failed to load chat details. Please try refreshing the page.'
      }
    },

    async connectToSocket() {
      try {
        // Get current session for authentication
        const { data } = await supabase.auth.getSession();
        const token = data.session?.access_token;

        // Initialize Socket.io connection with auth token
        this.socket = io(this.SOCKET_URL, {
          auth: {
            token: token
          },
          extraHeaders: {
            Authorization: token ? `Bearer ${token}` : ''
          }
        });

        // Connection events
        this.socket.on('connect', this.handleConnect);
        this.socket.on('connect_error', this.handleConnectionError);
        this.socket.on('disconnect', this.handleDisconnect);
        
        // Chat events
        this.socket.on('dialogue', this.handleDialogue);
        this.socket.on('status', this.handleStatus);
        this.socket.on('error', this.handleError);
        this.socket.on('objective_status', this.handleObjectiveStatus);
        this.socket.on('typing_indicator', this.handleTypingIndicator);
        this.socket.on('director_status', this.handleDirectorStatus);
        this.socket.on('player_action', this.handlePlayerAction);
      } catch (error) {
        console.error('Error connecting to socket:', error);
        this.errorMessage = 'Connection error. Please try refreshing the page.';
      }
    },

    disconnectSocket() {
  if (this.socket) {
    // First explicitly leave the chat to ensure proper cleanup
    if (this.chatId) {
      this.socket.emit('leave_chat', { chat_id: this.chatId });
      console.log(`Explicitly left chat: ${this.chatId}`);
    }
    
    // Short timeout to allow leave_chat to be processed
    setTimeout(() => {
      // Remove all event listeners
      this.socket.off('connect');
      this.socket.off('connect_error');
      this.socket.off('disconnect');
      this.socket.off('dialogue');
      this.socket.off('status');
      this.socket.off('error');
      this.socket.off('objective_status');
      this.socket.off('typing_indicator');
      this.socket.off('director_status');
      this.socket.off('player_action');
      
      // Then disconnect
      this.socket.disconnect();
      console.log('Socket disconnected');
    }, 200); // Short delay to allow leave_chat to be processed
  }
},

    handleConnect() {
      this.isConnected = true
      this.errorMessage = ''
      console.log('Connected to socket server')
      
      // Join the chat room
      this.socket.emit('join_chat', { chat_id: this.chatId })
    },

    handleConnectionError(error) {
      this.isConnected = false
      this.errorMessage = 'Connection to server failed. Please try refreshing the page.'
      console.error('Socket connection error:', error)
    },

    handleDisconnect(reason) {
      this.isConnected = false
      console.log('Disconnected from socket server:', reason)
      
      if (reason === 'io server disconnect') {
        // Server disconnected us, try to reconnect
        this.socket.connect()
      }
    },

    sendMessage() {
      if (!this.input.trim() || this.isSending || this.storyCompleted) return

      this.isSending = true
      
      // Add to local messages immediately for responsive UI
      this.messages.push({
        role: 'Player',
        content: this.input,
        type: 'player_input'
      })
      
      // Send to server
      this.socket.emit('player_input', {
        chat_id: this.chatId,
        input: this.input
      })
      
      // Clear input and scroll
      this.input = ''
      this.scrollToBottom()
      this.isSending = false
    },

    handleTyping() {
      // Clear existing timeout
      if (this.typingTimeout) {
        clearTimeout(this.typingTimeout)
      }
      
      // Do nothing if story is completed
      if (this.storyCompleted) return
      
      // Set timeout for typing indicator
      this.typingTimeout = setTimeout(() => {
        this.isTyping = false
      }, 2000)
    },

    handleDialogue(message) {
      // Validate message before adding
      if (message && typeof message === 'object' && message.content) {
        // Add message to the chat
        this.messages.push({
          role: message.role || 'Unknown',
          content: message.content,
          type: message.type || ''
        })
        this.scrollToBottom()
      }
    },

    handleStatus(statusData) {
     
      if (statusData && statusData.message) {
        this.statusMessage = statusData.message
        console.log('Status data:', statusData)
      }
      
      if (statusData && statusData.story_completed) {
        this.storyCompleted = true
      }
    },

    handleError(errorData) {
      console.error('Socket error:', errorData)
      if (!errorData) return
      
      if (errorData.message) {
        // If the error is related to a database column issue, handle it gracefully
        if (typeof errorData.message === 'string' && 
            (errorData.message.includes("column of 'chats' in the schema cache") || 
             errorData.message.includes("full_chat"))) {
          console.error('Database schema error:', errorData.message)
          // Don't display this specific error to the user, it's a backend issue
        } else {
          this.errorMessage = errorData.message
          console.error('Socket error:', errorData)
        }
      }
    },

    handleObjectiveStatus(objectiveData) {
      if (!objectiveData) return
      
      // Update objective progress
      this.objectiveIndex = objectiveData.index  || 0
      this.totalObjectives = objectiveData.total || 1
      console.log('Objective data:', objectiveData)
      // Calculate progress percentage (fixed to ensure proper display)
      // Make sure we have at least 1% visibility when there's any progress
      if (this.objectiveIndex > 0 && this.totalObjectives > 0) {
        this.progress = Math.max(1, Math.floor((this.objectiveIndex / this.totalObjectives) * 100));
      } else {
        this.progress = 0;
      }
      
      // Update progress text
      this.objectiveProgress = `${this.objectiveIndex} /${this.totalObjectives}`
      
      // Check if story is completed
      if (objectiveData.story_completed || objectiveData.final) {
        this.storyCompleted = true
        this.statusMessage = "Story completed! You've reached the end of this episode."
      }
      
      this.scrollToBottom()
    },

    handleTypingIndicator(typingData) {
      if (!typingData || !typingData.role) return
      
      // Update typing indicators
      this.typingIndicators = {
        ...this.typingIndicators,
        [typingData.role]: typingData.status || 'idle'
      }
      
      this.scrollToBottom()
    },

    handleDirectorStatus(directorData) {
      if (!directorData) return
      
      this.directorDirecting = directorData.status === 'directing'
      
      if (directorData.message) {
        this.director_message = directorData.message
      }
      
      this.scrollToBottom()
    },
    handlePlayerAction(actionData) {
      if (!actionData || !actionData.content) return;
      
      // Show a toast notification to nudge the player
      this.toast.info("Your character can respond now. What would you like to say or do?", {
        timeout: 8000,
        position: "top-center",
        closeButton: true,
        icon: true
      });
      
      // Optionally play a notification sound if you have one
      try {
        const audio = new Audio('/notification.mp3');
        audio.volume = 0.5;
        audio.play().catch(e => console.log('Audio play prevented:', e));
      } catch (e) {
        console.log('Audio notification not available');
      }
      
      // Focus the input field automatically
      this.$refs.messageInput.focus();
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    },

    goBack() {
      this.$router.go(-1)
    },
    getRoleColor(role) {
    const lowerRole = role.toLowerCase()
    // Check lowercase version
    if (this.characterColors[lowerRole]) {
      return this.characterColors[lowerRole]
    }
      
    // Default colors for system roles
    const colorMap = {
        'Narration': 'text-purple-600 dark:text-purple-400',
        'Player': 'text-blue-600 dark:text-blue-400',
        'system': 'text-gray-600 dark:text-gray-400'
      }
      
      return colorMap[role] || 'text-gray-600 dark:text-gray-400'
    },
    getMessageStyle(type, role) {
      const styleMap = {
        'narration': 'bg-purple-100 dark:bg-purple-900/30 italic',
        'player_input': 'bg-blue-100 dark:bg-blue-900/30 text-left', // Add text-left here
        'system': 'bg-gray-100 dark:bg-gray-800/50 text-sm'
      }

      // For actor dialogues
      if (type === 'actor_dialogue') {
        const lowerRole = role.toLowerCase()
        if (this.characterColors[lowerRole]) {
          const baseColor = this.characterColors[lowerRole].split(' ')[0]
          return `${baseColor.replace('text', 'bg')}/20 dark:${baseColor.replace('text', 'bg')}/30`
        }
      }

      return styleMap[type] || 'bg-gray-100 dark:bg-gray-800/30'
    }
  },
  
  watch: {
    // Auto-start chat when connected
    isConnected(newVal) {
    if (newVal && !this.isChatStarted && !this.storyCompleted) {
      setTimeout(() => {
        // Just set the flag, don't call the full method again
        this.isChatStarted = true;
      }, 1000)
    }
  },
    
    storyCompleted(newVal) {
      if (newVal) {
        this.statusMessage = "Story completed! You've reached the end of this episode."
        this.$router.push('/end/'+ this.episodeId + '/' + this.chatId)
      }
    }
  }
}
</script>

<style scoped>
/* Custom scrollbar for messages container */
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

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background-color: rgba(156, 163, 175, 0.7);
}

/* Dark mode scrollbar */
.dark .overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.3);
}

.dark .overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background-color: rgba(156, 163, 175, 0.5);
}

/* Director progress animation */
@keyframes directorProgress {
  from { width: 0%; }
  to { width: 100%; }
}

.animate-director-progress {
  animation: directorProgress 6s linear;
}
</style>