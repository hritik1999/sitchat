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
          <Badge v-if="storyState.completed" variant="success">
            Story Completed 🎉
          </Badge>
          <Badge v-else-if="storyState.objectiveCompleted" variant="success">Objective Completed</Badge>
          <Badge v-else>In Progress</Badge>
        </div>
      </div>
      
      <Card class="border-2">
        <CardHeader>
          <div class="flex justify-between items-center">
            <div>
              <!-- Show objective info -->
              <CardTitle v-if="storyState.completed">
                Story Completed 🎉
              </CardTitle>
              <CardTitle v-else-if="storyState.currentObjective">
                Objective {{ storyState.objectiveIndex + 1 }} of {{ storyState.totalObjectives }}
              </CardTitle>
              <CardDescription v-if="storyState.completed">
                All objectives have been completed!
              </CardDescription>
              <CardDescription v-else-if="storyState.currentObjective">
                {{ storyState.currentObjective }}
              </CardDescription>
            </div>
            
            <Badge v-if="storyState.directing" variant="outline" class="bg-amber-100 dark:bg-amber-900 animate-pulse">
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
            <div v-if="storyState.dialogue.length === 0" class="flex flex-col items-center justify-center h-full text-center">
              <MessageSquareIcon class="h-12 w-12 text-muted-foreground/40 mb-2" />
              <p class="text-muted-foreground">{{ storyStarting ? "The story is starting..." : "The story is about to begin..." }}</p>
              <div v-if="storyStarting" class="mt-4">
                <Loader2Icon class="h-6 w-6 animate-spin mx-auto mb-2" />
                <p class="text-sm text-muted-foreground">Loading conversation...</p>
              </div>
            </div>
            
            <!-- Dialogue history -->
            <template v-else>
              <div v-for="(line, index) in storyState.dialogue" :key="`msg-${index}`" 
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
            <div v-for="(status, role) in storyState.typingIndicators" :key="`typing-${role}`"
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
          <div v-if="!storyState.completed">
            <div class="space-y-2">
              <Label for="player-input">Your Response</Label>
              <Textarea 
                id="player-input" 
                v-model="playerInput" 
                placeholder="Type your response..."
                rows="3"
                :disabled="isInputDisabled"
                @keyup.enter.ctrl="sendPlayerInput"
              />
              <p class="text-xs text-muted-foreground">Press Ctrl+Enter to send</p>
            </div>
          </div>
        </CardContent>
        
        <CardFooter>
          <!-- Send button (only if story not completed) -->
          <Button 
            v-if="!storyState.completed" 
            @click="sendPlayerInput" 
            :disabled="isInputDisabled" 
            variant="default" 
            size="lg" 
            class="w-full"
          >
            <SendIcon v-if="!isInputDisabled" class="h-4 w-4 mr-2" />
            <Loader2Icon v-else class="h-4 w-4 mr-2 animate-spin" />
            {{ isInputDisabled ? 'Please wait...' : 'Send' }}
          </Button>
          
          <!-- Start new story button if completed -->
          <Button 
            v-if="storyState.completed" 
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
      <Alert v-if="storyState.completed" variant="success">
        <AlertTitle>Story Complete! 🎉</AlertTitle>
        <AlertDescription>
          All objectives have been fulfilled. You can start a new story or review the dialogue above.
        </AlertDescription>
      </Alert>

      <!-- Connection status -->
      <Alert v-if="socketStatus !== 'Connected'" variant="warning" class="animate-pulse">
        <AlertCircleIcon class="h-4 w-4 mr-2" />
        <AlertTitle>Connection Status: {{ socketStatus }}</AlertTitle>
        <AlertDescription>
          <Button 
            @click="reconnectSocket" 
            variant="outline" 
            size="sm" 
            class="mt-2"
          >
            <RefreshCwIcon class="h-4 w-4 mr-2" />
            Reconnect
          </Button>
        </AlertDescription>
      </Alert>

      <!-- Debug panel (hidden in production) -->
      <div class="text-xs text-muted-foreground mt-2 flex flex-col gap-1" v-if="isDebugMode">
        <p>Socket Status: {{ socketStatus }}</p>
        <p>Messages: {{ storyState.dialogue.length }} | Typing: {{ Object.keys(storyState.typingIndicators).filter(k => storyState.typingIndicators[k] === 'typing').length }}</p>
        <div class="flex gap-2">
          <Button 
            @click="refreshSession" 
            variant="outline" 
            size="sm" 
            class="text-xs"
          >
            Refresh Session
          </Button>
          <Button 
            @click="testTypingIndicator" 
            variant="outline" 
            size="sm" 
            class="text-xs"
          >
            Test Typing
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSupabase } from '@/composables/useSupabase'
import { useToast } from 'vue-toastification'
import { io } from 'socket.io-client'
import { 
  HomeIcon, SendIcon, MessageSquareIcon, Loader2Icon, 
  AlertCircleIcon, RefreshCwIcon
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

// Environment settings
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001'
const isDebugMode = import.meta.env.DEV // Only show debug in development mode

// Centralized story state management
const storyState = reactive({
  dialogue: [],
  typingIndicators: {},
  processing: false,
  directing: false,
  objectiveIndex: 0,
  totalObjectives: 0,
  currentObjective: null,
  objectiveCompleted: false,
  completed: false,
  objectives: []
})

// UI state
const loading = ref(true)
const chat = ref(null)
const playerInput = ref('')
const socket = ref(null)
const socketStatus = ref('Disconnected')
const dialogueContainer = ref(null)
const storyStarting = ref(false)
const socketKeepAliveInterval = ref(null)
const lastMessageTimestamp = ref(Date.now())
const socketReconnectAttempts = ref(0)

// Computed properties
const progressPercentage = computed(() => {
  if (!storyState.totalObjectives) return 0
  return (storyState.objectiveIndex / storyState.totalObjectives) * 100
})

const isInputDisabled = computed(() => {
  return !playerInput.value.trim() || 
         storyState.processing || 
         storyState.directing || 
         socketStatus.value !== 'Connected'
})

// Watch for dialogue changes to scroll
watch(() => storyState.dialogue.length, (newLength, oldLength) => {
  if (newLength > oldLength) {
    // Update timestamp to track activity
    lastMessageTimestamp.value = Date.now()
    nextTick(scrollToBottom)
  }
})

// Watch for typing indicators changes
watch(() => Object.keys(storyState.typingIndicators).filter(k => storyState.typingIndicators[k] === 'typing').length, 
  (newCount) => {
    if (newCount > 0) {
      // Someone is typing, update timestamp to track activity
      lastMessageTimestamp.value = Date.now()
      // Make sure we're scrolled to the bottom to see typing indicators
      nextTick(scrollToBottom)
    }
  }
)

// Watch for socket status changes to update UI
watch(socketStatus, (newStatus, oldStatus) => {
  if (newStatus === 'Connected' && oldStatus !== 'Connected') {
    // If we were reconnected, request the latest data
    refreshSession()
  }
})

function scrollToBottom() {
  nextTick(() => {
    const container = dialogueContainer.value
    if (container) {
      container.scrollTop = container.scrollHeight
      
      // Double-check scroll position after a short delay
      setTimeout(() => {
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      }, 100)
    }
  })
}

function setupSocket() {
  const chatId = route.params.id
  if (!chatId) return
  
  // Clean up existing connection if any
  if (socket.value) {
    socket.value.disconnect()
    socket.value = null
  }

  socketStatus.value = 'Connecting...'
  
  // Initialize Socket.IO with better connection options
  socket.value = io(API_URL, {
    transports: ['websocket', 'polling'],
    reconnection: true,
    reconnectionAttempts: Infinity,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    timeout: 20000,
    autoConnect: true,
    forceNew: true
  })
  
  // Socket event listeners
  socket.value.on('connect', () => {
    console.log("Socket connected")
    socketStatus.value = 'Connected'
    socketReconnectAttempts.value = 0 // Reset reconnect attempts counter
    
    // Join the session immediately
    socket.value.emit('join_session', { session_id: chatId })
    
    // Set up a keep-alive interval
    if (socketKeepAliveInterval.value) {
      clearInterval(socketKeepAliveInterval.value)
    }
    
    socketKeepAliveInterval.value = setInterval(() => {
      if (socket.value && socket.value.connected) {
        socket.value.emit('ping', { timestamp: Date.now() })
        
        // Check for inactivity (no messages or typing for 30 seconds)
        const inactiveTime = Date.now() - lastMessageTimestamp.value
        if (inactiveTime > 30000 && !storyState.completed) {
          // Request dialogue history to ensure we're up to date
          socket.value.emit('get_dialogue_history', { session_id: chatId })
        }
      }
    }, 15000) // Send ping every 15 seconds
  })
  
  socket.value.on('connect_error', (error) => {
    console.error("Socket connect error:", error)
    socketStatus.value = `Connection Error`
    handleReconnect()
  })
  
  socket.value.on('disconnect', (reason) => {
    console.warn("Socket disconnected:", reason)
    socketStatus.value = `Disconnected`
    handleReconnect()
  })
  
  socket.value.on('pong', () => {
    socketStatus.value = 'Connected'
  })
  
  // Story state event handlers
  socket.value.on('dialogue', (data) => {
    console.log("Received dialogue:", data)
    // Check if the message already exists to avoid duplicates
    const messageExists = storyState.dialogue.some(msg => 
      msg.role === data.role && 
      msg.content === data.content && 
      msg.type === data.type
    )
    
    if (!messageExists) {
      storyState.dialogue.push(data)
      lastMessageTimestamp.value = Date.now()
      
      // When we get actual dialogue, we can consider the story started
      storyStarting.value = false
    }
  })
  
  socket.value.on('typing_indicator', (data) => {
    const { role, status } = data
    console.log(`Typing indicator received: ${role} is ${status}`)
    
    // Update the typing indicators in a reactive way
    storyState.typingIndicators = { ...storyState.typingIndicators, [role]: status }
    
    // Auto-clear typing indicator after timeout as a failsafe
    if (status === 'typing') {
      setTimeout(() => {
        if (storyState.typingIndicators[role] === 'typing') {
          storyState.typingIndicators = { ...storyState.typingIndicators, [role]: 'idle' }
        }
      }, 10000)
    }
  })
  
  socket.value.on('director_status', (data) => {
    console.log('Director status event received:', data)
    storyState.directing = data.status === 'directing'
    storyState.processing = data.status === 'directing'
    
    if (data.status === 'directing') {
      // When director is working, mark story as starting if no messages yet
      if (storyState.dialogue.length === 0) {
        storyStarting.value = true
      }
      
      // Update timestamp to track activity
      lastMessageTimestamp.value = Date.now()
      console.log("Director is now directing...")
    } else {
      console.log("Director is now idle")
    }
  })
  
  socket.value.on('objective_status', (data) => {
    console.log('Objective status update received:', data)
    storyState.objectiveIndex = data.index || 0
    storyState.totalObjectives = data.total || 0
    storyState.currentObjective = data.current || null
    storyState.objectiveCompleted = data.completed || false
    storyState.completed = data.story_completed || data.final || false
    
    if (data.completed && data.message) {
      toast.success(data.message)
    }
    
    if (data.story_completed || data.final) {
      toast.success('🎉 Story completed! All objectives have been fulfilled.')
    }
  })
  
  socket.value.on('status', (data) => {
    console.log("Status message:", data.message)
    if (!data.message.includes('Already processing')) {
      toast.info(data.message)
    }
    
    // If starting a message is received, set storyStarting
    if (data.message.includes('Starting conversation')) {
      storyStarting.value = true
      lastMessageTimestamp.value = Date.now()
    }
  })
  
  socket.value.on('error', (data) => {
    console.error("Socket error:", data)
    toast.error(data.message)
  })
}

// Reconnect logic
function handleReconnect() {
  socketReconnectAttempts.value++
  
  if (socketReconnectAttempts.value <= 3) {
    console.log(`Attempting automatic reconnect (${socketReconnectAttempts.value}/3)`)
    // Let Socket.IO's built-in reconnection handle it
  } else if (socketReconnectAttempts.value <= 5) {
    // After 3 attempts, try a more aggressive approach
    console.log(`Trying manual reconnect (${socketReconnectAttempts.value}/5)`)
    setTimeout(() => {
      if (socketStatus.value !== 'Connected') {
        reconnectSocket()
      }
    }, 3000)
  } else {
    // After 5 attempts, show manual reconnect UI
    console.log('Maximum reconnection attempts reached')
    socketStatus.value = 'Connection failed - please refresh page'
    toast.error('Connection to server lost. Please try reconnecting or refresh the page.')
    
    // Clear any keep-alive interval
    if (socketKeepAliveInterval.value) {
      clearInterval(socketKeepAliveInterval.value)
    }
  }
}

// Manually reconnect socket
function reconnectSocket() {
  toast.info('Reconnecting to server...')
  setupSocket()
}

async function fetchChatData(chatId) {
  loading.value = true
  
  try {
    // Fetch chat data from Supabase
    const { data, error } = await supabase
      .from('chats')
      .select('*, episodes(*), users(*)')
      .eq('id', chatId)
      .single()
    
    if (error) throw error
    
    chat.value = data
    
    // Parse objectives from episode data
    if (chat.value.episodes.plot_objectives) {
      const objectives = typeof chat.value.episodes.plot_objectives === 'string'
        ? JSON.parse(chat.value.episodes.plot_objectives)
        : chat.value.episodes.plot_objectives
      
      storyState.objectives = objectives
      storyState.totalObjectives = objectives.length
    }
    
    // Set initial objective status
    storyState.objectiveIndex = chat.value.current_objective_index
    storyState.currentObjective = storyState.objectives[chat.value.current_objective_index]
    storyState.completed = chat.value.completed
    
    // Fetch initial messages directly from database
    const hasMessages = await fetchMessagesFromDatabase(chatId)
    
    // If we have messages, the story has started
    if (hasMessages) {
      storyStarting.value = false
    }
    
  } catch (error) {
    console.error('Error fetching chat data:', error)
    toast.error('Failed to load chat data')
  } finally {
    loading.value = false
  }
}

async function fetchMessagesFromDatabase(chatId) {
  try {
    const { data: messages, error } = await supabase
      .from('messages')
      .select('*')
      .eq('chat_id', chatId)
      .order('sequence', { ascending: true })
    
    if (error) throw error
    
    if (messages && messages.length > 0) {
      // Update the dialogue state with database messages
      storyState.dialogue = messages.map(msg => ({
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

async function sendPlayerInput() {
  if (isInputDisabled.value) {
    return
  }
  
  storyState.processing = true
  const chatId = route.params.id
  const messageText = playerInput.value.trim()
  
  try {
    // Add player's message to local state immediately for better UX
    const playerMsg = {
      role: chat.value?.player_name || 'Player',
      content: messageText,
      type: "player_input"
    }
    storyState.dialogue.push(playerMsg)
    
    // Clear input field right away to show the input was accepted
    playerInput.value = ''
    
    // Force scroll to bottom to show the sent message
    scrollToBottom()
    
    // Send player input to the backend
    const response = await fetch(`${API_URL}/api/stage/${chatId}/interrupt`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        player_input: messageText
      })
    })
    
    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.error || 'Failed to send input')
    }
    
  } catch (error) {
    console.error('Error sending player input:', error)
    toast.error(error.message || 'Failed to send your message. Please try again.')
    
    // If there was an error, reset the processing state so user can try again
    storyState.processing = false
  }
}

function refreshSession() {
  const chatId = route.params.id
  if (!chatId) return
  
  // Only show toast if manually triggered (not automatic)
  toast.info('Refreshing story data...')
  
  if (socket.value && socket.value.connected) {
    // Request the latest dialogue and status
    socket.value.emit('get_dialogue_history', { session_id: chatId })
    
    // If the session appears stuck, try to restart it
    if ((storyState.dialogue.length === 0 && !storyStarting.value) || 
        (storyState.processing && Date.now() - lastMessageTimestamp.value > 30000)) {
      storyStarting.value = true
      socket.value.emit('restart_stage', { session_id: chatId })
      toast.info('Restarting conversation...')
    }
  } else {
    // If socket is disconnected, try to reconnect and fetch from database
    reconnectSocket()
    fetchMessagesFromDatabase(chatId).then(success => {
      if (success) {
        toast.success(`Loaded ${storyState.dialogue.length} messages from database`)
      } else {
        toast.error('Could not load messages')
      }
    })
  }
}

function testTypingIndicator() {
  if (!isDebugMode) return
  
  // For testing typing indicators
  const testCharacter = 'Test Character'
  storyState.typingIndicators = { ...storyState.typingIndicators, [testCharacter]: 'typing' }
  
  // Clear after 5 seconds
  setTimeout(() => {
    storyState.typingIndicators = { ...storyState.typingIndicators, [testCharacter]: 'idle' }
  }, 5000)
}

function finishStory() {
  router.push('/shows')
}

function getShowName(chat) {
  try {
    const showId = chat.episodes.show_id
    return showId ? 'Show #' + showId : 'Unknown Show'
  } catch (e) {
    return 'Unknown Show'
  }
}

// Lifecycle hooks
onMounted(async () => {
  const chatId = route.params.id
  if (!chatId) {
    router.push('/shows')
    return
  }
  
  try {
    // Fetch initial data and setup socket
    await fetchChatData(chatId)
    setupSocket()
    
    // Set up inactivity checker to handle potentially missed events
    const inactivityChecker = setInterval(() => {
      const inactiveTime = Date.now() - lastMessageTimestamp.value
      
      // If nothing has happened for 60 seconds but the story isn't completed
      // and we have an active socket, check for updates
      if (inactiveTime > 60000 && !storyState.completed && socket.value && socket.value.connected) {
        console.log("Inactivity detected, requesting updates")
        socket.value.emit('get_dialogue_history', { session_id: chatId })
        
        // If there are still no messages after inactivity and the story should be starting
        if (storyState.dialogue.length === 0 && storyStarting.value) {
          // Try to restart the conversation
          socket.value.emit('restart_stage', { session_id: chatId })
        }
      }
    }, 15000)
    
    // Cleanup function
    onBeforeUnmount(() => {
      clearInterval(inactivityChecker)
      
      if (socketKeepAliveInterval.value) {
        clearInterval(socketKeepAliveInterval.value)
      }
      
      if (socket.value) {
        socket.value.disconnect()
        socket.value = null
      }
    })
    
  } catch (error) {
    console.error('Error during chat initialization:', error)
    toast.error('Failed to initialize chat')
    loading.value = false
  }
})
</script>

<style scoped>
.scroll-smooth {
  scroll-behavior: smooth;
}

/* Improve typing indicator animation */
@keyframes typing-bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-5px); }
}

.animate-bounce {
  animation: typing-bounce 1.4s infinite ease-in-out;
}
</style>