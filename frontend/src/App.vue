<template>
  <div class="min-h-screen bg-background text-foreground flex flex-col">
    <header class="border-b">
      <div class="container mx-auto flex h-16 items-center justify-between px-4">
        <div class="flex items-center gap-6">
          <router-link to="/" class="flex items-center gap-2 font-bold">
            <span class="text-2xl">SitChat</span>
          </router-link>
          <nav class="flex items-center gap-6">
            <router-link to="/" class="text-sm font-medium">Home</router-link>
            <router-link to="/shows" class="text-sm font-medium">Shows</router-link>
          </nav>
        </div>
        <div class="flex items-center gap-4">
          <template v-if="user">
            <div class="text-sm">{{ user.username || user.email }}</div>
            <Button @click="logout" variant="outline" size="sm">Logout</Button>
          </template>
          <template v-else>
            <router-link to="/auth">
              <Button variant="default" size="sm">Sign In</Button>
            </router-link>
          </template>
        </div>
      </div>
    </header>
    <main class="flex-1">
      <router-view />
    </main>
    <footer class="border-t py-6">
      <div class="container mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <p class="text-sm text-muted-foreground">© 2025 SitChat. All rights reserved.</p>
        <div class="flex items-center gap-4">
          <a href="#" class="text-sm text-muted-foreground hover:text-foreground">Privacy Policy</a>
          <a href="#" class="text-sm text-muted-foreground hover:text-foreground">Terms of Service</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Button } from '@/components/ui/button'
import { useSupabase } from '@/composables/useSupabase'
import { useToast } from 'vue-toastification'
import { useRouter } from 'vue-router'

const { supabase } = useSupabase()
const toast = useToast()
const router = useRouter()
const user = ref(null)

onMounted(async () => {
  // Get the initial session
  const { data, error } = await supabase.auth.getSession()
  
  if (data?.session) {
    await getUser(data.session.user.id)
  }
  
  // Listen for auth state changes
  supabase.auth.onAuthStateChange(async (event, session) => {
    if (event === 'SIGNED_IN' && session) {
      await getUser(session.user.id)
    } else if (event === 'SIGNED_OUT') {
      user.value = null
    }
  })
})

async function getUser(userId) {
  try {
    // Try to fetch the user profile
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .eq('id', userId)
      .maybeSingle() // Use maybeSingle() instead of single() to avoid errors when no records found
    
    if (error && error.code !== 'PGRST116') {
      // Only throw for errors other than "no records found"
      throw error
    }
    
    if (data) {
      // If data exists, use it
      user.value = data
    } else {
      // If no profile exists yet, create a minimal user object
      // This provides a fallback while the profile is being created
      const { data: sessionData } = await supabase.auth.getSession()
      const email = sessionData?.session?.user?.email || 'User'
      
      user.value = { 
        id: userId, 
        username: 'User',
        email: email
      }
      
      // Optionally, retry after a short delay
      setTimeout(() => {
        // This will retry once after 2 seconds
        getUser(userId)
      }, 2000)
    }
  } catch (error) {
    console.error('Error fetching user:', error)
    // Fallback with minimal user info
    const { data: sessionData } = await supabase.auth.getSession()
    const email = sessionData?.session?.user?.email || 'User'
    
    user.value = { 
      id: userId, 
      email: email
    }
  }
}

async function logout() {
  try {
    await supabase.auth.signOut()
    user.value = null
    toast.success('Logged out successfully')
    router.push('/')
  } catch (error) {
    toast.error('Error logging out')
    console.error(error)
  }
}
</script>