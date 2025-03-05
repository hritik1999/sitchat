import { createClient } from "@supabase/supabase-js";

const supabaseUrl = "https://wpwichwnfgbpggcqujld.supabase.co";
const supabaseAnonKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indwd2ljaHduZmdicGdnY3F1amxkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA2NjAzMDcsImV4cCI6MjA1NjIzNjMwN30.y0QCwf--milc8b-3TjJvE-hHIFPKm8QqONFI8m7AjL4";

// Create Supabase client with persistent sessions
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
    storage: {
      getItem: (key) => {
        try {
          return JSON.parse(localStorage.getItem(key) || '');
        } catch {
          return null;
        }
      },
      setItem: (key, value) => {
        localStorage.setItem(key, JSON.stringify(value));
      },
      removeItem: (key) => {
        localStorage.removeItem(key);
      },
    }
  }
});