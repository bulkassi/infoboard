<template>
  <Card
    :pt="{
      root: 'p-1 h-full flex flex-col min-h-0',
      body: 'flex flex-col flex-1 min-h-0',
      content: 'flex-1 min-h-0 overflow-auto',
      title: 'text-brand-500',
    }"
    class="card-normal h-full w-full overflow-hidden"
  >
    <template #header>
      <Image
        class="w-full rounded"
        imageStyle="border-radius: 8px; width: 100%; height: 100%; object-fit: cover;"
        :src="imageSrc"
        alt=""
        width="100%"
        preview
      />
    </template>
    <template #title>{{ title }}</template>
    <template #content>{{ content }}</template>
    <template #footer>
      <InfoTag text="Важная информация" textColor="ffffff" bgColor="025EA1" />
    </template>
  </Card>
</template>

<script setup>
import Card from 'primevue/card'
import Image from 'primevue/image'
import InfoTag from './tags/InfoTag.vue'

defineProps(['imageSrc', 'title', 'content'])
</script>

<style scoped>
.card-normal {
  min-height: 0;
}
</style>
