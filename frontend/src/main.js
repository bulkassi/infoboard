import './assets/tailwind.css'
import './assets/base.css'
import 'quill/dist/quill.snow.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ConfirmationService from 'primevue/confirmationservice'
import { MyPreset } from './assets/myPreset'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(PrimeVue, {
  theme: {
    preset: MyPreset,
    options: {
      darkModeSelector: false,
    },
  },
})
app.use(ConfirmationService)
app.use(router)

app.mount('#app')
