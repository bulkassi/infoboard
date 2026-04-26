<template>
  <Card
    :pt="{
      root: 'h-[380px] w-[260px] p-6 flex flex-col',
      header: 'min-h-0 p-0 overflow-hidden',
      title: 'text-center text-brand-500',
      content: 'text-center',
    }"
  >
    <template #header>
      <div class="aspect-square w-full overflow-hidden rounded-full border border-brand-500">
        <img :src="imageSrc" alt="Фото сотрудника" class="block h-full w-full object-cover" />
      </div>
    </template>
    <template #title>{{ surname }} {{ name }} {{ patronymic }}</template>
    <template #content>{{ position }}</template>
  </Card>
</template>

<script setup>
import Card from 'primevue/card'

defineProps(['imageSrc', 'surname', 'name', 'patronymic', 'position'])
</script>
