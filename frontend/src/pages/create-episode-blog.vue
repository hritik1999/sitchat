<template>
    <div class="min-h-screen transition-colors">
      <header class="px-4 py-8 bg-background/80 backdrop-blur-md border-b border-foreground/10">
        <div class="container mx-auto max-w-3xl">
          <div class="flex items-center gap-3 mb-2">
            <div class="p-2 rounded-full bg-primary/10">
              🎬
            </div>
            <h1 class="text-4xl font-bold tracking-tight">
              How to Create an Episode in Sitchat
            </h1>
          </div>
          <p class="text-xl text-foreground/80 mt-4">
            Become the Writer of the Stories You've Always Wanted to See
          </p>
        </div>
      </header>
  
      <main class="container mx-auto px-4 py-8 prose dark:prose-invert max-w-3xl">
        <section class="mb-12">
          <p class="lead">
            Sitchat episodes are interactive AI-powered group chats where characters act out your story 
            and users become part of the action. Let's create your first unforgettable episode.
          </p>
        </section>
  
        <section class="space-y-8">
          <!-- Step-by-Step Guide -->
          <article class="relative p-6 bg-background rounded-xl border border-foreground/10">
            <div class="absolute -top-4 -left-4 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
              🪄
            </div>
            <h2 class="text-2xl font-bold mb-6">Step-by-Step Episode Creation</h2>
            
            <div class="space-y-6">
              <div class="space-y-2">
                <h3 class="font-semibold text-lg">1. Enter Your Show</h3>
                <p class="text-foreground/80">
                  Navigate to your show's page and click <Button variant="default" size="sm" class="mx-1">Add Episode</Button> 
                  to begin crafting.
                </p>
              </div>
  
              <div class="space-y-2">
                <h3 class="font-semibold text-lg">2. Episode Details</h3>
                <ul class="list-disc ml-6 space-y-2 marker:text-foreground/50">
                  <li><strong>Name</strong> - Make it intriguing!</li>
                  <li><strong>Description</strong> - Set the stakes and tone without spoilers</li>
                  <li><strong>Player Role</strong> - Define the user's perspective (e.g., "New bartender")</li>
                </ul>
              </div>
  
              <div class="space-y-2">
                <h3 class="font-semibold text-lg">3. Scene Background</h3>
                <p class="text-foreground/80">
                  Paint the initial setting: location, character positions, and opening action. 
                  Be vivid but spoiler-free — this is the AI's starting point.
                </p>
              </div>
  
              <div class="space-y-2">
                <h3 class="font-semibold text-lg">4. Plot Objectives</h3>
                <div class="p-4 bg-muted/30 rounded-lg">
                  <p class="text-sm text-foreground/70 mb-2">Structure your story arc:</p>
                  <ul class="list-decimal ml-6 space-y-2 marker:text-foreground/50">
                    <li>Setup</li>
                    <li>Rising tension</li>
                    <li>Midpoint twist</li>
                    <li>Climax</li>
                    <li>Resolution</li>
                  </ul>
                </div>
              </div>
  
              <div class="p-4 bg-success/10 rounded-lg border border-success/20">
                <h3 class="font-semibold text-lg text-success">5. Publish & Launch! 🚀</h3>
                <p class="mt-2 text-success/90">
                  Your episode is now playable! Watch users interact with your story in real-time.
                </p>
              </div>
            </div>
          </article>
  
          <!-- Pro Tip Section -->
          <article class="p-6 bg-background rounded-xl border border-foreground/10">
            <div class="flex items-center gap-3 mb-4">
              <div class="p-2 rounded-lg bg-primary/10">
                🧠
              </div>
              <h2 class="text-2xl font-bold">Pro Writer Tip</h2>
            </div>
            <p class="text-foreground/80 mb-4">
              Use this AI prompt to generate episode ideas:
            </p>
            <div class="overflow-auto w-full">
            <pre class="bg-muted p-4 rounded-lg text-sm min-w-full">
              <code class="whitespace-pre">
You are an creative writer who is writing episode scripts for an interactive storytelling platform where user's come to experience show's episodes in an group chat with AI characters.

Create a {short description} episode of {show name} by providing:

