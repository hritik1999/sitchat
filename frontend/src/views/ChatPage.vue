<template>
  <div class="container mx-auto max-w-4xl py-6 px-4">
    <!-- Loading state -->
    <div v-if="loading" class="space-y-6">
      <Skeleton class="h-10 w-64" />
      <Skeleton class="h-4 w-full" />
      <Skeleton class="h-80 w-full" />
      <Skeleton class="h-28 w-full" />
    </div>
  
    <!-- Chat interface -->
    <div v-else class="space-y-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold tracking-tight">{{ chat?.episodes?.name || 'Interactive Story' }}</h1>
          <p v-if="chat?.episodes" class="text-muted-foreground">
            {{ chat.episodes.name }} - {{ getShowName(chat) }}
          </p>
        </div>
        
        <div class="flex items-center gap-2">
          <Badge v-if="currentStatus?.story_completed || isStoryCompleted" variant="success">
            Story Completed 🎉
          </Badge>
          <Badge v-else-if="currentStatus?.completed" variant="success">Completed</Badge>
          <Badge v-else>In Progress</Badge>
        </div>
      </div>
      
      <Card class="border-2">
        <CardHeader>
          <div class="flex justify-between items-center">
            <div>
              <!-- Show objective info -->
              <CardTitle v-if="isStoryCompleted">
                Story Completed 🎉
              </CardTitle>
              <CardTitle v-else-if="currentStatus?.current">
                Objective {{ (currentStatus?.index || 0) + 1 }} of {{ currentStatus?.total || objectives.length }}
              </CardTitle>
              <CardDescription v-if="isStoryCompleted">
                All objectives have been completed!
              </CardDescription>
              <CardDescription v-else-if="currentStatus?.current">
                {{ currentStatus.current }}
              </CardDescription>
            </div>
            
            <Badge v-if="isDirecting" variant="outline" class="bg-amber-100 dark:bg-amber-900 animate-pulse">
              Director is directing...
            </Badge>
          </div>
        </CardHeader>
        
        <CardContent>
          <!-- Progress bar -->
          <Progress :value="progressPercentage" class="mb-4" />
          
          <!-- Dialogue container -->
          <div id="dialogue-container" ref="dialogueContainer" class="h-96 overflow-y-auto p-4 bg-muted rounded-md space-y-3 mb-4 scroll-smooth">
            <!-- Empty state -->
            <div v-if="dialogueHistory.length === 0" class="flex flex-col items-center justify-center h-full text-center">
              <MessageSquareIcon class="h-12 w-12 text-muted-foreground/40 mb-2" />
              <p class="text-muted-foreground">The story is about to begin...</p>
            </div>
            
            <!-- Dialogue history -->
            <template v-else>
              <div v-for="(line, index) in dialogueHistory" :key="index" 
                  class="p-3 rounded-lg" 
                  :class="{
                    'bg-primary/10': line.type === 'actor_dialogue',
                    'bg-secondary/20 italic': line.type === 'narration',
                    'bg-accent/20 ml-auto max-w-[80%]': line.type === 'player_input',
                    'bg-muted-foreground/10': line.type === 'other'
                  }">
                <div class="font-semibold">{{ line.role }}</div>
                <div>{{ line.content }}</div>
              </div>
            </template>
            
            <!-- Typing indicators -->
            <div v-for="(status, role) in typingIndicators" :key="`typing-${role}`"
              v-show="status === 'typing'"
              class="p-3 rounded-lg bg-muted-foreground/5 animate-pulse">
            <div class="font-semibold">{{ role }}</div>
            <div class="flex space-x-1">
              <span class="h-2 w-2 bg-current rounded-full animate-bounce" style="animation-delay: 0ms"></span>
              <span class="h-2 w-2 bg-current rounded-full animate-bounce" style="animation-delay: 150ms"></span>
              <span class="h-2 w-2 bg-current rounded-full animate-bounce" style="animation-delay: 300ms"></span>
            </div>
          </div>
          </div>
          
          <!-- Player input area (only if story not completed) -->
          <div v-if="!isStoryCompleted">
            <div class="space-y-2">
              <Label for="player-input">Your Response</Label>
              <Textarea 
                id="player-input" 
                v-model="playerInput" 
                placeholder="Type your response..."
                rows="3"
                :disabled="isProcessing || isDirecting"
              />
            </div>
          </div>
        </CardContent>
        
        <CardFooter>
          <!-- Send button (only if story not completed) -->
          <Button 
            v-if="!isStoryCompleted" 
            @click="sendPlayerInput" 
            :disabled="!playerInput.trim() || isProcessing || isDirecting" 
            variant="default" 
            size="lg" 
            class="w-full"
          >
            <SendIcon class="h-4 w-4 mr-2" />
            Send
            <span v-if="isProcessing || isDirecting" class="ml-2">(Please wait...)</span>
          </Button>
          
          <!-- Start new story button if completed -->
          <Button 
            v-if="isStoryCompleted" 
            @click="finishStory" 
            variant="default" 
            size="lg" 
            class="w-full"
          >
            <HomeIcon class="h-4 w-4 mr-2" />
            Back to Shows
          </Button>
        </CardFooter>
      </Card>
      
      <!-- Story complete alert -->
      <Alert v-if="isStoryCompleted" variant="success">
        <AlertTitle>Story Complete! 🎉</AlertTitle>
        <AlertDescription>
          All objectives have been fulfilled. You can start a new story or review the dialogue above.
        </AlertDescription>
      </Alert>

      <!-- Connection status for debugging -->
      <div class="text-xs text-muted-foreground mt-2 flex flex-col gap-1">
  <p>Socket Status: {{ socketStatus }}</p>
  <p>Messages: {{ dialogueHistory.length }} | Typing Indicators: {{ Object.keys(typingIndicators).length }}</p>
  <div class="flex gap-2">
    <Button 
      @click="manuallyRefreshMessages" 
      variant="outline" 
      size="sm" 
      class="text-xs"
    >
      Refresh Messages
    </Button>
    <Button 
      @click="setupSocket" 
      variant="outline" 
      size="sm" 
      class="text-xs"
    >
      Reconnect Socket
    </Button>
    <Button 
      @click="resetTypingIndicators" 
      variant="outline" 
      size="sm" 
      class="text-xs"
    >
      Reset Indicators
    </Button>
  </div>
