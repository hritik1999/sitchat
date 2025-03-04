<template>
    <div class="container mx-auto p-4 md:p-6 max-w-4xl">
      <!-- Loading State -->
      <div v-if="loading" class="flex flex-col items-center justify-center min-h-[50vh]">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
        <p class="text-muted-foreground">Loading chat...</p>
      </div>
      
      <!-- Chat Interface -->
      <div v-else class="space-y-6">
        <!-- Header with Episode Info -->
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 class="text-3xl font-bold tracking-tight">{{ episodeInfo.name }}</h1>
            <p class="text-muted-foreground">{{ episodeInfo.description }}</p>
          </div>
          
          <!-- Connection Status & Objective Progress -->
          <div class="flex flex-col items-end gap-2">
            <Badge v-if="!socketConnected" variant="destructive" class="animate-pulse">
              Disconnected
            </Badge>
            <Badge v-else-if="storyCompleted" variant="success">
              Story Completed
            </Badge>
            <Badge v-else-if="isProcessing" variant="secondary" class="animate-pulse">
              Processing...
            </Badge>
            <Badge v-else variant="outline">
              Connected
            </Badge>
            
            <div class="text-sm text-muted-foreground">
              Objective {{ currentObjectiveIndex + 1 }} of {{ totalObjectives }}
            </div>
          </div>
        </div>
        
        <!-- Current Objective Card -->
        <Card>
          <CardHeader>
            <CardTitle>Current Objective</CardTitle>
            <CardDescription>{{ currentObjective || 'Story completed!' }}</CardDescription>
          </CardHeader>
          <CardContent>
            <Progress :value="progressPercentage" class="mb-2" />
          </CardContent>
        </Card>
        
        <!-- Chat Messages -->
        <Card>
          <CardHeader>
            <CardTitle>Dialogue</CardTitle>
          </CardHeader>
          <CardContent>
            <div id="chat-container" ref="chatContainer" class="h-96 overflow-y-auto p-4 bg-muted rounded-md space-y-3 mb-4">
              <!-- Connection lost warning -->
              <div v-if="!socketConnected" class="p-3 bg-destructive/20 rounded-lg mb-2 animate-pulse">
                <p class="font-semibold">Connection lost</p>
                <p>Attempting to reconnect to the server...</p>
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
            
            <!-- Player Input -->
            <div v-if="!storyCompleted">
              <div class="space-y-2">
                <div class="flex justify-between">
                  <Label for="player-input">Your Response</Label>
                  <span class="text-xs text-muted-foreground">{{ playerInput.length }}/500</span>
                </div>
                <Textarea 
                  id="player-input" 
                  v-model="playerInput" 
                  placeholder="Type your response..."
                  rows="3"
                  :disabled="isProcessing || !socketConnected || !chatStarted"
                  :maxlength="500"
                />
              </div>
            </div>
          </CardContent>
          <CardFooter>
            <!-- Show Send button if story is not completed -->
            <div class="w-full flex flex-col md:flex-row gap-4">
              <Button 
                v-if="!storyCompleted && !chatStarted" 
                @click="startChat" 
                :disabled="!socketConnected || isProcessing" 
                variant="default" 
                size="lg" 
                class="flex-1">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                Start Story
              </Button>
              
              <Button 
                v-if="!storyCompleted && chatStarted" 
                @click="sendMessage" 
                :disabled="!playerInput.trim() || isProcessing || !socketConnected" 
                variant="default" 
                size="lg" 
                class="flex-1">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                Send
                <span v-if="isProcessing" class="ml-2">(Please wait...)</span>
              </Button>
              
              <!-- Show Start New Episode button if story is completed -->
              <Button 
                v-if="storyCompleted" 
                @click="goToEpisodes" 
                variant="default" 
                size="lg" 
                class="flex-1">
                Start New Episode
              </Button>
              
              <!-- Always show Back button -->
              <Button 
                @click="goBack" 
                variant="outline" 
                size="lg">
                Back to Episodes
              </Button>
            </div>
          </CardFooter>
        </Card>
        
        <!-- Story Completed Message -->
        <Alert v-if="storyCompleted" variant="success">
          <AlertTitle>Story Complete! 🎉</AlertTitle>
          <AlertDescription>
            All objectives have been fulfilled. You can start a new episode or review the dialogue above.
          </AlertDescription>
        </Alert>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, reactive, computed, nextTick, onMounted, onBeforeUnmount, watch } from 'vue';
  import { useRouter, useRoute } from 'vue-router';
  import { io } from 'socket.io-client';
  import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
  import { Textarea } from '@/components/ui/textarea';
  import { Button } from '@/components/ui/button';
  import { Progress } from '@/components/ui/progress';
  import { Badge } from '@/components/ui/badge';
  import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
  import { Label } from '@/components/ui/label';
  import { useToast } from 'vue-toastification';
