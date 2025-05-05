<template>
  <div class="min-h-screen flex flex-col md:flex-row bg-white">
    <!-- Left Side - Compact Auth (30%) -->
    <div class="w-full md:w-[30%] flex items-center justify-center p-6 bg-white">
      <div class="w-full max-w-[320px] space-y-6">
        <div class="text-center space-y-2">
          <div class="mb-6">
            <span class="text-4xl font-bold text-black tracking-wider dark:text-white">SitChat</span>
          </div>
          <h1 class="text-2xl font-bold text-black dark:text-white">Begin Your Story</h1>
          <p class="text-sm text-gray-500 dark:text-gray-400">Experience your Favourite Sitcoms!</p>
        </div>

        <div class="space-y-3">
          <Button variant="outline" class="w-full h-11 gap-2 hover:bg-gray-100 transition-all dark:hover:bg-gray-800" @click="signInWithProvider('google')">
            <img src="https://upload.wikimedia.org/wikipedia/commons/7/7e/Gmail_icon_%282020%29.svg" alt="Google Logo" class="h-4 w-4" />
            <span class="text-sm text-black dark:text-white">Continue with Google</span>
          </Button>
          
          <div class="relative py-4">
            <div class="absolute inset-0 flex items-center">
              <span class="w-full border-t border-gray-300" />
            </div>
          </div>
        </div>

        <p class="text-center text-xs text-gray-500 px-4">
          By continuing, you agree to our 
          <Button variant="link" class="text-xs h-auto p-0 text-gray-500">Terms</Button> 
          and 
          <Button variant="link" class="text-xs h-auto p-0 text-gray-500">Privacy</Button>
        </p>
      </div>
    </div>

    <!-- Right Side - Immersive Preview (70%) -->
    <div class="w-full md:w-[70%] relative min-h-[60vh] bg-black">
      <div class="absolute inset-0 pattern-dots pattern-gray-500 pattern-opacity-20 pattern-size-4"></div>
      
      <div class="relative h-full flex items-center justify-center p-8">
        <div class="max-w-4xl space-y-8 text-center">
          <div class="space-y-4 animate-fade-in">
            <h2 class="text-5xl font-bold text-white leading-tight">
              Where Your Favourite Sitcoms Come<br>to <span class="text-gray-400">Life</span>
            </h2>
            <p class="text-xl text-gray-300">Interactive stories powered by AI</p>
          </div>

          <!-- Responsive Grid -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
            <div class="feature-card">
              <div class="icon-container">
                <SparklesIcon class="h-6 w-6 text-white" />
              </div>
              <h3 class="text-lg font-medium text-white mt-4">Dynamic Episodes</h3>
              <p class="text-sm text-gray-300 mt-2">Experience dynamic stories where you become part of the narrative.</p>
            </div>

            <div class="feature-card">
              <div class="icon-container">
                <GlobeIcon class="h-6 w-6 text-white" />
              </div>
              <h3 class="text-lg font-medium text-white mt-4">Create Stories</h3>
              <p class="text-sm text-gray-300 mt-2">Design your shows with detailed characters, relationships, and plot objectives.</p>
            </div>

            <div class="feature-card">
              <div class="icon-container">
                <ShareIcon class="h-6 w-6 text-white" />
              </div>
              <h3 class="text-lg font-medium text-white mt-4">Participate</h3>
              <p class="text-sm text-gray-300 mt-2">Join the conversation as an interactive character, influencing the story's direction.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { PlayIcon, SparklesIcon, GlobeIcon, ShareIcon } from 'lucide-vue-next'
import { supabase } from '@/composables/useSupabase';
import { fetchApi } from '@/lib/utils';

export default {
  name: 'AuthPage',
  components: {
    Button,
    PlayIcon,
    SparklesIcon,
    GlobeIcon,
    ShareIcon
  },
  setup() {
    const router = useRouter()
    return { router }
  },
  data() {
    return {
      api_url: import.meta.env.VITE_API_URL || 'http://localhost:5001',
      authSubscription: null,
      email: '',
      username: '',
      password: '',
      confirmPassword: ''
    }
  },
  created() {
    // Check for existing session
    this.checkExistingSession();

    // Set up the auth state listener when the component is created
    const { data: authListener } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log("Auth state changed:", event);
        if (session) {
          // If we have a session, verify with backend
          if (event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED') {
            try {
              const data = await fetchApi('auth/verify', {
                method: "POST",
                body: JSON.stringify({ access_token: session.access_token }),
              });
              
              console.log("Backend verification on auth change:", data);
              
              // If user is authenticated, redirect to home
              if (data.user) {
                this.$router.push('/');
              }
            } catch (err) {
              console.error("Error verifying session:", err);
            }
          }
        } else if (event === 'SIGNED_OUT') {
          localStorage.removeItem("supabase_session");
          this.$router.push('/auth');
        }
      }
    );
    this.authSubscription = authListener;
  },
  beforeDestroy() {
    // Clean up the subscription to avoid memory leaks
    if (this.authSubscription) {
      this.authSubscription.unsubscribe();
    }
  },
  methods: {
    async signInWithProvider(provider) {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: provider, // "google" or "apple"
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
        },
      });
      if (error) console.error("OAuth error:", error);
    },
    async checkExistingSession() {
      try {
        // Check if we have an existing session
        const { data: { session } } = await supabase.auth.getSession();
        if (session) {
          // Verify with backend
          const data = await fetchApi('auth/verify', {
            method: "POST",
            body: JSON.stringify({ access_token: session.access_token }),
          });
          
          console.log("Existing session verification:", data);
          
          // If user is authenticated, redirect to home
          if (data.user) {
            this.$router.push('/');
          }
        }
      } catch (err) {
        console.error("Error checking existing session:", err);
      }
    }
  }
}
</script>

<style>
/* Custom styles for black & white theme */
.pattern-dots {
  background-image: radial-gradient(currentColor 1px, transparent 1px);
  background-size: 16px 16px;
}

.feature-card {
  @apply p-6 rounded-xl backdrop-blur-sm bg-gray-900 hover:bg-gray-800 transition-all cursor-pointer border border-white;
}

.icon-container {
  @apply p-3 rounded-lg w-fit transition-transform hover:scale-105;
}

.animate-fade-in {
  animation: fadeIn 0.8s ease-out;
}

.animate-slide-up {
  animation: slideUp 0.6s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.icon-container {
  @apply p-3 rounded-lg w-full flex justify-center items-center transition-transform hover:scale-105;
}
</style>