</div>
      
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSupabase } from '@/composables/useSupabase'
import { useToast } from 'vue-toastification'
import { io } from 'socket.io-client'
import { 
  HomeIcon, SendIcon, MessageSquareIcon, Loader2Icon
} from 'lucide-vue-next'
import { 
  Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle 
} from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'

const route = useRoute()
const router = useRouter()
const { supabase } = useSupabase()
const toast = useToast()

// State
const loading = ref(true)
const chat = ref(null)
const dialogueHistory = ref([])
const playerInput = ref('')
const socket = ref(null)
const typingIndicators = ref({})
const isProcessing = ref(false)
const isDirecting = ref(false)
const dialogueContainer = ref(null)
const currentStatus = ref(null)
const objectives = ref([])
const socketStatus = ref('Disconnected') // Track socket status for debugging
const connectionAttempts = ref(0)
const maxConnectionAttempts = 5

// Computed properties
const isStoryCompleted = computed(() => {
  if (currentStatus.value?.story_completed) return true
  if (!currentStatus.value || !objectives.value.length) return false
  
  return currentStatus.value.index >= currentStatus.value.total
})

const progressPercentage = computed(() => {
  if (!currentStatus.value || !currentStatus.value.total) return 0
  return (currentStatus.value.index / currentStatus.value.total) * 100
})

  // Watch for dialogue changes to scroll and ensure reactivity
