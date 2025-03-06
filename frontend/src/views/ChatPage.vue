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

    <!-- Status Indicators -->
    <div class="container mx-auto px-4 pt-2 space-y-2">
      <!-- Director Directing Message -->
      <div v-if="directorDirecting" class="text-center text-sm text-white py-2 bg-indigo-600 dark:bg-indigo-800 rounded-md p-2 animate-pulse">
        <span class="font-medium">Director is directing the scene...</span>
      </div>
      
      <!-- Processing State Indicator -->
      <div v-if="processingState && processingState !== 'IDLE'" 
           class="text-center text-sm py-2 rounded-md p-2"
           :class="getProcessingStateClass(processingState)">
        <span class="font-medium">{{ getProcessingStateMessage(processingState) }}</span>
      </div>
      
      <!-- Reconnection Indicator -->
      <div v-if="isReconnecting" class="text-center text-sm text-white py-2 bg-yellow-600 dark:bg-yellow-800 rounded-md p-2 animate-pulse">
        <span class="font-medium">Reconnecting to server...</span>
      </div>
    </div>

    <!-- Chat Container -->
    <div class="flex-1 overflow-hidden container mx-auto p-4">
      <div class="h-full flex flex-col border rounded-lg bg-background dark:bg-gray-900">
        <!-- Messages Area -->
        <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4">

          <!-- Messages -->
          <div v-for="(msg, index) in messages" :key="index" class="flex gap-3">
            <div class="flex-1 max-w-[90%]">
              <div class="flex items-center gap-2 mb-1">
                <span class="font-semibold text-sm" :class="getRoleColor(msg.role || '')">
                  {{ msg.role }}
                </span>
              </div>
              <div class="p-3 rounded-lg" :class="getMessageStyle(msg.type || '', msg.role || '')">
                {{ msg.content }}
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
                      {{ role }}
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

          <!-- Error Message with Details -->
          <div v-if="errorMessage" class="space-y-2">
            <div class="bg-red-100 dark:bg-red-900/30 p-3 rounded-lg text-red-700 dark:text-red-300 text-sm">
              {{ errorMessage }}
            </div>
            <div v-if="errorDetails" class="bg-red-50 dark:bg-red-900/20 p-3 rounded-lg text-red-600 dark:text-red-400 text-xs">
              <p>Details: {{ errorDetails }}</p>
              <button @click="errorDetails = null" class="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 underline mt-1">
                Hide Details
              </button>
            </div>
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
              :disabled="isSending || storyCompleted || !canSendMessage"
              maxlength="500"
              @keydown.enter.exact.prevent="sendMessage"
              @keydown="handleTyping"
            />
            <div class="flex justify-between items-center">
              <span class="text-sm text-muted-foreground">
                {{ input.length }}/500
              </span>
              <Button @click="sendMessage" :disabled="!input.trim() || isSending || storyCompleted || !canSendMessage">
                <span v-if="isSending" class="mr-2">Sending...</span>
                <span v-else>Send</span>
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
      isSending: false,
      directorDirecting: false,
      typingIndicators: {},
      messages: [],
      statusMessage: '',
      errorMessage: '',
      errorDetails: null,
      socket: null,
      isConnected: false,
      isReconnecting: false,
      isChatStarted: false,
      storyCompleted: false,
      typingTimeout: null,
      reconnectAttempts: 0,
      maxReconnectAttempts: 5,
      processingState: 'IDLE',
      connectionErrorTime: null,
      lastHeartbeat: Date.now(),
      heartbeatInterval: null
    }
  },

  computed: {
    hasActiveTypingIndicators() {
      // Check if any indicator has 'typing' status
      return Object.values(this.typingIndicators).some(status => status === 'typing');
    },
    
    canSendMessage() {
      // Can only send if connected and state is IDLE
      return this.isConnected && 
        !this.isReconnecting && 
        (this.processingState === 'IDLE' || !this.processingState);
    }
  },

  mounted() {
    // Initialize Socket.io connection
    this.connectToSocket()
    
    // Fetch show and episode details
    this.fetchChatDetails()
    
    // Setup heartbeat interval
    this.setupHeartbeat()
  },

  beforeUnmount() {
    this.disconnectSocket()
    this.clearHeartbeatInterval()
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
        console.log('Fetched chat details:', chatData)
        this.episodeId = chatData.episode_id || this.episodeId
        this.episodeName = chatData.episodes?.name || 'Unknown Episode'
        this.storyCompleted = chatData.completed || chatData.story_completed || false
        
        // Get processing state if available
        if (chatData.processing_state) {
          this.processingState = chatData.processing_state
        }
        
        // If we have a show ID from the episode
        if (chatData.episodes?.show_id) {
          const showData = await fetchApi(`api/shows/${chatData.episodes.show_id}`)
          if (showData && showData.show) {
            this.showId = showData.show.id
            this.showName = showData.show.name || 'Unknown Show'
          }
        }
      } catch (error) {
        console.error('Error fetching chat details:', error)
        this.errorMessage = 'Failed to load chat details. Please try refreshing the page.'
        this.errorDetails = error.message || 'Unknown error'
      }
    },

    setupHeartbeat() {
      // Send a heartbeat every 30 seconds to keep the connection alive
      this.heartbeatInterval = setInterval(() => {
        if (this.socket && this.isConnected) {
          this.socket.emit('heartbeat')
          this.lastHeartbeat = Date.now()
        }
        
        // If it's been too long since the last successful heartbeat (over 2 minutes),
        // attempt to reconnect
        if (Date.now() - this.lastHeartbeat > 120000 && this.isConnected) {
          console.log('No recent heartbeat, attempting reconnection')
          this.handleConnectionTimeout()
        }
      }, 30000)
    },
    
    clearHeartbeatInterval() {
      if (this.heartbeatInterval) {
        clearInterval(this.heartbeatInterval)
        this.heartbeatInterval = null
      }
    },
    
    handleConnectionTimeout() {
      this.isConnected = false
      this.isReconnecting = true
      
      // Try to reconnect
      if (this.socket) {
        this.socket.disconnect()
        setTimeout(() => {
          this.connectToSocket()
        }, 1000)
      }
    },

    async connectToSocket() {
      try {
        this.isReconnecting = true
        
        // Get current session for authentication
        const { data } = await supabase.auth.getSession();
        const token = data.session?.access_token;

        if (!token) {
          this.errorMessage = 'Authentication error. Please log in again.'
          this.isReconnecting = false
          return
        }

        // Initialize Socket.io connection with auth token
        this.socket = io(this.SOCKET_URL, {
          auth: {
            token: token
          },
          extraHeaders: {
            Authorization: token ? `Bearer ${token}` : ''
          },
          reconnection: true,
          reconnectionAttempts: this.maxReconnectAttempts,
          reconnectionDelay: 1000,
          timeout: 10000
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
        
        // Add a reconnect event handler
        this.socket.io.on('reconnect_attempt', this.handleReconnectAttempt);
        this.socket.io.on('reconnect', this.handleReconnect);
        this.socket.io.on('reconnect_failed', this.handleReconnectFailed);
        
      } catch (error) {
        console.error('Error connecting to socket:', error);
        this.errorMessage = 'Connection error. Please try refreshing the page.';
        this.errorDetails = error.message || 'Unknown error';
        this.isReconnecting = false;
      }
    },

    disconnectSocket() {
      if (this.socket) {
        this.socket.off('connect')
        this.socket.off('connect_error')
        this.socket.off('disconnect')
        this.socket.off('dialogue')
        this.socket.off('status')
        this.socket.off('error')
        this.socket.off('objective_status')
        this.socket.off('typing_indicator')
        this.socket.off('director_status')
        
        this.socket.io.off('reconnect_attempt')
        this.socket.io.off('reconnect')
        this.socket.io.off('reconnect_failed')
        
        this.socket.disconnect()
      }
    },

    handleConnect() {
  this.isConnected = true
  this.isReconnecting = false
  this.reconnectAttempts = 0
  this.errorMessage = ''
  this.lastHeartbeat = Date.now()
  console.log('[Socket] Connected to socket server');
  
  // Clear existing messages if we're reconnecting to avoid duplicates
  if (this.messages.length > 0 && !this.isChatStarted) {
    console.log('[UI] Clearing existing messages before joining chat room');
    this.messages = [];
  }
  
  // Join the chat room
  console.log('[Socket] Joining chat room:', this.chatId);
  this.socket.emit('join_chat', { chat_id: this.chatId })
},

    handleConnectionError(error) {
      this.isConnected = false
      this.connectionErrorTime = Date.now()
      console.error('Socket connection error:', error)
      
      // Only show the error message if we're not actively trying to reconnect
      if (!this.isReconnecting) {
        this.errorMessage = 'Connection to server failed. Please try refreshing the page.'
        this.errorDetails = error.message || 'Unknown error'
      }
    },

    handleDisconnect(reason) {
      this.isConnected = false
      console.log('Disconnected from socket server:', reason)
      
      // If we're not already trying to reconnect, start now
      if (!this.isReconnecting) {
        this.isReconnecting = true
        
        if (reason === 'io server disconnect') {
          // Server disconnected us, try to reconnect
          this.socket.connect()
        }
      }
    },
    
    handleReconnectAttempt(attemptNumber) {
      this.isReconnecting = true
      this.reconnectAttempts = attemptNumber
      console.log(`Reconnect attempt ${attemptNumber}/${this.maxReconnectAttempts}`)
    },
    
    handleReconnect() {
      this.isReconnecting = false
      this.reconnectAttempts = 0
      this.errorMessage = ''
      console.log('Successfully reconnected to server')
    },
    
    handleReconnectFailed() {
      this.isReconnecting = false
      this.errorMessage = 'Failed to reconnect to server after multiple attempts. Please refresh the page.'
      console.error('Reconnection failed after maximum attempts')
    },

    startChat() {
      if (!this.isConnected || this.isChatStarted || this.storyCompleted) return
      
      this.statusMessage = 'Starting chat...'
      this.socket.emit('start_chat', { chat_id: this.chatId })
      this.isChatStarted = true
    },

    sendMessage() {
      if (!this.input.trim() || this.isSending || this.storyCompleted || !this.canSendMessage) return

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
      const inputContent = this.input
      this.input = ''
      this.scrollToBottom()
      
      // Set a timeout to clear sending state if no response
      setTimeout(() => {
        if (this.isSending) {
          this.isSending = false
          console.log('Message send operation timed out')
          
          // If we didn't get a response in 10 seconds, check connection
          if (!this.errorMessage) {
            this.checkConnectionStatus()
          }
        }
      }, 10000)
    },
    
    checkConnectionStatus() {
      // Check if we're still connected
      if (!this.isConnected || this.isReconnecting) {
        this.errorMessage = 'You appear to be disconnected. Please wait for reconnection or refresh the page.'
        return
      }
      
      // Send a heartbeat to check connection
      if (this.socket) {
        this.socket.emit('heartbeat')
      }
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
  // Clear sending state once we get a dialogue response
  this.isSending = false
  
  // Debug log
  console.log('[Socket] Received dialogue:', message);
  
  // Validate message before adding
  if (message && typeof message === 'object' && message.content) {
    // Add message to the chat
    this.messages.push({
      role: message.role || 'Unknown',
      content: message.content,
      type: message.type || ''
    })
    
    // Debug log
    console.log('[UI] Added message to display, total messages:', this.messages.length);
    
    this.scrollToBottom()
  } else {
    console.warn('[Socket] Received invalid dialogue message:', message);
  }
},

    handleStatus(statusData) {
      if (!statusData) return
      
      // Clear sending state
      this.isSending = false
      
      if (statusData.message) {
        this.statusMessage = statusData.message
      }
      
      // Update processing state if provided
      if (statusData.state) {
        this.processingState = statusData.state
      }
      
      // Auto-start the chat if ready and not already started
      if (statusData.ready === true && !this.isChatStarted && !this.storyCompleted) {
        // Delay starting to allow UI to render
        setTimeout(() => {
          this.startChat()
        }, 1000)
      }
    },

    handleError(errorData) {
      // Clear sending state
      this.isSending = false
      
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
          
          // If there's a detailed error, store it separately
          if (errorData.details) {
            this.errorDetails = errorData.details
          } else {
            this.errorDetails = null
          }
          
          console.error('Socket error:', errorData)
        }
      }
    },

    handleObjectiveStatus(objectiveData) {
      if (!objectiveData) return
      
      // Update objective progress
      this.objectiveIndex = objectiveData.index || 0
      this.totalObjectives = objectiveData.total || 1
      
      // Calculate progress percentage (fixed to ensure proper display)
      // Make sure we have at least 1% visibility when there's any progress
      if (this.objectiveIndex > 0 && this.totalObjectives > 0) {
        this.progress = Math.max(1, Math.floor((this.objectiveIndex / this.totalObjectives) * 100));
      } else {
        this.progress = 0;
      }
      
      // Update progress text
      this.objectiveProgress = `${this.objectiveIndex}/${this.totalObjectives}`
      
      // Check if story is completed
      if (objectiveData.story_completed || objectiveData.final) {
        this.storyCompleted = true
        this.processingState = 'COMPLETED'
        this.statusMessage = "Story completed! You've reached the end of this episode."
      }
      
      console.log('Progress updated:', this.progress, '%', this.objectiveProgress);
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
        this.statusMessage = directorData.message
      }
      
      this.scrollToBottom()
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
      const colorMap = {
        'Narration': 'text-purple-600 dark:text-purple-400',
        'Player': 'text-blue-600 dark:text-blue-400',
        'system': 'text-gray-600 dark:text-gray-400'
      }
      
      // Default color for character roles
      return colorMap[role] || 'text-green-600 dark:text-green-400'
    },
    
    getMessageStyle(type, role) {
      const styleMap = {
        'narration': 'bg-purple-100 dark:bg-purple-900/30 italic',
        'player_input': 'bg-blue-100 dark:bg-blue-900/30',
        'actor_dialogue': 'bg-green-100 dark:bg-green-900/30',
        'system': 'bg-gray-100 dark:bg-gray-800/50 text-sm'
      }
      
      // If we have a message type, use that, otherwise fall back to role
      if (type && styleMap[type]) {
        return styleMap[type]
      }
      
      // Default style based on role
      if (role === 'Narration') return styleMap['narration']
      if (role === 'Player') return styleMap['player_input']
      
      // Default for any actor
      return styleMap['actor_dialogue']
    },
    
    getProcessingStateClass(state) {
      const stateClasses = {
        'INITIALIZING': 'bg-blue-500 dark:bg-blue-700 text-white',
        'PROCESSING': 'bg-indigo-600 dark:bg-indigo-800 text-white animate-pulse',
        'IDLE': '',
        'FAILED': 'bg-red-500 dark:bg-red-700 text-white',
        'COMPLETED': 'bg-green-600 dark:bg-green-800 text-white'
      }
      
      return stateClasses[state] || 'bg-gray-500 dark:bg-gray-700 text-white'
    },
    
    getProcessingStateMessage(state) {
      const stateMessages = {
        'INITIALIZING': 'Initializing story...',
        'PROCESSING': 'Processing...',
        'IDLE': '',
        'FAILED': 'Error processing story',
        'COMPLETED': 'Story completed!'
      }
      
      return stateMessages[state] || `Status: ${state}`
    }
  },
  
  watch: {
    // Auto-start chat when connected
    isConnected(newVal) {
      if (newVal && !this.isChatStarted && !this.storyCompleted) {
        // Small delay to ensure join_chat has completed
        setTimeout(() => {
          this.startChat()
        }, 1000)
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
</style>