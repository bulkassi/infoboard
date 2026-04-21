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
      <Button
        v-if="!boardsStore.isLayoutEditMode"
        variant="outlined"
        class="w-full flex-1 justify-start whitespace-normal text-left"
        :disabled="!isMainBoardRoute || !isDesktop"
        @click="beginBoardLayoutEdit"
      >
        <PhStack :size="32" weight="duotone" />
        Настроить положение карточек
      </Button>
      <div
        v-else-if="isMainBoardRoute"
        class="flex flex-col gap-3 rounded-md border border-slate-300 bg-slate-50 p-3"
      >
        <p class="text-sm font-medium text-slate-700">Параметры сетки карточек</p>
        <label class="flex flex-col gap-1 text-xs text-slate-600" for="grid-rows-input">
          Количество рядов ({{ boardsStore.MIN_GRID_ROWS }}-{{ boardsStore.MAX_GRID_ROWS }})
          <input
            id="grid-rows-input"
            v-model.number="rowCount"
            :min="boardsStore.MIN_GRID_ROWS"
            :max="boardsStore.MAX_GRID_ROWS"
            type="number"
            class="rounded-md border border-slate-300 px-2 py-1 text-sm"
          />
        </label>

        <p v-if="rowCountError" class="text-xs text-red-600">
          {{ rowCountError }}
        </p>

        <div class="flex items-center gap-2">
          <Button size="small" @click="saveBoardLayoutEdit">Сохранить</Button>
          <Button
            size="small"
            severity="secondary"
            variant="outlined"
            @click="cancelBoardLayoutEdit"
            >Отменить</Button
          >
        </div>
      </div>
      <div
        v-else
        class="flex flex-col gap-2 rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-800"
      >
        <p>Режим редактирования карточек доступен только на странице "Главная".</p>
        <Button size="small" severity="secondary" variant="outlined" @click="cancelBoardLayoutEdit"
          >Выйти из редактирования</Button
        >
      </div>
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
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
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
import { useBoardsStore } from '@/stores/boards'

const visible = defineModel('visible')
const emit = defineEmits(['open-tag-manage', 'open-about-edit'])
const route = useRoute()
const boardsStore = useBoardsStore()
const BOARD_MAIN_ID = 0
const isDesktop = ref(false)
const rowCountError = ref('')

const isMainBoardRoute = computed(() => route.path === '/' || route.path === '/main')

const updateViewportState = () => {
  isDesktop.value = window.matchMedia('(min-width: 1024px)').matches
}

const rowCount = computed({
  get() {
    return boardsStore.getActiveGridSettings(BOARD_MAIN_ID).rows
  },
  set(value) {
    const changed = boardsStore.setDraftRowCount(BOARD_MAIN_ID, value)
    rowCountError.value = changed
      ? ''
      : 'Нельзя уменьшить количество рядов: карточки пересекутся после смещения вверх.'
  },
})

const closeDrawer = () => {
  visible.value = false
}

const beginBoardLayoutEdit = () => {
  rowCountError.value = ''
  boardsStore.beginLayoutEdit(BOARD_MAIN_ID)
}

const saveBoardLayoutEdit = () => {
  rowCountError.value = ''
  boardsStore.saveLayoutEdit(BOARD_MAIN_ID)
}

const cancelBoardLayoutEdit = () => {
  rowCountError.value = ''
  boardsStore.cancelLayoutEdit()
}

const openTagManageDialog = () => {
  closeDrawer()
  emit('open-tag-manage')
}

const openAboutEditDialog = () => {
  closeDrawer()
  emit('open-about-edit')
}

onMounted(() => {
  updateViewportState()
  window.addEventListener('resize', updateViewportState)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateViewportState)
})
</script>
