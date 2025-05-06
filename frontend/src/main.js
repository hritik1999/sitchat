import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
// Import the Toast plugin and its styles
import Toast from 'vue-toastification';
import 'vue-toastification/dist/index.css';
import './assets/index.css'
import VueGtag from 'vue-gtag-next';

const app = createApp(App);

app.use(router);
app.use(Toast);
app.use(VueGtag, {
    config: { id: 'G-K30HLVRLW4' }
  })

app.mount('#app');
