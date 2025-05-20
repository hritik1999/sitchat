<template>
    <div class="py-8 container mx-auto px-4">
      <!-- User Profile Section -->
    <Card class="mb-8">
      <CardHeader class="flex flex-col md:flex-row md:items-start items-start justify-between gap-4">
        <div class="flex items-center gap-4 w-full">
          <Avatar class="h-16 w-16">
            <AvatarImage v-if="userDetails.avatar_url" :src="userDetails.avatar_url" />
            <AvatarFallback>{{ userInitials }}</AvatarFallback>
          </Avatar>
          <div class="min-w-0">
            <CardTitle class="text-2xl truncate">{{ userDetails.username || 'User' }}</CardTitle>
            <CardDescription v-if="userDetails.email" class="truncate">{{ userDetails.email }}</CardDescription>
          </div>
        </div>
        <Button @click="editUser" variant="outline" class="w-full md:w-auto mt-4 md:mt-0 self-end md:self-auto">
          <PencilIcon class="h-4 w-4 mr-2" />
          Edit Profile
        </Button>
      </CardHeader>
    </Card>
  
  <!-- Settings Section -->
  <Card class="mb-8">
    <CardHeader>
      <CardTitle class="text-xl">Settings</CardTitle>
      <div class="flex flex-wrap items-center justify-between pt-4 gap-4">
        <div>
          <CardTitle class="text-sm">Theme</CardTitle>
          <CardDescription>Toggle between dark and light mode</CardDescription>
        </div>
        <div class="flex flex-col md:flex-row md:items-center gap-2 w-full md:w-auto">
          <Button @click="toggleDarkMode" variant="outline" class="w-full md:w-auto">
            <SunIcon class="h-4 w-4 mr-2 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <MoonIcon class="h-4 w-4 mr-2 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            Toggle Theme
          </Button>
          <Button @click="logout" variant="destructive" class="w-full md:hidden">
            <LogOutIcon class="h-4 w-4 mr-2" />
            Logout
          </Button>
        </div>
      </div>
    </CardHeader>
  </Card>

        <!-- Mobile-Only Links & Social Media Section -->
        <Card class="mb-8 block md:hidden">
        <CardHeader>
          <CardTitle class="text-xl">Quick Links</CardTitle>
          <div class="flex flex-col space-y-2 pt-4">
            <RouterLink to="/about" class="text-primary hover:underline">About</RouterLink>
            <RouterLink to="/blogs" class="text-primary hover:underline">Blog</RouterLink>
            <RouterLink to="/career" class="text-primary hover:underline">Careers</RouterLink>
            <RouterLink to="/terms" class="text-primary hover:underline">Terms & Conditions</RouterLink>
            <RouterLink to="/privacy" class="text-primary hover:underline">Privacy Policy</RouterLink>
          </div>
                    <!-- Social Links -->
          <div>
            <h3 class="text-lg font-semibold mb-4 text-slate-900 dark:text-slate-50">Social</h3>
            <div class="flex gap-4">
              <!-- Reddit -->
            <a href="https://www.reddit.com/r/Sitchat/" target="_blank" rel="noopener noreferrer" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">
             <svg xmlns="http://www.w3.org/2000/svg" x="0px" y="0px" width="24" height="24" viewBox="0 0 80 80">
            <path fill="#fff" d="M69,45.5c-4.7,0-8.5-3.8-8.5-8.5s3.8-8.5,8.5-8.5s8.5,3.8,8.5,8.5S73.7,45.5,69,45.5z"></path><path fill="#788b9c" d="M69,29c4.4,0,8,3.6,8,8s-3.6,8-8,8s-8-3.6-8-8S64.6,29,69,29 M69,28c-5,0-9,4-9,9s4,9,9,9s9-4,9-9 S74,28,69,28L69,28z"></path><path fill="#fff" d="M11,45.5c-4.7,0-8.5-3.8-8.5-8.5s3.8-8.5,8.5-8.5s8.5,3.8,8.5,8.5S15.7,45.5,11,45.5z"></path><path fill="#788b9c" d="M11,29c4.4,0,8,3.6,8,8s-3.6,8-8,8s-8-3.6-8-8S6.6,29,11,29 M11,28c-5,0-9,4-9,9s4,9,9,9s9-4,9-9 S16,28,11,28L11,28z"></path><path fill="#fff" d="M40,73.5c-19.6,0-35.5-11-35.5-24.5S20.4,24.5,40,24.5s35.5,11,35.5,24.5S59.6,73.5,40,73.5z"></path><path fill="#788b9c" d="M40,25c19.3,0,35,10.8,35,24S59.3,73,40,73S5,62.2,5,49S20.7,25,40,25 M40,24C20,24,4,35.3,4,49 s16,25,36,25s36-11.3,36-25S60,24,40,24L40,24z"></path><path fill="#f78f8f" d="M27 40.5A4.5 4.5 0 1 0 27 49.5A4.5 4.5 0 1 0 27 40.5Z"></path><path fill="#c74343" d="M27,41c2.2,0,4,1.8,4,4s-1.8,4-4,4s-4-1.8-4-4S24.8,41,27,41 M27,40c-2.8,0-5,2.2-5,5s2.2,5,5,5 s5-2.2,5-5S29.8,40,27,40L27,40z"></path><g><path fill="#f78f8f" d="M53 40.5A4.5 4.5 0 1 0 53 49.5A4.5 4.5 0 1 0 53 40.5Z"></path><path fill="#c74343" d="M53,41c2.2,0,4,1.8,4,4s-1.8,4-4,4s-4-1.8-4-4S50.8,41,53,41 M53,40c-2.8,0-5,2.2-5,5s2.2,5,5,5 s5-2.2,5-5S55.8,40,53,40L53,40z"></path></g><path fill="#788b9c" d="M40,63.5c-8.8,0-13.2-5.2-13.4-5.4c-0.2-0.2-0.1-0.5,0.1-0.7s0.5-0.2,0.7,0.1c0,0.1,4.3,5,12.6,5 c8.3,0,12.6-5,12.6-5c0.2-0.2,0.5-0.2,0.7-0.1c0.2,0.2,0.2,0.5,0.1,0.7C53.2,58.3,48.8,63.5,40,63.5z"></path><g><path fill="#b6c9d6" d="M70.5 6.5A5 5 0 1 0 70.5 16.5A5 5 0 1 0 70.5 6.5Z"></path><path fill="#788b9c" d="M70.5,7C73,7,75,9,75,11.5S73,16,70.5,16S66,14,66,11.5S68,7,70.5,7 M70.5,6c-3,0-5.5,2.5-5.5,5.5 s2.5,5.5,5.5,5.5s5.5-2.5,5.5-5.5S73.5,6,70.5,6L70.5,6z"></path></g><path fill="#788b9c" d="M41,24h-1v-8.2c0-4.4,3.3-7.7,7.7-7.7c1.8,0,3.7,0.5,5.8,1.1c3,0.8,6.7,1.9,12,1.9v1 c-5.4,0-9.2-1.1-12.2-1.9C51.2,9.5,49.4,9,47.7,9c-3.9,0-6.7,2.8-6.7,6.7V24z"></path>
            </svg>
            </a>

              <!-- Instagram -->
              <a href="https://www.instagram.com/sitchat.ai/" target="_blank" rel="noopener noreferrer" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/>
                </svg>
              </a>

              <!-- X (Twitter) -->
              <a href="https://x.com/AI_Bhaiiii" target="_blank" rel="noopener noreferrer" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"/>
                </svg>
              </a>

              <!-- YouTube -->
              <a href="https://www.youtube.com/@Sitchat-ai" target="_blank" rel="noopener noreferrer" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
              </a>

              <!-- Discord -->
              <a href="https://discord.gg/T32mC8nPZY" target="_blank" rel="noopener noreferrer" class="text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19.27 5.33C17.94 4.71 16.5 4.26 15 4a.09.09 0 0 0-.07.03c-.18.33-.39.76-.53 1.09a16.09 16.09 0 0 0-4.8 0c-.14-.34-.35-.76-.54-1.09c-.01-.02-.04-.03-.07-.03c-1.5.26-2.93.71-4.27 1.33c-.01 0-.02.01-.03.02c-2.72 4.07-3.47 8.03-3.1 11.95c0 .02.01.04.03.05c1.8 1.32 3.53 2.12 5.24 2.65c.03.01.06 0 .07-.02c.4-.55.76-1.13 1.07-1.74c.02-.04 0-.08-.04-.09c-.57-.22-1.11-.48-1.64-.78c-.04-.02-.04-.08-.01-.11c.11-.08.22-.17.33-.25c.02-.02.05-.02.07-.01c3.44 1.57 7.15 1.57 10.55 0c.02-.01.05-.01.07.01c.11.09.22.17.33.26c.04.03.04.09-.01.11c-.52.31-1.07.56-1.64.78c-.04.01-.05.06-.04.09c.32.61.68 1.19 1.07 1.74c.03.01.06.02.09.01c1.72-.53 3.45-1.33 5.25-2.65c.02-.01.03-.03.03-.05c.44-4.53-.73-8.46-3.1-11.95c-.01-.01-.02-.02-.04-.02zM8.52 14.91c-1.03 0-1.89-.95-1.89-2.12s.84-2.12 1.89-2.12c1.06 0 1.9.96 1.89 2.12c0 1.17-.84 2.12-1.89 2.12zm6.97 0c-1.03 0-1.89-.95-1.89-2.12s.84-2.12 1.89-2.12c1.06 0 1.9.96 1.89 2.12c0 1.17-.83 2.12-1.89 2.12z"/>
                </svg>
              </a>
            </div>
          </div>
        </CardHeader>
      </Card>

    <!-- Writer Statistics Section -->
    <Card v-if="userShows.length > 0 || normalizedEpisodes.length > 0" class="mb-8">
      <CardHeader>
        <CardTitle class="text-xl">Writer Statistics</CardTitle>
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4 pt-4">
          <div class="flex flex-col p-4 bg-muted/50 rounded-lg">
            <div class="flex items-center gap-2">
              <Book class="h-5 w-5 text-primary" />
              <span class="text-sm font-medium">Shows</span>
            </div>
            <span class="text-2xl font-bold mt-2">{{ writerStats.totalShows }}</span>
          </div>

          <div class="flex flex-col p-4 bg-muted/50 rounded-lg">
            <div class="flex items-center gap-2">
              <FileText class="h-5 w-5 text-primary" />
              <span class="text-sm font-medium">Episodes</span>
            </div>
            <span class="text-2xl font-bold mt-2">{{ writerStats.totalEpisodes }}</span>
          </div>

          <div class="flex flex-col p-4 bg-muted/50 rounded-lg">
            <div class="flex items-center gap-2">
              <StarIcon class="h-5 w-5 text-primary" />
              <span class="text-sm font-medium">Avg Rating</span>
            </div>
            <span class="text-2xl font-bold mt-2">{{ writerStats.averageRating }}</span>
          </div>

          <div class="flex flex-col p-4 bg-muted/50 rounded-lg">
            <div class="flex items-center gap-2">
              <Eye class="h-5 w-5 text-primary" />
              <span class="text-sm font-medium">Total Views</span>
            </div>
            <span class="text-2xl font-bold mt-2">{{ writerStats.totalViews.toLocaleString() }}</span>
          </div>

          <div class="flex flex-col p-4 bg-muted/50 rounded-lg">
            <div class="flex items-center gap-2">
              <PiggyBank class="h-5 w-5 text-primary" />
              <span class="text-sm font-medium">Total Earnings</span>
            </div>
            <span class="text-2xl font-bold mt-2 text-muted-foreground">
              {{ writerStats.totalEarnings }}
            </span>
          </div>
        </div>
      </CardHeader>
    </Card>

      <!-- Achievements Section -->
      <Card v-if="userAchievements.length > 0" class="mb-8">
        <CardHeader>
          <CardTitle class="text-xl">Achievements</CardTitle>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-4">
            <div v-for="(achievement, index) in visibleAchievements" :key="achievement.id" 
                class="p-4 bg-muted/50 rounded-lg">
              <div class="flex justify-between items-start mb-2">
                <div class="flex items-center gap-2">
                  <span class="text-2xl">{{ getAchievementEmoji(achievement.score) }}</span>
                  <CardTitle class="text-base">{{ achievement.title }}</CardTitle>
                </div>
                <div class="flex items-center gap-1 text-amber-500">
                  <span v-for="n in 5" :key="n" 
                        :class="n <= achievement.score ? 'text-amber-500' : 'text-muted-foreground'">
                    ★
                  </span>
                </div>
              </div>
              <CardDescription class="text-sm">
                {{ getShowName(achievement.show_id) || 'General Achievement' }}
              </CardDescription>
            </div>
          </div>
          <Button v-if="hasMoreAchievements" @click="showAllAchievements = !showAllAchievements" 
                  variant="ghost" class="mt-4 mx-auto">
            {{ showAllAchievements ? 'Show less' : 'Show more' }}
            <ChevronDownIcon class="h-4 w-4 ml-2 transition-transform" 
                            :class="{ 'rotate-180': showAllAchievements }" />
          </Button>
        </CardHeader>
      </Card>
  
      <!-- User's Shows Section -->
      <section class="mb-8">
        <h2 class="text-xl font-semibold mb-6">Your Shows</h2>
  
        <div v-if="loadingShows" class="flex justify-center py-8">
          <Loader2Icon class="h-8 w-8 animate-spin" />
        </div>
  
        <div v-else-if="!userShows || userShows.length === 0" class="text-center py-8">
          <p class="text-muted-foreground">You haven't created any shows yet.</p>
        </div>
  
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <Card v-for="show in userShows" :key="show.id" class="relative group">
            <div class="aspect-video bg-muted relative">
              <img
                :src="show.image_url || '/placeholder-show.jpg'"
                class="w-full h-full object-cover"
                :alt="`${show.name} thumbnail`"
                loading="lazy"
              >
              <div class="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent" />
            </div>
            <CardHeader>
              <div class="flex justify-between items-start">
                <CardTitle class="line-clamp-1">{{ show.name }}</CardTitle>
                <Button @click="editShow(show.id)" variant="ghost" size="icon">
                  <PencilIcon class="h-4 w-4" />
                </Button>
              </div>
              <CardDescription class="line-clamp-2">{{ show.description }}</CardDescription>
            </CardHeader>
            <CardContent>
              <div class="flex justify-between text-sm text-muted-foreground">
                <span>{{ getCharacterCount(show) }} characters</span>
                <span>{{ formatDate(show.created_at) }}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>
  
      <!-- User's Episodes Section -->
        <section>
        <h2 class="text-xl font-semibold mb-6">Your Episodes</h2>

        <div v-if="loadingEpisodes" class="flex justify-center py-8">
            <Loader2Icon class="h-8 w-8 animate-spin" />
        </div>

        <div v-else-if="!userEpisodes || userEpisodes.length === 0" class="text-center py-8">
            <p class="text-muted-foreground">You haven't created any episodes yet.</p>
        </div>

        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card v-for="episode in normalizedEpisodes" :key="episode.id" class="relative group">
            <CardHeader>
                <div class="flex justify-between items-start">
                <CardTitle class="line-clamp-1">{{ episode.name }}</CardTitle>
                <div class="flex gap-1">
                    <Button @click="editEpisode(episode.show_id, episode.id)" variant="ghost" size="icon">
                    <PencilIcon class="h-4 w-4" />
                    </Button>
                </div>
                </div>
                <CardDescription class="line-clamp-2">{{ episode.description }}</CardDescription>

                <div class="flex gap-4 mt-4 text-sm">
                <div class="flex items-center gap-1.5 text-muted-foreground">
                  <StarIcon class="h-4 w-4 text-amber-500" />
                  <span>{{ episode.average_ratings?.toFixed(1) || '0.0' }}</span>
                </div>
                <div class="flex items-center gap-1.5 text-muted-foreground">
                  <ClockIcon class="h-4 w-4 text-emerald-500" />
                  <span>{{ calculateDuration(episode) }}m</span>
                </div>
                <div class="flex items-center gap-1.5 text-muted-foreground">
                  <EyeIcon class="h-4 w-4 text-blue-500" />
                  <span>{{ episode.views?.toLocaleString() || 0 }}</span>
                </div>
              </div>
            </CardHeader>
            <CardContent>
                <div class="flex justify-between text-sm text-muted-foreground">
                <span>{{ getShowNameForEpisode(episode.show_id) }}</span>
                <span>{{ formatDate(episode.created_at) }}</span>
                </div>
            </CardContent>
            </Card>
        </div>
        </section>
    </div>
  </template>
  
  <script>
  import { Button } from '@/components/ui/button'
  import { useToast } from 'vue-toastification'
  import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
  import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
  import { Loader2Icon, MoonIcon, SunIcon, PencilIcon, Trash2Icon, LogOutIcon,StarIcon, EyeIcon, ClockIcon,ChevronDownIcon,Book, FileText, Eye, PiggyBank } from 'lucide-vue-next'
