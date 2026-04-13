<template>
  <Card>
    <template #header>
      <Avatar :image="imageSrc" shape="circle" />
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

<style scoped>
.p-card {
  height: 380px;
  width: 260px;
  padding: 24px;
}

:deep(.p-card-title),
:deep(.p-card-content) {
  text-align: center;
}

:deep(.p-card-title) {
  color: #025ea1;
}

.p-avatar {
  width: 100%;
  height: 100%;
  border: 1px solid #025ea1;
}
</style>
