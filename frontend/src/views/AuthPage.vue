<template>
  <div class="min-h-screen flex flex-col md:flex-row bg-white">
    <!-- Left Side – unified auth panel -->
    <div
      class="w-full md:w-1/3 bg-white dark:bg-gray-900 flex items-start justify-center p-6"
    >
    <div class="w-full max-w-md space-y-8 pt-6 md:pt-16">
        <!-- Logo & Tagline -->
        <div class="text-center">
          <h1 class="text-4xl font-extrabold text-gray-900 dark:text-gray-100">
            SitChat
          </h1>
          <p class="mt-2 text-sm text-gray-600 dark:text-gray-400 pt-4">
            Begin Your Story. Experience your Favourite Sitcoms!
          </p>
        </div>

        <!-- Social Login -->
        <button
        v-if="!showForgotPassword"
          @click="signInWithProvider('google')"
          class="w-full flex items-center justify-center gap-2 py-3 border border-gray-300 dark:border-gray-600 rounded-md
                 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700
                 text-gray-800 dark:text-gray-200 transition"
        >
          <img
            src="https://upload.wikimedia.org/wikipedia/commons/7/7e/Gmail_icon_%282020%29.svg"
            alt="Google"
            class="h-5 w-5"
          />
          Continue with Google
        </button>

        <!-- Divider -->
        <div v-if="!showForgotPassword"  class="flex items-center">
          <span class="flex-grow border-t border-gray-300 dark:border-gray-700"></span>
          <span class="mx-3 text-gray-500 dark:text-gray-400 text-sm">or</span>
          <span class="flex-grow border-t border-gray-300 dark:border-gray-700"></span>
        </div>

                <!-- Forgot Password Form -->
                <form v-if="showForgotPassword" @submit.prevent="handleResetPassword" class="space-y-4">
          <div class="text-center mb-6">
            <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100">Reset Your Password</h2>
            <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Enter your email address and we'll send you a link to reset your password.
            </p>
          </div>
          
          <!-- Email -->
          <div class="space-y-1">
            <label
              for="reset-email"
              class="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >Email</label
            >
            <input
              id="reset-email"
              v-model="resetEmail"
              type="email"
              required
              placeholder="you@example.com"
              :disabled="loading"
              class="w-full px-4 py-2 border rounded-md
                     border-gray-300 dark:border-gray-600
                     bg-white dark:bg-gray-800
                     text-gray-900 dark:text-gray-100
                     placeholder-gray-400 dark:placeholder-gray-500
                     focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <!-- Submit -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 rounded-md bg-primary text-black dark:text-white border border-gray-300 dark:border-gray-600
                   hover:bg-primary-dark transition disabled:opacity-50"
          >
            <svg
              v-if="loading"
              class="animate-spin h-5 w-5 mr-2 inline-block text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              ></circle>
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v8z"
              ></path>
            </svg>
            Send Reset Link
          </button>
          
          <p class="text-center text-sm text-gray-600 dark:text-gray-400 mt-4">
            <a
              href="#"
              @click.prevent="showForgotPassword = false"
              class="font-medium text-primary hover:underline dark:text-primary-light"
            >
              Back to Sign In
            </a>
          </p>
        </form>

        <!-- Email / Password Form -->
        <form v-if="!showForgotPassword" @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Email -->
          <div class="space-y-1">
            <label
              for="email"
              class="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >Email</label
            >
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              placeholder="you@example.com"
              :disabled="loading"
              class="w-full px-4 py-2 border rounded-md
                     border-gray-300 dark:border-gray-600
                     bg-white dark:bg-gray-800
                     text-gray-900 dark:text-gray-100
                     placeholder-gray-400 dark:placeholder-gray-500
                     focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <!-- Username (Sign up only) -->
          <div v-if="!isLogin" class="space-y-1">
            <label
              for="username"
              class="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >Name</label
            >
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              placeholder="johndoe"
              :disabled="loading"
              class="w-full px-4 py-2 border rounded-md
                     border-gray-300 dark:border-gray-600
                     bg-white dark:bg-gray-800
                     text-gray-900 dark:text-gray-100
                     placeholder-gray-400 dark:placeholder-gray-500
                     focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <!-- Password -->
          <div class="space-y-1">
            <div class="flex justify-between items-center">
              <label
                for="password"
                class="block text-sm font-medium text-gray-700 dark:text-gray-300"
                >Password</label
              >
              <a
                href="#"
                @click.prevent="showForgotPassword = true"
                class="text-xs text-primary hover:underline dark:text-white"
                >Forgot?</a
              >
            </div>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              :disabled="loading"
              class="w-full px-4 py-2 border rounded-md
                     border-gray-300 dark:border-gray-600
                     bg-white dark:bg-gray-800
                     text-gray-900 dark:text-gray-100
                     placeholder-gray-400 dark:placeholder-gray-500
                     focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <!-- Confirm Password (Sign up only) -->
          <div v-if="!isLogin" class="space-y-1">
            <label
              for="confirmPassword"
              class="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >Confirm Password</label
            >
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              type="password"
              required
              :disabled="loading"
              class="w-full px-4 py-2 border rounded-md
                     border-gray-300 dark:border-gray-600
                     bg-white dark:bg-gray-800
                     text-gray-900 dark:text-gray-100
                     placeholder-gray-400 dark:placeholder-gray-500
                     focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <!-- Submit -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 rounded-md bg-primary text-black dark:text-white border border-gray-300 dark:border-gray-600
                   hover:bg-primary-dark transition disabled:opacity-50"
          >
            <svg
              v-if="loading"
              class="animate-spin h-5 w-5 mr-2 inline-block text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              ></circle>
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v8z"
              ></path>
            </svg>
            {{ isLogin ? 'Sign In' : 'Create Account' }}
          </button>
        </form>

        <!-- Toggle Sign In / Sign Up -->
        <p v-if="!showForgotPassword" class="text-center text-sm text-gray-600 dark:text-gray-400">
          {{ isLogin
            ? "Don't have an account?"
            : 'Already have an account?' }}
          <a
            href="#"
            @click.prevent="isLogin = !isLogin"
            class="ml-1 font-medium text-primary hover:underline dark:text-primary-light"
            >{{ isLogin ? 'Sign Up' : 'Sign In' }}</a
          >
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
import { useToast } from 'vue-toastification';

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
      form: {
        email: '',
        username: '',
        password: '',
        confirmPassword: '',
      },
      isLogin: true,
      loading: false,
      error: null,
      showForgotPassword: false,
      resetEmail: '',
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
              this.toast.error("Failed to verify your session. Please try logging in again.");
            }
          }
        } else if (event === 'SIGNED_OUT') {
          localStorage.removeItem("supabase_session");
          localStorage.removeItem("user_id");
          localStorage.removeItem("username");
          this.$router.push('/auth');
        }
      }
    );
    this.authSubscription = authListener;
  },
  beforeUnmount() {
    // Clean up the subscription to avoid memory leaks (updated from beforeDestroy)
    if (this.authSubscription) {
      this.authSubscription.subscription.unsubscribe();
    }
  },
  methods: {
    async signInWithProvider(provider) {
      this.loading = true;
      try {
        const { data, error } = await supabase.auth.signInWithOAuth({
          provider: provider, // "google" or "apple"
          options: {
            redirectTo: `${window.location.origin}/auth/callback`,
          },
        });
        if (error) {
          console.error("OAuth error:", error);
          this.toast.error(`Failed to sign in with ${provider}: ${error}`);
        }
      } catch (err) {
        console.error("OAuth exception:", err);
        this.toast.error(`An unexpected error occurred: ${err.message}`);
      } finally {
        this.loading = false;
      }
    },
    
    async handleSubmit() {
      this.loading = true;
      const toast = useToast();
      try {
        if (this.isLogin) {
          await this.login();
        } else {
          await this.register();
        }
      } catch (error) {
        console.error("Form submission error:", error);
        // Use Vue toast if available or fallback to alert
        if (toast) {
          toast.error(error.message || 'An unexpected error occurred');
        } else {
          alert(error.message || 'An unexpected error occurred');
        }
      } finally {
        this.loading = false;
      }
    },
    
    async login() {
      const toast = useToast();
      // Validate form fields first
      if (!this.form.email || !this.form.password) {
        const errorMsg = 'Please provide both email and password';
        if (toast) {
          toast.error(errorMsg);
        } else {
          alert(errorMsg);
        }
        return;
      }

      try {
        const { data, error } = await supabase.auth.signInWithPassword({
          email: this.form.email,
          password: this.form.password
        });
        
        if (error) {
          console.error("Login error:", error);
          if (toast) {
            toast.error(error.message || 'Login failed');
          } else {
            alert(error.message || 'Login failed');
          }
          return;
        }
        
        if (!data || !data.user) {
          const errorMsg = 'Login failed: No user data returned';
          console.error(errorMsg);
          if (toast) {
            toast.error(errorMsg);
          } else {
            alert(errorMsg);
          }
          return;
        }
        
        if (toast) {
          toast.success('Logged in successfully');
        }
        
        // Store user information
        localStorage.setItem('user_id', data.user.id);
        
        // If username is available in user metadata, store it
        if (data.user.user_metadata && data.user.user_metadata.username) {
          localStorage.setItem("username", data.user.user_metadata.username);
        }
        
        this.$router.push('/');
      } catch (err) {
        console.error("Login exception:", err);
        if (toast) {
          toast.error(`Login error: ${err.message || 'Unknown error'}`);
        } else {
          alert(`Login error: ${err.message || 'Unknown error'}`);
        }
      }
    },

    async register() {
      const toast = useToast();
      // Validate form fields first
      if (!this.form.email || !this.form.password || !this.form.username) {
        const errorMsg = 'Please fill out all required fields';
        if (toast) {
          toast.error(errorMsg);
        } else {
          alert(errorMsg);
        }
        return;
      }
      
      // Validate passwords match
      if (this.form.password !== this.form.confirmPassword) {
        const errorMsg = 'Passwords do not match';
        if (this.toast) {
          this.toast.error(errorMsg);
        } else {
          alert(errorMsg);
        }
        return;
      }

      const { data: existing, error: fetchErr } = await supabase
            .from('users')
            .select('id')
            .eq('email', this.form.email)
            .single();

        if (!fetchErr || existing) {
          toast.error('Account already exists for that email. Please Sign In.');
          this.loading = false;
          return;
        }
      
      try {
        // Step 1: Sign up with Supabase Auth
        const { data, error } = await supabase.auth.signUp({
          email: this.form.email,
          password: this.form.password,
          options: {
            data: {
              username: this.form.username
            }
          }
        });
        if (error) {
          console.error('Registration error:', error);
          if (toast) {
            toast.error(error.message || 'Registration failed');
          } else {
            alert(error.message || 'Registration failed');
          }
          return;
        }
        
        if (!data || !data.user) {
          const errorMsg = 'Registration failed: No user data returned';
          console.error(errorMsg);
          if (toast) {
            toast.error(errorMsg);
          } else {
            alert(errorMsg);
          }
          return;
        }
        
        console.log('User registered successfully:', data.user);
        
        // Store user information
        localStorage.setItem('user_id', data.user.id);
        localStorage.setItem("username", this.form.username);
        
        // Check if email confirmation is required
        if (data.session) {
          // User is automatically signed in (email confirmation not required)
          if (toast) {
            toast.success('Account created successfully!');
          } else {
            alert('Account created successfully!');
          }
          
          try {
            // Attempt to verify with backend, but handle failure gracefully
            await fetchApi('auth/verify', {
              method: "POST",
              body: JSON.stringify({ access_token: data.session.access_token }),
            }).then(verifyData => {
              console.log("Backend verification after registration:", verifyData);
              this.$router.push('/');
            }).catch(verifyErr => {
              console.error("Backend verification failed, but proceeding with local registration:", verifyErr);
              this.$router.push('/');
            });
          } catch (verifyErr) {
            console.error("Backend verification exception:", verifyErr);
            // Continue anyway since registration was successful
            this.$router.push('/');
          }
        } else {
          // Email confirmation is required
          if (toast) {
            toast.info('Check your email to confirm your account.');
          } else {
            alert('Please check your email to confirm your account');
          }
          // Stay on the auth page but switch to login view
          this.isLogin = true;
        }
      } catch (error) {
        console.error('Registration exception:', error);
        if (toast) {
          toast.error(error || 'An error occurred during registration');
        } else {
          alert(error || 'An error occurred during registration');
        }
      }
    },

    async handleResetPassword() {
      const toast = useToast();
      this.loading = true;
      
      try {
        // Validate email
        if (!this.resetEmail) {
          if (toast) {
            toast.error('Please enter your email address');
          } else {
            alert('Please enter your email address');
          }
          return;
        }

        const { data: existing, error: fetchErr } = await supabase
            .from('users')
            .select('id')
            .eq('email', this.resetEmail)
            .single();

        if (fetchErr || !existing) {
          toast.error('No account found for that email. Please Sign Up first.');
          this.loading = false;
          return;
        }
        
        // Send password reset email via Supabase
        const { error } = await supabase.auth.resetPasswordForEmail(this.resetEmail, {
          redirectTo: `${window.location.origin}/reset-password/`, // You'll need to create this route
        });
        
        if (error) {
          console.error("Password reset error:", error);
          if (toast) {
            toast.error(error.message || 'Failed to send password reset email');
          } else {
            alert(error.message || 'Failed to send password reset email');
          }
          return;
        }
        
        // Show success message
        if (toast) {
          toast.success('Password reset email sent. Please check your inbox.');
        } else {
          alert('Password reset email sent. Please check your inbox.');
        }
        
        // Reset form and show login
        this.resetEmail = '';
        this.showForgotPassword = false;
        this.isLogin = true;
      } catch (error) {
        console.error("Password reset exception:", error);
        if (toast) {
          toast.error(error.message || 'An error occurred while sending the reset email');
        } else {
          alert(error.message || 'An error occurred while sending the reset email');
        }
      } finally {
        this.loading = false;
      }
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