import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const BOARD_KIND = {
  MAIN: 'main',
  ABOUT: 'about',
  EMPLOYEES: 'employees',
  SERVICES: 'services',
  USER: 'user',
}

const SYSTEM_BOARD_KINDS = new Set([
  BOARD_KIND.MAIN,
  BOARD_KIND.ABOUT,
  BOARD_KIND.EMPLOYEES,
  BOARD_KIND.SERVICES,
])

export function usePermissions() {
  const authStore = useAuthStore()

  const currentUserId = computed(() => authStore.currentUser?.id ?? null)

  const isOwnedByCurrentUser = (entity) => {
    if (!entity || !Number.isInteger(currentUserId.value)) {
      return false
    }

    return entity.ownerUserId === currentUserId.value
  }

  const isSystemBoard = (board) => {
    return Boolean(board?.kind && SYSTEM_BOARD_KINDS.has(board.kind))
  }

  const canAccessAdminPage = computed(() => authStore.isAdmin)

  const canCreateBoard = computed(() => Number.isInteger(currentUserId.value))

  const canManageBoard = (board) => {
    if (!board) {
      return false
    }

    if (authStore.isAdmin) {
      return board.kind === BOARD_KIND.USER
    }

    return board.kind === BOARD_KIND.USER && isOwnedByCurrentUser(board)
  }

  const canManageCards = (board) => {
    if (!board) {
      return false
    }

    if (authStore.isAdmin) {
      return true
    }

    return board.kind === BOARD_KIND.USER && isOwnedByCurrentUser(board)
  }

  const canManageAbout = computed(() => authStore.isAdmin)

  const canManageTags = computed(() => Number.isInteger(currentUserId.value))

  const canSetTagGlobal = computed(() => authStore.isAdmin)

  const canEditTag = (tag) => {
    if (!tag) {
      return false
    }

    if (authStore.isAdmin) {
      return true
    }

    return isOwnedByCurrentUser(tag)
  }

  const canDeleteTag = (tag) => {
    return canEditTag(tag)
  }

  const canAssignTagToCard = (tag, board) => {
    if (!tag || !board) {
      return false
    }

    if (authStore.isAdmin) {
      return true
    }

    if (board.kind !== BOARD_KIND.USER || !isOwnedByCurrentUser(board)) {
      return false
    }

    return tag.isGlobal || isOwnedByCurrentUser(tag)
  }

  const canCreateShareLink = (board) => {
    if (!board || board.kind !== BOARD_KIND.USER) {
      return false
    }

    if (authStore.isAdmin) {
      return true
    }

    return isOwnedByCurrentUser(board)
  }

  return {
    currentUserId,
    canAccessAdminPage,
    canCreateBoard,
    canManageBoard,
    canManageCards,
    canManageAbout,
    canManageTags,
    canSetTagGlobal,
    canEditTag,
    canDeleteTag,
    canAssignTagToCard,
    canCreateShareLink,
    isSystemBoard,
    isOwnedByCurrentUser,
  }
}
