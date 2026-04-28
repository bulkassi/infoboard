<template>
  <header
    class="flex items-center justify-between bg-white px-[120px] py-2 shadow-[0_2px_4px_rgba(0,0,0,0.1)]"
  >
    <div class="m-2 flex items-center">
      <img src="/src/assets/Greenatom_horizont_rus_blue.png" alt="Logo" class="h-[60px] w-auto" />
    </div>
    <nav class="flex h-full flex-1 items-center justify-center gap-2.5">
      <Button
        v-for="navItem in navLinks"
        :key="navItem.to"
        asChild
        variant="text"
        v-slot="slotProps"
      >
        <RouterLink :to="navItem.to" :class="slotProps.class">{{ navItem.label }}</RouterLink>
      </Button>
      <Select
        v-if="authStore.isAuthenticated"
        placeholder="Выбрать доску"
        :options="boards"
        optionLabel="name"
        optionValue="id"
        :modelValue="selectedBoardId"
        filter
        @update:modelValue="onBoardSelect"
      >
        <template #dropdownicon>
          <PhChalkboardSimple weight="duotone" :size="20" />
        </template>

        <template #option="slotProps">
          <div class="flex w-full flex-col items-start gap-0 px-0 py-1 text-left">
            <span class="text-[20px] font-medium text-brand-500">{{ slotProps.option.name }}</span>
            <small class="text-xs text-[#888888]">{{ slotProps.option.owner }}</small>
          </div>
        </template>

        <template #footer>
          <div class="px-2 pb-1">
            <Button
              variant="text"
              class="flex w-full items-center gap-[5px]"
              :disabled="!canCreateBoard"
              @click="onCreateBoard"
            >
              <PhPlusCircle :size="16" />
              Добавить доску
            </Button>
          </div>
        </template>
      </Select>
    </nav>

    <div class="flex w-[190px] justify-end">
      <Button variant="text" @click="drawerVisible = true">
        <PhList :size="32" weight="bold" />
      </Button>
    </div>
  </header>

  <AppDrawer
    v-model:visible="drawerVisible"
    @open-tag-manage="tagManageDialogVisible = true"
    @open-about-edit="aboutEditDialogVisible = true"
    @open-card-create="openCardCreateDialog"
    @open-card-edit="openCardEditPicker"
    @open-card-delete="openCardDeletePicker"
    @board-deleted="clearCardSelection"
  />
  <TagManageDialog v-model:visible="tagManageDialogVisible" />
  <AboutEditDialog
    v-model:visible="aboutEditDialogVisible"
    :content="aboutContent"
    @save="onAboutSave"
  />
  <CardEditDialog
    v-model:visible="cardEditDialogVisible"
    :boardId="currentBoardId"
    :card="cardEditMode === 'edit' ? activeCard : null"
    @save="onCardSave"
  />
  <ConfirmDialog />
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { PhChalkboardSimple, PhList, PhPlusCircle } from '@phosphor-icons/vue'
import { Button, Select } from 'primevue'
import ConfirmDialog from 'primevue/confirmdialog'
import { useConfirm } from 'primevue/useconfirm'

import AppDrawer from './AppDrawer.vue'
import AboutEditDialog from '../about/AboutEditDialog.vue'
import TagManageDialog from '../tags/TagManageDialog.vue'
import CardEditDialog from '../cards/CardEditDialog.vue'
import { useAboutBoardState } from '@/state/aboutBoard'
import { useAuthStore } from '@/stores/auth'
import { usePermissions } from '@/composables/usePermissions'
import {
  clearCardSelection,
  createUserBoard,
  createCard,
  deleteCard,
  getBoardById,
  getBoardDisplayName,
  getBoardIdFromRoute,
  getBoardRoute,
  getCardById,
  getCardDisplayName,
  getSelectableBoards,
  isCardBoard,
  normalizeBoardId,
  selectedCardActionEvent,
  startCardSelection,
  updateCard,
} from '@/state/boardCards'