watch(dialogueHistory, (newMessages, oldMessages) => {
  console.log(`Dialogue history changed: ${oldMessages.length} -> ${newMessages.length} messages`)
  if (newMessages.length > oldMessages.length) {
    // New messages have been added - scroll to bottom
    scrollToBottom()
  }
  
  // Force reactivity update for the component
  nextTick(() => {
    if (newMessages.length > 0 && dialogueContainer.value) {
      console.log('Forcing dialogue container update')
      // This forces a DOM update in Vue
      const temp = dialogueContainer.value.className
      dialogueContainer.value.className = temp + ' '
      setTimeout(() => {
        dialogueContainer.value.className = temp
      }, 0)
    }
  })
}, { deep: true })

  // Socket setup with reconnection logic
  function setupSocket() {
  const chatId = route.params.id
  if (!chatId) return
  
  if (socket.value) {
    // Clean up existing connection if any
    socket.value.disconnect()
    socket.value = null
  }

  socketStatus.value = 'Connecting...'
  console.log(`Setting up socket connection to http://localhost:5001 for chat: ${chatId}`)
  
  // Initialize Socket.IO with more robust options
  socket.value = io("http://localhost:5001", {
    transports: ['polling', 'websocket'], // Try polling first for better compatibility
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: 10,
    timeout: 20000, // Longer timeout
    forceNew: true, // Force new connection
    query: { session_id: chatId } // Pass chatId as query parameter
  })
  
  // Socket event listeners
  socket.value.on('connect', () => {
    console.log('✅ Connected to Socket.IO server')
    socketStatus.value = 'Connected'
    connectionAttempts.value = 0
    
    // Join the chat room explicitly
    console.log(`Joining session with ID: ${chatId}`)
    socket.value.emit('join_session', { session_id: chatId })
    
    // Ping the server to keep connection alive
    socket.value.emit('ping', { message: 'Client ping' })
    
    // Set up a ping interval to prevent timeouts
    const pingInterval = setInterval(() => {
      if (socket.value && socket.value.connected) {
        socket.value.emit('ping', { message: 'Keep alive ping' })
      } else {
        clearInterval(pingInterval)
      }
    }, 25000)
    
    // Clear interval when component unmounts
    onBeforeUnmount(() => {
      clearInterval(pingInterval)
    })
  })
  
  socket.value.on('pong', (data) => {
    console.log('Received pong from server:', data)
    // Update socket status to confirm active connection
    socketStatus.value = `Connected (last ping: ${new Date().toLocaleTimeString()})`
  })
  
  socket.value.on('connect_error', (error) => {
    console.error('❌ Socket.IO connection error:', error)
    socketStatus.value = `Connection Error: ${error.message}`
    handleReconnect()
  })
  
  socket.value.on('disconnect', (reason) => {
    console.log('⚠️ Disconnected from Socket.IO server:', reason)
    socketStatus.value = `Disconnected: ${reason}`
    handleReconnect()
  })
  
  socket.value.on('dialogue', (data) => {
    console.log('📩 Received dialogue event:', data)
    // Check if the message already exists
    const messageExists = dialogueHistory.value.some(msg => 
      msg.role === data.role && 
      msg.content === data.content && 
      msg.type === data.type
    )
    
    if (!messageExists) {
      console.log('Adding new message to dialogue history')
      // Use Vue's reactivity system properly
      dialogueHistory.value = [...dialogueHistory.value, data]
      // Force UI update and scroll
      nextTick(() => {
        scrollToBottom()
      })
    } else {
      console.log('Message already exists in dialogue history')
    }
  })
  
  socket.value.on('typing_indicator', (data) => {
    console.log('⌨️ Typing indicator event received:', data)
    const { role, status } = data
    
    // Create a new object to ensure reactivity
    const updatedIndicators = { ...typingIndicators.value }
    updatedIndicators[role] = status
    typingIndicators.value = updatedIndicators
    
    // If typing, make sure it clears after a timeout (failsafe)
    if (status === 'typing') {
      setTimeout(() => {
        // Only clear if it's still showing typing
        if (typingIndicators.value[role] === 'typing') {
          const updated = { ...typingIndicators.value }
          updated[role] = 'idle'
          typingIndicators.value = updated
        }
      }, 10000) // Clear after 10 seconds if no update
    }
  })
  
  socket.value.on('director_status', (data) => {
    console.log('🎬 Director status event received:', data)
    isDirecting.value = data.status === 'directing'
    isProcessing.value = data.status === 'directing'
  })
  
  socket.value.on('objective_status', (data) => {
    console.log('🎯 Objective status update received:', data)
    currentStatus.value = { ...data } // Create new object to ensure reactivity
    
    if (data.completed && data.message) {
      toast.success(data.message)
    }
    
    if (data.story_completed || data.final) {
      toast.success('🎉 Story completed! All objectives have been fulfilled.')
    }
  })
  
  socket.value.on('status', (data) => {
    console.log('ℹ️ Status event received:', data.message)
    if (!data.message.includes('Already processing')) {
      toast.info(data.message)
    }
  })
  
  socket.value.on('error', (data) => {
    console.error('❌ Socket error event received:', data.message)
    toast.error(data.message)
  })
  
  // Add socket reconnection logic
  function handleReconnect() {
    if (connectionAttempts.value < maxConnectionAttempts) {
      connectionAttempts.value++
      console.log(`🔄 Attempting to reconnect (${connectionAttempts.value}/${maxConnectionAttempts})...`)
      socketStatus.value = `Reconnecting... (${connectionAttempts.value}/${maxConnectionAttempts})`
      
      // Let Socket.IO handle reconnection but also implement our own fallback
      setTimeout(() => {
        if (socket.value && !socket.value.connected) {
          console.log('Socket still not connected, manually reconnecting...')
          setupSocket() // Recreate the socket connection
        }
      }, 5000)
    } else {
      socketStatus.value = 'Failed to connect. Try refreshing the page.'
      toast.error('Connection lost. Please click "Refresh Messages" or reload the page.')
    }
  }
}

