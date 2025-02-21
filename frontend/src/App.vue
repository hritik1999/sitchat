<script>
import { Button } from '@/components/ui/button'

export default {
  components: {
    Button
  }
}

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