<template>
  <Drawer v-model:visible="visible" position="right" header="Боковая панель">
    <div class="flex flex-col justify-center gap-2.5">
      <Button variant="outlined" class="w-full flex-1 justify-start whitespace-normal text-left">
        <PhCornersOut :size="32" weight="duotone" />
        Полноэкранный режим
      </Button>
      <Button variant="outlined" class="w-full flex-1 justify-start whitespace-normal text-left">
        <PhSlideshow :size="32" weight="duotone" />
        Слайд-шоу
      </Button>
      <Button variant="outlined" class="w-full flex-1 justify-start whitespace-normal text-left">
        <PhPencilSimple :size="32" weight="duotone" />
        Слайд-шоу
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
      <Button variant="outlined" class="w-full flex-1 justify-start whitespace-normal text-left">
        <PhBookmark :size="32" weight="duotone" />
        Управление тегами
      </Button>
      <Button variant="outlined" class="w-full flex-1 justify-start whitespace-normal text-left">
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
</script>
