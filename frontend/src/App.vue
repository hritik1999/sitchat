<template>
  <Card class="w-full h-full flex flex-col">
    <CardHeader class="border-b text-center">
      <CardTitle>SitChat</CardTitle>
    </CardHeader>
    <CardContent class="flex-1 p-4 overflow-hidden">
      <ScrollArea class="h-full w-full">
        <div ref="messagesContainer" class="space-y-4">
          <div
            v-for="(message, index) in messages"
            :key="index"
            class="flex items-end"
            :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              class="flex flex-col space-y-2 max-w-[80%]"
              :class="message.role === 'user' ? 'items-end' : 'items-start'"
            >
              <div
                class="rounded-lg px-4 py-2"
                :class="
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                "
              >
                {{ message.content }}
              </div>
              <span class="text-xs text-muted-foreground">
                {{ message.timestamp }} - {{ message.role }}
              </span>
            </div>
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
      messages: [
        {
          content: 'Hello! How can I help you today?',
          role: 'bot',
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
        role: 'user',
        timestamp: this.getCurrentTime()
      }

      this.messages.push(userMessage)
      this.newMessage = ''

      // Simulate bot response
      setTimeout(() => {
        this.messages.push({
          content: 'This is a simulated response',
          role: 'bot',
          timestamp: this.getCurrentTime()
        })
        this.scrollToBottom()
      }, 1000)

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
