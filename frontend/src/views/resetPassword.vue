<template>
    <div class="min-h-screen flex flex-col md:flex-row bg-white">
      <!-- Left Side – Reset Password panel -->
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
  
          <!-- Reset Password Form -->
          <form @submit.prevent="handleResetPassword" class="space-y-4">
            <div class="text-center mb-6">
              <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100">Reset Your Password</h2>
              <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Enter your new password below to update your account.
              </p>
            </div>
            
            <!-- Password -->
            <div class="space-y-1">
              <label
                for="new-password"
                class="block text-sm font-medium text-gray-700 dark:text-gray-300"
                >New Password</label
              >
              <input
                id="new-password"
                v-model="form.password"
                type="password"
                required
                placeholder="Enter your new password"
                :disabled="loading"
                class="w-full px-4 py-2 border rounded-md
                       border-gray-300 dark:border-gray-600
                       bg-white dark:bg-gray-800
                       text-gray-900 dark:text-gray-100
                       placeholder-gray-400 dark:placeholder-gray-500
                       focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
  
            <!-- Confirm Password -->
            <div class="space-y-1">
              <label
                for="confirm-password"
                class="block text-sm font-medium text-gray-700 dark:text-gray-300"
                >Confirm Password</label
              >
              <input
                id="confirm-password"
                v-model="form.confirmPassword"
                type="password"
                required
                placeholder="Confirm your new password"
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
              :disabled="loading || !passwordsValid"
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
              Reset Password
            </button>
            
            <div v-if="passwordValidationMessage" class="text-sm text-red-500 dark:text-red-400 mt-2">
              {{ passwordValidationMessage }}
            </div>
            
            <p class="text-center text-sm text-gray-600 dark:text-gray-400 mt-4">
              <a
                href="/auth"
                class="font-medium text-primary hover:underline dark:text-primary-light"
              >
                Back to Sign In
              </a>
            </p>
          </form>
        </div>
      </div>
  
      <!-- Right Side - Immersive Preview (70%) -->
      <div class="w-full md:w-[75%] relative min-h-[60vh] bg-black">
        <!-- Hero Section -->
        <section class="container mx-auto px-4 py-4 md:py-4">
          <div class="text-center space-y-6">
            <Badge variant="outline" class="text-lg py-2 px-4 bg-purple-100 dark:bg-purple-900/20">
              🔐 Account Security
            </Badge>
            <h1 class="text-5xl md:text-6xl font-bold bg-gradient-to-r from-purple-400 to-blue-500 bg-clip-text text-transparent">
              Reset Your Password
            </h1>
            <p class="text-xl md:text-2xl text-white text-muted-foreground max-w-3xl mx-auto">
              Choose a strong password to keep your SitChat adventures secure!
            </p>
          </div>
        </section>
  
        <!-- Password Tips -->
        <section class="bg-muted/50 py-6">
          <div class="container mx-auto px-4">
            <Card class="p-6 bg-white dark:bg-gray-800 rounded-xl shadow">
              <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Password Safety Tips</h3>
              <ul class="space-y-2 text-muted-foreground">
                <li class="flex items-start space-x-2">
                  <div class="mt-1 text-green-500">✓</div>
                  <p>Use at least 8 characters with a mix of letters, numbers, and symbols</p>
                </li>
                <li class="flex items-start space-x-2">
                  <div class="mt-1 text-green-500">✓</div>
                  <p>Avoid using easily guessable information like your name or birthday</p>
                </li>
                <li class="flex items-start space-x-2">
                  <div class="mt-1 text-green-500">✓</div>
                  <p>Use a unique password that you don't use on other websites</p>
                </li>
                <li class="flex items-start space-x-2">
                  <div class="mt-1 text-green-500">✓</div>
                  <p>Consider using a password manager to generate and store strong passwords</p>
                </li>
              </ul>
            </Card>
          </div>
        </section>
  
        <!-- CTA Section -->
        <section class="">
          <div class="mx-auto px-4 text-center">
            <h3 class="text-xl text-muted-foreground mx-auto py-4 max-w-3xl text-white">
              Secure your account and get back to creating amazing stories with your favorite characters!
            </h3>
          </div>
        </section>
      </div>
    </div>
  </template>
  
  <script>
  import { useRouter, useRoute } from 'vue-router'
  import { Badge } from '@/components/ui/badge'
  import { Card } from '@/components/ui/card'
  import { supabase } from '@/composables/useSupabase'
  import { useToast } from 'vue-toastification'
  import { onMounted } from 'vue'
  
  export default {
    name: 'ResetPasswordPage',
    components: {
      Badge,
      Card
    },
    setup() {
      const router = useRouter()
      const route = useRoute()
      const toast = useToast()
      return { router, route, toast }
    },
    data() {
      return {
        form: {
          password: '',
          confirmPassword: ''
        },
        loading: false,
        accessToken: null,
        refreshToken: null,
        recoveryType: false
      }
    },
    computed: {
      passwordsValid() {
        return this.form.password && 
               this.form.password === this.form.confirmPassword && 
               this.form.password.length >= 8
      },
      passwordValidationMessage() {
        if (!this.form.password) return ''
        if (this.form.password.length < 8) return 'Password must be at least 8 characters long'
        if (this.form.confirmPassword && this.form.password !== this.form.confirmPassword) {
          return 'Passwords do not match'
        }
        return ''
      }
    },
    created() {
      // Check if we have a hash fragment containing access token
      this.checkForPasswordResetToken()
    },
    
    // Prevent the default Supabase auth handling
    mounted() {
      // If we have a recovery token in the hash, we need to intercept it
      // before Supabase's auto-handling redirects us
      window.addEventListener('hashchange', this.handleHashChange)
      this.handleHashChange()
    },
    
    beforeUnmount() {
      window.removeEventListener('hashchange', this.handleHashChange)
    },
    methods: {
      handleHashChange() {
        // Check if URL has hash parameters that might be handled by Supabase
        const hash = window.location.hash
        if (hash && hash.includes('type=recovery')) {
          // Prevent the default Supabase handling
          const hashParams = new URLSearchParams(hash.substring(1))
          
          // Extract the tokens and store them
          this.accessToken = hashParams.get('access_token')
          this.refreshToken = hashParams.get('refresh_token')
          
          // Remove the hash to prevent Supabase from auto-handling it
          if (window.history.replaceState) {
            window.history.replaceState(null, null, window.location.pathname)
          }
          
          // Store parameters in local state
          if (this.accessToken) {
            this.recoveryType = true
            this.toast.info('Please enter your new password')
          }
        }
      },
      
      async checkForPasswordResetToken() {
        try {
          // First check if we already have the tokens from handleHashChange
          if (this.accessToken && this.recoveryType) {
            return // We already have what we need
          }
          
          // Extract token from URL hash if present
          const hashParams = new URLSearchParams(window.location.hash.substring(1))
          const accessToken = hashParams.get('access_token')
          const refreshToken = hashParams.get('refresh_token')
          const type = hashParams.get('type')
          
          if (accessToken && type === 'recovery') {
            // Store tokens in component state
            this.accessToken = accessToken
            this.refreshToken = refreshToken
            this.recoveryType = true
            
            // Remove the hash to prevent Supabase from auto-handling it
            if (window.history.replaceState) {
              window.history.replaceState(null, null, window.location.pathname)
            }
            
            this.toast.info('Please enter your new password')
          } else {
            // Check if token is in query params instead (older Supabase versions)
            const queryParams = new URLSearchParams(window.location.search)
            const token = queryParams.get('token')
            
            if (token) {
              this.accessToken = token
              this.toast.info('Please enter your new password')
            } else {
              // No valid token found
              this.toast.error('Invalid or missing password reset token')
              setTimeout(() => {
                this.router.push('/auth')
              }, 2000)
            }
          }
        } catch (error) {
          console.error('Error processing reset token:', error)
          this.toast.error('An error occurred. Please try requesting a new password reset link.')
        }
      },
      
      async handleResetPassword() {
        if (!this.passwordsValid) {
          return
        }
        
        this.loading = true
        
        try {
          // Check if we have a recovery token
          if (this.accessToken && this.recoveryType) {
            // Set the session manually to use this token
            await supabase.auth.setSession({
              access_token: this.accessToken,
              refresh_token: this.refreshToken || ''
            })
            
            // Now update the user password
            const { error } = await supabase.auth.updateUser({
              password: this.form.password
            })
            
            if (error) {
              throw error
            }
          } else if (this.accessToken) {
            // Use the recovery token if available (older method)
            const { error } = await supabase.auth.resetPasswordForEmail(undefined, {
              token: this.accessToken,
              password: this.form.password
            })
            
            if (error) {
              throw error
            }
          } else {
            throw new Error('No valid recovery session found')
          }
          
          // Success! Clear auth state to prevent automatic login
          await supabase.auth.signOut()
          
          this.toast.success('Password has been reset successfully!')
          
          // Redirect to login page after success
          setTimeout(() => {
            this.router.push('/login')
          }, 1500)
        } catch (error) {
          console.error('Password reset error:', error)
          this.toast.error(error.message || 'Failed to reset password. Please try again.')
        } finally {
          this.loading = false
        }
      }
    }
  }
  </script>
  
  <style scoped>
  /* Custom styles for this page */
  .animate-fade-in {
    animation: fadeIn 0.8s ease-out;
  }
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  </style>