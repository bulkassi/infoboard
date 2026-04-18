<script setup>
import AppFooter from './components/layout/AppFooter.vue'
import AppHeader from './components/layout/AppHeader.vue'
</script>

<template>
  <AppHeader />
  <main class="flex flex-1 align-center justify-center min-h-0 w-full px-[120px] py-10">
    <RouterView />
  </main>
  <AppFooter />
</template>
