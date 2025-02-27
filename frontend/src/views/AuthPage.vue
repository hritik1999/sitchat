<template>
    <div class="container mx-auto py-10 px-4">
      <div class="mx-auto max-w-md space-y-6">
        <div class="space-y-2 text-center">
          <h1 class="text-3xl font-bold">{{ isLogin ? 'Welcome Back' : 'Create Account' }}</h1>
          <p class="text-muted-foreground">
            {{ isLogin ? 'Enter your credentials to sign in' : 'Enter your information to create an account' }}
          </p>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle>{{ isLogin ? 'Sign In' : 'Sign Up' }}</CardTitle>
            <CardDescription>
              {{ isLogin ? 'Enter your email and password to sign in to your account' : 'Create a new account' }}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form @submit.prevent="handleSubmit" class="space-y-4">
              <div class="space-y-2">
                <Label for="email">Email</Label>
                <Input 
                  id="email" 
                  v-model="form.email" 
                  type="email" 
                  placeholder="name@example.com" 
                  required
                  :disabled="loading"
                />
              </div>
              
              <div v-if="!isLogin" class="space-y-2">
                <Label for="username">Username</Label>
                <Input 
                  id="username" 
                  v-model="form.username" 
                  placeholder="johndoe" 
                  required
                  :disabled="loading"
                />
              </div>
              
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <Label for="password">Password</Label>
                  <a href="#" class="text-xs text-muted-foreground underline-offset-4 hover:underline">
                    Forgot password?
                  </a>
                </div>
                <Input 
                  id="password" 
                  v-model="form.password" 
                  type="password" 
                  required
                  :disabled="loading"
                />
              </div>
              
              <div v-if="!isLogin" class="space-y-2">
                <Label for="confirmPassword">Confirm Password</Label>
                <Input 
                  id="confirmPassword" 
                  v-model="form.confirmPassword" 
                  type="password" 
                  required
                  :disabled="loading"
                />
              </div>
              
              <Button type="submit" class="w-full" :disabled="loading">
                <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" />
                {{ isLogin ? 'Sign In' : 'Create Account' }}
              </Button>
            </form>
          </CardContent>
          <CardFooter>
            <div class="text-center w-full text-sm">
              {{ isLogin ? "Don't have an account?" : "Already have an account?" }}
              <a 
                href="#" 
                @click.prevent="isLogin = !isLogin" 
                class="font-medium text-primary underline-offset-4 hover:underline"
              >
                {{ isLogin ? 'Sign Up' : 'Sign In' }}
              </a>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { useSupabase } from '@/composables/useSupabase'
  import { useToast } from 'vue-toastification'
  import { Loader2 } from 'lucide-vue-next'
  import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
  import { Button } from '@/components/ui/button'
  import { Input } from '@/components/ui/input'
  import { Label } from '@/components/ui/label'
  
  const router = useRouter()
  const route = useRoute()
  const { supabase } = useSupabase()
  const toast = useToast()
  
  const isLogin = ref(true)
  const loading = ref(false)
  const form = ref({
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  })
  
  // Handle form submission
  async function handleSubmit() {
    loading.value = true
    
    try {
      if (isLogin.value) {
        await login()
      } else {
        await register()
      }
    } catch (error) {
      toast.error(error.message || 'An error occurred')
    } finally {
      loading.value = false
    }
  }
  
  // Log in user
  async function login() {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: form.value.email,
      password: form.value.password
    })
    
    if (error) throw error
    
    toast.success('Logged in successfully')
    router.push(route.query.redirect || '/')
  }
  
  // Register new user
  async function register() {
    // Validate passwords match
    if (form.value.password !== form.value.confirmPassword) {
      throw new Error('Passwords do not match')
    }
    
    // Register with Supabase Auth
    const { data: authData, error: authError } = await supabase.auth.signUp({
      email: form.value.email,
      password: form.value.password
    })
    
    if (authError) throw authError
    
    if (!authData?.user?.id) {
      throw new Error('Failed to create account')
    }
    
    // Create user profile in the database
    const { error: profileError } = await supabase
      .from('users')
      .insert([
        {
          id: authData.user.id,
          username: form.value.username,
          email: form.value.email
        }
      ])
    
    if (profileError) {
      // Attempt to clean up the auth account if profile creation fails
      await supabase.auth.signOut()
      throw profileError
    }
    
    toast.success('Account created successfully!')
    router.push('/')
  }
  </script>