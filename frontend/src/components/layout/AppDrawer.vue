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
      <Button
        variant="outlined"
        class="w-full flex-1 justify-start whitespace-normal text-left"
        :disabled="!isUserBoardRoute"
        @click="openBoardRenameDialog"
      >
        <PhPencilSimple :size="32" weight="duotone" />
        Редактировать название доски
      </Button>
      <Button
        variant="outlined"
        severity="danger"
        class="w-full flex-1 justify-start whitespace-normal text-left"
        :disabled="!isUserBoardRoute"
        @click="confirmBoardDelete"
      >
        <PhTrash :size="32" weight="duotone" />
        Удалить доску
      </Button>
      <Button
        variant="outlined"
        class="w-full flex-1 justify-start whitespace-normal text-left"
        :disabled="!isCardBoardRoute"
        @click="openCardCreateDialog"
      >
        <PhPlusSquare :size="32" weight="duotone" />
        Добавить карточку
      </Button>
      <Button
        variant="outlined"
        class="w-full flex-1 justify-start whitespace-normal text-left"
        :disabled="!isCardBoardRoute"
        @click="openCardEditPicker"
      >
        <PhPencilSimple :size="32" weight="duotone" />
        Редактировать карточку
      </Button>
      <Button
        variant="outlined"
        severity="danger"
        class="w-full flex-1 justify-start whitespace-normal text-left"
        :disabled="!isCardBoardRoute"
        @click="openCardDeletePicker"
      >
        <PhTrash :size="32" weight="duotone" />
        Удалить карточку
      </Button>
      <Button
        v-if="!boardsStore.isLayoutEditMode"
        variant="outlined"
        class="w-full flex-1 justify-start whitespace-normal text-left"
        :disabled="!isLayoutEditableRoute || !isDesktop"
        @click="beginBoardLayoutEdit"
      >
        <PhStack :size="32" weight="duotone" />
        Изменить положение карточек
      </Button>
      <div
        v-else-if="isLayoutEditableRoute"
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
        <p>
          Режим редактирования карточек доступен только на страницах "Главная" и пользовательских
          досках.
        </p>
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
      <Button asChild variant="outlined" v-slot="slotProps">
        <RouterLink
          to="/admin"
          :class="[slotProps.class, 'w-full flex-1 justify-start whitespace-normal text-left']"
          @click="closeDrawer"
        >
          <PhAddressBookTabs :size="32" weight="duotone" />
          Администрирование
        </RouterLink>
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

    <Dialog v-model:visible="isBoardRenameDialogVisible" modal class="w-[28rem]">
      <template #header>
        <div class="inline-flex items-center gap-2">
          <PhPencilSimple :size="20" weight="duotone" />
          <span class="text-lg font-semibold">Редактирование доски</span>
        </div>
      </template>

      <div class="flex flex-col gap-3">
        <InputText
          v-model="boardNameDraft"
          type="text"
          placeholder="Название доски"
          :invalid="Boolean(boardNameError)"
        />
        <small v-if="boardNameError" class="text-red-600">{{ boardNameError }}</small>

        <div class="flex justify-end gap-2">
          <Button severity="secondary" @click="closeBoardRenameDialog">Отмена</Button>
          <Button @click="submitBoardRename">Сохранить</Button>
        </div>
      </div>
    </Dialog>

    <ConfirmDialog group="board-actions" />
  </Drawer>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Drawer, Button } from 'primevue'
import ConfirmDialog from 'primevue/confirmdialog'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import { useConfirm } from 'primevue/useconfirm'
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
  PhTrash,
  PhUserCircle,
} from '@phosphor-icons/vue'
import { useBoardsStore } from '@/stores/boards'
import {
  MAIN_BOARD_KEY,
  deleteUserBoard,
  getBoardById,
  getBoardDisplayName,
  getBoardIdFromRoute,
  getBoardRoute,
  isCardBoard,
  isUserBoard,
  renameUserBoard,
} from '@/state/boardCards'

