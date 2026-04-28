<script setup>
import { useRoute } from 'vue-router'
import { Message } from 'primevue'
import { useAuthStore } from '@/stores/auth'
import AppFooter from './components/layout/AppFooter.vue'
import AppHeader from './components/layout/AppHeader.vue'

const route = useRoute()
const authStore = useAuthStore()
</script>

<template>
  <AppHeader v-if="route.name !== 'login'" />
  <main class="flex flex-1 flex-col align-center justify-start min-h-0 w-full px-[120px] py-10">
    <Message
      v-if="!authStore.isAuthenticated && route.name !== 'login'"
      severity="info"
      :closable="false"
      class="mb-6 w-full"
    >
      Режим гостя. Для доступа к пользовательским доскам и настройкам, пожалуйста,
      <RouterLink to="/login" class="font-bold underline">войдите в систему</RouterLink>.
    </Message>
    <div class="flex flex-1 justify-center w-full">
      <RouterView />
    </div>
  </main>
  <AppFooter v-if="route.name !== 'login'" />
</template>
