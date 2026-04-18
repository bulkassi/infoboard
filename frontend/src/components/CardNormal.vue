<template>
  <Card
    :pt="{
      root: 'p-1',
      title: 'text-brand-500',
    }"
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
  </Card>
</template>

<script setup>
import Card from 'primevue/card'
import Image from 'primevue/image'

defineProps(['imageSrc', 'title', 'content'])
</script>
