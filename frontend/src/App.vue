<template>
  <div class="container mx-auto max-w-4xl p-6">
    <div v-if="!sessionId" class="space-y-8">
      <div class="space-y-2">
        <h1 class="text-3xl font-bold tracking-tight">Create Interactive Story</h1>
        <p class="text-muted-foreground">Set up your interactive narrative experience</p>
      </div>
      
      <!-- Basic Settings -->
      <Card>
        <CardHeader>
          <CardTitle>Story Settings</CardTitle>
          <CardDescription>Configure the basic parameters for your story</CardDescription>
        </CardHeader>
        <CardContent>
          <div class="grid gap-4">
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-2">
                <Label for="show">Show Name</Label>
                <Input id="show" v-model="setup.show" placeholder="e.g. Friends"/>
              </div>
              <div class="space-y-2">
                <Label for="player_name">Player Name</Label>
                <Input id="player_name" v-model="setup.player_name" placeholder="Your character's name"/>
              </div>
            </div>
            
            <div class="space-y-2">
              <Label for="description">Description</Label>
              <Textarea id="description" v-model="setup.description" placeholder="Brief description of the story setting" />
            </div>
            
            <div class="space-y-2">
              <Label for="background">Background</Label>
              <Textarea id="background" v-model="setup.background" placeholder="The initial scene setup" />
            </div>
            
            <div class="space-y-2">
              <Label for="player_description">Player Description</Label>
              <Textarea id="player_description" v-model="setup.player_description" placeholder="Description of your character" />
            </div>
            
            <div class="space-y-2">
              <Label for="relations">Character Relationships</Label>
              <Textarea id="relations" v-model="setup.relations" placeholder="Describe relationships between characters" />
            </div>
          </div>
        </CardContent>
      </Card>
      
      <!-- Actors -->
      <Card>
        <CardHeader>
          <CardTitle>Actors</CardTitle>
          <CardDescription>Configure the characters in your story</CardDescription>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div v-for="(actor, index) in actors" :key="index" class="p-4 border rounded-lg relative space-y-2">
              <Button variant="destructive" size="icon" class="absolute right-2 top-2" @click="removeActor(index)">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-x"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                <span class="sr-only">Remove</span>
              </Button>
              
              <div class="space-y-2">
                <Label :for="`actor_name_${index}`">Actor Name</Label>
                <Input :id="`actor_name_${index}`" v-model="actor.name" placeholder="Character name" />
              </div>
              
              <div class="space-y-2">
                <Label :for="`actor_desc_${index}`">Description</Label>
                <Textarea :id="`actor_desc_${index}`" v-model="actor.description" placeholder="Character description and personality" />
              </div>
            </div>
            
            <Button variant="outline" @click="addActor" class="w-full">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-plus mr-2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
              Add Actor
            </Button>
          </div>
        </CardContent>
      </Card>
      
      <!-- Plot Objectives -->
      <Card>
        <CardHeader>
          <CardTitle>Plot Objectives</CardTitle>
          <CardDescription>Define the goals that drive your narrative forward</CardDescription>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div v-for="(objective, index) in objectives" :key="index" class="p-4 border rounded-lg relative">
              <Button variant="destructive" size="icon" class="absolute right-2 top-2" @click="removeObjective(index)">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-x"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                <span class="sr-only">Remove</span>
              </Button>
              
              <div class="space-y-2">
                <Label :for="`objective_${index}`">Objective {{ index + 1 }}</Label>
                <Textarea :id="`objective_${index}`" v-model="objectives[index]" placeholder="Describe what needs to happen in this stage" />
              </div>
            </div>
            
            <Button variant="outline" @click="addObjective" class="w-full">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-plus mr-2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
              Add Objective
            </Button>
          </div>
        </CardContent>
        <CardFooter>
          <Button @click="createStage" size="lg" class="w-full">
            Create Story
          </Button>
        </CardFooter>
      </Card>
    </div>
    
    <!-- Story View -->
    <div v-else class="space-y-6">
      <div class="flex justify-between items-center">
        <h1 class="text-3xl font-bold tracking-tight">Interactive Story</h1>
        <Badge v-if="stageState.completed" variant="success">Completed</Badge>
        <Badge v-else>In Progress</Badge>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Objective {{ stageState.current_objective_index + 1 }} of {{ stageState.total_objectives }}</CardTitle>
          <CardDescription>{{ stageState.current_objective }}</CardDescription>
        </CardHeader>
        <CardContent>
          <Progress :value="progressPercentage" class="mb-4" />
          
          <div class="h-96 overflow-y-auto p-4 bg-muted rounded-md space-y-3 mb-4">
            <div v-for="(line, index) in dialogueHistory" :key="index" 
                 class="p-3 rounded-lg" 
                 :class="{
                   'bg-primary/10': line.type === 'actor_dialogue',
                   'bg-secondary/20 italic': line.type === 'narration',
                   'bg-accent/20 ml-auto max-w-[80%]': line.type === 'player_input',
                   'bg-muted-foreground/10': line.type === 'other'
                 }">
              <div class="font-semibold">{{ line.role }}</div>
              <div>{{ line.content }}</div>
            </div>
          </div>
          
          <div v-if="!stageState.completed">
            <div class="space-y-2">
              <Label for="player-input">Your Response</Label>
              <Textarea 
                id="player-input" 
                v-model="playerInput" 
                placeholder="Type your response or continue..."
                rows="3"
              />
            </div>
          </div>
        </CardContent>
        <CardFooter class="flex justify-between gap-2">
          <Button v-if="!stageState.completed" @click="sendPlayerInput" :disabled="!playerInput.trim()" variant="default" size="lg" class="flex-1">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-send mr-2"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            Send
          </Button>
          <Button v-if="!stageState.completed" @click="advanceTurn" variant="secondary" size="lg" class="flex-1">
            Continue
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-arrow-right ml-2"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
          </Button>
          <Button v-if="stageState.completed" @click="resetStory" variant="default" size="lg" class="w-full">
            Start New Story
          </Button>
        </CardFooter>
      </Card>
      
      <Alert v-if="stageState.completed" variant="success">
        <AlertTitle>Story Complete</AlertTitle>
        <AlertDescription>
          All objectives have been fulfilled. You can start a new story or review the dialogue above.
        </AlertDescription>
      </Alert>
    </div>
  </div>
