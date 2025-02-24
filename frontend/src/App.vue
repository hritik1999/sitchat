<template>
  <Card class="w-full h-full flex flex-col">
    <CardHeader class="border-b text-center">
      <CardTitle> SitChat</CardTitle>
    </CardHeader>
    <CardContent class="flex-1 p-4 overflow-hidden">
      <ScrollArea class="h-full w-full">
        <div ref="messagesContainer" class="space-y-4">
          <div
            v-for="(message, index) in messages"
            :key="index"
            class="flex items-end gap-2"
            :class="characters[message.character].alignRight ? 'justify-end' : 'justify-start'"
          >
            <img
              v-if="!characters[message.character].alignRight"
              :src="characters[message.character].avatar"
              class="h-8 w-8 rounded-full"
            />
            <div class="flex flex-col space-y-2 max-w-[70%]"
              :class="characters[message.character].alignRight ? 'items-end' : 'items-start'">
              <div
                class="rounded-lg px-4 py-2"
                :class="[
                  characters[message.character].bg,
                  characters[message.character].text
                ]"
              >
                {{ message.content }}
              </div>
              <span class="text-xs text-muted-foreground">
                {{ message.timestamp }} - {{ characters[message.character].name }}
              </span>
            </div>
            <img
              v-if="characters[message.character].alignRight"
              :src="characters[message.character].avatar"
              class="h-8 w-8 rounded-full"
            />
          </div>
        </div>
      </ScrollArea>
    </CardContent>
    <CardFooter class="border-t p-4">
      <form @submit.prevent="sendMessage" class="flex w-full space-x-2">
        <Input
          v-model="newMessage"
          placeholder="Type your message..."
          class="flex-1"
        />
        <Button type="submit">
          Send
        </Button>
      </form>
    </CardFooter>
  </Card>
</template>

<script>
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useColorMode } from '@vueuse/core'

export default {
  components: {
    Card,
    CardContent,
    CardFooter,
    CardHeader,
    CardTitle,
    Input,
    Button,
    ScrollArea
  },
  data() {
    return {
      newMessage: '',
      mode: useColorMode('dark'),
      characters: {
        user: {
          name: 'You',
          avatar: '/user-avatar.png',
          bg: 'bg-primary',
          text: 'text-primary-foreground',
          alignRight: true
        },
        assistant: {
          name: 'AI Assistant',
          avatar: '/assistant-avatar.png',
          bg: 'bg-muted',
          text: 'text-foreground',
          alignRight: false
        },
        dog: {
          name: 'Dog Bot',
          avatar: '/dog-avatar.png',
          bg: 'bg-amber-500',
          text: 'text-white',
          alignRight: false
        }
      },
      messages: [
        {
          content: 'Hello! How can I help you today?',
          character: 'assistant',
          timestamp: this.getCurrentTime()
        },
        {
          content: 'Woof! I\'m here to help with pet questions!',
          character: 'dog',
          timestamp: this.getCurrentTime()
        }
      ]
    }
  },
  methods: {
    getCurrentTime() {
      return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    },
    async sendMessage() {
      if (!this.newMessage.trim()) return

      const userMessage = {
        content: this.newMessage.trim(),
        character: 'user',
        timestamp: this.getCurrentTime()
      }

      this.messages.push(userMessage)
      this.newMessage = ''

      // Simulate different character responses
      setTimeout(() => {
        this.messages.push({
          content: 'This is an AI response',
          character: 'assistant',
          timestamp: this.getCurrentTime()
        })
      }, 1000)

      setTimeout(() => {
        this.messages.push({
          content: 'Woof! That\'s interesting!',
          character: 'dog',
          timestamp: this.getCurrentTime()
        })
      }, 1500)

      await this.$nextTick()
      this.scrollToBottom()
    },
    scrollToBottom() {
      const container = this.$refs.messagesContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    }
  },
  mounted() {
    this.scrollToBottom()
  }
}
</script>

<style scoped>
/* Custom avatar styling */
img {
  flex-shrink: 0;
}
</style>