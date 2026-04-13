<template>
  <Button class="service-button" as="a" :href="link" target="_blank" rel="noopener" unstyled>
    <Card>
      <template #header>
        <Avatar :image="imageSrc" shape="circle" />
      </template>
      <template #title>{{ serviceName }}</template>
      <template #content>{{ serviceDesc }}</template>
    </Card>
  </Button>
</template>

<script setup>
import Button from 'primevue/button'
import Card from 'primevue/card'
import Avatar from 'primevue/avatar'

defineProps(['link', 'imageSrc', 'serviceName', 'serviceDesc'])
</script>

<style scoped>
:deep(.p-card) {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 16px;
  height: 160px;
  width: 460px;
  padding: 24px;
}

:deep(.p-card-header) {
  height: 100%;
  aspect-ratio: 1 / 1;
  flex: 0 0 auto;
}

:deep(.p-card-body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: left;
}

:deep(.p-card-title),
:deep(.p-card-content) {
  text-align: left;
}

:deep(.p-avatar) {
  width: 100%;
  height: 100%;
}

:deep(.p-card-title) {
  color: #025ea1;
}

.p-avatar {
  width: 100%;
  height: 100%;
}
</style>
