import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { apiRequest, buildFileUrl } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { useUsersStore } from '@/stores/users'
import { useBoardsStore } from '@/stores/boards'

export const MAIN_BOARD_KEY = 'main'
export const ABOUT_BOARD_KEY = 'about'
export const EMPLOYEES_BOARD_KEY = 'employees'
export const SERVICES_BOARD_KEY = 'services'
export const INVALID_BOARD_ID = -1

const BOARD_KIND = {
  MAIN: MAIN_BOARD_KEY,
  ABOUT: ABOUT_BOARD_KEY,
  EMPLOYEES: EMPLOYEES_BOARD_KEY,
  SERVICES: SERVICES_BOARD_KEY,
  USER: 'user',
}

const SYSTEM_BOARD_ROUTE_BY_KIND = {
  [BOARD_KIND.MAIN]: '/main',
  [BOARD_KIND.ABOUT]: '/about',
  [BOARD_KIND.EMPLOYEES]: '/employees',
  [BOARD_KIND.SERVICES]: '/services',
}

const BOARD_KIND_BY_ROUTE = {
  '/': BOARD_KIND.MAIN,
  '/main': BOARD_KIND.MAIN,
  '/about': BOARD_KIND.ABOUT,
  '/employees': BOARD_KIND.EMPLOYEES,
  '/services': BOARD_KIND.SERVICES,
}

