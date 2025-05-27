import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'ai.sitchat.app',
  appName: 'Sitchat',
  webDir: 'dist',
  plugins: {
    "Keyboard": {
      "resize": "body"
    }
  }
};

export default config;
