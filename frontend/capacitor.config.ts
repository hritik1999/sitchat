import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'ai.sitchat.app',
  appName: 'Sitchat',
  webDir: 'dist',
    server: {
    allowNavigation: ['https://wpwichwnfgbpggcqujld.supabase.co','https://*.supabase.co'],
     hostname: 'sitchat',
    iosScheme: 'capacitor'
  },
  ios: {
    limitsNavigationsToAppBoundDomains: false, // Critical for iOS
    preferredContentMode: 'mobile',
    scheme: 'App'
  },
  plugins: {
    "keyboard": {
      "resize": "body"
    }
  }
};

export default config;