export const useBoardCardsStore = defineStore('boardCards', () => {
  const authStore = useAuthStore()
  const usersStore = useUsersStore()
  const boardsStore = useBoardsStore()

  const boards = ref([])
  const cardsByBoardId = ref({})
  const systemBoardIdsByKind = ref({})
  const loadingBoards = ref(false)
  const loadingCardsById = ref({})

  const pendingCardSelection = ref({
    action: null,
    boardId: null,
  })
  const selectedCardActionEvent = ref(null)

  function normalizeBoardId(boardId) {
    if (typeof boardId !== 'string') {
      return boardId
    }

    const trimmedBoardId = boardId.trim()
    if (!trimmedBoardId) {
      return boardId
    }

    const numericBoardId = Number(trimmedBoardId)
    return Number.isFinite(numericBoardId) ? numericBoardId : boardId
  }

  function getBoardKind(boardType) {
    const normalized = String(boardType ?? '').toLowerCase()
    if (normalized === 'main') return BOARD_KIND.MAIN
    if (normalized === 'about') return BOARD_KIND.ABOUT
    if (normalized === 'employees') return BOARD_KIND.EMPLOYEES
    if (normalized === 'services') return BOARD_KIND.SERVICES
    return BOARD_KIND.USER
  }

  function resolveOwnerLabel(ownerUserId) {
    if (ownerUserId == null) {
      return 'Системная доска'
    }

    if (authStore.currentUser?.id === ownerUserId) {
      return authStore.currentUser?.name || 'Пользователь'
    }

    const known = usersStore.getUserById(ownerUserId)
    return known?.name || 'Пользователь'
  }

  function mapBoard(board) {
    const kind = getBoardKind(board.type)
    return {
      id: board.id,
      name: board.name,
      owner: kind === BOARD_KIND.USER ? resolveOwnerLabel(board.owner_id) : 'Системная доска',
      ownerUserId: board.owner_id ?? null,
      kind,
      route: kind === BOARD_KIND.USER ? `/board/${board.id}` : SYSTEM_BOARD_ROUTE_BY_KIND[kind],
    }
  }

  async function requestWithOptionalAuth(path, options = {}) {
    if (authStore.accessToken) {
      return authStore.authorizedRequest(path, options)
    }

    return apiRequest(path, options)
  }

  async function loadBoards() {
    if (loadingBoards.value) {
      return boards.value
    }

    loadingBoards.value = true
    try {
      const response = await requestWithOptionalAuth('/boards')
      const mapped = Array.isArray(response) ? response.map(mapBoard) : []
      boards.value = mapped

      const nextSystemIds = {}
      mapped.forEach((board) => {
        if (board.kind !== BOARD_KIND.USER) {
          nextSystemIds[board.kind] = board.id
        }
      })
      systemBoardIdsByKind.value = nextSystemIds
      return boards.value
    } finally {
      loadingBoards.value = false
    }
  }

  async function fetchBoard(boardId, shareToken) {
    if (!Number.isInteger(boardId)) {
      return null
    }

    const query = shareToken ? `?share_token=${encodeURIComponent(shareToken)}` : ''
    const response = await requestWithOptionalAuth(`/boards/${boardId}${query}`)
    const mapped = mapBoard(response)
    const existingIndex = boards.value.findIndex((board) => board.id === mapped.id)
    if (existingIndex === -1) {
      boards.value = [...boards.value, mapped]
    } else {
      boards.value[existingIndex] = mapped
      boards.value = [...boards.value]
    }

    if (mapped.kind !== BOARD_KIND.USER) {
      systemBoardIdsByKind.value = {
        ...systemBoardIdsByKind.value,
        [mapped.kind]: mapped.id,
      }
    }

    return mapped
  }

  function getAllBoards() {
    return boards.value
  }

  function getSelectableBoards() {
    return boards.value.filter((board) => board.kind === BOARD_KIND.USER)
  }

  function getBoardById(boardId) {
    const normalized = normalizeBoardId(boardId)
    return boards.value.find((board) => board.id === normalized) ?? null
  }

  function getBoardRoute(boardId) {
    const board = getBoardById(boardId)
    if (!board) {
      return '/main'
    }
    return board.route || '/main'
  }

  function getBoardDisplayName(boardId) {
    return getBoardById(boardId)?.name ?? 'Доска'
  }

  function getBoardIdFromRoute(route) {
    const kind = BOARD_KIND_BY_ROUTE[route.path]
    if (kind && systemBoardIdsByKind.value[kind]) {
      return systemBoardIdsByKind.value[kind]
    }

    if (route.name === 'board-user') {
      const boardId = normalizeBoardId(route.params.boardId)
      if (Number.isInteger(boardId)) {
        return boardId
      }
    }

    return INVALID_BOARD_ID
  }

  function isUserBoard(boardId) {
    return getBoardById(boardId)?.kind === BOARD_KIND.USER
  }

  function isMainStyleCardBoard(boardId) {
    const kind = getBoardById(boardId)?.kind
    return kind === BOARD_KIND.MAIN || kind === BOARD_KIND.USER
  }

  function isCardBoard(boardId) {
    const kind = getBoardById(boardId)?.kind
    return (
      kind === BOARD_KIND.MAIN ||
      kind === BOARD_KIND.EMPLOYEES ||
      kind === BOARD_KIND.SERVICES ||
      kind === BOARD_KIND.USER
    )
  }

  function buildCardImageSrc(card) {
    if (Number.isInteger(card.file_id)) {
      return buildFileUrl(card.file_id)
    }
    return ''
  }

  function mapCard(card, boardKind) {
    const base = {
      id: card.id,
      type: card.type,
      imageSrc: buildCardImageSrc(card),
      fileId: card.file_id ?? null,
    }

    if (card.type === 'common') {
      return {
        ...base,
        title: card.title ?? '',
        content: card.content ?? '',
        tagIds: Array.isArray(card.tag_ids) ? card.tag_ids : [],
        col: card.col ?? 1,
        row: card.row ?? 1,
        colSpan: card.col_span ?? 1,
        rowSpan: card.row_span ?? 1,
      }
    }

    if (card.type === 'employee') {
      return {
        ...base,
        surname: card.surname ?? '',
        name: card.name ?? '',
        patronymic: card.patronymic ?? '',
        position: card.position ?? '',
      }
    }

    return {
      ...base,
      link: card.link ?? '',
      serviceName: card.name ?? '',
      serviceDesc: card.description ?? '',
    }
  }

  function getCards(boardId) {
    return cardsByBoardId.value[boardId] ?? []
  }

  function getCardById(boardId, cardId) {
    return getCards(boardId).find((card) => card.id === cardId) ?? null
  }

  function getCardDisplayName(boardId, cardId) {
    const card = getCardById(boardId, cardId)
    if (!card) {
      return ''
    }

    if (isMainStyleCardBoard(boardId)) {
      return card.title || 'Без названия'
    }

    const boardKind = getBoardById(boardId)?.kind
    if (boardKind === BOARD_KIND.EMPLOYEES) {
      return (
        [card.surname, card.name, card.patronymic].filter(Boolean).join(' ').trim() || 'Без имени'
      )
    }

    if (boardKind === BOARD_KIND.SERVICES) {
      return card.serviceName || 'Без названия'
    }

    return String(card.id)
  }

  function getLayoutsFromCards(cards) {
    const layouts = {}
    cards.forEach((card) => {
      if (card.type !== 'common') {
        return
      }
      layouts[card.id] = {
        col: card.col ?? 1,
        row: card.row ?? 1,
        colSpan: card.colSpan ?? 1,
        rowSpan: card.rowSpan ?? 1,
      }
    })
    return layouts
  }

  async function fetchCards(boardId, shareToken) {
    if (!Number.isInteger(boardId)) {
      return []
    }

    loadingCardsById.value[boardId] = true
    const board = getBoardById(boardId)
    const boardKind = board?.kind ?? BOARD_KIND.USER
    try {
      const query = shareToken ? `?share_token=${encodeURIComponent(shareToken)}` : ''
      const response = await requestWithOptionalAuth(`/boards/${boardId}/cards${query}`)
      const mapped = Array.isArray(response) ? response.map((card) => mapCard(card, boardKind)) : []

      cardsByBoardId.value = {
        ...cardsByBoardId.value,
        [boardId]: mapped,
      }

      const layouts = getLayoutsFromCards(mapped)
      boardsStore.initializeBoardLayout(boardId, layouts)
      return mapped
    } finally {
      loadingCardsById.value[boardId] = false
    }
  }

  function ensureCardLayouts(boardId) {
    const cards = getCards(boardId)
    const layouts = getLayoutsFromCards(cards)
    boardsStore.initializeBoardLayout(boardId, layouts)
  }

  async function uploadFile(file) {
    if (!(file instanceof File)) {
      return null
    }

    const formData = new FormData()
    formData.append('file', file)
    const response = await authStore.authorizedRequest('/files', {
      method: 'POST',
      body: formData,
    })
    return response?.id ?? null
  }

  async function createCard(boardId, payload, options = {}) {
    const board = getBoardById(boardId)
    if (!board) {
      return null
    }

    const boardKind = board.kind
    const cardType =
      boardKind === BOARD_KIND.EMPLOYEES
        ? 'employee'
        : boardKind === BOARD_KIND.SERVICES
          ? 'service'
          : 'common'

    let fileId = null
    if (payload.imageFile) {
      fileId = await uploadFile(payload.imageFile)
    }

    let layout = null
    if (cardType === 'common') {
      const existingLayouts = boardsStore.getActiveBoardLayouts(boardId)
      const gridSettings = boardsStore.getActiveGridSettings(boardId)
      const candidateSpan = { colSpan: 4, rowSpan: 3 }
      const knownLayouts = { ...existingLayouts }
      const rows = gridSettings.rows
      const columns = gridSettings.columns

      const overlaps = (candidate) =>
        Object.values(knownLayouts).some((layoutItem) => {
          const aRight = layoutItem.col + layoutItem.colSpan
          const bRight = candidate.col + candidate.colSpan
          const aBottom = layoutItem.row + layoutItem.rowSpan
          const bBottom = candidate.row + candidate.rowSpan
          return (
            layoutItem.col < bRight &&
            aRight > candidate.col &&
            layoutItem.row < bBottom &&
            aBottom > candidate.row
          )
        })

      let found = null
      for (let row = 1; row <= rows - candidateSpan.rowSpan + 1; row += 1) {
        for (let col = 1; col <= columns - candidateSpan.colSpan + 1; col += 1) {
          const candidate = {
            col,
            row,
            colSpan: candidateSpan.colSpan,
            rowSpan: candidateSpan.rowSpan,
          }
          if (!overlaps(candidate)) {
            found = candidate
            break
          }
        }
        if (found) {
          break
        }
      }

      layout = found ?? { col: 1, row: 1, colSpan: 1, rowSpan: 1 }
    }

    const response = await authStore.authorizedRequest(`/boards/${boardId}/cards`, {
      method: 'POST',
      body: {
        type: cardType,
        title: payload.title ?? undefined,
        content: payload.content ?? undefined,
        surname: payload.surname ?? undefined,
        name:
          cardType === 'service' ? (payload.serviceName ?? undefined) : (payload.name ?? undefined),
        patronymic: payload.patronymic ?? undefined,
        position: payload.position ?? undefined,
        description: payload.serviceDesc ?? undefined,
        link: payload.link ?? undefined,
        file_id: fileId ?? undefined,
        tag_ids: Array.isArray(payload.tagIds) ? payload.tagIds : [],
        col: layout?.col ?? 1,
        row: layout?.row ?? 1,
        col_span: layout?.colSpan ?? 1,
        row_span: layout?.rowSpan ?? 1,
      },
    })

    const card = mapCard(response, boardKind)
    cardsByBoardId.value = {
      ...cardsByBoardId.value,
      [boardId]: [...getCards(boardId), card],
    }

    if (layout && card.type === 'common') {
      boardsStore.setCardLayout(boardId, card.id, layout)
    }

    return card
  }

  async function updateCard(boardId, cardId, payload) {
    const board = getBoardById(boardId)
    if (!board) {
      return null
    }

    const cardType =
      board.kind === BOARD_KIND.EMPLOYEES
        ? 'employee'
        : board.kind === BOARD_KIND.SERVICES
          ? 'service'
          : 'common'

    const existing = getCardById(boardId, cardId)
    let fileId = existing?.fileId ?? null
    if (payload.imageFile instanceof File) {
      fileId = await uploadFile(payload.imageFile)
    } else if (payload.imageFile === null) {
      fileId = null
    }

    const response = await authStore.authorizedRequest(`/cards/${cardId}`, {
      method: 'PATCH',
      body: {
        title: payload.title ?? undefined,
        content: payload.content ?? undefined,
        surname: payload.surname ?? undefined,
        name:
          cardType === 'service' ? (payload.serviceName ?? undefined) : (payload.name ?? undefined),
        patronymic: payload.patronymic ?? undefined,
        position: payload.position ?? undefined,
        description: payload.serviceDesc ?? undefined,
        link: payload.link ?? undefined,
        file_id: fileId ?? undefined,
        tag_ids: Array.isArray(payload.tagIds) ? payload.tagIds : undefined,
      },
    })

    const updated = mapCard(response, board.kind)
    cardsByBoardId.value = {
      ...cardsByBoardId.value,
      [boardId]: getCards(boardId).map((card) => (card.id === cardId ? updated : card)),
    }
    return updated
  }

  async function deleteCard(boardId, cardId) {
    await authStore.authorizedRequest(`/cards/${cardId}`, {
      method: 'DELETE',
    })

    cardsByBoardId.value = {
      ...cardsByBoardId.value,
      [boardId]: getCards(boardId).filter((card) => card.id !== cardId),
    }
  }

  async function persistLayouts(boardId, layouts) {
    const cards = getCards(boardId)
    const updates = cards.filter((card) => card.type === 'common')

    await Promise.all(
      updates.map((card) => {
        const layout = layouts[card.id]
        if (!layout) {
          return Promise.resolve()
        }

        return authStore.authorizedRequest(`/cards/${card.id}/position`, {
          method: 'PATCH',
          body: {
            col: layout.col,
            row: layout.row,
            col_span: layout.colSpan,
            row_span: layout.rowSpan,
          },
        })
      }),
    )
  }

  async function createUserBoard(payload = {}) {
    const response = await authStore.authorizedRequest('/boards', {
      method: 'POST',
      body: {
        name: payload.name || 'Новая доска',
      },
    })

    const board = mapBoard(response)
    boards.value = [...boards.value, board]
    return board
  }

  async function renameUserBoard(boardId, nextName) {
    const response = await authStore.authorizedRequest(`/boards/${boardId}`, {
      method: 'PATCH',
      body: { name: nextName },
    })

    const updated = mapBoard(response)
    boards.value = boards.value.map((board) => (board.id === boardId ? updated : board))
    return updated
  }

  async function deleteUserBoard(boardId) {
    await authStore.authorizedRequest(`/boards/${boardId}`, {
      method: 'DELETE',
    })

    boards.value = boards.value.filter((board) => board.id !== boardId)
    const { [boardId]: _ignored, ...restCards } = cardsByBoardId.value
    cardsByBoardId.value = restCards
  }

  function removeTagFromMainStyleCards(tagId) {
    if (!Number.isInteger(tagId)) {
      return
    }

    const nextCardsByBoardId = { ...cardsByBoardId.value }
    Object.entries(nextCardsByBoardId).forEach(([boardId, cards]) => {
      const board = getBoardById(Number(boardId))
      if (!board || !isMainStyleCardBoard(board.id)) {
        return
      }

      nextCardsByBoardId[boardId] = cards.map((card) => {
        if (!Array.isArray(card.tagIds) || !card.tagIds.includes(tagId)) {
          return card
        }
        return {
          ...card,
          tagIds: card.tagIds.filter((id) => id !== tagId),
        }
      })
    })

    cardsByBoardId.value = nextCardsByBoardId
  }

  function startCardSelection(action, boardId) {
    selectedCardActionEvent.value = null
    pendingCardSelection.value = {
      action,
      boardId,
    }
  }

  function clearCardSelection() {
    pendingCardSelection.value = {
      action: null,
      boardId: null,
    }
  }

  function pickCardOnBoard(boardId, cardId) {
    const pending = pendingCardSelection.value
    if (!pending.action || pending.boardId !== boardId) {
      return
    }

    selectedCardActionEvent.value = {
      action: pending.action,
      boardId,
      cardId,
      timestamp: Date.now(),
    }

    clearCardSelection()
  }

  return {
    boards,
    cardsByBoardId,
    systemBoardIdsByKind,
    loadingBoards,
    loadingCardsById,
    pendingCardSelection,
    selectedCardActionEvent,
    BOARD_KIND,
    loadBoards,
    fetchBoard,
    getAllBoards,
    getSelectableBoards,
    getBoardById,
    getBoardRoute,
    getBoardDisplayName,
    getBoardIdFromRoute,
    normalizeBoardId,
    isUserBoard,
    isCardBoard,
    isMainStyleCardBoard,
    getCards,
    getCardById,
    getCardDisplayName,
    fetchCards,
    ensureCardLayouts,
    createCard,
    updateCard,
    deleteCard,
    persistLayouts,
    createUserBoard,
    renameUserBoard,
    deleteUserBoard,
    removeTagFromMainStyleCards,
    startCardSelection,
    clearCardSelection,
    pickCardOnBoard,
  }
})
