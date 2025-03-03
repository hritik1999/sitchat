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
            <router-link to="/leaderboards" class="text-sm font-medium text-slate-900 dark:text-slate-50 hover:text-primary transition-colors">
              Leaderboards
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
                Profile
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
          to="/leaderboards"
          class="flex flex-col items-center gap-1 text-xs font-medium text-slate-900 dark:text-slate-50 hover:text-primary transition-colors"
        >
          <TrophyIcon class="h-5 w-5" />
          <span>Leaderboards</span>
        </router-link>
        <router-link 
          to="/profile"
          class="flex flex-col items-center gap-1 text-xs font-medium text-slate-900 dark:text-slate-50 hover:text-primary transition-colors"
        >
          <UserIcon class="h-5 w-5" />
          <span>Profile</span>
        </router-link>
        <!-- Theme toggle in mobile nav -->
        <button 
          @click="toggleTheme"
          class="flex flex-col items-center gap-1 text-xs font-medium text-slate-900 dark:text-slate-50 hover:text-primary transition-colors"
        >
          <SunIcon v-if="isDarkTheme" class="h-5 w-5" />
          <MoonIcon v-else class="h-5 w-5" />
          <span>Theme</span>
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <main class="flex-1 container mx-auto px-4 pb-16 md:pb-4">
      <slot></slot>
    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 hidden md:block">
      <div class="container mx-auto px-4 py-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 class="text-lg font-semibold mb-4 text-slate-900 dark:text-slate-50">Sitchat</h3>
            <p class="text-sm text-slate-500 dark:text-slate-400">
              Bringing stories to life through interactive AI experiences
            </p>
          </div>
          <div>
            <h3 class="text-lg font-semibold mb-4 text-slate-900 dark:text-slate-50">Legal</h3>
            <ul class="space-y-2 text-sm">
              <li><a href="#" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">Privacy Policy</a></li>
              <li><a href="#" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">Terms of Service</a></li>
            </ul>
          </div>
          <div>
            <h3 class="text-lg font-semibold mb-4 text-slate-900 dark:text-slate-50">Social</h3>
            <div class="flex gap-4">
              <a href="#" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">
                <!-- <TwitterIcon class="h-5 w-5" /> -->
              </a>
              <a href="#" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">
                <!-- <DiscordIcon class="h-5 w-5" /> -->
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
  beforeUnmount() {
    // Clean up the subscription to avoid memory leaks
    if (this.authSubscription) {
      this.authSubscription.unsubscribe()
    }
  }
}
</script>