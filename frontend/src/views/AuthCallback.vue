<template>
    <div>Processing authentication...</div>
  </template>
  
  <script>
  import { supabase } from '@/composables/useSupabase';
import { fetchApi } from '@/lib/utils';

export default {
    name: "AuthCallback",
    data() {
      return {};
    },
    created() {
      // Let Supabase handle the OAuth callback automatically
      // The client is configured with detectSessionInUrl: true
      
      // Wait briefly to allow Supabase to process the URL
      setTimeout(async () => {
        try {
          // Get the current session
          const { data: { session } } = await supabase.auth.getSession();
          
          if (session) {
            // Verify the token on the backend using fetchApi
            const data = await fetchApi("auth/verify", {
              method: "POST",
              body: JSON.stringify({ access_token: session.access_token }),
            });
            // store username name in local storage data.user.user_metadata.full_name
            localStorage.setItem("username", data.user.user_metadata.full_name);
            
            // Redirect to main app after verification
            this.$router.push("/");
          } else {
            console.error("No active session found");
            this.$router.push("/auth");
          }
        } catch (err) {
          console.error("Auth callback error:", err);
          this.$router.push("/auth");
        }
      }, 500);
    },
  };
  </script>