<script setup>
import { Button } from '@/components/ui/button'
</script>

<template>
  <div>
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/about">About</router-link>
    </nav>
    <router-view />
    <Button>Click me</Button>
  </div>
</template>