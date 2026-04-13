<script setup>
import AppFooter from './components/layout/AppFooter.vue'
import AppHeader from './components/layout/AppHeader.vue'
</script>

<template>
  <AppHeader />
  <main class="main-content">
    <RouterView />
  </main>
  <AppFooter />
</template>

<style scoped>
.main-content {
  padding: 40px 120px;
}
</style>
