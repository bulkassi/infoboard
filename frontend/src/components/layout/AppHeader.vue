<template>
  <header class="app-header">
    <div class="logo-container">
      <img src="/src/assets/Greenatom_horizont_rus_blue.png" alt="Logo" class="logo" />
    </div>
    <nav class="boards-links">
      <Button as="RouterLink" variant="text" to="/main">Главная</Button>
      <Button as="RouterLink" variant="text" to="/">О нас</Button>
      <Button as="RouterLink" variant="text" to="/employees">Сотрудники</Button>
      <Button as="RouterLink" variant="text" to="/services">Сервисы</Button>
      <Select placeholder="Выбрать доску" :options="boards" optionLabel="name" filter>
        <template #dropdownicon>
          <PhChalkboardSimple weight="duotone" :size="20" />
        </template>

        <template #option="slotProps">
          <div class="board-option">
            <span class="board-option-name">{{ slotProps.option.name }}</span>
            <small class="board-option-owner">{{ slotProps.option.owner }}</small>
          </div>
        </template>

        <template #footer>
          <div style="padding: 0px 8px 4px 8px">
            <Button variant="text" class="add-board-btn">
              <PhPlusCircle :size="16" />
              Добавить доску
            </Button>
          </div>
        </template>
      </Select>
    </nav>

    <div class="action-btns">
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

<style scoped>
.app-header {
  padding-left: 120px;
  padding-right: 120px;

  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logo-container {
  margin: 8px;
  display: flex;
  align-items: center;
}

.logo {
  height: 60px;
  width: auto;
}

.boards-links {
  height: 100%;

  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  flex-grow: 1;
}

.action-btns {
  /* Ширина .logo-container */
  width: 190px;

  display: flex;
  justify-content: flex-end;
}

.board-option {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.board-option-name {
  font-size: 20px;
  font-weight: 500;
  color: #025ea1;
}

.board-option-owner {
  font-size: 12px;
  color: #888888;
}

.add-board-btn {
  width: 100%;

  display: flex;
  align-items: center;
  gap: 5px;
}
</style>