1.Episode Name
2.Description
3.Player Role -A single line telling the user's involvement in the episode
4.Initial Setup-One paragraph giving only the background needed to launch the episode—establish the scene, characters, and stakes without spoilers.
5.Sequential Plot Objectives- A numbered list of simple, one-task objectives that carry the story from the very beginning through rising tensions, a midpoint turning point, and finally to the climax and resolution.
Ensure objectives are strictly chronological and together they map out the complete episode arc—setup, confrontation, climax, and denouement.

remember-
Do not give player a name
Do not include the player in plot objectives 
It should be like an authentic episode of the show
              </code>
            </pre>
          </div>
          </article>
  
          <!-- Example Section -->
          <article class="p-6 bg-background rounded-xl border border-foreground/10">
            <div class="flex items-center gap-3 mb-4">
              <div class="p-2 rounded-lg bg-primary/10">
                ✨
              </div>
              <h2 class="text-2xl font-bold">Example: "The Puzzle of the Red Slipper"</h2>
            </div>
            
            <div class="space-y-4">
              <div class="p-4 bg-muted/30 rounded-lg">
                <p class="font-semibold">Player Role:</p>
                <p>New bartender at MacLaren's (observer and occasional drink refiller)</p>
              </div>
  
              <div class="p-4 bg-muted/30 rounded-lg">
                <p class="font-semibold">Initial Setup:</p>
                <p>Pre-art show chaos as Lily's red slipper disappears, tensions rising with theories</p>
              </div>
  
              <div class="p-4 bg-muted/30 rounded-lg">
                <p class="font-semibold">Plot Objectives:</p>
                <ul class="list-decimal ml-6 space-y-2 marker:text-foreground/50">
                  <li>Search art storage closet</li>
                  <li>Question gallery assistant</li>
                  <li>Decode cryptic note</li>
                  <li>Retrace Lily's steps</li>
                  <li>Reveal Barney's confession</li>
                  <li>Public art show confrontation</li>
                  <li>Ted's metaphor speech</li>
                  <li>Reunite slipper</li>
                  <li>Celebrate new opportunity</li>
                </ul>
              </div>
            </div>
          </article>
  
          <!-- Writing Tips -->
          <article class="p-6 bg-background rounded-xl border border-foreground/10">
            <div class="flex items-center gap-3 mb-4">
              <div class="p-2 rounded-lg bg-primary/10">
                🔥
              </div>
              <h2 class="text-2xl font-bold">Why Plot Objectives Matter</h2>
            </div>
            <p class="text-foreground/80">
              These are your episode's spine — focused tasks that drive the story forward. Each should represent:
            </p>
            <ul class="list-disc ml-6 mt-2 space-y-2 marker:text-foreground/50">
              <li>A key discovery</li>
              <li>An important decision</li>
              <li>A plot twist</li>
              <li>Character development moment</li>
            </ul>
          </article>
  
          <!-- Bonus Tip -->
          <article class="p-6 bg-background rounded-xl border border-foreground/10">
            <div class="flex items-center gap-3 mb-4">
              <div class="p-2 rounded-lg bg-primary/10">
                🧑💻
              </div>
              <h2 class="text-2xl font-bold">Pro Tip: Leverage AI Reasoning</h2>
            </div>
            <p class="text-foreground/80">
              Advanced AI models excel at structured narratives. The clearer your objectives:
            </p>
            <ul class="list-disc ml-6 mt-2 space-y-2 marker:text-foreground/50">
              <li>Better character interactions</li>
              <li>Tighter plot coherence</li>
              <li>More surprising twists</li>
              <li>Authentic dialogue</li>
            </ul>
          </article>
  
          <!-- Final CTA -->
          <article class="p-8 text-center bg-primary/10 rounded-xl border border-primary/20">
            <div class="text-4xl mb-4">🎉</div>
            <h2 class="text-2xl font-bold mb-4">Your Characters Await!</h2>
            <p class="text-foreground/80 mb-4">
              Craft sitcom misunderstandings, emotional arcs, or sci-fi betrayals — 
              the stage is yours. What story will you tell today?
            </p>
            <Button size="lg" class="mt-4" @click="$router.push('/shows') ">
              Start Writing Now
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ml-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"/>
              </svg>
            </Button>
          </article>
        </section>
      </main>
    </div>
  </template>
  
  <script setup>
  import { Button } from '@/components/ui/button'
  </script>
  