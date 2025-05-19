<template>
    <div class="min-h-screen transition-colors">
      <header class="px-4 py-8 bg-background/80 backdrop-blur-md border-b border-foreground/10">
        <div class="container mx-auto max-w-3xl">
          <div class="flex items-center gap-3 mb-2">
            <div class="p-2 rounded-full bg-primary/10">
              🎬
            </div>
            <h1 class="text-4xl font-bold tracking-tight">
              How to Create Your Own Show on Sitchat
            </h1>
          </div>
          <p class="text-xl text-foreground/80 mt-4">
            Your Imagination. Your Cast. Your Story.
          </p>
        </div>
      </header>
  
      <main class="container mx-auto px-4 py-8 prose dark:prose-invert max-w-3xl">
        <section class="mb-12">
          <p class="lead">
            Ever dreamed of being the showrunner for your favorite TV show — or even making your own? Now you can. 
            With Sitchat, creating your own sitcom-style experience is just a few clicks away.
          </p>
        </section>

                <!-- Experimental AI Feature -->
        <section class="mb-12">
          <article class="p-6 bg-accent/10 rounded-xl border border-accent/20">
            <div class="flex items-center gap-3 mb-4">
              <div class="p-2 rounded-lg bg-primary/10">
                🤖
              </div>
              <h2 class="text-2xl font-bold">New: AI-Generate Show (Experimental)</h2>
            </div>
            <p class="text-foreground/80">
              We’ve introduced an experimental "Generate with AI" feature! Now you can create a show by simply providing its name and pressing the <strong>Generate with AI</strong> button. 
              Please note, this feature is still in testing—make sure to review and confirm all show details before finalizing creation. It currently works only with existing shows.
            </p>
          </article>
        </section>
  
        <section class="space-y-8">
          <!-- Step-by-Step Guide -->
          <article class="relative p-6 bg-background rounded-xl border border-foreground/10">
            <div class="absolute -top-4 -left-4 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
              🚀
            </div>
            <h2 class="text-2xl font-bold mb-6">Step-by-Step Guide</h2>
            
            <div class="space-y-6">
              <div class="space-y-2">
                <h3 class="font-semibold text-lg">1. Go to the Shows Page</h3>
                <p class="text-foreground/80">
                  Hit that big <Button variant="default" size="sm" class="mx-1">Create Show</Button> button. 
                  You're officially in the director’s chair.
                </p>
              </div>
  
              <div class="space-y-2">
                <h3 class="font-semibold text-lg">2. Fill in Show Details</h3>
                <ul class="list-disc ml-6 space-y-2 marker:text-foreground/50">
                  <li><strong>Show Name</strong> - Make it catchy!</li>
                  <li><strong>Description</strong> - Keep it juicy but brief</li>
                  <li><strong>Thumbnail Image</strong> - Portrait format works best (use Pinterest or AI tools)</li>
                </ul>
              </div>
  
              <div class="space-y-2">
                <h3 class="font-semibold text-lg">3. Add Characters</h3>
                <div class="p-4 bg-muted/30 rounded-lg">
                  <p class="text-sm text-foreground/70 mb-2">For each character:</p>
                  <ul class="list-disc ml-6 space-y-2 marker:text-foreground/50">
                    <li>Name</li>
                    <li>Description</li>
                    <li>Image (Pinterest or AI generators work great)</li>
                  </ul>
                </div>
              </div>
  
              <div class="space-y-2">
                <h3 class="font-semibold text-lg">4. Define Relationships</h3>
                <p class="text-foreground/80">
                  Write a short paragraph explaining connections — crushes, rivalries, backstories. 
                  This fuels the AI and sets the show's vibe.
                </p>
              </div>
  
              <div class="p-4 bg-success/10 rounded-lg border border-success/20">
                <h3 class="font-semibold text-lg text-success">5. Publish & Launch! 🎉</h3>
                <p class="mt-2 text-success/90">
                  Your show is now live! Fans can discover it and dive into AI-powered group chat episodes.
                </p>
              </div>
            </div>
          </article>
  
          <!-- Why It Matters -->
          <article class="p-6 bg-background rounded-xl border border-foreground/10">
            <div class="flex items-center gap-3 mb-4">
              <div class="p-2 rounded-lg bg-primary/10">
                🧠
              </div>
              <h2 class="text-2xl font-bold">Why This Matters</h2>
            </div>
            <p class="text-foreground/80">
              Your inputs become the AI's storytelling brain. Better descriptions = better conversations, 
              drama, and jokes. Remember — this info is visible to users, so make it compelling!
            </p>
          </article>
  
          <!-- Regional Section -->
          <article class="p-6 bg-background rounded-xl border border-foreground/10">
            <div class="flex items-center gap-3 mb-4">
              <div class="p-2 rounded-lg bg-primary/10">
                🌍
              </div>
              <h2 class="text-2xl font-bold">Global Storytelling</h2>
            </div>
            <p class="text-foreground/80">
              Create in Hindi, Spanish, Tamil, French, or Klingon! Write descriptions in your chosen language, 
              and the AI will respond accordingly.
            </p>
          </article>
  
          <!-- AI Prompt -->
          <article class="p-6 bg-background rounded-xl border border-foreground/10">
            <div class="flex items-center gap-3 mb-4">
              <div class="p-2 rounded-lg bg-primary/10">
                💡
              </div>
              <h2 class="text-2xl font-bold">Pro AI Prompt</h2>
            </div>
            <p class="text-foreground/80 mb-4">
              Use this in ChatGPT or any AI assistant to generate show ideas:
            </p>
            <div class="overflow-auto w-full">
            <pre class="bg-muted p-4 rounded-lg text-sm min-w-full">
              <code class="whitespace-pre">
