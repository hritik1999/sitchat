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
  const head = document.head

  // Helper to upsert a meta tag
  function upsertMeta(attrName, attrValue, content) {
    let tag = head.querySelector(`meta[${attrName}="${attrValue}"]`)
    if (!tag) {
      tag = document.createElement('meta')
      tag.setAttribute(attrName, attrValue)
      head.appendChild(tag)
    }
    tag.setAttribute('content', content)
  }

  // standard description (not used by previews but good for SEO)
  if (to.meta.description) {
    upsertMeta('name', 'description', to.meta.description)
  }

  // Open Graph
  if (to.meta.ogTitle)       upsertMeta('property', 'og:title',       to.meta.ogTitle)
  if (to.meta.ogDescription) upsertMeta('property', 'og:description', to.meta.ogDescription)
  if (to.meta.ogImage)       upsertMeta('property', 'og:image',       to.meta.ogImage)

  // Twitter
  if (to.meta.twitterCard)        upsertMeta('name', 'twitter:card',        to.meta.twitterCard)
  if (to.meta.ogTitle)            upsertMeta('name', 'twitter:title',       to.meta.ogTitle)
  if (to.meta.ogDescription)      upsertMeta('name', 'twitter:description', to.meta.ogDescription)
  if (to.meta.ogImage)            upsertMeta('name', 'twitter:image',       to.meta.ogImage)

  document.dispatchEvent(new Event('render-event'))
})

export default router;