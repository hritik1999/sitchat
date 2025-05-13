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