//   import { useAuth } from '@/composables/useAuth';
  
  export default {
    name: 'ChatPage',
    components: {
      Card, 
      CardHeader, 
      CardTitle, 
      CardDescription, 
      CardContent,
      CardFooter,
      Label,
      Textarea,
      Button,
      Progress,
      Badge,
      Alert,
      AlertTitle,
      AlertDescription
    },
    
    setup() {
      const router = useRouter();
      const route = useRoute();
      const toast = useToast();
      
      // Chat state
      const chatId = ref(route.params.chat_id);
      const showId = ref(route.params.show_id);
      const episodeInfo = ref({
        name: '',
        description: ''
      });
      const loading = ref(true);
      const playerInput = ref('');
      const dialogueHistory = ref([]);
      const typingIndicators = reactive({});
      const isProcessing = ref(false);
      const chatStarted = ref(false);
      const session_token =  localStorage.getItem('supabase_session') 
          ? JSON.parse(localStorage.getItem('supabase_session')).access_token 
          : null;
      
      // Socket state
      const socket = ref(null);
      const socketConnected = ref(false);
      const reconnectAttempts = ref(0);
      const MAX_RECONNECT_ATTEMPTS = 5;
      const heartbeatInterval = ref(null);
      
      // Objective state
      const currentObjective = ref('');
      const currentObjectiveIndex = ref(0);
      const totalObjectives = ref(0);
      const storyCompleted = ref(false);
      
      // Chat container ref for scrolling
      const chatContainer = ref(null);
      
      // API URL
      const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001';
      
      // Computed properties
      const progressPercentage = computed(() => {
        if (totalObjectives.value === 0) return 0;
        
        // If story is completed, return 100%
        if (storyCompleted.value) return 100;
        
        return (currentObjectiveIndex.value / totalObjectives.value) * 100;
      });
      
      
      // Initialize the app
      onMounted(async () => {
        // Fetch chat details
        await fetchChatDetails();
        
        // Initialize Socket.IO connection
        initializeSocket();
        
        // Setup heartbeat interval
        heartbeatInterval.value = setInterval(() => {
          if (socketConnected.value && socket.value) {
            socket.value.emit('heartbeat');
          }
        }, 30000);
      });
      
      // Clean up on unmount
      onBeforeUnmount(() => {
        if (heartbeatInterval.value) {
          clearInterval(heartbeatInterval.value);
        }
        
        if (socket.value) {
          socket.value.disconnect();
        }
      });
      
      // Auto-scroll to bottom when new messages arrive
      watch(dialogueHistory, () => {
        scrollToBottom();
      });
      
      // Fetch chat details from API
      const fetchChatDetails = async () => {
        try {
          loading.value = true;
          
          const response = await fetch(`${apiBaseUrl}/api/chats/${chatId.value}`, {
            headers:{
                'Authorization': `Bearer ${session_token}`,
                'Content-Type': 'application/json'
              },
          });
          
          if (!response.ok) {
            throw new Error(`Failed to fetch chat: ${response.statusText}`);
          }
          
          const data = await response.json();
          
          // Get episode details
          const episodeResponse = await fetch(`${apiBaseUrl}/api/show/${showId}/episodes/${data.chat.episode_id}`, {
            headers: {
              'Authorization': `Bearer ${session_token}`
            }
          });
          
          if (!episodeResponse.ok) {
            throw new Error(`Failed to fetch episode: ${episodeResponse.statusText}`);
          }
          
          const episodeData = await episodeResponse.json();
          
          // Set chat and episode data
          dialogueHistory.value = data.messages.map(message => ({
            role: message.role,
            content: message.content,
            type: message.type
          }));
          
          episodeInfo.value = {
            name: episodeData.episode.name,
            description: episodeData.episode.description
          };
          
          totalObjectives.value = episodeData.episode.plot_objectives.length;
          
          // Check if story is already completed
          if (data.chat.completed) {
            storyCompleted.value = true;
            currentObjectiveIndex.value = totalObjectives.value;
          } else {
            currentObjectiveIndex.value = data.chat.current_objective_index;
            if (currentObjectiveIndex.value < totalObjectives.value) {
              currentObjective.value = episodeData.episode.plot_objectives[currentObjectiveIndex.value];
            }
          }
          
        } catch (error) {
          console.error('Error fetching chat details:', error);
          toast.error(`Error loading chat: ${error.message}`);
        } finally {
          loading.value = false;
        }
      };
      
      // Initialize Socket.IO connection
      const initializeSocket = () => {
        // Create Socket.IO connection
        socket.value = io(apiBaseUrl, {
          transports: ['websocket', 'polling'],
          reconnectionDelayMax: 10000,
          reconnectionAttempts: MAX_RECONNECT_ATTEMPTS,
          timeout: 20000,
          autoConnect: true
        });
        
        // Set up event handlers
        socket.value.on('connect', () => {
          console.log('Connected to Socket.IO server');
          socketConnected.value = true;
          reconnectAttempts.value = 0;
          
          // Authenticate with token
          const token = localStorage.getItem('token');
          if (token) {
            socket.value.emit('auth', { token });
          }
        });
        
        socket.value.on('connect_error', (error) => {
          console.error('Connection error:', error);
          socketConnected.value = false;
          reconnectAttempts.value++;
          
          if (reconnectAttempts.value === 1) {
            toast.error(`Connection error: ${error.message}. Attempting to reconnect...`);
          } else if (reconnectAttempts.value >= MAX_RECONNECT_ATTEMPTS) {
            toast.error('Failed to connect after multiple attempts. Please reload the page.');
          }
        });
        
        socket.value.on('disconnect', (reason) => {
          console.log('Disconnected from server:', reason);
          socketConnected.value = false;
          
          if (reason === 'io server disconnect') {
            toast.error('Disconnected by server. Please reload the page.');
            socket.value.connect();
          } else if (reason === 'transport close' || reason === 'ping timeout') {
            toast.warning('Connection to server lost. Attempting to reconnect...');
          }
        });
        
        socket.value.on('auth_success', (data) => {
          console.log('Authentication successful', data);
          // Join the chat room
          socket.value.emit('join_chat', { chat_id: chatId.value });
        });
        
        socket.value.on('error', (data) => {
          console.error('Socket error:', data.message);
          toast.error(data.message);
        });
        
        socket.value.on('status', (data) => {
          console.log('Status:', data);
          
          // Don't show "Already processing" as a toast
          if (!data.message.includes('Already processing')) {
            toast.info(data.message);
          }
          
          // Check if chat is ready or started
          if (data.ready) {
            chatStarted.value = false;
          }
          
          if (data.started) {
            chatStarted.value = true;
          }
        });
        
        socket.value.on('dialogue', (data) => {
          console.log('Dialogue:', data);
          dialogueHistory.value.push(data);
          scrollToBottom();
        });
        
        socket.value.on('typing_indicator', (data) => {
          console.log('Typing indicator:', data);
          typingIndicators[data.role] = data.status;
          scrollToBottom();
        });
        
        socket.value.on('director_status', (data) => {
          console.log('Director status:', data);
          isProcessing.value = data.status === 'directing';
        });
        
        socket.value.on('objective_status', (data) => {
          console.log('Objective status:', data);
          
          if (data.completed) {
            toast.success(data.message || 'Objective completed!');
            
            // Update objective index
            if (data.index !== undefined) {
              currentObjectiveIndex.value = data.index;
            }
            
            // Update current objective
            if (data.current !== undefined) {
              currentObjective.value = data.current;
            } else {
              currentObjective.value = '';
            }
            
            // Check for story completion
            if (data.story_completed || data.final || currentObjectiveIndex.value >= totalObjectives.value) {
              storyCompleted.value = true;
              toast.success('🎉 Story completed! All objectives have been fulfilled.');
            }
          }
        });
      };
      
      // Scroll to bottom of chat container
      const scrollToBottom = () => {
        nextTick(() => {
          if (chatContainer.value) {
            chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
          }
        });
      };
      
      // Start the chat
      const startChat = () => {
        if (!socketConnected.value || isProcessing.value) return;
        
        socket.value.emit('start_chat', { chat_id: chatId.value });
        isProcessing.value = true;
      };
      
      // Send player message
      const sendMessage = () => {
        if (!socketConnected.value || isProcessing.value || !playerInput.value.trim()) return;
        
        socket.value.emit('player_input', { 
          chat_id: chatId.value, 
          input: playerInput.value.trim() 
        });
        
        // Clear input after sending
        playerInput.value = '';
        isProcessing.value = true;
      };
      
      // Navigation methods
      const goBack = () => {
        router.push(`/episodes/${episodeInfo.value.id}`);
      };
      
      const goToEpisodes = () => {
        router.push('/episodes');
      };
      
      return {
        // State
        loading,
        chatId,
        episodeInfo,
        playerInput,
        dialogueHistory,
        typingIndicators,
        isProcessing,
        chatStarted,
        socketConnected,
        currentObjective,
        currentObjectiveIndex,
        totalObjectives,
        storyCompleted,
        chatContainer,
        
        // Computed
        progressPercentage,
        
        // Methods
        startChat,
        sendMessage,
        goBack,
        goToEpisodes,
        scrollToBottom
      };
    }
  };
  </script>
  
  <style scoped>
  #chat-container {
    scroll-behavior: smooth;
  }
  
  @media (max-width: 640px) {
    .container {
      padding: 0.5rem;
    }
    
    #chat-container {
      height: 16rem;
    }
  }
  </style>