// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import { supabase } from '@/composables/useSupabase';
import AuthPage from '@/views/AuthPage.vue';
import AuthCallback from '@/views/AuthCallback.vue';
import ChatPage from '@/views/ChatPage.vue';
import ShowPage from '@/views/ShowPage.vue';
import CreateShow from '@/views/CreateShow.vue';
import ShowDetailsPage from '@/views/ShowDetailsPage.vue';
import CreateEpisode from '@/views/CreateEpisode.vue';
import Profile from '@/views/Profile.vue';
import EditProfile from '@/views/EditProfile.vue';
import End from '@/views/End.vue';
import ChatHistoryPage from '@/views/ChatHistory.vue';
import LeaderboardPage from '@/views/Leaderboard.vue';
import About from '@/pages/about.vue';
import Terms from '@/pages/terms.vue';
import Privacy from '@/pages/privacy.vue';
import Blogs from '@/pages/blogs.vue';
import createShowBlog from '@/pages/create-show-blog.vue';
import createEpisodeBlog from '@/pages/create-episode-blog.vue';
import Career from '@/pages/career.vue';
import resetPassword from '@/views/resetPassword.vue';    
import ogDefault from '@/assets/og_default.jpg'
// Define routes with meta for layout and auth requirements
const DEFAULT_OG_IMAGE = ogDefault
const SITE_NAME = 'Sitchat'
const SITE_DESC = `Sitchat is an interactive storytelling platform where you don’t just watch — you participate in your favorite shows by diving into immersive group chats with AI characters. Experience stories like never before.`

