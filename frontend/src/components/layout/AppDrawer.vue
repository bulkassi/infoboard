<template>
  <Drawer v-model:visible="visible" position="right" header="Боковая панель">
    <div class="flex flex-col justify-content gap-2">
      <Button
        variant="outlined"
        class="w-full flex-1 justify-start whitespace-normal text-left"
        @click="enterFullscreen"
      >
        <PhCornersOut :size="32" weight="duotone" />
        Полноэкранный режим
      </Button>
      <Button
        variant="outlined"
        class="w-full flex-1 justify-start whitespace-normal text-left"
        @click="toggleSlideshow"
      >
        <PhSlideshow :size="32" weight="duotone" />
        Слайд-шоу
      </Button>
      <template v-if="authStore.isAuthenticated">
        <Button
          v-if="canManageAbout"
          @click="openAboutEditDialog"
          variant="outlined"
          class="w-full flex-1 justify-start whitespace-normal text-left"
        >
          <PhPencilSimple :size="32" weight="duotone" />
          Редактировать About
        </Button>
        <Button
          variant="outlined"
          class="w-full flex-1 justify-start whitespace-normal text-left"
          :disabled="!canCreateCurrentBoardShareLink"
          @click="openShareLinksDialog"
        >
          <PhShareFat :size="32" weight="duotone" />
          Поделиться доской
        </Button>
        <Button
          variant="outlined"
          class="w-full flex-1 justify-start whitespace-normal text-left"
          :disabled="!canManageCurrentBoard"
          @click="openBoardRenameDialog"
        >
          <PhPencilSimple :size="32" weight="duotone" />
          Редактировать название доски
        </Button>
        <Button
          variant="outlined"
          severity="danger"
          class="w-full flex-1 justify-start whitespace-normal text-left"
          :disabled="!canManageCurrentBoard"
          @click="confirmBoardDelete"
        >
          <PhTrash :size="32" weight="duotone" />
          Удалить доску
        </Button>
        <Button
          variant="outlined"
          class="w-full flex-1 justify-start whitespace-normal text-left"
          :disabled="!isCardBoardRoute || !canManageCurrentBoardCards"
          @click="openCardCreateDialog"
        >
          <PhPlusSquare :size="32" weight="duotone" />
          Добавить карточку
        </Button>
        <Button
          variant="outlined"
          class="w-full flex-1 justify-start whitespace-normal text-left"
          :disabled="!isCardBoardRoute || !canManageCurrentBoardCards"
          @click="openCardEditPicker"
        >
          <PhPencilSimple :size="32" weight="duotone" />
          Редактировать карточку
        </Button>
        <Button
          variant="outlined"
          severity="danger"
          class="w-full flex-1 justify-start whitespace-normal text-left"
          :disabled="!isCardBoardRoute || !canManageCurrentBoardCards"
          @click="openCardDeletePicker"
        >
          <PhTrash :size="32" weight="duotone" />
          Удалить карточку
        </Button>
        <Button
          v-if="!boardsStore.isLayoutEditMode"
          variant="outlined"
          class="w-full flex-1 justify-start whitespace-normal text-left"
          :disabled="!isLayoutEditableRoute || !isDesktop || !canManageCurrentBoardCards"
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
          <Button
            size="small"
            severity="secondary"
            variant="outlined"
            @click="cancelBoardLayoutEdit"
            >Выйти из редактирования</Button
          >
        </div>
        <Button
          @click="openTagManageDialog"
          variant="outlined"
          class="w-full flex-1 justify-start whitespace-normal text-left"
          :disabled="!canManageTags"
        >
          <PhBookmark :size="32" weight="duotone" />
          Управление тегами
        </Button>
        <Button v-if="canAccessAdminPage" asChild variant="outlined" v-slot="slotProps">
          <RouterLink
            to="/admin"
            :class="[slotProps.class, 'w-full flex-1 justify-start whitespace-normal text-left']"
            @click="closeDrawer"
          >
            <PhAddressBookTabs :size="32" weight="duotone" />
            Администрирование
          </RouterLink>
        </Button>
        <Button
          ref="profileButtonRef"
          variant="outlined"
          class="w-full flex-1 justify-start whitespace-normal text-left"
          @click="openProfileSettings"
        >
          <PhUserCircle :size="32" weight="duotone" />
          Настройки профиля
        </Button>
      </template>
    </div>

    <template #footer>
      <Button
        v-if="authStore.isAuthenticated"
        variant="outlined"
        severity="danger"
        @click="handleLogout"
      >
        <PhSignOut :size="32" weight="duotone" />
        Выйти из аккаунта
      </Button>
      <Button v-else variant="outlined" severity="success" @click="handleLogin">
        <PhSignIn :size="32" weight="duotone" />
        Войти в аккаунт
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
    <ProfileSettingsPopover ref="profilePopoverRef" />
  </Drawer>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
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
  PhSignIn,
  PhSlideshow,
  PhStack,
  PhTrash,
  PhUserCircle,
} from '@phosphor-icons/vue'

import { useBoardsStore } from '@/stores/boards'
import { useBoardCardsStore, MAIN_BOARD_KEY } from '@/stores/boardCards'
import { useAuthStore } from '@/stores/auth'
import { usePermissions } from '@/composables/usePermissions'
import ProfileSettingsPopover from '@/components/profile/ProfileSettingsPopover.vue'