function setupRealTimeSupport() {
  // Request message history explicitly 1 second after socket setup
  setTimeout(() => {
    if (socket.value && socket.value.connected) {
      console.log("Requesting dialogue history explicitly")
      socket.value.emit('get_dialogue_history', { session_id: route.params.id })
    }
  }, 1000)
  
  // Set up a reconnection checker that runs every 5 seconds
  const connectionChecker = setInterval(() => {
    if (socket.value && !socket.value.connected) {
      console.log("Connection checker: Socket is disconnected, attempting to reconnect")
      socketStatus.value = "Disconnected - attempting to reconnect..."
      setupSocket()
    }
  }, 5000)
  
  // Clear interval when component unmounts
  onBeforeUnmount(() => {
    clearInterval(connectionChecker)
  })
}

// Enhanced manual refresh function with more options
async function manuallyRefreshMessages() {
  const chatId = route.params.id
  if (!chatId) return
  
  toast.info('Manually refreshing...')
  
  // First try to get messages through socket if connected
  if (socket.value && socket.value.connected) {
    console.log("Requesting dialogue history through socket")
    socket.value.emit('get_dialogue_history', { session_id: chatId })
    
    // Wait a bit to see if messages arrive through socket
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // If we still don't have messages, try database
    if (dialogueHistory.value.length === 0) {
      console.log("No messages received through socket, trying database")
      const hadMessages = await pollMessagesFromDatabase(chatId)
      
      if (hadMessages) {
        toast.success(`Loaded ${dialogueHistory.value.length} messages from database`)
      } else {
        toast.info('No messages found. Attempting to restart...')
        
        // Try to restart the stage
        if (socket.value && socket.value.connected) {
          socket.value.emit('restart_stage', { session_id: chatId })
        }
      }
    } else {
      toast.success(`Loaded ${dialogueHistory.value.length} messages`)
    }
  } else {
    // Socket not connected, try database directly
    console.log("Socket not connected, fetching from database directly")
    const hadMessages = await pollMessagesFromDatabase(chatId)
    
    if (hadMessages) {
      toast.success(`Loaded ${dialogueHistory.value.length} messages from database`)
    } else {
      toast.error('No messages found and socket disconnected')
      
      // Try to reconnect socket
      setupSocket()
    }
  }
}

// Helper to force refresh typing indicators
function resetTypingIndicators() {
  console.log("Resetting typing indicators")
  typingIndicators.value = {}
}

onMounted(async () => {
  console.log('ChatPage mounted')
  const chatId = route.params.id
  if (!chatId) {
    console.error('No chat ID provided')
    router.push('/shows')
    return
  }
  
  try {
    await fetchChatData(chatId)
    setupSocket()
    setupRealTimeSupport() // Add this new function call
    
    // Set up polling for messages as a fallback
    const pollInterval = setInterval(async () => {
      if (dialogueHistory.value.length === 0) {
        console.log("No messages yet, polling database...")
        await pollMessagesFromDatabase(chatId)
      } else {
        clearInterval(pollInterval)
      }
    }, 3000)
    
    // Clear the interval after 30 seconds regardless
    setTimeout(() => {
      clearInterval(pollInterval)
    }, 30000)
    
  } catch (error) {
    console.error('Error during chat initialization:', error)
    toast.error('Failed to initialize chat. Please try again.')
  }
})

// Lifecycle hooks
onMounted(async () => {
  console.log('ChatPage mounted')
  const chatId = route.params.id
  if (!chatId) {
    console.error('No chat ID provided')
    router.push('/shows')
    return
  }
  
  try {
    await fetchChatData(chatId)
    setupSocket() 
    
    // Set up polling for messages as a fallback
    const pollInterval = setInterval(async () => {
      if (dialogueHistory.value.length === 0) {
        console.log("No messages yet, polling database...")
        await pollMessagesFromDatabase(chatId)
      } else {
        clearInterval(pollInterval)
      }
    }, 3000)
    
    // Clear the interval after 30 seconds regardless
    setTimeout(() => {
      clearInterval(pollInterval)
    }, 30000)
    
  } catch (error) {
    console.error('Error during chat initialization:', error)
    toast.error('Failed to initialize chat. Please try again.')
  }
})

onBeforeUnmount(() => {
  console.log('ChatPage unmounting, disconnecting socket')
  if (socket.value) {
    socket.value.disconnect()
    socket.value = null
  }
})

