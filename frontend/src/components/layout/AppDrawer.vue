<template>
  <Drawer v-model:visible="visible" position="right" header="Боковая панель">
    <div class="flex flex-col justify-content gap-2">
      <Button variant="outlined" class="w-full flex-1 justify-start whitespace-normal text-left">
        <PhCornersOut :size="32" weight="duotone" />
        Полноэкранный режим
      </Button>
      <Button variant="outlined" class="w-full flex-1 justify-start whitespace-normal text-left">
        <PhSlideshow :size="32" weight="duotone" />
        Слайд-шоу
      </Button>
      <Button
        @click="openAboutEditDialog"
        variant="outlined"
        class="w-full flex-1 justify-start whitespace-normal text-left"
      >
        <PhPencilSimple :size="32" weight="duotone" />
        Редактировать About
      </Button>
      <Button variant="outlined" class="w-full flex-1 justify-start whitespace-normal text-left">
        <PhShareFat :size="32" weight="duotone" />
        Поделиться доской
      </Button>
      <Button variant="outlined" class="w-full flex-1 justify-start whitespace-normal text-left">
        <PhPlusSquare :size="32" weight="duotone" />
        Добавить карточку
      </Button>
      <Button variant="outlined" class="w-full flex-1 justify-start whitespace-normal text-left">
        <PhStack :size="32" weight="duotone" />
        Настроить положение карточек
      </Button>
      <Button
        @click="openTagManageDialog"
        variant="outlined"
        class="w-full flex-1 justify-start whitespace-normal text-left"
      >
        <PhBookmark :size="32" weight="duotone" />
        Управление тегами
      </Button>
      <Button
        as="RouterLink"
        to="/admin"
        @click="closeDrawer"
        variant="outlined"
        class="w-full flex-1 justify-start whitespace-normal text-left"
      >
        <PhAddressBookTabs :size="32" weight="duotone" />
        Администрирование
      </Button>
      <Button variant="outlined" class="w-full flex-1 justify-start whitespace-normal text-left">
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
const emit = defineEmits(['open-tag-manage', 'open-about-edit'])

const closeDrawer = () => {
  visible.value = false
}

const openTagManageDialog = () => {
  closeDrawer()
  emit('open-tag-manage')
}

const openAboutEditDialog = () => {
  closeDrawer()
  emit('open-about-edit')
}
</script>
