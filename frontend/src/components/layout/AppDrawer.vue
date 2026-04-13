<template>
  <Drawer v-model:visible="visible" position="right" header="Боковая панель">
    <div class="drawer-content">
      <Button variant="outlined">
        <PhCornersOut :size="32" weight="duotone" />
        Полноэкранный режим
      </Button>
      <Button variant="outlined">
        <PhSlideshow :size="32" weight="duotone" />
        Слайд-шоу
      </Button>
      <Button variant="outlined">
        <PhPencilSimple :size="32" weight="duotone" />
        Слайд-шоу
      </Button>
      <Button variant="outlined">
        <PhShareFat :size="32" weight="duotone" />
        Поделиться доской
      </Button>
      <Button variant="outlined">
        <PhPlusSquare :size="32" weight="duotone" />
        Добавить карточку
      </Button>
      <Button variant="outlined">
        <PhStack :size="32" weight="duotone" />
        Настроить положение карточек
      </Button>
      <Button variant="outlined">
        <PhBookmark :size="32" weight="duotone" />
        Управление тегами
      </Button>
      <Button variant="outlined">
        <PhAddressBookTabs :size="32" weight="duotone" />
        Администрирование
      </Button>
      <Button variant="outlined">
        <PhUserCircle :size="32" weight="duotone" />
        Настройки профиля
      </Button>
    </div>

    <template #footer>
      <Button variant="outlined" severity="danger">
        <PhSignOut :size="32" weight="duotone" />
        Выйти из аккаунта
      </Button>
    </template>
  </Drawer>
</template>

<script setup>
import { Drawer, Button } from 'primevue'
import {
  PhAddressBookTabs,
  PhBookmark,
  PhCornersOut,
  PhPencilSimple,
  PhPlusSquare,
  PhShareFat,
  PhSignOut,
  PhSlideshow,
  PhStack,
  PhUserCircle,
} from '@phosphor-icons/vue'

const visible = defineModel('visible')
</script>

<style scoped>
.drawer-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
}

:deep(.p-button) {
  width: 100%;
  justify-content: flex-start;

  text-align: left;
  white-space: normal; /* allow wrapping */
  flex: 1;
}
</style>
