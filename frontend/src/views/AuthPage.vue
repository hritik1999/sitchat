<template>
  <div class="min-h-screen flex flex-col md:flex-row bg-white">
    <!-- Left Side - Compact Auth (30%) -->
    <div class="w-full md:w-[25%] flex items-center justify-center p-6 bg-white">
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
          <Button variant="link" class="text-xs h-auto p-0 text-gray-500" @click="router.push('/terms')">Terms</Button> 
          and 
          <Button variant="link" class="text-xs h-auto p-0 text-gray-500" @click="router.push('/privacy')">Privacy</Button>
        </p>
      </div>
    </div>

    <!-- Right Side - Immersive Preview (70%) -->
    <div class="w-full md:w-[75%] relative min-h-[60vh] bg-black">
      <!-- Hero Section -->
      <section class="container mx-auto px-4 py-4 md:py-4">
        <div class="text-center space-y-6">
          <Badge variant="outline" class="text-lg py-2 px-4 bg-purple-100 dark:bg-purple-900/20">
            🎬 The Future of Fan-Powered Storytelling
          </Badge>
          <h1 class="text-5xl md:text-6xl font-bold bg-gradient-to-r from-purple-400 to-blue-500 bg-clip-text text-transparent">
            Welcome to Sitchat
          </h1>
          <p class="text-xl md:text-2xl text-white text-muted-foreground max-w-3xl mx-auto">
            Where you don't just watch - you participate. Dive into immersive group chats with AI versions of your favorite characters!
          </p>
        </div>
      </section>
  
      <!-- Features Grid -->
      <section class="bg-muted/50 py-6">
        <div class="container mx-auto px-4 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card
            v-for="(feature, index) in features"
            :key="index"
            class="p-4 bg-white dark:bg-gray-800 rounded-xl shadow hover:shadow-xl transition-shadow duration-300"
          >
            <div class="flex items-center space-x-4 mb-4">
              <div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
                <Component :is="feature.icon" class="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
              <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
                {{ feature.title }}
              </h3>
            </div>
            <p class="text-muted-foreground mb-4">
              {{ feature.description }}
            </p>
            <div class="flex flex-wrap gap-2">
              <Badge
                v-for="(tag, tagIndex) in feature.tags"
                :key="tagIndex"
                variant="secondary"
                class="px-2 py-1 text-sm"
              >
                {{ tag }}
              </Badge>
            </div>
          </Card>
        </div>
      </section>
      <!-- CTA Section -->
      <section class="">
        <div class=" mx-auto px-4 text-center">
          <h3 class="text-xl text-muted-foreground mx-auto py-4 max-w-3xl text-white">
            Create shows, build episodes, earn achievements, and experience being part of the show!
          </h3>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { PlayIcon, SparklesIcon, GlobeIcon, ShareIcon,
  Sparkles, 
    Mail, 
    Phone, 
    Play,
    Users,
    Bot,
    LayoutDashboard,
    Trophy,
    GalleryVerticalEnd
 } from 'lucide-vue-next'
 import { Badge } from '@/components/ui/badge'
  import { Card } from '@/components/ui/card'
  import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar'
import { supabase } from '@/composables/useSupabase';
import { fetchApi } from '@/lib/utils';

export default {
  name: 'AuthPage',
  components: {
    Button,
    Badge,
    Card,
    Avatar,
    AvatarImage,
    AvatarFallback,
    PlayIcon,
    SparklesIcon,
    GlobeIcon,
    ShareIcon,
    Sparkles,
    Mail,
    Phone,
    Play,
    Users,
    Bot,
    LayoutDashboard,
    Trophy,
    GalleryVerticalEnd
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
      confirmPassword: '',
      features : [
  {
    icon: Users,
    title: "Group Chat Stories",
    description: "Interact with multiple AI characters from your favourite shows in dynamic group chats",
    tags: ["Multi-character", "Immersive", "Interactive"]
  },
  {
    icon: LayoutDashboard,
    title: "Create Your Shows",
    description: "Create your favorite shows or imagine entirely new ones—craft worlds, characters. and storylines.",
    tags: ["Customization", "Creative Freedom", "Fan-fiction"]
  },
  {
    icon: Sparkles,
    title: "Create Episodes",
    description: "Design episodes by setting plot objectives and explore unique, personalized storylines!",
    tags: ["Story Builder", "Unique Plots", "Episode Creation"]
  },
  {
    icon: Trophy,
    title: "Earn Achievements",
    description: "Unlock hilarious milestones as you interact with characters",
    tags: ["Badges", "Milestones", "Fun"]
  },
  {
    icon: GalleryVerticalEnd,
    title: "Story Progression",
    description: "Structured narratives with real plot development",
    tags: ["Plotlines", "Objectives", "Challenges"]
  },
  {
  icon: ShareIcon,
  title: "Share Your Stories",
  description: "Create captivating storylines and share them with your friends to experience together.",
  tags: ["Social", "Story Sharing", "Collaborative"]
}
]
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
.card:hover {
  border-color: theme('colors.purple.600');
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