import { fetchApi } from '@/lib/utils'
  import { supabase } from '@/composables/useSupabase'
  export default {
    components: {
      Button,
      Card,
      CardContent,
      CardDescription,
      CardHeader,
      CardTitle,
      Avatar,
      AvatarFallback,
      AvatarImage,
      Loader2Icon,
      MoonIcon,
      SunIcon,
      PencilIcon,
      Trash2Icon,
      LogOutIcon,
      StarIcon,
    EyeIcon, 
    ClockIcon,
    ChevronDownIcon,
    Book, 
    FileText, 
    Eye,
    PiggyBank
    },
    data() {
      return {
        userDetails: {
          username: '',
          email: '',
          avatar_url: null
        },
        BASE_API_URL: import.meta.env.VITE_BASE_API_URL || 'http://localhost:5001',
        // No longer storing session token directly
        // fetchApi utility will handle authentication
        userShows: [],
        userEpisodes: null, // Can be an object or array
        userAchievements:[],
        loadingShows: true,
        loadingEpisodes: true,
        error: null,
        showAllAchievements: false,
      }
    },
    computed: {
        userInitials() {
            // Use username since that's what exists in the data
            if (!this.userDetails || !this.userDetails.username) {
            return 'U'; // Default to 'U' for User if no username available
            }
            
            return this.userDetails.username
            .split(/[\s_-]/) // Split by space, underscore or hyphen to handle usernames
            .map(n => n[0])
            .join('')
            .toUpperCase();
        },
        normalizedEpisodes() {
            // Handle both single object and array cases
            if (!this.userEpisodes) return [];
            
            // If userEpisodes is already an array, return it
            if (Array.isArray(this.userEpisodes)) return this.userEpisodes;
            
            // If userEpisodes is a single object, convert it to an array
            if (typeof this.userEpisodes === 'object') return [this.userEpisodes];
            
            // Fallback for unexpected formats
            return [];
        },
        writerStats() {
          const stats = {
            totalShows: this.userShows.length,
            totalEpisodes: this.normalizedEpisodes.length,
            averageRating: 0,
            totalViews: 0,
            totalEarnings: 'Soon'
          };

          // Calculate ratings only for episodes with rating > 0
          const ratedEpisodes = this.normalizedEpisodes.filter(ep => ep.average_ratings > 0);
          if (ratedEpisodes.length > 0) {
            const totalRatings = ratedEpisodes.reduce((sum, ep) => sum + ep.average_ratings, 0);
            stats.averageRating = (totalRatings / ratedEpisodes.length).toFixed(1);
          }

          if (this.normalizedEpisodes.length > 0) {
            stats.totalViews = this.normalizedEpisodes.reduce((sum, ep) => sum + (ep.views || 0), 0);
          }

          return stats;
        },
        visibleAchievements() {
            return this.showAllAchievements 
              ? this.userAchievements 
              : this.userAchievements.slice(0, 3);
          },
          hasMoreAchievements() {
            return this.userAchievements.length > 3;
          }
        },
    mounted() {
      this.getUserDetails()
      this.initializeTheme()
    },
    methods: {
      initializeTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light'
        document.documentElement.classList.toggle('dark', savedTheme === 'dark')
      },
      toggleDarkMode() {
        const isDark = document.documentElement.classList.toggle('dark')
        localStorage.setItem('theme', isDark ? 'dark' : 'light')
      },
      async logout() {
        try {
          // Sign out
          localStorage.removeItem('sb-wpwichwnfgbpggcqujld-auth-token')
          await supabase.auth.signOut()
          // Force a full page reload to reset auth state
          window.location.href = '/login'
        } catch (error) {
          console.error('Error during logout:', error)
        }
      },
      formatDate(dateString) {
        if (!dateString) return '';
        return new Date(dateString).toLocaleDateString();
      },
      getCharacterCount(show) {
        if (!show.characters) return 0;
        
        try {
            // Handle case where characters is already an object
            if (typeof show.characters === 'object' && show.characters !== null) {
            return Array.isArray(show.characters) ? show.characters.length : 1;
            }
            
            // Handle case where characters is a string that needs to be parsed
            if (typeof show.characters === 'string') {
            const characters = JSON.parse(show.characters);
            return Array.isArray(characters) ? characters.length : 1;
            }
            
            return 0;
        } catch (e) {
            console.error('Error processing characters data:', e);
            return 0;
        }
        },
      getShowNameForEpisode(showId) {
        if (!showId || !this.userShows) return '';
        
        const show = this.userShows.find(s => s.id === showId);
        return show ? show.name : '';
      },
      async deleteEpisode(showId, episodeId) {
        if (confirm('Are you sure you want to delete this episode?')) {
          try {
            // Add delete API call here
            await fetchApi(`api/show/${showId}/episodes/${episodeId}`, {
              method: 'DELETE'
            })
            // If userEpisodes is an object (single episode)
            if (!Array.isArray(this.userEpisodes)) {
              if (this.userEpisodes.id === episodeId) {
                this.userEpisodes = null;
              }
            } else {
              // If userEpisodes is an array (multiple episodes)
              this.userEpisodes = this.userEpisodes.filter(e => e.id !== episodeId);
            }
          } catch (error) {
            console.error('Failed to delete episode:', error);
          }
        }
      },
      editUser() {
        // Navigate to edit user profile
        this.$router.push('/edit/profile');
      },
      calculateDuration(episode) {
    try {
      const objectives = typeof episode.plot_objectives === 'string' 
        ? JSON.parse(episode.plot_objectives || '[]')
        : episode.plot_objectives || [];
      return objectives.length * 2;
    } catch (e) {
      console.error('Error parsing plot objectives:', e);
      return 0;
    }
  },
      editShow(showId) {
        // Navigate to edit show
        this.$router.push('/edit/show/' + showId);
      },
      editEpisode(showId, episodeId) {
        // Navigate to edit episode
        this.$router.push('/edit/episode/'+ showId + '/' + episodeId);
      },
      async getUserDetails() {
        const toast = useToast();
        try {
            const data = await fetchApi(`api/user`);
            console.log('API Response:', data);
            
            // Update userDetails with the user data
            this.userDetails = data.user || {};
            
            // Handle shows data
            this.userShows = Array.isArray(data.user_shows) ? data.user_shows : [];
            this.userAchievements = Array.isArray(data.user_achievements) ? data.user_achievements : [];
            console.log('User shows:', this.userShows);
            // Handle episodes data - ensure it's always an array
            if (data.user_episodes) {
            // If it's a single object (not an array), convert to array
            if (!Array.isArray(data.user_episodes) && typeof data.user_episodes === 'object') {
                this.userEpisodes = [data.user_episodes];
            } else if (Array.isArray(data.user_episodes)) {
                this.userEpisodes = data.user_episodes;
            } else {
                this.userEpisodes = [];
            }
            } else {
            this.userEpisodes = [];
            }
            
            // Update loading states
            this.loadingShows = false;
            this.loadingEpisodes = false;
            
            console.log('User details processed:', {
            user: this.userDetails,
            shows: this.userShows,
            episodes: this.userEpisodes
            });
        } catch (error) {
            toast.error('Failed to load user details:', error);
            console.error('Failed to fetch user details:', error);
            this.error = 'Failed to load user details';
            this.loadingShows = false;
            this.loadingEpisodes = false;
        }
        },
        getAchievementEmoji(score) {
        const emojis = ['🎯', '🌟', '🏅', '🏆', '💎', '🚀'];
        return emojis[Math.min(score, emojis.length - 1)];
      },
        getShowName(showId) {
          const show = this.userShows.find(s => s.id === showId);
          return show ? show.name : null;
        }
    }
  }
  </script>