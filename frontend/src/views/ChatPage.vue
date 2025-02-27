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
            
            <div id="dialogue-container" ref="dialogueContainer" class="h-96 overflow-y-auto p-4 bg-muted rounded-md space-y-3 mb-4 scroll-smooth">
              <!-- Empty state -->
              <div v-if="dialogueHistory.length === 0" class="flex flex-col items-center justify-center h-full text-center">
                <MessageSquareIcon class="h-12 w-12 text-muted-foreground/40 mb-2" />
                <p class="text-muted-foreground">The story is about to begin...</p>
              </div>
              
              <!-- Dialogue history -->
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
  
  // Socket setup
  function setupSocket() {
    const chatId = route.params.id
    if (!chatId) return
    
    // Initialize Socket.IO
    socket.value = io("http://localhost:5001", {
      transports: ['polling', 'websocket'],
      reconnectionDelayMax: 10000,
      reconnectionAttempts: 10
    })
    
    // Socket event listeners
    socket.value.on('connect', () => {
      console.log('Connected to Socket.IO server')
      // Join the chat room
      socket.value.emit('join_session', { session_id: chatId })
    })
    
    socket.value.on('disconnect', () => {
      console.log('Disconnected from Socket.IO server')
    })
    
    socket.value.on('dialogue', (data) => {
      dialogueHistory.value.push(data)
      scrollToBottom()
    })
    
    socket.value.on('typing_indicator', (data) => {
      const { role, status } = data
      typingIndicators.value[role] = status
      scrollToBottom()
    })
    
    socket.value.on('director_status', (data) => {
      isDirecting.value = data.status === 'directing'
      isProcessing.value = data.status === 'directing'
    })
    
    socket.value.on('objective_status', (data) => {
      currentStatus.value = data
      
      if (data.completed && data.message) {
        toast.success(data.message)
      }
      
      // Check if story completed
      if (data.story_completed || data.final) {
        toast.success('🎉 Story completed! All objectives have been fulfilled.')
      }
    })
    
    socket.value.on('status', (data) => {
      if (!data.message.includes('Already processing')) {
        toast.info(data.message)
      }
    })
    
    socket.value.on('error', (data) => {
      toast.error(data.message)
    })
  }
  
  // Lifecycle hooks
  onMounted(async () => {
    const chatId = route.params.id
    if (!chatId) {
      router.push('/shows')
      return
    }
    
    await fetchChatData(chatId)
    setupSocket()
  })
  
  onBeforeUnmount(() => {
    if (socket.value) {
      socket.value.disconnect()
    }
  })
  
  // Methods
  async function fetchChatData(chatId) {
    loading.value = true
    
    try {
      // Fetch chat data from the backend
      const { data, error } = await supabase
        .from('chats')
        .select('*, episodes(*), users(*)')
        .eq('id', chatId)
        .single()
      
      if (error) throw error
      
      chat.value = data
      
      // Parse objectives
      if (chat.value.episodes.plot_objectives) {
        objectives.value = typeof chat.value.episodes.plot_objectives === 'string'
          ? JSON.parse(chat.value.episodes.plot_objectives)
          : chat.value.episodes.plot_objectives
      }
      
      // Fetch messages
      const { data: messages, error: messagesError } = await supabase
        .from('messages')
        .select('*')
        .eq('chat_id', chatId)
        .order('sequence', { ascending: true })
      
      if (messagesError) throw messagesError
      
      // Format messages for display
      dialogueHistory.value = messages.map(msg => ({
        role: msg.role,
        content: msg.content,
        type: msg.type
      }))
      
      // Set current objective status
      currentStatus.value = {
        index: chat.value.current_objective_index,
        total: objectives.value.length,
        current: objectives.value[chat.value.current_objective_index],
        completed: chat.value.completed,
        story_completed: chat.value.completed
      }
      
      // Scroll to bottom of dialogue
      await nextTick()
      scrollToBottom()
      
    } catch (error) {
      console.error('Error fetching chat data:', error)
      toast.error('Failed to load chat data')
    } finally {
      loading.value = false
    }
  }
  
  async function sendPlayerInput() {
    if (!playerInput.value.trim()) return
    if (isProcessing.value || isDirecting.value) return
    
    isProcessing.value = true
    const chatId = route.params.id
    
    try {
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
      isProcessing.value = false
    }
  }
  
  function scrollToBottom() {
    nextTick(() => {
      if (dialogueContainer.value) {
        dialogueContainer.value.scrollTop = dialogueContainer.value.scrollHeight
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