const visible = defineModel('visible')
const emit = defineEmits([
  'open-tag-manage',
  'open-about-edit',
  'open-card-create',
  'open-card-edit',
  'open-card-delete',
  'open-share-links',
  'board-deleted',
  'toggle-slideshow',
])
const route = useRoute()
const router = useRouter()
const confirm = useConfirm()
const boardsStore = useBoardsStore()
const boardCardsStore = useBoardCardsStore()
const authStore = useAuthStore()
const {
  canAccessAdminPage,
  canManageBoard,
  canManageCards,
  canManageAbout,
  canManageTags,
  canCreateShareLink,
} = usePermissions()
const isDesktop = ref(false)
const rowCountError = ref('')
const isBoardRenameDialogVisible = ref(false)
const boardNameDraft = ref('')
const boardNameError = ref('')
const profilePopoverRef = ref(null)
const profileButtonRef = ref(null)

const { systemBoardIdsByKind } = storeToRefs(boardCardsStore)
const isMainBoardRoute = computed(() => route.path === '/' || route.path === '/main')
const currentBoardId = computed(() => boardCardsStore.getBoardIdFromRoute(route))
const currentBoard = computed(() => boardCardsStore.getBoardById(currentBoardId.value))
const isCardBoardRoute = computed(() => boardCardsStore.isCardBoard(currentBoardId.value))
const isUserBoardRoute = computed(() => boardCardsStore.isUserBoard(currentBoardId.value))
const canManageCurrentBoard = computed(() => canManageBoard(currentBoard.value))
const canManageCurrentBoardCards = computed(() => canManageCards(currentBoard.value))
const canCreateCurrentBoardShareLink = computed(() => canCreateShareLink(currentBoard.value))
const isLayoutEditableRoute = computed(
  () => (isMainBoardRoute.value || isUserBoardRoute.value) && canManageCurrentBoardCards.value,
)
const mainBoardId = computed(
  () => systemBoardIdsByKind.value[MAIN_BOARD_KEY] ?? currentBoardId.value,
)
const layoutBoardId = computed(() =>
  isLayoutEditableRoute.value ? currentBoardId.value : mainBoardId.value,
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

const enterFullscreen = async () => {
  try {
    if (!document.fullscreenElement) {
      await document.documentElement.requestFullscreen()
    } else {
      await document.exitFullscreen()
    }
  } catch (err) {
    // ignore failures silently
    // could show toast here in future
    // console.warn('fullscreen failed', err)
  }
}

const toggleSlideshow = () => {
  // emit event to parent header which manages navigation and timing
  closeDrawer()
  emit('toggle-slideshow')
}

const handleLogout = async () => {
  await authStore.logout()
  visible.value = false
  router.push('/login')
}

const handleLogin = () => {
  visible.value = false
  router.push('/login')
}

const openProfileSettings = (event) => {
  profilePopoverRef.value?.open(event)
}

const beginBoardLayoutEdit = () => {
  rowCountError.value = ''
  boardsStore.beginLayoutEdit(layoutBoardId.value)
}

const saveBoardLayoutEdit = () => {
  rowCountError.value = ''
  boardsStore.saveLayoutEdit(layoutBoardId.value)
  const layouts = boardsStore.getActiveBoardLayouts(layoutBoardId.value)
  boardCardsStore.persistLayouts(layoutBoardId.value, layouts)
}

const cancelBoardLayoutEdit = () => {
  rowCountError.value = ''
  boardsStore.cancelLayoutEdit()
}

const openTagManageDialog = () => {
  if (!canManageTags.value) {
    return
  }

  closeDrawer()
  emit('open-tag-manage')
}

const openAboutEditDialog = () => {
  if (!canManageAbout.value) {
    return
  }

  closeDrawer()
  emit('open-about-edit')
}

const openCardCreateDialog = () => {
  if (!canManageCurrentBoardCards.value) {
    return
  }

  closeDrawer()
  emit('open-card-create')
}

const openCardEditPicker = () => {
  if (!canManageCurrentBoardCards.value) {
    return
  }

  closeDrawer()
  emit('open-card-edit')
}

const openCardDeletePicker = () => {
  if (!canManageCurrentBoardCards.value) {
    return
  }

  closeDrawer()
  emit('open-card-delete')
}

const openShareLinksDialog = () => {
  if (!canCreateCurrentBoardShareLink.value) {
    return
  }

  closeDrawer()
  emit('open-share-links')
}

const openBoardRenameDialog = () => {
  if (!isUserBoardRoute.value || !currentBoard.value || !canManageCurrentBoard.value) {
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

const submitBoardRename = async () => {
  const nextName = boardNameDraft.value.trim()
  if (!nextName) {
    boardNameError.value = 'Введите название доски.'
    return
  }

  const actor = {
    actorUserId: authStore.currentUser.id,
    isAdmin: authStore.isAdmin,
  }
  try {
    await boardCardsStore.renameUserBoard(currentBoardId.value, nextName, actor)
  } catch {
    boardNameError.value = 'Не удалось сохранить новое название доски.'
    return
  }

  closeBoardRenameDialog()
}

const deleteCurrentBoard = async () => {
  const boardId = currentBoardId.value
  if (!boardCardsStore.isUserBoard(boardId)) {
    return
  }

  await boardCardsStore.deleteUserBoard(boardId, {
    actorUserId: authStore.currentUser.id,
    isAdmin: authStore.isAdmin,
  })

  emit('board-deleted')
  boardsStore.removeBoardLayoutState(boardId)
  closeDrawer()
  router.push(boardCardsStore.getBoardRoute(MAIN_BOARD_KEY))
}

const confirmBoardDelete = () => {
  if (!isUserBoardRoute.value || !canManageCurrentBoard.value) {
    return
  }

  const boardName = boardCardsStore.getBoardDisplayName(currentBoardId.value)
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