// Methods
async function fetchChatData(chatId) {
  loading.value = true
  console.log(`Fetching chat data for ID: ${chatId}`)
  
  try {
    // Fetch chat data from the backend
    const { data, error } = await supabase
      .from('chats')
      .select('*, episodes(*), users(*)')
      .eq('id', chatId)
      .single()
    
    if (error) throw error
    
    console.log('Chat data fetched:', data)
    chat.value = data
    
    // Parse objectives
    if (chat.value.episodes.plot_objectives) {
      objectives.value = typeof chat.value.episodes.plot_objectives === 'string'
        ? JSON.parse(chat.value.episodes.plot_objectives)
        : chat.value.episodes.plot_objectives
      console.log('Parsed objectives:', objectives.value)
    }
    
    // Fetch messages directly from database to ensure we have initial state
    await fetchMessagesFromDatabase(chatId)
    
    // Set current objective status
    currentStatus.value = {
      index: chat.value.current_objective_index,
      total: objectives.value.length,
      current: objectives.value[chat.value.current_objective_index],
      completed: chat.value.completed,
      story_completed: chat.value.completed
    }
    
    console.log('Initial current status:', currentStatus.value)
    
    // Wait for component to finish rendering before scrolling
    await nextTick()
    
    // Don't try to scroll immediately, wait for the container to be available
    setTimeout(() => {
      scrollToBottom()
    }, 100)
    
  } catch (error) {
    console.error('Error fetching chat data:', error)
    toast.error('Failed to load chat data')
  } finally {
    loading.value = false
  }
}

// Separate function to fetch messages from database
async function fetchMessagesFromDatabase(chatId) {
  console.log('Fetching messages from database')
  try {
    const { data: messages, error: messagesError } = await supabase
      .from('messages')
      .select('*')
      .eq('chat_id', chatId)
      .order('sequence', { ascending: true })
    
    if (messagesError) throw messagesError
    
    console.log(`Found ${messages.length} messages in database`)
    
    if (messages.length > 0) {
      // Format messages for display and ensure they're reactive
      dialogueHistory.value = messages.map(msg => ({
        role: msg.role,
        content: msg.content,
        type: msg.type
      }))
      return true
    }
    return false
  } catch (error) {
    console.error('Error fetching messages:', error)
    return false
  }
}

// Function to poll for messages if socket fails
async function pollMessagesFromDatabase(chatId) {
  const hadMessages = await fetchMessagesFromDatabase(chatId)
  
  if (hadMessages) {
    console.log("Successfully polled messages from database")
    // If we found messages, try manually triggering a check for completed objectives
    if (socket.value && socket.value.connected) {
      console.log("Manually triggering objective status update")
      // Request an objective status update from the server
      socket.value.emit('get_objective_status', { session_id: chatId })
    }
  }
  
  return hadMessages
}

async function sendPlayerInput() {
  if (!playerInput.value.trim()) return
  if (isProcessing.value || isDirecting.value) return
  
  isProcessing.value = true
  const chatId = route.params.id
  console.log(`Sending player input to chat ${chatId}:`, playerInput.value)
  
  try {
    // Add the player's message to the local dialogue history immediately
    // This gives instant feedback to the user
    const playerMsg = {
      role: chat.value?.player_name || 'Player',
      content: playerInput.value,
      type: "player_input"
    }
    dialogueHistory.value = [...dialogueHistory.value, playerMsg]
    
    // Send player input to the backend
    const response = await fetch(`http://localhost:5001/api/stage/${chatId}/interrupt`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        player_input: playerInput.value
      })
    })
    
    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.error || 'Failed to send input')
    }
    
    // Clear input
    playerInput.value = ''
    
  } catch (error) {
    console.error('Error sending player input:', error)
    toast.error(error.message || 'Failed to send input')
  } finally {
    isProcessing.value = false
  }
}

function scrollToBottom() {
  nextTick(() => {
    // Use both the ref and querySelector as fallback
    const container = dialogueContainer.value || document.querySelector('#dialogue-container')
    if (container) {
      // Log to debug scrolling
      console.log(`Scrolling to bottom: ${container.scrollHeight}px`)
      container.scrollTop = container.scrollHeight
      
      // Sometimes a single scroll isn't enough due to image loading or other factors
      // So we schedule another scroll after a small delay
      setTimeout(() => {
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      }, 100)
    }
  })
}

function finishStory() {
  router.push('/shows')
}

// Utility functions
function getShowName(chat) {
  try {
    // Navigate from episode to show
    const showId = chat.episodes.show_id
    return showId ? 'Show #' + showId : 'Unknown Show'
  } catch (e) {
    return 'Unknown Show'
  }
}
</script>

<style scoped>
.scroll-smooth {
  scroll-behavior: smooth;
}
</style>