Give me the following information about {Show Name} in {Language}:
  1. Name of the Show
  2. Description
  3. Character names and descriptions
  4. Character relationships (in one paragraph)
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
              <h2 class="text-2xl font-bold">Example: Rick and Morty</h2>
            </div>
            
            <div class="space-y-4">
              <div class="p-4 bg-muted/30 rounded-lg">
                <p class="font-semibold">Show Name:</p>
                <p>Rick and Morty</p>
              </div>
              
              <div class="p-4 bg-muted/30 rounded-lg">
                <p class="font-semibold">Description:</p>
                <p>A chaotic sci-fi sitcom about a cynical scientist and his anxious grandson traveling across the multiverse.</p>
              </div>
  
              <div class="p-4 bg-muted/30 rounded-lg">
                <p class="font-semibold">Characters:</p>
                <ul class="list-disc ml-6 space-y-2">
                  <li>Rick Sanchez — Genius, nihilist, grandpa</li>
                  <li>Morty Smith — Nervous teen sidekick</li>
                  <li>Summer — Sassy sister</li>
                  <li>Beth — Horse surgeon with daddy issues</li>
                  <li>Jerry — Hopeless dad, usually confused</li>
                </ul>
              </div>
  
              <div class="p-4 bg-muted/30 rounded-lg">
                <p class="font-semibold">Character Relationships:</p>
                <p>Rick is the reckless glue holding this dysfunctional family together, dragging Morty into dangerous adventures while Beth yearns for his approval. Jerry disapproves but can’t stop it. Summer is slowly becoming a sidekick herself.</p>
              </div>
            </div>
          </article>
  
          <!-- Final CTA -->
          <article class="p-8 text-center bg-primary/10 rounded-xl border border-primary/20">
            <div class="text-4xl mb-4">🎉</div>
            <h2 class="text-2xl font-bold mb-4">Let the Stories Begin!</h2>
            <p class="text-foreground/80 mb-4">
              You're not just a fan — you're a writer, director, and co-star all in one. 
              Bring your dream cast together and let the AI-powered drama unfold!
            </p>
            <Button size="lg" class="mt-4" @click="$router.push('/shows')">
              Start Creating Now
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