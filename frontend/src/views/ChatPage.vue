<template>
  <div class="h-screen flex flex-col">
    <!-- Header Section -->
    <div class="bg-background border-b p-4">
      <div class="container mx-auto flex justify-between items-center">
        <div class="flex items-center">
          <!-- Show Thumbnail -->
          <img v-if="showImageUrl" :src="showImageUrl" alt="Show Thumbnail" class="h-12 w-12 mr-4 rounded" />
          <div>
            <h1 class="text-xl font-bold inline-block">{{ showName }}</h1>
            <p class="text-sm text-muted-foreground">{{ episodeName }}</p>
          </div>
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
          <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" :style="{ width: `${progress}%` }">
          </div>
        </div>
      </div>
    </div>

    <!-- Director Directing Message -->
    <div v-if="directorDirecting" class="container mx-auto px-4 pt-2">
      <div class="text-center text-sm text-white py-2 bg-indigo-600 dark:bg-indigo-800 rounded-md p-2 animate-pulse">
        <span class="font-medium">{{ director_message }}</span>
      </div>
      <div class="mt-2 h-1 bg-gray-200 dark:bg-gray-700 rounded-full">
        <div class="h-full bg-indigo-500 dark:bg-indigo-400 rounded-full animate-director-progress"></div>
      </div>
    </div>

    <!-- Chat Container -->
    <div class="flex-1 overflow-hidden container mx-auto p-4">
      <div class="h-full flex flex-col border rounded-lg bg-background dark:bg-gray-900">
        <!-- Messages Area -->
        <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4">

          <div v-for="(msg, index) in messages" :key="index" class="flex items-start gap-3"
            :class="{ 'justify-end flex-row-reverse': msg.role === 'Player' }">
            <!-- Avatar -->
            <img
              v-if="(msg.role !== 'Player' && getCharacterImageUrl(msg.role)) || (msg.role === 'Player' && playerImageUrl)"
              :src="msg.role === 'Player' ? playerImageUrl : getCharacterImageUrl(msg.role)" alt="Avatar"
              class="h-14 w-14 rounded-full flex-shrink-0" />

            <!-- Content -->
            <div class="flex-1 max-w-[70%]">
              <div class="flex items-center -mb-1" :class="{ 'justify-between': msg.role === 'Player' }">
                <span class="font-semibold text-sm" :class="getRoleColor(msg.role || '')">
                  {{ msg.role === 'Player' ? player_name : msg.role }}
                </span>
              </div>
              <div class="mt-1 p-2 rounded-lg whitespace-pre-wrap break-words"
                :class="getMessageStyle(msg.type || '', msg.role || '')">
                {{ msg.content }}
              </div>
            </div>
          </div>

          <!-- Typing Indicators -->
          <div v-if="hasActiveTypingIndicators" class="my-2">
            <div v-for="(status, role) in typingIndicators" :key="role">
              <div v-if="status === 'typing'" class="flex items-start gap-3">
                <img v-if="getCharacterImageUrl(role)" :src="getCharacterImageUrl(role)" alt="Typing Avatar"
                  class="h-10 w-10 rounded-full flex-shrink-0" />
                <div class="flex-1 max-w-[70%]">
                  <div class="flex items-center">
                    <span class="font-semibold text-sm" :class="getRoleColor(role)">
                      {{ role === 'Player' ? player_name : role }}
                    </span>
                  </div>
                  <div class="mt-1 p-3 rounded-lg bg-gray-100 dark:bg-gray-800 inline-flex items-center">
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

          <div v-if="errorMessage"
            class="bg-red-100 dark:bg-red-900/30 p-3 rounded-lg text-red-700 dark:text-red-300 text-sm">
            {{ errorMessage }}
          </div>
        </div>

        <!-- Input Area -->
        <div class="border-t p-4">
          <Textarea ref="messageInput" v-model="input" placeholder="Type your response..." class="resize-none" rows="2"
            :disabled="isSending || storyCompleted" maxlength="500" @keydown.enter.exact.prevent="sendMessage"
            @keydown="handleTyping" />
          <div class="mt-2 flex justify-between items-center">
            <span class="text-sm text-muted-foreground">{{ input.length }}/500</span>
            <Button @click="sendMessage" :disabled="!input.trim() || isSending || storyCompleted">
              Send
              <SendIcon class="h-4 w-4 ml-2" />
            </Button>
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
  components: { Button, Progress, Textarea, ArrowLeftIcon, SendIcon },
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
      showImageUrl: '',
      episodeId: '',
      chatId: this.$route.params.chat_id,
      showName: 'Loading...',
      episodeName: 'Loading...',
      playerImageUrl: '',
      input: '',
      toast: null,
      characters: [],
      player_name: '',
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
  created() { this.toast = useToast() },
  mounted() { this.connectToSocket(); this.fetchChatDetails() },
  beforeUnmount() { this.disconnectSocket() },
  computed: {
    hasActiveTypingIndicators() { return Object.values(this.typingIndicators).some(s => s === 'typing'); }
  },
  methods: {
    async fetchChatDetails() {
      try {
        const data = await fetchApi(`api/chats/${this.chatId}`)
        if (!data?.chat) throw new Error('Invalid chat data')
        const chatData = data.chat
        this.player_name = chatData.player_name || 'Player'
        this.episodeId = chatData.episode_id
        this.episodeName = chatData.episodes?.name || 'Unknown Episode'
        this.totalObjectives = JSON.parse(chatData.episodes.plot_objectives).length
        this.objectiveIndex = chatData.current_objective_index
        this.objectiveProgress = `${this.objectiveIndex}/${this.totalObjectives}`
        this.storyCompleted = chatData.story_completed
        if (chatData.player_image_url) this.playerImageUrl = chatData.player_image_url
        if (chatData.episodes?.show_id) {
          const showRes = await fetchApi(`api/shows/${chatData.episodes.show_id}`)
          if (showRes?.show) {
            const show = showRes.show
            this.showName = show.name
            this.showImageUrl = show.image_url || ''
            let chars = []
            try { chars = typeof show.characters === 'string' ? JSON.parse(show.characters) : show.characters || [] } catch { chars = [] }
            chars.forEach((c, i) => {
              const key = c.name.trim().toLowerCase()
              this.characterColors[key] = this.colorPalette[i % this.colorPalette.length]
              this.characterColors[c.name.trim()] = this.colorPalette[i % this.colorPalette.length]
              this.characterImages[key] = c.image_url
              this.characterImages[c.name.trim()] = c.image_url
            })
          }
        }
        ; (data.messages || []).forEach(m => this.messages.push({ role: m.role, content: m.content, type: m.type, sequence: m.sequence }))
        this.messages.sort((a, b) => a.sequence - b.sequence)
      } catch (e) { console.error(e); this.errorMessage = 'Failed to load chat details. Please refresh.' }
    },
    connectToSocket() {
      supabase.auth.getSession().then(({ data }) => {
        const token = data.session?.access_token
        this.socket = io(this.SOCKET_URL, { auth: { token }, extraHeaders: { Authorization: token ? `Bearer ${token}` : '' } })
        this.socket.on('connect', this.handleConnect)
        this.socket.on('connect_error', this.handleConnectionError)
        this.socket.on('disconnect', this.handleDisconnect)
        this.socket.on('dialogue', this.handleDialogue)
        this.socket.on('status', this.handleStatus)
        this.socket.on('error', this.handleError)
        this.socket.on('objective_status', this.handleObjectiveStatus)
        this.socket.on('typing_indicator', this.handleTypingIndicator)
        this.socket.on('director_status', this.handleDirectorStatus)
        this.socket.on('player_action', this.handlePlayerAction)
      }).catch(err => { console.error('Auth error', err); this.errorMessage = 'Auth failed' })
    },
    
    disconnectSocket() { if (this.socket) { if (this.chatId) this.socket.emit('leave_chat', { chat_id: this.chatId }); setTimeout(() => { this.socket.off(); this.socket.disconnect() }, 200) } },
    handleConnect() { this.isConnected = true; this.errorMessage = ''; this.socket.emit('join_chat', { chat_id: this.chatId }) },
    handleConnectionError(err) { console.error(err); this.isConnected = false; this.errorMessage = 'Server connection failed. Please refresh.' },
    handleDisconnect(reason) { console.log('Disconnected:', reason); this.isConnected = false; if (reason === 'io server_disconnect') this.socket.connect() },
    sendMessage() { if (!this.input.trim() || this.isSending || this.storyCompleted) return; this.isSending = true; this.messages.push({ role: 'Player', content: this.input, type: 'player_input' }); this.socket.emit('player_input', { chat_id: this.chatId, input: this.input }); this.input = ''; this.scrollToBottom(); this.isSending = false },
    handleTyping() { if (this.typingTimeout) clearTimeout(this.typingTimeout); if (this.storyCompleted) return; this.typingTimeout = setTimeout(() => { this.isTyping = false }, 2000) },
    handleDialogue(m) { if (m?.content) { this.messages.push({ role: m.role, content: m.content, type: m.type }); this.scrollToBottom() } },
    handleStatus(d) {console.log(d); if (d.message) this.statusMessage = d.message; if (d.story_completed) this.storyCompleted = true },
    handleError(e) { console.error(e); if (e.message) this.errorMessage = e.message },
    handleObjectiveStatus(o) { console.log(o); this.objectiveIndex = o.index || 0; this.totalObjectives = o.total || 1; this.progress = this.objectiveIndex > 0 && this.totalObjectives > 0 ? Math.max(1, Math.floor((this.objectiveIndex / this.totalObjectives) * 100)) : 0; this.objectiveProgress = `${this.objectiveIndex}/${this.totalObjectives}`; if (o.story_completed || o.final) { this.storyCompleted = true; this.statusMessage = "Story completed! You've reached the end of this episode." } this.scrollToBottom() },
    handleTypingIndicator(d) { if (d.role) { this.typingIndicators = { ...this.typingIndicators, [d.role]: d.status }; this.scrollToBottom() } },
    handleDirectorStatus(d) { this.directorDirecting = d.status === 'directing'; if (d.message) this.director_message = d.message; this.scrollToBottom() },
    handlePlayerAction(d) { if (d.content) this.toast.info("Your character needs to respond now.", { timeout: 8000, position: "top-center" }) },
    scrollToBottom() {
      this.
        $nextTick(() => { const c = this.$refs.messagesContainer; if (c) c.scrollTop = c.scrollHeight })
    },
    goBack() { this.$router.go(-1) },
    getCharacterImageUrl(r) { return this.characterImages[r.trim().toLowerCase()] || '' },
    getRoleColor(r) { const c = r.trim().toLowerCase(); if (this.characterColors[c]) return this.characterColors[c]; const m = { narration: 'text-purple-600 dark:text-purple-400', player: 'text-blue-600 dark:text-blue-400', system: 'text-gray-600 dark:text-gray-400' }; return m[c] || 'text-gray-600 dark:text-gray-400' },
    getMessageStyle(t, r) { const m = { narration: 'bg-purple-100 dark:bg-purple-900/30 italic', player_input: 'bg-blue-100 dark:bg-blue-900/30 text-left', system: 'bg-gray-100 dark:bg-gray-800/50 text-sm' }; if (t === 'actor_dialogue') { const l = r.trim().toLowerCase(); if (this.characterColors[l]) { const b = this.characterColors[l].split(' ')[0].replace('text', 'bg'); return `${b}/20 dark:${b}/30` } } return m[t] || 'bg-gray-100 dark:bg-gray-800/30' }
  },
  watch: {
    isConnected(v) { if (v && !this.isChatStarted && !this.storyCompleted) setTimeout(() => { this.isChatStarted = true }, 1000) },
    storyCompleted(v) { if (v) { this.statusMessage = "Story completed! You've reached the end of this episode.";const chat_id = this.$route.params.chat_id; this.$router.push(`/end/${this.episodeId}/${chat_id}`) } }
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

.dark .overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.3);
}

.dark .overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background-color: rgba(156, 163, 175, 0.5);
}

/* Director progress animation */
@keyframes directorProgress {
  from {
    width: 0%;
  }

  to {
    width: 100%;
  }
}

.animate-director-progress {
  animation: directorProgress 6s linear;
}
</style>
