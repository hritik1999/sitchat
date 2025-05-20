<!-- src/layouts/MainLayout.vue -->
<template>
  <div class="min-h-screen flex flex-col bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-50">
    <!-- Desktop Navbar -->
    <nav class="bg-white/95 dark:bg-slate-950/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:supports-[backdrop-filter]:bg-slate-950/60 border-b border-slate-200 dark:border-slate-800 hidden md:block">
      <div class="container mx-auto px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-8">
          <router-link to="/" class="flex items-center gap-2">
            <span class="text-2xl font-bold">Sitchat</span>
          </router-link>
          <div class="flex gap-6">
            <router-link to="/shows" class="text-sm font-medium text-slate-900 dark:text-slate-50 hover:text-primary transition-colors">
              Shows
            </router-link>
            <router-link to="/Chat/History" class="text-sm font-medium text-slate-900 dark:text-slate-50 hover:text-primary transition-colors">
              Chat History
            </router-link>
            <router-link to="/leaderboard" class="text-sm font-medium text-slate-900 dark:text-slate-50 hover:text-primary transition-colors">
              Leaderboard
            </router-link>
          </div>
        </div>

        <div class="flex items-center gap-4">
          <!-- Theme Toggle Button -->
          <Button
            variant="ghost"
            size="icon"
            class="rounded-full"
            @click="toggleTheme"
            :title="isDarkTheme ? 'Switch to light mode' : 'Switch to dark mode'"
          >
            <SunIcon v-if="isDarkTheme" class="h-5 w-5" />
            <MoonIcon v-else class="h-5 w-5" />
            <span class="sr-only">{{ isDarkTheme ? 'Light Mode' : 'Dark Mode' }}</span>
          </Button>
          
          <DropdownMenu v-if="user">
            <DropdownMenuTrigger class="flex items-center gap-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full p-2">
              <div class="h-8 w-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center">
                <UserIcon class="h-4 w-4" />
              </div>
              <ChevronDownIcon class="h-4 w-4" />
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem>
                <UserIcon class="mr-2 h-4 w-4" />
                <Router-link to="/profile">Profile</Router-link>
              </DropdownMenuItem>
              <DropdownMenuItem @click="logout">
                <LogOutIcon class="mr-2 h-4 w-4" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <Button v-else @click="login">
            Sign In
          </Button>
        </div>
      </div>
    </nav>

    <!-- Mobile Bottom Nav -->
    <div class="fixed bottom-0 left-0 right-0 border-t border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-slate-950/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:supports-[backdrop-filter]:bg-slate-950/60 md:hidden z-50">
      <div class="grid grid-cols-4 gap-2 p-2">
        <router-link 
          to="/shows"
          class="flex flex-col items-center gap-1 text-xs font-medium text-slate-900 dark:text-slate-50 hover:text-primary transition-colors"
        >
          <TvIcon class="h-5 w-5" />
          <span>Shows</span>
        </router-link>
        <router-link 
          to="/Chat/History"
          class="flex flex-col items-center gap-1 text-xs font-medium text-slate-900 dark:text-slate-50 hover:text-primary transition-colors"
        >
          <ChatIcon class="h-5 w-5" />
          <span>Chat History</span>
        </router-link>
        <router-link 
          to="/leaderboard"
          class="flex flex-col items-center gap-1 text-xs font-medium text-slate-900 dark:text-slate-50 hover:text-primary transition-colors"
        >
          <TrophyIcon class="h-5 w-5" />
          <span>Leaderboard</span>
        </router-link>
        <router-link 
          to="/profile"
          class="flex flex-col items-center gap-1 text-xs font-medium text-slate-900 dark:text-slate-50 hover:text-primary transition-colors"
        >
          <UserIcon class="h-5 w-5" />
          <span>Profile</span>
        </router-link>
        <!-- Theme toggle in mobile nav -->
      </div>
    </div>

    <!-- Main Content -->
    <main class="flex-1 container mx-auto px-4 pb-16 md:pb-4">
      <slot></slot>
    </main>

        <!-- Footer -->
        <footer class="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 hidden md:block">
      <div class="container mx-auto px-4 py-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <!-- Brand Info -->
          <div>
            <h3 class="text-lg font-semibold mb-4 text-slate-900 dark:text-slate-50">Sitchat</h3>
            <p class="text-sm text-slate-500 dark:text-slate-400">
              Bringing stories to life through interactive AI experiences
            </p>
          </div>

          <!-- Company Links -->
          <div>
            <h3 class="text-lg font-semibold mb-4 text-slate-900 dark:text-slate-50">Company</h3>
            <ul class="space-y-2 text-sm">
              <li><router-link to="/about" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">About Us</router-link></li>
              <li><router-link to="/career" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">Careers</router-link></li>
              <li><router-link to="/blogs" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">Blog</router-link></li>
            </ul>
          </div>

          <!-- Legal Links -->
          <div>
            <h3 class="text-lg font-semibold mb-4 text-slate-900 dark:text-slate-50">Legal</h3>
            <ul class="space-y-2 text-sm">
              <li><router-link to="/terms" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">Terms & Conditions</router-link></li>
              <li><router-link to="/privacy" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">Privacy Policy</router-link></li>
            </ul>
          </div>

          <!-- Social Links -->
          <div>
            <h3 class="text-lg font-semibold mb-4 text-slate-900 dark:text-slate-50">Social</h3>
            <div class="flex gap-4">
              <!-- Reddit -->
            <a href="https://www.reddit.com/r/Sitchat/" target="_blank" rel="noopener noreferrer" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">
             <svg xmlns="http://www.w3.org/2000/svg" x="0px" y="0px" width="24" height="24" viewBox="0 0 80 80">
            <path fill="#fff" d="M69,45.5c-4.7,0-8.5-3.8-8.5-8.5s3.8-8.5,8.5-8.5s8.5,3.8,8.5,8.5S73.7,45.5,69,45.5z"></path><path fill="#788b9c" d="M69,29c4.4,0,8,3.6,8,8s-3.6,8-8,8s-8-3.6-8-8S64.6,29,69,29 M69,28c-5,0-9,4-9,9s4,9,9,9s9-4,9-9 S74,28,69,28L69,28z"></path><path fill="#fff" d="M11,45.5c-4.7,0-8.5-3.8-8.5-8.5s3.8-8.5,8.5-8.5s8.5,3.8,8.5,8.5S15.7,45.5,11,45.5z"></path><path fill="#788b9c" d="M11,29c4.4,0,8,3.6,8,8s-3.6,8-8,8s-8-3.6-8-8S6.6,29,11,29 M11,28c-5,0-9,4-9,9s4,9,9,9s9-4,9-9 S16,28,11,28L11,28z"></path><path fill="#fff" d="M40,73.5c-19.6,0-35.5-11-35.5-24.5S20.4,24.5,40,24.5s35.5,11,35.5,24.5S59.6,73.5,40,73.5z"></path><path fill="#788b9c" d="M40,25c19.3,0,35,10.8,35,24S59.3,73,40,73S5,62.2,5,49S20.7,25,40,25 M40,24C20,24,4,35.3,4,49 s16,25,36,25s36-11.3,36-25S60,24,40,24L40,24z"></path><path fill="#f78f8f" d="M27 40.5A4.5 4.5 0 1 0 27 49.5A4.5 4.5 0 1 0 27 40.5Z"></path><path fill="#c74343" d="M27,41c2.2,0,4,1.8,4,4s-1.8,4-4,4s-4-1.8-4-4S24.8,41,27,41 M27,40c-2.8,0-5,2.2-5,5s2.2,5,5,5 s5-2.2,5-5S29.8,40,27,40L27,40z"></path><g><path fill="#f78f8f" d="M53 40.5A4.5 4.5 0 1 0 53 49.5A4.5 4.5 0 1 0 53 40.5Z"></path><path fill="#c74343" d="M53,41c2.2,0,4,1.8,4,4s-1.8,4-4,4s-4-1.8-4-4S50.8,41,53,41 M53,40c-2.8,0-5,2.2-5,5s2.2,5,5,5 s5-2.2,5-5S55.8,40,53,40L53,40z"></path></g><path fill="#788b9c" d="M40,63.5c-8.8,0-13.2-5.2-13.4-5.4c-0.2-0.2-0.1-0.5,0.1-0.7s0.5-0.2,0.7,0.1c0,0.1,4.3,5,12.6,5 c8.3,0,12.6-5,12.6-5c0.2-0.2,0.5-0.2,0.7-0.1c0.2,0.2,0.2,0.5,0.1,0.7C53.2,58.3,48.8,63.5,40,63.5z"></path><g><path fill="#b6c9d6" d="M70.5 6.5A5 5 0 1 0 70.5 16.5A5 5 0 1 0 70.5 6.5Z"></path><path fill="#788b9c" d="M70.5,7C73,7,75,9,75,11.5S73,16,70.5,16S66,14,66,11.5S68,7,70.5,7 M70.5,6c-3,0-5.5,2.5-5.5,5.5 s2.5,5.5,5.5,5.5s5.5-2.5,5.5-5.5S73.5,6,70.5,6L70.5,6z"></path></g><path fill="#788b9c" d="M41,24h-1v-8.2c0-4.4,3.3-7.7,7.7-7.7c1.8,0,3.7,0.5,5.8,1.1c3,0.8,6.7,1.9,12,1.9v1 c-5.4,0-9.2-1.1-12.2-1.9C51.2,9.5,49.4,9,47.7,9c-3.9,0-6.7,2.8-6.7,6.7V24z"></path>
            </svg>
            </a>

              <!-- Instagram -->
              <a href="https://www.instagram.com/sitchat.ai/" target="_blank" rel="noopener noreferrer" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/>
                </svg>
              </a>

              <!-- X (Twitter) -->
              <a href="https://x.com/AI_Bhaiiii" target="_blank" rel="noopener noreferrer" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"/>
                </svg>
              </a>

              <!-- YouTube -->
              <a href="https://www.youtube.com/@Sitchat-ai" target="_blank" rel="noopener noreferrer" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
              </a>

              <!-- Discord -->
              <a href="https://discord.gg/T32mC8nPZY" target="_blank" rel="noopener noreferrer" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19.27 5.33C17.94 4.71 16.5 4.26 15 4a.09.09 0 0 0-.07.03c-.18.33-.39.76-.53 1.09a16.09 16.09 0 0 0-4.8 0c-.14-.34-.35-.76-.54-1.09c-.01-.02-.04-.03-.07-.03c-1.5.26-2.93.71-4.27 1.33c-.01 0-.02.01-.03.02c-2.72 4.07-3.47 8.03-3.1 11.95c0 .02.01.04.03.05c1.8 1.32 3.53 2.12 5.24 2.65c.03.01.06 0 .07-.02c.4-.55.76-1.13 1.07-1.74c.02-.04 0-.08-.04-.09c-.57-.22-1.11-.48-1.64-.78c-.04-.02-.04-.08-.01-.11c.11-.08.22-.17.33-.25c.02-.02.05-.02.07-.01c3.44 1.57 7.15 1.57 10.55 0c.02-.01.05-.01.07.01c.11.09.22.17.33.26c.04.03.04.09-.01.11c-.52.31-1.07.56-1.64.78c-.04.01-.05.06-.04.09c.32.61.68 1.19 1.07 1.74c.03.01.06.02.09.01c1.72-.53 3.45-1.33 5.25-2.65c.02-.01.03-.03.03-.05c.44-4.53-.73-8.46-3.1-11.95c-.01-.01-.02-.02-.04-.02zM8.52 14.91c-1.03 0-1.89-.95-1.89-2.12s.84-2.12 1.89-2.12c1.06 0 1.9.96 1.89 2.12c0 1.17-.84 2.12-1.89 2.12zm6.97 0c-1.03 0-1.89-.95-1.89-2.12s.84-2.12 1.89-2.12c1.06 0 1.9.96 1.89 2.12c0 1.17-.83 2.12-1.89 2.12z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  ChevronDownIcon,
  DiscIcon as TrophyIcon,
  UserIcon,
  LogOutIcon,
  TvIcon,
  SunIcon,
  MoonIcon,
  MessageCircleMore as ChatIcon,
} from 'lucide-vue-next'
import { supabase } from '@/composables/useSupabase'

