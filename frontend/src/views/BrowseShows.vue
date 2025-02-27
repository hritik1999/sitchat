<template>
    <div class="container mx-auto max-w-6xl p-6">
      <div class="space-y-6">
        <div class="flex justify-between items-center">
          <h1 class="text-3xl font-bold tracking-tight">Browse Shows</h1>
          <div class="flex space-x-2">
            <Button v-if="supabase.auth.getUser()" @click="createNewShow" variant="default">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-plus mr-2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
              Create Show
            </Button>
            <Button @click="toggleAuth" variant="outline">
              {{ supabase.auth.getUser() ? 'Sign Out' : 'Sign In' }}
            </Button>
          </div>
        </div>
        
        <!-- Authentication Form -->
        <Card v-if="showAuthForm">
          <CardHeader>
            <CardTitle>{{ isLogin ? 'Sign In' : 'Sign Up' }}</CardTitle>
            <CardDescription>{{ isLogin ? 'Sign in to your account' : 'Create a new account' }}</CardDescription>
          </CardHeader>
          <CardContent>
            <form @submit.prevent="handleAuth" class="space-y-4">
              <div class="space-y-2">
                <Label for="email">Email</Label>
                <Input id="email" v-model="auth.email" type="email" placeholder="your@email.com" required />
              </div>
              
              <div v-if="!isLogin" class="space-y-2">
                <Label for="username">Username</Label>
                <Input id="username" v-model="auth.username" placeholder="username" required />
              </div>
              
              <div class="space-y-2">
                <Label for="password">Password</Label>
                <Input id="password" v-model="auth.password" type="password" required />
              </div>
              
              <div class="flex justify-between">
                <Button @click="isLogin = !isLogin" type="button" variant="ghost">
                  {{ isLogin ? 'Need an account? Sign Up' : 'Already have an account? Sign In' }}
                </Button>
                <Button type="submit" :disabled="isLoading">
                  {{ isLoading ? 'Processing...' : (isLogin ? 'Sign In' : 'Sign Up') }}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
        
        <!-- Loading State -->
        <div v-if="isLoading" class="flex justify-center items-center p-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
        
        <!-- Shows Grid -->
        <div v-else-if="shows.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card v-for="show in shows" :key="show.id" class="overflow-hidden flex flex-col">
            <CardHeader class="pb-2">
              <CardTitle>{{ show.name }}</CardTitle>
              <CardDescription class="line-clamp-2">{{ show.description }}</CardDescription>
            </CardHeader>
            
            <CardContent class="flex-grow">
              <div v-if="show.image_url" class="w-full h-40 bg-muted rounded-md mb-4 overflow-hidden">
                <img :src="show.image_url" alt="Show thumbnail" class="w-full h-full object-cover" />
              </div>
              <div v-else class="w-full h-40 bg-muted rounded-md mb-4 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="text-muted-foreground/40"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"></rect><circle cx="9" cy="9" r="2"></circle><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"></path></svg>
              </div>
              
              <div class="text-sm">
                <p><span class="font-medium">Creator:</span> {{ show.users?.username || 'Unknown' }}</p>
                <p><span class="font-medium">Characters:</span> {{ getCharacterNames(show.characters) }}</p>
              </div>
            </CardContent>
            
            <CardFooter class="pt-0">
              <Button @click="selectShow(show)" class="w-full">View Episodes</Button>
            </CardFooter>
          </Card>
        </div>
        
        <!-- No Shows State -->
        <Card v-else>
          <CardHeader>
            <CardTitle>No Shows Found</CardTitle>
            <CardDescription>There are no shows available yet.</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Be the first to create a show! Sign in and click the "Create Show" button above.</p>
          </CardContent>
        </Card>
        
        <!-- Episodes Dialog -->
        <Dialog :open="!!selectedShow" @update:open="selectedShow = null">
          <DialogContent class="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>{{ selectedShow?.name }} Episodes</DialogTitle>
              <DialogDescription>Select an episode to start playing</DialogDescription>
            </DialogHeader>
            
            <div v-if="loadingEpisodes" class="flex justify-center items-center p-12">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
            
            <div v-else-if="episodes.length === 0" class="text-center py-8">
              <p class="text-muted-foreground">No episodes available yet.</p>
              <Button v-if="canCreateEpisode" @click="createNewEpisode" class="mt-4">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-plus mr-2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                Create Episode
              </Button>
            </div>
            
            <div v-else class="space-y-4 max-h-[400px] overflow-y-auto py-4">
              <Card v-for="episode in episodes" :key="episode.id" class="cursor-pointer hover:bg-accent/30" @click="startEpisode(episode)">
                <CardHeader class="py-4">
                  <CardTitle>{{ episode.name }}</CardTitle>
                  <CardDescription class="line-clamp-2">{{ episode.description }}</CardDescription>
                </CardHeader>
                <CardContent class="pb-4 pt-0">
                  <p class="text-sm"><span class="font-medium">Background:</span> {{ truncate(episode.background, 100) }}</p>
                  <p class="text-sm mt-2"><span class="font-medium">Objectives:</span> {{ getObjectivesCount(episode.plot_objectives) }}</p>
                </CardContent>
              </Card>
            </div>
            
            <DialogFooter>
              <Button @click="selectedShow = null" variant="outline">Cancel</Button>
              <Button v-if="canCreateEpisode" @click="createNewEpisode">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-plus mr-2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                Create Episode
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
        
        <!-- Create/Edit Show Dialog -->
        <Dialog :open="showEditDialog" @update:open="closeEditDialog">
          <DialogContent class="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>{{ editingShow ? 'Edit Show' : 'Create New Show' }}</DialogTitle>
              <DialogDescription>
                {{ editingShow ? 'Update your show details' : 'Fill in the details to create a new show' }}
              </DialogDescription>
            </DialogHeader>
            
            <form @submit.prevent="saveShow" class="space-y-4">
              <div class="space-y-2">
                <Label for="show-name">Show Name</Label>
                <Input id="show-name" v-model="showForm.name" placeholder="e.g. Friends" required />
              </div>
              
              <div class="space-y-2">
                <Label for="show-description">Description</Label>
                <Textarea id="show-description" v-model="showForm.description" placeholder="Brief description of the show" />
              </div>
              
              <div class="space-y-2">
                <Label for="show-image">Image URL (optional)</Label>
                <Input id="show-image" v-model="showForm.image_url" placeholder="https://example.com/image.jpg" />
              </div>
              
              <div class="space-y-2">
                <Label for="show-relations">Character Relationships</Label>
                <Textarea id="show-relations" v-model="showForm.relations" placeholder="Describe relationships between characters" />
              </div>
              
              <div class="space-y-2">
                <div class="flex justify-between items-center">
                  <Label>Characters</Label>
                  <Button @click="addCharacter" type="button" variant="outline" size="sm">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-plus mr-2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                    Add Character
                  </Button>
                </div>
                
                <div v-for="(character, name) in showForm.characters" :key="name" class="p-4 border rounded-lg relative space-y-2 mt-2">
                  <Button type="button" variant="destructive" size="icon" class="absolute right-2 top-2" @click="removeCharacter(name)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-x"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                    <span class="sr-only">Remove</span>
                  </Button>
                  
                  <div class="space-y-2">
                    <Label :for="`character-name-${name}`">Character Name</Label>
                    <Input :id="`character-name-${name}`" :value="name" @input="updateCharacterName(name, $event)" placeholder="Character name" />
                  </div>
                  
                  <div class="space-y-2">
                    <Label :for="`character-desc-${name}`">Description</Label>
                    <Textarea :id="`character-desc-${name}`" v-model="showForm.characters[name]" placeholder="Character description and personality" />
                  </div>
                </div>
              </div>
            </form>
            
            <DialogFooter>
              <Button @click="closeEditDialog" variant="outline">Cancel</Button>
              <Button @click="saveShow" :disabled="isSaving">
                {{ isSaving ? 'Saving...' : 'Save Show' }}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
        
        <!-- Create Episode Dialog -->
        <Dialog :open="showEpisodeDialog" @update:open="closeEpisodeDialog">
          <DialogContent class="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>Create New Episode</DialogTitle>
              <DialogDescription>
                Create a new episode for "{{ selectedShow?.name }}"
              </DialogDescription>
            </DialogHeader>
            
            <form @submit.prevent="saveEpisode" class="space-y-4">
              <div class="space-y-2">
                <Label for="episode-name">Episode Name</Label>
                <Input id="episode-name" v-model="episodeForm.name" placeholder="e.g. The One With the Reunion" required />
              </div>
              
              <div class="space-y-2">
                <Label for="episode-description">Description</Label>
                <Textarea id="episode-description" v-model="episodeForm.description" placeholder="Brief description of the episode" />
              </div>
              
              <div class="space-y-2">
                <Label for="episode-background">Scene Background</Label>
                <Textarea id="episode-background" v-model="episodeForm.background" placeholder="The initial scene setup" />
              </div>
              
              <div class="space-y-2">
                <div class="flex justify-between items-center">
                  <Label>Plot Objectives</Label>
                  <Button @click="addObjective" type="button" variant="outline" size="sm">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-plus mr-2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                    Add Objective
                  </Button>
                </div>
                
                <div v-for="(objective, index) in episodeForm.plot_objectives" :key="index" class="p-4 border rounded-lg relative mt-2">
                  <Button type="button" variant="destructive" size="icon" class="absolute right-2 top-2" @click="removeObjective(index)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-x"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                    <span class="sr-only">Remove</span>
                  </Button>
                  
                  <div class="space-y-2">
                    <Label :for="`objective-${index}`">Objective {{ index + 1 }}</Label>
                    <Textarea :id="`objective-${index}`" v-model="episodeForm.plot_objectives[index]" placeholder="Describe what needs to happen in this stage" />
                  </div>
                </div>
              </div>
            </form>
            
            <DialogFooter>
              <Button @click="closeEpisodeDialog" variant="outline">Cancel</Button>
              <Button @click="saveEpisode" :disabled="isSaving">
                {{ isSaving ? 'Saving...' : 'Save Episode' }}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
        
        <!-- Player Dialog -->
        <Dialog :open="showPlayerDialog" @update:open="closePlayerDialog">
          <DialogContent class="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>Start Episode</DialogTitle>
              <DialogDescription>
                Enter your character details to begin "{{ selectedEpisode?.name }}"
              </DialogDescription>
            </DialogHeader>
            
            <form @submit.prevent="startPlaying" class="space-y-4">
              <div class="space-y-2">
                <Label for="player-name">Your Character Name</Label>
                <Input id="player-name" v-model="playerForm.player_name" placeholder="Your character's name" required />
              </div>
              
              <div class="space-y-2">
                <Label for="player-description">Character Description</Label>
                <Textarea id="player-description" v-model="playerForm.player_description" placeholder="Brief description of your character" />
              </div>
            </form>
            
            <DialogFooter>
              <Button @click="closePlayerDialog" variant="outline">Cancel</Button>
              <Button @click="startPlaying" :disabled="isStarting">
                {{ isStarting ? 'Starting...' : 'Start Episode' }}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { useToast } from 'vue-toastification';
  import { createClient } from '@supabase/supabase-js';
  import {
    Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle
  } from '@/components/ui/card';
  import {
    Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle
  } from '@/components/ui/dialog';
  import { Button } from '@/components/ui/button';
  import { Input } from '@/components/ui/input';
  import { Textarea } from '@/components/ui/textarea';
  import { Label } from '@/components/ui/label';
  
  // Initialize Supabase client
  const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
  const supabaseKey = import.meta.env.VITE_SUPABASE_KEY;
  const supabase = createClient(supabaseUrl, supabaseKey);
  
  // Router and toast
  const router = useRouter();
  const toast = useToast();
  
  // Data
  const shows = ref([]);
  const episodes = ref([]);
  const isLoading = ref(false);
  const loadingEpisodes = ref(false);
  const selectedShow = ref(null);
  const selectedEpisode = ref(null);
  const isSaving = ref(false);
  const isStarting = ref(false);
  
  // Auth state
  const showAuthForm = ref(false);
  const isLogin = ref(true);
  const auth = ref({
    email: '',
    password: '',
    username: ''
  });
  
  // Show form
  const showEditDialog = ref(false);
  const editingShow = ref(null);
  const showForm = ref({
    name: '',
    description: '',
    characters: {},
    relations: '',
    image_url: ''
  });
  
  // Episode form
  const showEpisodeDialog = ref(false);
  const episodeForm = ref({
    name: '',
    description: '',
    background: '',
    plot_objectives: []
  });
  
  // Player form
  const showPlayerDialog = ref(false);
  const playerForm = ref({
    player_name: '',
    player_description: ''
  });
  
  // Computed
  const canCreateEpisode = computed(() => {
    if (!selectedShow.value || !supabase.auth.getUser()) return false;
    
    const user = supabase.auth.getUser();
    return selectedShow.value.creator_id === user.id;
  });
  
  // Lifecycle
  onMounted(() => {
    loadShows();
  });
  
  // Methods
  async function loadShows() {
    isLoading.value = true;
    
    try {
      const { data, error } = await supabase
        .from('shows')
        .select('*, users(username)')
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      
      shows.value = data || [];
    } catch (error) {
      console.error('Error loading shows:', error);
      toast.error('Failed to load shows');
    } finally {
      isLoading.value = false;
    }
  }
  
  async function selectShow(show) {
    selectedShow.value = show;
    loadingEpisodes.value = true;
    
    try {
      const { data, error } = await supabase
        .from('episodes')
        .select('*')
        .eq('show_id', show.id)
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      
      episodes.value = data || [];
    } catch (error) {
      console.error('Error loading episodes:', error);
      toast.error('Failed to load episodes');
    } finally {
      loadingEpisodes.value = false;
    }
  }
  
  function startEpisode(episode) {
    selectedEpisode.value = episode;
    showPlayerDialog.value = true;
  }
  
  async function startPlaying() {
    if (!selectedEpisode.value) return;
    
    isStarting.value = true;
    
    try {
      // Create a chat/session in the database
      const response = await fetch('http://localhost:5001/api/chats', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${supabase.auth.getSession()?.access_token || ''}`
        },
        body: JSON.stringify({
          episode_id: selectedEpisode.value.id,
          player_name: playerForm.value.player_name,
          player_description: playerForm.value.player_description
        })
      });
      
      const data = await response.json();
      
      if (!response.ok) throw new Error(data.error || 'Failed to start episode');
      
      // Navigate to the chat session
      router.push(`/chat/${data.chat_id}`);
    } catch (error) {
      console.error('Error starting episode:', error);
      toast.error('Failed to start episode: ' + error.message);
    } finally {
      isStarting.value = false;
      closePlayerDialog();
    }
  }
  
  function toggleAuth() {
    if (supabase.auth.getUser()) {
      // Sign out
      supabase.auth.signOut();
      toast.success('Signed out successfully');
      loadShows(); // Reload shows to reflect auth state
    } else {
      // Show auth form
      showAuthForm.value = true;
    }
  }
  
  async function handleAuth() {
    isLoading.value = true;
    
    try {
      if (isLogin.value) {
        // Sign in
        const { data, error } = await supabase.auth.signInWithPassword({
          email: auth.value.email,
          password: auth.value.password
        });
        
        if (error) throw error;
        
        toast.success('Signed in successfully');
      } else {
        // Sign up
        const { data, error } = await supabase.auth.signUp({
          email: auth.value.email,
          password: auth.value.password,
          options: {
            data: {
              username: auth.value.username
            }
          }
        });
        
        if (error) throw error;
        
        // Create user profile
        const { error: profileError } = await supabase
          .from('users')
          .insert([
            { 
              id: data.user.id, 
              username: auth.value.username 
            }
          ]);
        
        if (profileError) throw profileError;
        
        toast.success('Account created successfully! You can now sign in.');
        isLogin.value = true;
      }
      
      // Reset form and hide it
      auth.value = { email: '', password: '', username: '' };
      showAuthForm.value = false;
      
      // Reload shows to reflect auth state
      loadShows();
      
    } catch (error) {
      console.error('Authentication error:', error);
      toast.error(error.message || 'Authentication failed');
    } finally {
      isLoading.value = false;
    }
  }
  
  function createNewShow() {
    editingShow.value = null;
    showForm.value = {
      name: '',
      description: '',
      characters: {
        'Character 1': 'Description of character 1'
      },
      relations: '',
      image_url: ''
    };
    
    showEditDialog.value = true;
  }
  
  function createNewEpisode() {
    if (!selectedShow.value) return;
    
    episodeForm.value = {
      name: `Episode ${episodes.value.length + 1}`,
      description: '',
      background: '',
      plot_objectives: ['First objective']
    };
    
    showEpisodeDialog.value = true;
  }
  
  async function saveShow() {
    if (!supabase.auth.getUser()) {
      toast.error('You must be signed in to create or edit shows');
      return;
    }
    
    isSaving.value = true;
    
    try {
      // Process characters object to ensure it's valid
      const characters = {};
      Object.entries(showForm.value.characters).forEach(([name, desc]) => {
        if (name.trim()) {
          characters[name.trim()] = desc;
        }
      });
      
      if (Object.keys(characters).length === 0) {
        throw new Error('You must add at least one character');
      }
      
      const formData = {
        name: showForm.value.name,
        description: showForm.value.description,
        characters,
        relations: showForm.value.relations,
        image_url: showForm.value.image_url
      };
      
      let result;
      
      if (editingShow.value) {
        // Update existing show
        const { data, error } = await supabase
          .from('shows')
          .update(formData)
          .eq('id', editingShow.value.id)
          .select();
        
        if (error) throw error;
        result = data[0];
        toast.success('Show updated successfully');
      } else {
        // Create new show
        const { data, error } = await supabase
          .from('shows')
          .insert([{
            ...formData,
            creator_id: supabase.auth.getUser().id
          }])
          .select();
        
        if (error) throw error;
        result = data[0];
        toast.success('Show created successfully');
      }
      
      // Reload shows and close dialog
      await loadShows();
      showEditDialog.value = false;
      
    } catch (error) {
      console.error('Error saving show:', error);
      toast.error(error.message || 'Failed to save show');
    } finally {
      isSaving.value = false;
    }
  }
  
  async function saveEpisode() {
    if (!selectedShow.value || !supabase.auth.getUser()) {
      toast.error('You must be signed in to create episodes');
      return;
    }
    
    if (episodeForm.value.plot_objectives.length === 0) {
      toast.error('You must add at least one plot objective');
      return;
    }
    
    isSaving.value = true;
    
    try {
      const formData = {
        show_id: selectedShow.value.id,
        creator_id: supabase.auth.getUser().id,
        name: episodeForm.value.name,
        description: episodeForm.value.description,
        background: episodeForm.value.background,
        plot_objectives: episodeForm.value.plot_objectives
      };
      
      const { data, error } = await supabase
        .from('episodes')
        .insert([formData])
        .select();
      
      if (error) throw error;
      
      // Add to episodes list
      episodes.value.unshift(data[0]);
      toast.success('Episode created successfully');
      
      // Close dialog
      showEpisodeDialog.value = false;
      
    } catch (error) {
      console.error('Error saving episode:', error);
      toast.error(error.message || 'Failed to save episode');
    } finally {
      isSaving.value = false;
    }
  }
  
  function addCharacter() {
    const newName = `Character ${Object.keys(showForm.value.characters).length + 1}`;
    showForm.value.characters[newName] = '';
  }
  
  function removeCharacter(name) {
    const updatedCharacters = { ...showForm.value.characters };
    delete updatedCharacters[name];
    showForm.value.characters = updatedCharacters;
  }
  
  function updateCharacterName(oldName, event) {
    const newName = event.target.value;
    if (newName === oldName) return;
    
    // Create a new characters object with the updated key
    const updatedCharacters = {};
    Object.entries(showForm.value.characters).forEach(([name, desc]) => {
      if (name === oldName) {
        updatedCharacters[newName] = desc;
      } else {
        updatedCharacters[name] = desc;
      }
    });
    
    showForm.value.characters = updatedCharacters;
  }
  
  function addObjective() {
    episodeForm.value.plot_objectives.push('');
  }
  
  function removeObjective(index) {
    episodeForm.value.plot_objectives.splice(index, 1);
  }
  
  function closeEditDialog() {
    showEditDialog.value = false;
    editingShow.value = null;
  }
  
  function closeEpisodeDialog() {
    showEpisodeDialog.value = false;
  }
  
  function closePlayerDialog() {
    showPlayerDialog.value = false;
    selectedEpisode.value = null;
  }
  
  // Utility functions
  function getCharacterNames(characters) {
    if (!characters) return 'None';
    
    try {
      const chars = typeof characters === 'string' ? JSON.parse(characters) : characters;
      return Object.keys(chars).join(', ');
    } catch (e) {
      return 'Error parsing characters';
    }
  }
  
  function getObjectivesCount(objectives) {
    if (!objectives) return 'None';
    
    try {
      const objs = typeof objectives === 'string' ? JSON.parse(objectives) : objectives;
      return `${objs.length} objectives`;
    } catch (e) {
      return 'Error parsing objectives';
    }
  }
  
  function truncate(text, length) {
    if (!text) return '';
    return text.length > length ? text.substring(0, length) + '...' : text;
  }
  </script>