const drawerVisible = ref(false)
const tagManageDialogVisible = ref(false)
const aboutEditDialogVisible = ref(false)
const cardEditDialogVisible = ref(false)
const cardEditMode = ref('create')
const selectedCardId = ref(null)
const selectedBoardId = ref(null)

const { aboutContent } = useAboutBoardState()
const route = useRoute()
const router = useRouter()
const confirm = useConfirm()
const authStore = useAuthStore()
const { canCreateBoard, canManageCards, canManageAbout } = usePermissions()

const navLinks = [
  { to: '/main', label: 'Главная' },
  { to: '/about', label: 'О нас' },
  { to: '/employees', label: 'Сотрудники' },
  { to: '/services', label: 'Сервисы' },
]

const boards = computed(() => getSelectableBoards())

const currentBoardId = computed(() => getBoardIdFromRoute(route))
const currentBoard = computed(() => getBoardById(currentBoardId.value))

const isCardBoardRoute = computed(() => isCardBoard(currentBoardId.value))
const canManageCurrentBoardCards = computed(() => canManageCards(currentBoard.value))

const activeCard = computed(() => {
  if (!isCardBoardRoute.value || !selectedCardId.value) {
    return null
  }

  return getCardById(currentBoardId.value, selectedCardId.value)
})

const getBoardName = () => {
  return getBoardDisplayName(currentBoardId.value)
}

const onCreateBoard = () => {
  if (!canCreateBoard.value) {
    return
  }

  const board = createUserBoard({
    owner: authStore.currentUser.name,
    ownerUserId: authStore.currentUser.id,
  })
  router.push(getBoardRoute(board.id))
}

const onBoardSelect = (boardId) => {
  const normalizedBoardId = normalizeBoardId(boardId)

  if (normalizedBoardId == null || normalizedBoardId === currentBoardId.value) {
    return
  }

  router.push(getBoardRoute(normalizedBoardId))
}

const openCardCreateDialog = () => {
  if (!isCardBoardRoute.value || !canManageCurrentBoardCards.value) {
    return
  }

  clearCardSelection()
  cardEditMode.value = 'create'
  selectedCardId.value = null
  cardEditDialogVisible.value = true
}

const openCardEditPicker = () => {
  if (!isCardBoardRoute.value || !canManageCurrentBoardCards.value) {
    return
  }

  startCardSelection('edit', currentBoardId.value)
}

const openCardDeletePicker = () => {
  if (!isCardBoardRoute.value || !canManageCurrentBoardCards.value) {
    return
  }

  startCardSelection('delete', currentBoardId.value)
}

const onCardSave = (payload) => {
  if (!isCardBoardRoute.value || !canManageCurrentBoardCards.value) {
    return
  }

  const actor = {
    actorUserId: authStore.currentUser.id,
    isAdmin: authStore.isAdmin,
  }

  if (cardEditMode.value === 'edit' && selectedCardId.value) {
    updateCard(currentBoardId.value, selectedCardId.value, payload, actor)
    return
  }

  createCard(currentBoardId.value, payload, actor)
}

watch(selectedCardActionEvent, (event) => {
  if (!event || event.boardId !== currentBoardId.value) {
    return
  }

  if (!canManageCurrentBoardCards.value) {
    return
  }

  selectedCardId.value = event.cardId

  if (event.action === 'edit') {
    cardEditMode.value = 'edit'
    cardEditDialogVisible.value = true
    return
  }

  const cardName = getCardDisplayName(event.boardId, event.cardId)
  confirm.require({
    header: 'Подтверждение удаления',
    message: `Удалить карточку "${cardName}" на доске "${getBoardName()}"?`,
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
      deleteCard(event.boardId, event.cardId, {
        actorUserId: authStore.currentUser.id,
        isAdmin: authStore.isAdmin,
      })
    },
  })
})

watch(
  () => route.path,
  () => {
    clearCardSelection()
  },
)

watch(
  currentBoardId,
  (boardId) => {
    selectedBoardId.value = isCardBoard(boardId) ? boardId : null
  },
  { immediate: true },
)

const onAboutSave = (nextContent) => {
  if (!canManageAbout.value) {
    return
  }

  aboutContent.value = nextContent
}
</script>