const visible = defineModel('visible')
const emit = defineEmits([
  'open-tag-manage',
  'open-about-edit',
  'open-card-create',
  'open-card-edit',
  'open-card-delete',
  'board-deleted',
])
const route = useRoute()
const router = useRouter()
const confirm = useConfirm()
const boardsStore = useBoardsStore()
const isDesktop = ref(false)
const rowCountError = ref('')
const isBoardRenameDialogVisible = ref(false)
const boardNameDraft = ref('')
const boardNameError = ref('')

const isMainBoardRoute = computed(() => route.path === '/' || route.path === '/main')
const currentBoardId = computed(() => getBoardIdFromRoute(route))
const currentBoard = computed(() => getBoardById(currentBoardId.value))
const isCardBoardRoute = computed(() => isCardBoard(currentBoardId.value))
const isUserBoardRoute = computed(() => isUserBoard(currentBoardId.value))
const isLayoutEditableRoute = computed(() => isMainBoardRoute.value || isUserBoardRoute.value)
const layoutBoardId = computed(() =>
  isLayoutEditableRoute.value ? currentBoardId.value : MAIN_BOARD_KEY,
)

const updateViewportState = () => {
  isDesktop.value = window.matchMedia('(min-width: 1024px)').matches
}

const rowCount = computed({
  get() {
    return boardsStore.getActiveGridSettings(layoutBoardId.value).rows
  },
  set(value) {
    const changed = boardsStore.setDraftRowCount(layoutBoardId.value, value)
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
  boardsStore.beginLayoutEdit(layoutBoardId.value)
}

const saveBoardLayoutEdit = () => {
  rowCountError.value = ''
  boardsStore.saveLayoutEdit(layoutBoardId.value)
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

const openCardCreateDialog = () => {
  closeDrawer()
  emit('open-card-create')
}

const openCardEditPicker = () => {
  closeDrawer()
  emit('open-card-edit')
}

const openCardDeletePicker = () => {
  closeDrawer()
  emit('open-card-delete')
}

const openBoardRenameDialog = () => {
  if (!isUserBoardRoute.value || !currentBoard.value) {
    return
  }

  boardNameDraft.value = currentBoard.value.name
  boardNameError.value = ''
  isBoardRenameDialogVisible.value = true
}

const closeBoardRenameDialog = () => {
  boardNameError.value = ''
  isBoardRenameDialogVisible.value = false
}

const submitBoardRename = () => {
  const nextName = boardNameDraft.value.trim()
  if (!nextName) {
    boardNameError.value = 'Введите название доски.'
    return
  }

  const isRenamed = renameUserBoard(currentBoardId.value, nextName)
  if (!isRenamed) {
    boardNameError.value = 'Не удалось сохранить новое название доски.'
    return
  }

  closeBoardRenameDialog()
}

const deleteCurrentBoard = () => {
  const boardId = currentBoardId.value
  if (!isUserBoard(boardId)) {
    return
  }

  const isDeleted = deleteUserBoard(boardId)
  if (!isDeleted) {
    return
  }

  emit('board-deleted')
  boardsStore.removeBoardLayoutState(boardId)
  closeDrawer()
  router.push(getBoardRoute(MAIN_BOARD_KEY))
}

const confirmBoardDelete = () => {
  if (!isUserBoardRoute.value) {
    return
  }

  const boardName = getBoardDisplayName(currentBoardId.value)
  confirm.require({
    group: 'board-actions',
    header: 'Подтверждение удаления',
    message: `Удалить доску "${boardName}"?`,
    icon: 'pi pi-exclamation-triangle',
    rejectLabel: 'Отмена',
    acceptLabel: 'Удалить',
    rejectProps: {
      severity: 'secondary',
      outlined: true,
    },
    acceptProps: {
      severity: 'danger',
    },
    accept: () => {
      deleteCurrentBoard()
    },
  })
}

onMounted(() => {
  updateViewportState()
  window.addEventListener('resize', updateViewportState)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateViewportState)
})
</script>
