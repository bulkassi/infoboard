<template>
  <Button as="a" :href="link" target="_blank" rel="noopener" unstyled>
    <Card
      :pt="{
        root: 'flex h-[160px] w-[460px] flex-row items-center gap-4 p-6 bg-(--p-card-background) text-(--p-card-color) shadow-(--p-card-shadow) border-(--pa-card-border-radius)',
        header: 'h-full aspect-square shrink-0',
        body: 'flex flex-1 flex-col justify-center text-left',
        title: 'text-left text-brand-500',
        content: 'text-left',
      }"
      unstyled
    >
      <template #header>
        <div class="h-full w-full overflow-hidden rounded-[10%]">
          <img :src="imageSrc" alt="Логотип сервиса" class="block h-full w-full object-cover" />
        </div>
      </template>
      <template #title>{{ serviceName }}</template>
      <template #content>{{ serviceDesc }}</template>
    </Card>
  </Button>
</template>

<script setup>
import Button from 'primevue/button'
import Card from 'primevue/card'

defineProps(['link', 'imageSrc', 'serviceName', 'serviceDesc'])
</script>
