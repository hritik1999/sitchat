<template>
    <div class="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-100 transition-colors duration-300">
      <div class="container mx-auto px-4 py-16 space-y-12">
        <!-- Hero Section -->
        <section class="text-center space-y-4">
          <h1 class="text-5xl md:text-6xl font-extrabold">🎬 About Sitchat</h1>
          <p class="text-xl md:text-2xl text-gray-600 dark:text-gray-300">
            Welcome to Sitchat — the future of fan-powered storytelling.
          </p>
          <p class="max-w-2xl mx-auto">
            Ever wished your favorite shows never ended? Jump into the story, crack jokes with Chandler, pull stunts with Barney, or get a brainy lecture from Sheldon. Sitchat isn’t just about watching—you’re part of the cast.
          </p>
        </section>
  
        <!-- What You Can Do -->
        <Card class="p-6 bg-white dark:bg-gray-800 shadow-lg">
          <CardHeader>
            <CardTitle class="text-3xl font-semibold">📺 What You Can Do</CardTitle>
          </CardHeader>
          <CardContent class="mt-4 space-y-4">
            <ul class="list-disc list-inside space-y-2">
              <li>Create shows by adding names, descriptions, and character details.</li>
              <li>Define plot objectives and build episodes just the way you imagine them.</li>
              <li>Play shows and episodes created by other fans around the world.</li>
              <li>
                Unlock hilarious, memorable achievements like:
                <ul class="list-circle list-inside ml-6 space-y-1 mt-2">
                  <li>“Flirted with Rachel/Joey”</li>
                  <li>“Got roasted by Chandler”</li>
                  <li>“Got called dumb by Sheldon”</li>
                  <li>“Enacted a playbook stunt with Barney”</li>
                  <li>“Received a nihilistic lecture from Gilfoyle”</li>
                </ul>
              </li>
            </ul>
            <p class="mt-4 italic">Your choices shape the story. Your actions unlock the comedy. Your fandom fuels the fun.</p>
          </CardContent>
        </Card>
  
        <!-- Why Sitchat Exists -->
        <Card class="p-6 bg-white dark:bg-gray-800 shadow-lg">
          <CardHeader>
            <CardTitle class="text-3xl font-semibold">💡 Why Sitchat Exists</CardTitle>
          </CardHeader>
          <CardContent class="mt-4 space-y-4">
            <p>
              Like many of you, I (Hritik here 👋) am obsessed with sitcoms—Silicon Valley, Friends, HIMYM, and more. When a series ends, reruns just don’t cut it, and the fifth rewatch feels stale.
            </p>
            <p>
              So earlier this year, while rewatching Silicon Valley for the umpteenth time, an idea hit me: What if I could craft new episodes… and be part of them too? That spark became Sitchat. Built solo and funded from savings, it’s my passion project—now ready for you.
            </p>
          </CardContent>
        </Card>
  
        <!-- Mission & Vision -->
        <Card class="p-6 bg-white dark:bg-gray-800 shadow-lg">
          <CardHeader>
            <CardTitle class="text-3xl font-semibold">🚀 Mission & Vision</CardTitle>
          </CardHeader>
          <CardContent class="mt-4 space-y-3">
            <p><strong>Mission:</strong> Become the Netflix of interactive storytelling.</p>
            <p><strong>Vision:</strong> Start with text-based group chats, expand to voice calls, and evolve into full interactive video and game-like experiences—powered by ever-advancing AI.</p>
          </CardContent>
        </Card>
  
        <!-- What Makes Sitchat Different -->
        <Card class="p-6 bg-white dark:bg-gray-800 shadow-lg">
          <CardHeader>
            <CardTitle class="text-3xl font-semibold">✨ What Makes Sitchat Different?</CardTitle>
          </CardHeader>
          <CardContent class="mt-4">
            <ul class="list-disc list-inside space-y-2">
              <li>You don’t just chat with one character—you’re in a group chat with the whole cast.</li>
              <li>Structured storytelling with real plot progression, not random back-and-forths.</li>
              <li>Dynamic, playable stories with goals, challenges, and plenty of laughs.</li>
            </ul>
          </CardContent>
        </Card>
  
        <!-- Meet the Creator -->
        <Card class="p-6 bg-white dark:bg-gray-800 shadow-lg">
          <CardHeader>
            <CardTitle class="text-3xl font-semibold">👨‍💻 Meet the Creator</CardTitle>
          </CardHeader>
          <CardContent class="mt-4 space-y-2">
            <p><strong>Hritik Gupta</strong> — Founder & Developer</p>
            <p>Tech enthusiast. Gamer. Sitcom & anime addict.</p>
            <p>Email: <a href="mailto:founder@sitchat.ai" class="underline text-blue-600 dark:text-blue-400">founder@sitchat.ai</a></p>
            <p>Phone: <a href="tel:+918875749079" class="underline text-blue-600 dark:text-blue-400">+91 88757 49079</a></p>
          </CardContent>
        </Card>
  
        <!-- Call to Action -->
        <section class="text-center py-8">
          <h2 class="text-4xl font-bold">🎉 Ready to Join the Fun?</h2>
          <p class="mt-2 mb-6">Go create, share episodes, unlock achievements, and become part of the shows you love.</p>
          <Button variant="default" size="lg" class="transform hover:scale-105 transition" @click="$router.push('/shows')">
            Create Your First Episode
          </Button>
        </section>
      </div>
    </div>
  </template>
  
  <script setup>
  import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
  import { Button } from '@/components/ui/button';
  </script>
  
  <style>
  /* Ensure Tailwind’s dark mode is set to class in tailwind.config.js */
  </style>