const routes = [
  {
    path: '/',
    name: 'Home',
    component: ShowPage,
    meta: {
      requiresAuth: false,
      layout: 'main',
      title: `${SITE_NAME} – Home`,
      description: SITE_DESC,
      ogTitle: `${SITE_NAME} – Home`,
      ogDescription: SITE_DESC,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/about',
    name: 'About',
    component: About,
    meta: {
      requiresAuth: false,
      layout: 'main',
      title: `About – ${SITE_NAME}`,
      description: `Learn more about ${SITE_NAME}—our mission, team, and how we’re redefining interactive storytelling.`,
      ogTitle: `About – ${SITE_NAME}`,
      ogDescription: `Learn more about ${SITE_NAME}—our mission, team, and how we’re redefining interactive storytelling.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/blogs',
    name: 'Blogs',
    component: Blogs,
    meta: {
      requiresAuth: false,
      layout: 'main',
      title: `Blog – ${SITE_NAME}`,
      description: `Read tips, updates, and behind-the-scenes on building immersive AI stories on ${SITE_NAME}.`,
      ogTitle: `Blog – ${SITE_NAME}`,
      ogDescription: `Read tips, updates, and behind-the-scenes on building immersive AI stories on ${SITE_NAME}.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/career',
    name: 'Career',
    component: Career,
    meta: {
      requiresAuth: false,
      layout: 'main',
      title: `Careers – ${SITE_NAME}`,
      description: `Join the ${SITE_NAME} team and help build the next generation of interactive entertainment.`,
      ogTitle: `Careers – ${SITE_NAME}`,
      ogDescription: `Join the ${SITE_NAME} team and help build the next generation of interactive entertainment.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/blog/create-show',
    name: 'CreateShowBlog',
    component: createShowBlog,
    meta: {
      requiresAuth: false,
      layout: 'main',
      title: `How to Create a Show – ${SITE_NAME} Blog`,
      description: `Step-by-step guide to creating your own AI-powered interactive show on ${SITE_NAME}.`,
      ogTitle: `How to Create a Show – ${SITE_NAME} Blog`,
      ogDescription: `Step-by-step guide to creating your own AI-powered interactive show on ${SITE_NAME}.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/blog/create-episode',
    name: 'CreateEpisodeBlog',
    component: createEpisodeBlog,
    meta: {
      requiresAuth: false,
      layout: 'main',
      title: `How to Design an Episode – ${SITE_NAME} Blog`,
      description: `Learn how to craft engaging episodes with clear objectives and AI characters on ${SITE_NAME}.`,
      ogTitle: `How to Design an Episode – ${SITE_NAME} Blog`,
      ogDescription: `Learn how to craft engaging episodes with clear objectives and AI characters on ${SITE_NAME}.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/terms',
    name: 'Terms',
    component: Terms,
    meta: {
      requiresAuth: false,
      layout: 'main',
      title: `Terms of Service – ${SITE_NAME}`,
      description: `Review the Terms of Service for ${SITE_NAME}, your interactive storytelling playground.`,
      ogTitle: `Terms of Service – ${SITE_NAME}`,
      ogDescription: `Review the Terms of Service for ${SITE_NAME}, your interactive storytelling playground.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/privacy',
    name: 'Privacy',
    component: Privacy,
    meta: {
      requiresAuth: false,
      layout: 'main',
      title: `Privacy Policy – ${SITE_NAME}`,
      description: `Learn how ${SITE_NAME} protects your data and respects your privacy.`,
      ogTitle: `Privacy Policy – ${SITE_NAME}`,
      ogDescription: `Learn how ${SITE_NAME} protects your data and respects your privacy.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: AuthPage,
    meta: {
      requiresAuth: false,
      layout: 'none',
      title: `Login – ${SITE_NAME}`,
      description: `Sign in to ${SITE_NAME} and start creating or joining immersive AI story chats.`,
      ogTitle: `Login – ${SITE_NAME}`,
      ogDescription: `Sign in to ${SITE_NAME} and start creating or joining immersive AI story chats.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: AuthCallback,
    meta: {
      requiresAuth: false,
      layout: 'none',
      title: `Authenticating – ${SITE_NAME}`,
      description: `Completing your sign-in to ${SITE_NAME}. Please wait…`,
      ogTitle: `Authenticating – ${SITE_NAME}`,
      ogDescription: `Completing your sign-in to ${SITE_NAME}. Please wait…`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: resetPassword,
    meta: {
      requiresAuth: false,
      layout: 'none',
      title: `Reset Password – ${SITE_NAME}`,
      description: `Enter your email to reset your ${SITE_NAME} account password.`,
      ogTitle: `Reset Password – ${SITE_NAME}`,
      ogDescription: `Enter your email to reset your ${SITE_NAME} account password.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/shows',
    name: 'Shows',
    component: ShowPage,
    meta: {
      requiresAuth: false,
      layout: 'main',
      title: `All Shows – ${SITE_NAME}`,
      description: `Browse user-created shows and AI-driven experiences on ${SITE_NAME}.`,
      ogTitle: `All Shows – ${SITE_NAME}`,
      ogDescription: `Browse user-created shows and AI-driven experiences on ${SITE_NAME}.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/show/:show_id/chat/:chat_id',
    name: 'Chat',
    component: ChatPage,
    meta: {
      requiresAuth: true,
      layout: 'none',
      // these can be updated dynamically in afterEach using to.params
      title: `Chat – Immersive Story`,
      description: `Dive into the chat for this story episode with our AI characters on ${SITE_NAME}.`,
      ogTitle: `Chat – Immersive Story`,
      ogDescription: `Dive into the chat for this story episode with our AI characters on ${SITE_NAME}.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/create/show',
    name: 'CreateShow',
    component: CreateShow,
    meta: {
      requiresAuth: true,
      layout: 'main',
      title: `Create a New Show – ${SITE_NAME}`,
      description: `Give your show a name, description, and characters—and bring it to life on ${SITE_NAME}.`,
      ogTitle: `Create a New Show – ${SITE_NAME}`,
      ogDescription: `Give your show a name, description, and characters—and bring it to life on ${SITE_NAME}.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/show/:id',
    name: 'ShowDetails',
    component: ShowDetailsPage,
    meta: {
      requiresAuth: false,
      layout: 'main',
      title: `Show Details – ${SITE_NAME}`,
      description: `View episode list, descriptions, and join the chat for this ${SITE_NAME} show.`,
      ogTitle: `Show Details – ${SITE_NAME}`,
      ogDescription: `View episode list, descriptions, and join the chat for this ${SITE_NAME} show.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/create/episode/:id',
    name: 'CreateEpisode',
    component: CreateEpisode,
    meta: {
      requiresAuth: true,
      layout: 'main',
      title: `Craft a New Episode – ${SITE_NAME}`,
      description: `Define plot objectives and AI character actions for your next episode on ${SITE_NAME}.`,
      ogTitle: `Craft a New Episode – ${SITE_NAME}`,
      ogDescription: `Define plot objectives and AI character actions for your next episode on ${SITE_NAME}.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/edit/episode/:showId/:episodeId',
    name: 'EditEpisode',
    component: CreateEpisode,
    meta: {
      requiresAuth: true,
      layout: 'main',
      title: `Edit Episode – ${SITE_NAME}`,
      description: `Update objectives, story beats, or characters for this episode on ${SITE_NAME}.`,
      ogTitle: `Edit Episode – ${SITE_NAME}`,
      ogDescription: `Update objectives, story beats, or characters for this episode on ${SITE_NAME}.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/edit/show/:showId',
    name: 'EditShow',
    component: CreateShow,
    meta: {
      requiresAuth: true,
      layout: 'main',
      title: `Edit Show – ${SITE_NAME}`,
      description: `Change your show’s name, description, or characters on ${SITE_NAME}.`,
      ogTitle: `Edit Show – ${SITE_NAME}`,
      ogDescription: `Change your show’s name, description, or characters on ${SITE_NAME}.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: {
      requiresAuth: true,
      layout: 'main',
      title: `Your Profile – ${SITE_NAME}`,
      description: `View and manage your shows, episodes, and chat history on ${SITE_NAME}.`,
      ogTitle: `Your Profile – ${SITE_NAME}`,
      ogDescription: `View and manage your shows, episodes, and chat history on ${SITE_NAME}.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/edit/profile',
    name: 'EditProfile',
    component: EditProfile,
    meta: {
      requiresAuth: true,
      layout: 'main',
      title: `Edit Profile – ${SITE_NAME}`,
      description: `Update your username, avatar, or bio for your ${SITE_NAME} account.`,
      ogTitle: `Edit Profile – ${SITE_NAME}`,
      ogDescription: `Update your username, avatar, or bio for your ${SITE_NAME} account.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/chat/history',
    name: 'ChatHistory',
    component: ChatHistoryPage,
    meta: {
      requiresAuth: true,
      layout: 'main',
      title: `Chat History – ${SITE_NAME}`,
      description: `Review past chats and story progress in your ${SITE_NAME} account.`,
      ogTitle: `Chat History – ${SITE_NAME}`,
      ogDescription: `Review past chats and story progress in your ${SITE_NAME} account.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/leaderboard',
    name: 'Leaderboard',
    component: LeaderboardPage,
    meta: {
      requiresAuth: false,
      layout: 'main',
      title: `Leaderboard – ${SITE_NAME}`,
      description: `See the top storytellers and most-played shows on ${SITE_NAME}.`,
      ogTitle: `Leaderboard – ${SITE_NAME}`,
      ogDescription: `See the top storytellers and most-played shows on ${SITE_NAME}.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  },
  {
    path: '/end/:chat_id',
    name: 'End',
    component: End,
    meta: {
      requiresAuth: true,
      layout: 'main',
      title: `End of Chat – ${SITE_NAME}`,
      description: `This chat session has ended. See your story wrap-up and next steps on ${SITE_NAME}.`,
      ogTitle: `End of Chat – ${SITE_NAME}`,
      ogDescription: `This chat session has ended. See your story wrap-up and next steps on ${SITE_NAME}.`,
      ogImage: DEFAULT_OG_IMAGE,
      twitterCard: 'summary_large_image'
    }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Global navigation guard for authentication
router.beforeEach(async (to, from, next) => {
  // Check if the route requires authentication
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  
  // Get current session
  const { data, error } = await supabase.auth.getSession();
  const session = data?.session;
  
  // For debugging
  console.log('Route:', to.path, 'Auth required:', requiresAuth, 'Session exists:', !!session);
  
  if (requiresAuth && !session) {
    // Redirect to login if authentication is required but user is not logged in
    console.log('Redirecting to login, auth required but no session');
    return next('/login');
  } else if (to.path === '/login' && session) {
    // Redirect to home if user is already logged in and tries to access login page
    console.log('Redirecting to home, user is logged in but trying to access login');
    return next('/');
  } else {
    // Proceed as normal
    console.log('Proceeding to route:', to.path);
    return next();
  }
});

router.afterEach((to) => {
  // Helper function to update or create meta tag
  const updateMetaTag = (selector, attribute, attributeName, content) => {
    let tag = document.querySelector(selector);
    if (!tag) {
      tag = document.createElement('meta');
      tag.setAttribute(attribute, attributeName);
      document.head.appendChild(tag);
    }
    tag.setAttribute('content', content);
  };

  // 1) Document title
  if (to.meta.title) {
    document.title = to.meta.title;
  }

  // 2) Meta description
  if (to.meta.description) {
    updateMetaTag('meta[name="description"]', 'name', 'description', to.meta.description);
  }

  // 3) Open Graph title
  if (to.meta.ogTitle) {
    updateMetaTag('meta[property="og:title"]', 'property', 'og:title', to.meta.ogTitle);
  }

  // 4) Open Graph description
  if (to.meta.ogDescription) {
    updateMetaTag('meta[property="og:description"]', 'property', 'og:description', to.meta.ogDescription);
  }

  // 5) Open Graph image
  if (to.meta.ogImage) {
    updateMetaTag('meta[property="og:image"]', 'property', 'og:image', to.meta.ogImage);
  }

  // 6) Open Graph type (default to 'website' if not specified)
  const ogType = to.meta.ogType || 'website';
  updateMetaTag('meta[property="og:type"]', 'property', 'og:type', ogType);

  // 7) Open Graph URL (current page URL)
  const ogUrl = window.location.href;
  updateMetaTag('meta[property="og:url"]', 'property', 'og:url', ogUrl);

  // 8) Open Graph site name
  updateMetaTag('meta[property="og:site_name"]', 'property', 'og:site_name', SITE_NAME);

  // 9) Twitter card type
  if (to.meta.twitterCard) {
    updateMetaTag('meta[name="twitter:card"]', 'name', 'twitter:card', to.meta.twitterCard);
  }

  // 10) Twitter title (use ogTitle or title as fallback)
  const twitterTitle = to.meta.twitterTitle || to.meta.ogTitle || to.meta.title;
  if (twitterTitle) {
    updateMetaTag('meta[name="twitter:title"]', 'name', 'twitter:title', twitterTitle);
  }

  // 11) Twitter description (use ogDescription or description as fallback)
  const twitterDescription = to.meta.twitterDescription || to.meta.ogDescription || to.meta.description;
  if (twitterDescription) {
    updateMetaTag('meta[name="twitter:description"]', 'name', 'twitter:description', twitterDescription);
  }

  // 12) Twitter image (use ogImage as fallback)
  const twitterImage = to.meta.twitterImage || to.meta.ogImage;
  if (twitterImage) {
    updateMetaTag('meta[name="twitter:image"]', 'name', 'twitter:image', twitterImage);
  }

  // 13) Twitter site handle (if you have one)
  if (to.meta.twitterSite) {
    updateMetaTag('meta[name="twitter:site"]', 'name', 'twitter:site', to.meta.twitterSite);
  }

  // 14) Twitter creator handle (if specified)
  if (to.meta.twitterCreator) {
    updateMetaTag('meta[name="twitter:creator"]', 'name', 'twitter:creator', to.meta.twitterCreator);
  }

  // 15) Canonical URL (helps with SEO)
  let canonical = document.querySelector('link[rel="canonical"]');
  if (!canonical) {
    canonical = document.createElement('link');
    canonical.setAttribute('rel', 'canonical');
    document.head.appendChild(canonical);
  }
  canonical.setAttribute('href', window.location.href);

  // 16) Additional meta tags if specified
  if (to.meta.keywords) {
    updateMetaTag('meta[name="keywords"]', 'name', 'keywords', to.meta.keywords);
  }

  if (to.meta.author) {
    updateMetaTag('meta[name="author"]', 'name', 'author', to.meta.author);
  }

  if (to.meta.robots) {
    updateMetaTag('meta[name="robots"]', 'name', 'robots', to.meta.robots);
  }

  // 17) Viewport meta tag (if not already set globally)
  if (!document.querySelector('meta[name="viewport"]')) {
    updateMetaTag('meta[name="viewport"]', 'name', 'viewport', 'width=device-width, initial-scale=1.0');
  }

  // 18) Theme color (if specified)
  if (to.meta.themeColor) {
    updateMetaTag('meta[name="theme-color"]', 'name', 'theme-color', to.meta.themeColor);
  }

  // Dispatch the render event (keeping your existing functionality)
  document.dispatchEvent(new Event('render-event'));
});

export default router;