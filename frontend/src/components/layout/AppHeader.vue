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
    @toggle-slideshow="handleToggleSlideshow"
    @open-tag-manage="tagManageDialogVisible = true"
    @open-about-edit="aboutEditDialogVisible = true"
    @open-card-create="openCardCreateDialog"
    @open-card-edit="openCardEditPicker"
    @open-card-delete="openCardDeletePicker"
    @open-share-links="shareLinksDialogVisible = true"
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
  <ShareLinksDialog v-model:visible="shareLinksDialogVisible" :boardId="currentBoardId" />
  <ConfirmDialog />
</template>

<script setup>
import { computed, onMounted, ref, watch, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'

import { PhChalkboardSimple, PhList, PhPlusCircle } from '@phosphor-icons/vue'
import { Button, Select } from 'primevue'
import ConfirmDialog from 'primevue/confirmdialog'
import { useConfirm } from 'primevue/useconfirm'

import AppDrawer from './AppDrawer.vue'
import AboutEditDialog from '../about/AboutEditDialog.vue'
import TagManageDialog from '../tags/TagManageDialog.vue'
import CardEditDialog from '../cards/CardEditDialog.vue'
import ShareLinksDialog from '../share/ShareLinksDialog.vue'
import { useAboutStore } from '@/stores/about'
import { useAuthStore } from '@/stores/auth'
import { useUsersStore } from '@/stores/users'
import { usePermissions } from '@/composables/usePermissions'
import { useBoardCardsStore } from '@/stores/boardCards'

const drawerVisible = ref(false)
const tagManageDialogVisible = ref(false)
const aboutEditDialogVisible = ref(false)
const cardEditDialogVisible = ref(false)
const shareLinksDialogVisible = ref(false)
const cardEditMode = ref('create')
const selectedCardId = ref(null)
const selectedBoardId = ref(null)

const boardCardsStore = useBoardCardsStore()
const aboutStore = useAboutStore()
const usersStore = useUsersStore()
const { content: aboutContent } = storeToRefs(aboutStore)
const route = useRoute()
const router = useRouter()
const confirm = useConfirm()
const authStore = useAuthStore()
const { canCreateBoard, canManageCards, canManageAbout } = usePermissions()
const { selectedCardActionEvent } = storeToRefs(boardCardsStore)

const navLinks = [
  { to: '/main', label: 'Главная' },
  { to: '/about', label: 'О нас' },
  { to: '/employees', label: 'Сотрудники' },
  { to: '/services', label: 'Сервисы' },
]

// Slideshow configuration
const SLIDESHOW_ROUTES = ['/main', '/about', '/employees', '/services']
const SLIDESHOW_INTERVAL_MS = 5000
const isSlideshowActive = ref(false)
let slideshowTimer = null

const stopSlideshowOnInteraction = (ev) => {
  stopSlideshow()
}

const startSlideshow = () => {
  if (isSlideshowActive.value) return
  isSlideshowActive.value = true

  // immediately go to first slide
  router.push(SLIDESHOW_ROUTES[0])

  slideshowTimer = setInterval(() => {
    const current = router.currentRoute.value.path || '/'
    const idx = SLIDESHOW_ROUTES.indexOf(current)
    const nextIdx = idx === -1 ? 0 : (idx + 1) % SLIDESHOW_ROUTES.length
    router.push(SLIDESHOW_ROUTES[nextIdx])
  }, SLIDESHOW_INTERVAL_MS)

  window.addEventListener('keydown', stopSlideshowOnInteraction, { once: true })
  window.addEventListener('mousedown', stopSlideshowOnInteraction, { once: true })
  window.addEventListener('touchstart', stopSlideshowOnInteraction, { once: true })
}

const stopSlideshow = () => {
  if (!isSlideshowActive.value) return
  isSlideshowActive.value = false
  if (slideshowTimer) {
    clearInterval(slideshowTimer)
    slideshowTimer = null
  }
  window.removeEventListener('keydown', stopSlideshowOnInteraction)
  window.removeEventListener('mousedown', stopSlideshowOnInteraction)
  window.removeEventListener('touchstart', stopSlideshowOnInteraction)
}

const handleToggleSlideshow = () => {
  if (isSlideshowActive.value) {
    stopSlideshow()
  } else {
    startSlideshow()
  }
}

const boards = computed(() => boardCardsStore.getSelectableBoards())

const currentBoardId = computed(() => boardCardsStore.getBoardIdFromRoute(route))
const currentBoard = computed(() => boardCardsStore.getBoardById(currentBoardId.value))

const isCardBoardRoute = computed(() => boardCardsStore.isCardBoard(currentBoardId.value))
const canManageCurrentBoardCards = computed(() => canManageCards(currentBoard.value))

const activeCard = computed(() => {
  if (!isCardBoardRoute.value || !selectedCardId.value) {
    return null
  }

  return boardCardsStore.getCardById(currentBoardId.value, selectedCardId.value)
})

const getBoardName = () => {
  return boardCardsStore.getBoardDisplayName(currentBoardId.value)
}

const onCreateBoard = async () => {
  if (!canCreateBoard.value) {
    return
  }

  const board = await boardCardsStore.createUserBoard({
    owner: authStore.currentUser.name,
    ownerUserId: authStore.currentUser.id,
  })
  router.push(boardCardsStore.getBoardRoute(board.id))
}

const onBoardSelect = (boardId) => {
  const normalizedBoardId = boardCardsStore.normalizeBoardId(boardId)

  if (normalizedBoardId == null || normalizedBoardId === currentBoardId.value) {
    return
  }

  router.push(boardCardsStore.getBoardRoute(normalizedBoardId))
}

const openCardCreateDialog = () => {
  if (!isCardBoardRoute.value || !canManageCurrentBoardCards.value) {
    return
  }

  boardCardsStore.clearCardSelection()
  cardEditMode.value = 'create'
  selectedCardId.value = null
  cardEditDialogVisible.value = true
}

const openCardEditPicker = () => {
  if (!isCardBoardRoute.value || !canManageCurrentBoardCards.value) {
    return
  }

  boardCardsStore.startCardSelection('edit', currentBoardId.value)
}

const openCardDeletePicker = () => {
  if (!isCardBoardRoute.value || !canManageCurrentBoardCards.value) {
    return
  }

  boardCardsStore.startCardSelection('delete', currentBoardId.value)
}

const clearCardSelection = () => {
  boardCardsStore.clearCardSelection()
}

const onCardSave = async (payload) => {
  if (!isCardBoardRoute.value || !canManageCurrentBoardCards.value) {
    return
  }

  const actor = {
    actorUserId: authStore.currentUser.id,
    isAdmin: authStore.isAdmin,
  }

  if (cardEditMode.value === 'edit' && selectedCardId.value) {
    await boardCardsStore.updateCard(currentBoardId.value, selectedCardId.value, payload, actor)
    return
  }

  await boardCardsStore.createCard(currentBoardId.value, payload, actor)
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

  const cardName = boardCardsStore.getCardDisplayName(event.boardId, event.cardId)
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
      boardCardsStore.deleteCard(event.boardId, event.cardId, {
        actorUserId: authStore.currentUser.id,
        isAdmin: authStore.isAdmin,
      })
    },
  })
})

watch(
  () => route.path,
  () => {
    boardCardsStore.clearCardSelection()
  },
)

watch(
  currentBoardId,
  (boardId) => {
    selectedBoardId.value = boardCardsStore.isCardBoard(boardId) ? boardId : null
  },
  { immediate: true },
)

const onAboutSave = (nextContent) => {
  if (!canManageAbout.value) {
    return
  }

  aboutStore.updateAbout(nextContent)
}

const syncAdminUsers = () => {
  if (authStore.isAdmin) {
    usersStore.fetchUsers()
    return
  }

  usersStore.clearUsers()
}

onMounted(() => {
  boardCardsStore.loadBoards()
  if (authStore.isAuthenticated) {
    aboutStore.fetchAbout()
  }
  syncAdminUsers()
})

onBeforeUnmount(() => {
  stopSlideshow()
})

watch(
  () => authStore.isAuthenticated,
  (isAuthenticated) => {
    boardCardsStore.loadBoards()
    if (isAuthenticated) {
      aboutStore.fetchAbout()
    }
  },
)

watch(
  () => authStore.isAdmin,
  () => {
    syncAdminUsers()
  },
)
</script>