</template>

<script>
import io from 'socket.io-client';
import { Input } from '@/components/ui/input'
import {Card,CardContent,CardDescription,CardFooter,CardHeader,CardTitle,} from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Label } from '@/components/ui/label'
import { useColorMode } from '@vueuse/core'
import { useToast } from 'vue-toastification';
export default {
  components: {
    Card, 
    CardHeader, 
    CardTitle, 
    CardDescription, 
    CardContent,
    CardFooter,
    Input,
    Label,
    Textarea,
    Button,
    Progress,
    Badge,
    Alert,
    AlertTitle,
    AlertDescription
  },
  
  data() {
    return {
      socket: null,
      apiBaseUrl: 'http://localhost:5001/api',
      sessionId: null,
      playerInput: '',
      // mode: useColorMode('dark'),
      dialogueHistory: [],
      stageState: {
        current_objective_index: 0,
        total_objectives: 0,
        current_objective: '',
        plot_failure_reason: '',
        completed: false
      },
      setup: {
        show: 'Friends',
        description: 'A show about 6 friends and their day to day life in New York.',
        background: 'Chandler, Joey and Ross are sitting in Central Perk waiting for their coffee after a long day at work!',
        player_name: 'Player',
        player_description: 'A person sharing a table with them due to over capacity in the cafe.',
        relations: 'Chandler is best friends with Joey, and Ross is Chandler\'s roommate.'
      },
      actors: [
        { name: 'Chandler', description: 'A sarcastic and witty character from a famous TV show.' },
        { name: 'Joey', description: 'A charming and sometimes clueless friend.' },
        { name: 'Ross', description: 'A caring friend who often finds himself in awkward situations.' }
      ],
      objectives: [
        'Ross tells a boring story about dinosaur and chandler starts roasting him about it.',
        'Ross becomes enraged at chandler for joking about dinosours.',
        'Joey stops chandler from making anymore jokes and chandler stops. Also joey calms ross down.',
        'Ross and joey make chandler pay the coffee bill for making stupid jokes.'
      ]
    };
  },
  
  computed: {
    progressPercentage() {
      if (this.stageState.total_objectives === 0) return 0;
      return (this.stageState.current_objective_index / this.stageState.total_objectives) * 100;
    }
  },
  
  created() {
    this.setupSocketConnection();
  },
  
  beforeUnmount() {
    if (this.socket) {
      this.socket.disconnect();
    }
  },
  
  methods: {
    setupSocketConnection() {
  // Make sure you've imported io correctly
  this.socket = io("http://localhost:5001", {
    transports: ['polling', 'websocket'],  // Try polling first, then websocket
    reconnectionDelayMax: 10000,
    reconnectionAttempts: 10
  });
  
  this.socket.on('connect', () => {
    console.log('Connected to Socket.IO server with ID:', this.socket.id);
    console.log('Transport used:', this.socket.io.engine.transport.name);
  });
  
  this.socket.on('connect_error', (error) => {
    console.error('Connection error:', error);
  });
      
      this.socket.on('status', (data) => {
        console.log('Status:', data.message);
      });
      
      this.socket.on('error', (data) => {
        console.error('Error:', data.message);
        this.$toast.error(data.message);
      });
      
      this.socket.on('objective_status', (data) => {
        if (data.completed) {
          this.$toast.success('Objective completed: ' + data.message);
        } else {
          console.log('Objective not yet complete:', data.message);
        }
      });
    },
    
    async createStage() {
      try {
        // Transform actors array to object format needed by API
        const actorsData = {};
        this.actors.forEach(actor => {
          actorsData[actor.name] = actor.description;
        });
        
        const response = await fetch(`${this.apiBaseUrl}/stage`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            show: this.setup.show,
            description: this.setup.description,
            background: this.setup.background,
            actors_data: actorsData,
            relations: this.setup.relations,
            player_name: this.setup.player_name,
            player_description: this.setup.player_description,
            plot_objectives: this.objectives
          })
        });
        
        const data = await response.json();
        
        if (response.ok) {
          this.sessionId = data.session_id;
          this.stageState = data.state;
          this.dialogueHistory = data.state.dialogue_history || [];
          
          // Join the Socket.IO room for this session
          this.socket.emit('join_session', { session_id: this.sessionId });
          
          // Advance the first turn automatically
          this.advanceTurn();
          this.toast.success('Story created successfully!');
        } else {
          this.toast.error('Error creating stage: ' + (data.error || 'Unknown error'));
        }
      } catch (error) {
        console.error('Error creating stage:', error);
        this.toast.error('Error creating stage: ' + error.message);
      }
    },
    
    async advanceTurn() {
      if (this.stageState.completed) return;
      
      try {
        const response = await fetch(`${this.apiBaseUrl}/stage/${this.sessionId}/advance`, {
          method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
          this.stageState = data.state;
        } else {
          this.toast.error('Error advancing turn: ' + (data.error || 'Unknown error'));
        }
      } catch (error) {
        console.error('Error advancing turn:', error);
        this.toast.error('Error advancing turn: ' + error.message);
      }
    },
    
    async sendPlayerInput() {
      if (!this.playerInput.trim()) return;
      
      try {
        const response = await fetch(`${this.apiBaseUrl}/stage/${this.sessionId}/interrupt`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            player_input: this.playerInput
          })
        });
        
        const data = await response.json();
        
        if (response.ok) {
          this.stageState = data.state;
          this.playerInput = ''; // Clear input after sending
        } else {
          this.$toast.error('Error sending input: ' + (data.error || 'Unknown error'));
        }
      } catch (error) {
        console.error('Error sending player input:', error);
        this.toast.error('Error sending input: ' + error.message);
      }
    },
    
    resetStory() {
      this.sessionId = null;
      this.dialogueHistory = [];
      this.playerInput = '';
      this.stageState = {
        current_objective_index: 0,
        total_objectives: 0,
        current_objective: '',
        plot_failure_reason: '',
        completed: false
      };
      this.toast.info('Started a new story');
    },
    
    addActor() {
      this.actors.push({ name: '', description: '' });
    },
    
    removeActor(index) {
      this.actors.splice(index, 1);
    },
    
    addObjective() {
      this.objectives.push('');
    },
    
    removeObjective(index) {
      this.objectives.splice(index, 1);
    }
  },
  setup() {
    const toast = useToast(); // Get the toast instance

    return { toast };
  },
};
</script>