export default {
  name: 'MainLayout',
  components: {
    Button,
    ChevronDownIcon,
    TrophyIcon,
    UserIcon,
    LogOutIcon,
    TvIcon,
    SunIcon,
    MoonIcon,
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
    ChatIcon,
  },
  data() {
    return {
      user: null,
      authSubscription: null,
      isDarkTheme: false
    }
  },
  methods: {
    login() {
      // Use window.location for more direct navigation
      window.location.href = '/login'
    },
    async logout() {
      try {
        localStorage.removeItem('sb-wpwichwnfgbpggcqujld-auth-token')
        await supabase.auth.signOut()
        // Force a full page reload to reset auth state
        window.location.href = '/login'
      } catch (error) {
        console.error('Error during logout:', error)
      }
    },
    async checkUser() {
      const { data } = await supabase.auth.getSession()
      this.user = data.session?.user || null
    },
    toggleTheme() {
      // Toggle dark theme state
      this.isDarkTheme = !this.isDarkTheme
      
      // Apply theme
      if (this.isDarkTheme) {
        document.documentElement.classList.add('dark')
        console.log('Dark mode enabled')
      } else {
        document.documentElement.classList.remove('dark')
        console.log('Light mode enabled')
      }
      
      // Save preference to localStorage
      localStorage.setItem('theme', this.isDarkTheme ? 'dark' : 'light')
    },
    initTheme() {
      // Check if theme is stored in localStorage
      const savedTheme = localStorage.getItem('theme')
      
      if (savedTheme) {
        // Apply saved theme
        this.isDarkTheme = savedTheme === 'dark'
      } else {
        // Check for system preference
        this.isDarkTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
      }
      
      // Apply initial theme
      if (this.isDarkTheme) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
      
      // Set up listener for system preference changes
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (localStorage.getItem('theme') === null) {
          this.isDarkTheme = e.matches
          if (this.isDarkTheme) {
            document.documentElement.classList.add('dark')
          } else {
            document.documentElement.classList.remove('dark')
          }
        }
      })
    }
  },
  async mounted() {
    // Initialize theme
    this.initTheme()
    
    // Get initial auth state
    await this.checkUser()
    
    // Set up auth state listener
    const { data } = supabase.auth.onAuthStateChange(async (event, session) => {
      this.user = session?.user || null
      
      // If user logged out, redirect to login page
      if (event === 'SIGNED_OUT') {
        window.location.href = '/login'
      }
    })
    
    this.authSubscription = data
  },
}
</script>