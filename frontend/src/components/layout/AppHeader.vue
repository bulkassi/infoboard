<template>
  <header
    class="flex items-center justify-between bg-white px-[120px] shadow-[0_2px_4px_rgba(0,0,0,0.1)]"
  >
    <div class="m-2 flex items-center">
      <img src="/src/assets/Greenatom_horizont_rus_blue.png" alt="Logo" class="h-[60px] w-auto" />
    </div>
    <nav class="flex h-full flex-1 items-center justify-center gap-2.5">
      <Button as="RouterLink" variant="text" to="/main">Главная</Button>
      <Button as="RouterLink" variant="text" to="/">О нас</Button>
      <Button as="RouterLink" variant="text" to="/employees">Сотрудники</Button>
      <Button as="RouterLink" variant="text" to="/services">Сервисы</Button>
      <Select placeholder="Выбрать доску" :options="boards" optionLabel="name" filter>
        <template #dropdownicon>
          <PhChalkboardSimple weight="duotone" :size="20" />
        </template>

        <template #option="slotProps">
          <div class="flex flex-col gap-0">
            <span class="text-[20px] font-medium text-brand-500">{{ slotProps.option.name }}</span>
            <small class="text-xs text-[#888888]">{{ slotProps.option.owner }}</small>
          </div>
        </template>

        <template #footer>
          <div class="px-2 pb-1">
            <Button variant="text" class="flex w-full items-center gap-[5px]">
              <PhPlusCircle :size="16" />
              Добавить доску
            </Button>
          </div>
        </template>
      </Select>
    </nav>

    <div class="flex w-[190px] justify-end">
      <Button variant="text" @click="isDrawerOpen = true">
        <PhList :size="32" weight="bold" />
      </Button>
    </div>
  </header>

  <AppDrawer v-model:visible="isDrawerOpen" />
</template>

<script setup>
import { ref } from 'vue'

import { PhChalkboardSimple, PhList, PhPlusCircle } from '@phosphor-icons/vue'
import { Button, Select } from 'primevue'

import AppDrawer from './AppDrawer.vue'

const isDrawerOpen = ref(false)

const boards = ref([
  { name: 'Доска 1', owner: 'Пользователь 1' },
  { name: 'Доска 2', owner: 'Пользователь 2' },
])
</script>
