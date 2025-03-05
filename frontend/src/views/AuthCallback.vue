<template>
    <div>Processing authentication...</div>
  </template>
  
  <script>
  export default {
    name: "AuthCallback",
    data() {
      return {
        API_BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:5001'
      };
    },
    created() {
      // Extract the access token from the URL fragment
      const hash = window.location.hash.slice(1);
      const params = new URLSearchParams(hash);
      const accessToken = params.get("access_token");
      
      if (accessToken) {
        // Save it locally or update your auth state
        localStorage.setItem("supabase_session", JSON.stringify({ access_token: accessToken }));
        
        // Optionally, verify the token on the backend:
        fetch("" + this.API_BASE_URL + "/auth/verify", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ access_token: accessToken }),
        })
        .then((res) => res.json())
        .then((data) => {
          console.log("Backend verification:", data);
          // Redirect to your main app/dashboard after verification
          this.$router.push("/");
        })
        .catch((err) => console.error("Verification error:", err));
      } else {
        console.error("Access token not found.");
        this.$router.push("/login");
      }
    },
  };
  </script>