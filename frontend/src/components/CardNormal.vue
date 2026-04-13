<template>
  <Card>
    <template #header>
      <Image imageStyle="border-radius: 8px;" :src="imageSrc" alt="" width="100%" preview />
    </template>
    <template #title>{{ title }}</template>
    <template #content>{{ content }}</template>
  </Card>
</template>

<script setup>
import Card from 'primevue/card'
import Image from 'primevue/image'

defineProps(['imageSrc', 'title', 'content'])
</script>

<style scoped>
.p-card {
  padding: 4px;
}

.p-card-header {
  border-radius: 4px;
}

:deep(.p-card-title) {
  color: #025ea1;
}

.p-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
