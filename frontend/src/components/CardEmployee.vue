<template>
  <Card
    :pt="{
      root: 'h-[380px] w-[260px] p-6 flex flex-col',
      header: 'min-h-0',
      title: 'text-center text-brand-500',
      content: 'text-center',
    }"
  >
    <template #header>
      <Avatar
        :image="imageSrc"
        shape="circle"
        class="border border-brand-500"
        :pt="{ image: 'h-full w-full' }"
      />
    </template>
    <template #title>{{ surname }} {{ name }} {{ patronymic }}</template>
    <template #content>{{ position }}</template>
  </Card>
</template>

<script setup>
import Card from 'primevue/card'
import Avatar from 'primevue/avatar'

defineProps(['imageSrc', 'surname', 'name', 'patronymic', 'position'])
</script>
