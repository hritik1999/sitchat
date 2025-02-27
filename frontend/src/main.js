import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Toast, { POSITION } from 'vue-toastification'
import './assets/index.css'

// Import toast styles
import 'vue-toastification/dist/index.css'

// Create the app
const app = createApp(App)

// Configure toast
const toastOptions = {
  position: POSITION.TOP_RIGHT,
  timeout: 5000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: 'button',
  icon: true,
  rtl: false
}

// Use plugins
app.use(router)
app.use(Toast, toastOptions)

// Mount the app
app.mount('#app')