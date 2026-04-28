import { ref } from 'vue'

export const MAIN_BOARD_KEY = 'main'
export const ABOUT_BOARD_KEY = 'about'
export const EMPLOYEES_BOARD_KEY = 'employees'
export const SERVICES_BOARD_KEY = 'services'
export const INVALID_BOARD_ID = -1

const BOARD_KIND = {
  MAIN: 'main',
  ABOUT: 'about',
  EMPLOYEES: 'employees',
  SERVICES: 'services',
  USER: 'user',
}

const STATIC_BOARDS = [
  {
    key: MAIN_BOARD_KEY,
    name: 'Главная',
    owner: 'Системная доска',
    ownerUserId: null,
    kind: BOARD_KIND.MAIN,
    route: '/main',
  },
  {
    key: ABOUT_BOARD_KEY,
    name: 'О нас',
    owner: 'Системная доска',
    ownerUserId: null,
    kind: BOARD_KIND.ABOUT,
    route: '/about',
  },
  {
    key: EMPLOYEES_BOARD_KEY,
    name: 'Сотрудники',
    owner: 'Системная доска',
    ownerUserId: null,
    kind: BOARD_KIND.EMPLOYEES,
    route: '/employees',
  },
  {
    key: SERVICES_BOARD_KEY,
    name: 'Сервисы',
    owner: 'Системная доска',
    ownerUserId: null,
    kind: BOARD_KIND.SERVICES,
    route: '/services',
  },
]

const STATIC_BOARD_BY_ROUTE = {
  '/': MAIN_BOARD_KEY,
  '/main': MAIN_BOARD_KEY,
  '/about': ABOUT_BOARD_KEY,
  '/employees': EMPLOYEES_BOARD_KEY,
  '/services': SERVICES_BOARD_KEY,
}

const DEFAULT_USER_BOARD_OWNER = 'Пользователь'

const userBoards = ref([])

const DEFAULT_IMAGE_BY_BOARD = {
  [MAIN_BOARD_KEY]:
    'https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1200&q=80',
  [EMPLOYEES_BOARD_KEY]:
    'https://yt3.googleusercontent.com/zqWZEp5yBw-Ap3B5ljLA5y66MnJTWAMuGH0T-8usRA0jUA-Y4il0jcqrSHGOa0XX8zYeHr0yF_w=s900-c-k-c0x00ffffff-no-rj',
  [SERVICES_BOARD_KEY]:
    'https://img.icons8.com/external-others-inmotus-design/1200/external-Yandex-browser-others-inmotus-design-2.jpg',
}

function getBoardDefinitionById(boardId) {
  const normalizedBoardId = normalizeBoardId(boardId)
  return getAllBoards().find((board) => board.key === normalizedBoardId || board.id === normalizedBoardId) ?? null
}

export function normalizeBoardId(boardId) {
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

function getNextUserBoardId() {
  const maxBoardId = userBoards.value.reduce((maxId, board) => Math.max(maxId, board.id), -1)
  return maxBoardId + 1
}

function cleanupBoardCardImages(boardId) {
  const cards = cardsByBoardId.value[boardId] ?? []
  cards.forEach((card) => {
    if (isBlobUrl(card.imageSrc)) {
      URL.revokeObjectURL(card.imageSrc)
    }
  })
}

function getBoardKind(boardId) {
  const board = getBoardDefinitionById(boardId)
  return board?.kind ?? null
}

function isMainStyleBoard(boardId) {
  const kind = getBoardKind(boardId)
  return kind === BOARD_KIND.MAIN || kind === BOARD_KIND.USER
}

const cardsByBoardId = ref({
  [MAIN_BOARD_KEY]: [
    {
      id: 'card-1',
      imageSrc:
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80',
      title: 'План на неделю',
      content: 'Проверить задачи, обновить статус по заявкам и согласовать приоритеты на ближайшие дни.',
    },
    {
      id: 'card-2',
      imageSrc:
        'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=1200&q=80',
      title: 'Важное объявление',
      content: 'Сегодня до 16:00 нужно подтвердить участие в встрече с подрядчиками и отправить вопросы.',
    },
    {
      id: 'card-3',
      imageSrc:
        'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1200&q=80',
      title: 'Результаты месяца',
      content: 'В этом месяце закрыли ключевые задачи по поддержке и ускорили обработку обращений клиентов.',
    },
  ],
  [EMPLOYEES_BOARD_KEY]: [
    {
      id: 'employee-1',
      imageSrc: 'https://randomuser.me/api/portraits/men/32.jpg',
      surname: 'Иванов',
      name: 'Алексей',
      patronymic: 'Сергеевич',
      position: 'Руководитель проекта',
    },
    {
      id: 'employee-2',
      imageSrc: 'https://randomuser.me/api/portraits/women/44.jpg',
      surname: 'Петрова',
      name: 'Мария',
      patronymic: 'Андреевна',
      position: 'Тестировщик ПО',
    },
  ],
  [SERVICES_BOARD_KEY]: [
    {
      id: 'service-1',
      link: 'https://ya.ru/',
      imageSrc:
        'https://img.icons8.com/external-others-inmotus-design/1200/external-Yandex-browser-others-inmotus-design-2.jpg',
      serviceName: 'Яндекс',
      serviceDesc: 'Партнер предприятия',
    },
    {
      id: 'service-2',
      link: 'https://1c.ru/',
      imageSrc: 'https://online-kassa.ru/wp-content/uploads/2023/12/1S_LOGO_PNG.webp',
      serviceName: '1С',
      serviceDesc: 'Официальный партнер предприятия уже на протяжении долгого времени!',
    },
  ],
})

export const pendingCardSelection = ref({
  action: null,
  boardId: null,
})

export const selectedCardActionEvent = ref(null)

export function getAllBoards() {
  return [...STATIC_BOARDS, ...userBoards.value]
}

export function getSelectableBoards() {
  return [...userBoards.value]
}

export function getBoardById(boardId) {
  return getBoardDefinitionById(boardId)
}

export function getBoardRoute(boardId) {
  const board = getBoardDefinitionById(boardId)
  return board?.route ?? '/main'
}

export function getBoardDisplayName(boardId) {
  return getBoardDefinitionById(boardId)?.name ?? 'Доска'
}

export function isUserBoard(boardId) {
  return getBoardKind(boardId) === BOARD_KIND.USER
}

export function isCardBoard(boardId) {
  const kind = getBoardKind(boardId)
  return (
    kind === BOARD_KIND.MAIN ||
    kind === BOARD_KIND.EMPLOYEES ||
    kind === BOARD_KIND.SERVICES ||
    kind === BOARD_KIND.USER
  )
}

export function getBoardIdFromRoute(route) {
  const staticBoardKey = STATIC_BOARD_BY_ROUTE[route.path]
  if (staticBoardKey) {
    return staticBoardKey
  }

  if (route.name === 'board-user') {
    const boardId = normalizeBoardId(route.params.boardId)
    if (Number.isInteger(boardId)) {
      return boardId
    }
  }

  return INVALID_BOARD_ID
}

export function createUserBoard(payload = {}) {
  const boardId = getNextUserBoardId()
  const index = userBoards.value.length + 1
  const ownerUserId = Number.isInteger(payload.ownerUserId) ? payload.ownerUserId : null
  const board = {
    id: boardId,
    name: String(payload.name ?? '').trim() || `Доска ${index}`,
    owner: String(payload.owner ?? '').trim() || DEFAULT_USER_BOARD_OWNER,
    ownerUserId,
    kind: BOARD_KIND.USER,
    route: `/board/${boardId}`,
  }

  userBoards.value = [...userBoards.value, board]
  cardsByBoardId.value[boardId] = []
  return board
}

export function renameUserBoard(boardId, nextName, options = {}) {
  if (!isUserBoard(boardId)) {
    return false
  }

  const board = getBoardById(boardId)
  if (!canManageUserBoard(board, options)) {
    return false
  }

  const trimmedName = String(nextName ?? '').trim()
  if (!trimmedName) {
    return false
  }

  userBoards.value = userBoards.value.map((board) => {
    if (board.id !== boardId) {
      return board
    }

    return {
      ...board,
      name: trimmedName,
    }
  })

  return true
}

export function deleteUserBoard(boardId, options = {}) {
  if (!isUserBoard(boardId)) {
    return false
  }

  const board = getBoardById(boardId)
  if (!canManageUserBoard(board, options)) {
    return false
  }

  cleanupBoardCardImages(boardId)

  const { [boardId]: _ignoredCards, ...nextCardsByBoardId } = cardsByBoardId.value
  cardsByBoardId.value = nextCardsByBoardId

  userBoards.value = userBoards.value.filter((board) => board.id !== boardId)

  if (pendingCardSelection.value.boardId === boardId) {
    clearCardSelection()
  }

  if (selectedCardActionEvent.value?.boardId === boardId) {
    selectedCardActionEvent.value = null
  }

  return true
}

function canManageUserBoard(board, options = {}) {
  if (!board || board.kind !== BOARD_KIND.USER) {
    return false
  }

  if (options.isAdmin === true) {
    return true
  }

  if (!Number.isInteger(options.actorUserId)) {
    return true
  }

  return board.ownerUserId === options.actorUserId
}

function canManageBoardCards(boardId, options = {}) {
  const board = getBoardById(boardId)
  if (!board) {
    return false
  }

  if (options.isAdmin === true) {
    return true
  }

  if (board.kind !== BOARD_KIND.USER) {
    return false
  }

  if (!Number.isInteger(options.actorUserId)) {
    return true
  }

  return board.ownerUserId === options.actorUserId
}

export function isMainStyleCardBoard(boardId) {
  return isMainStyleBoard(boardId)
}

function isBlobUrl(url) {
  return typeof url === 'string' && url.startsWith('blob:')
}

function buildCardId(boardId) {
  const cards = cardsByBoardId.value[boardId] ?? []
  const usedIds = new Set(cards.map((card) => String(card.id)))
  const prefix = `board-${boardId}-card-`
  let counter = cards.length + 1

  while (usedIds.has(`${prefix}${counter}`)) {
    counter += 1
  }

  return `${prefix}${counter}`
}

function createImageSrc(boardId, payload, previousCard = null) {
  if (payload.imageFile instanceof File) {
    return URL.createObjectURL(payload.imageFile)
  }

  return previousCard?.imageSrc ?? DEFAULT_IMAGE_BY_BOARD[boardId] ?? ''
}

function normalizeCardPayload(boardId, payload, previousCard = null) {
  const imageSrc = createImageSrc(boardId, payload, previousCard)
  const fallbackTagIds = Array.isArray(previousCard?.tagIds) ? previousCard.tagIds : []
  const sourceTagIds = Array.isArray(payload.tagIds) ? payload.tagIds : fallbackTagIds
  const tagIds = [...new Set(sourceTagIds.filter((tagId) => Number.isInteger(tagId)))]

  if (isMainStyleBoard(boardId)) {
    return {
      id: payload.id,
      imageSrc,
      title: payload.title?.trim() ?? '',
      content: payload.content?.trim() ?? '',
      tagIds,
    }
  }

  if (boardId === EMPLOYEES_BOARD_KEY) {
    return {
      id: payload.id,
      imageSrc,
      surname: payload.surname?.trim() ?? '',
      name: payload.name?.trim() ?? '',
      patronymic: payload.patronymic?.trim() ?? '',
      position: payload.position?.trim() ?? '',
    }
  }

  if (boardId === SERVICES_BOARD_KEY) {
    return {
      id: payload.id,
      imageSrc,
      link: payload.link?.trim() ?? '',
      serviceName: payload.serviceName?.trim() ?? '',
      serviceDesc: payload.serviceDesc?.trim() ?? '',
    }
  }

  return {
    id: payload.id,
    ...payload,
    imageSrc,
  }
}

export function getCards(boardId) {
  return cardsByBoardId.value[boardId] ?? []
}

export function getCardById(boardId, cardId) {
  return getCards(boardId).find((card) => card.id === cardId) ?? null
}

export function getCardDisplayName(boardId, cardId) {
  const card = getCardById(boardId, cardId)
  if (!card) {
    return ''
  }

  if (isMainStyleBoard(boardId)) {
    return card.title || 'Без названия'
  }

  if (boardId === EMPLOYEES_BOARD_KEY) {
    return [card.surname, card.name, card.patronymic].filter(Boolean).join(' ').trim() || 'Без имени'
  }

  if (boardId === SERVICES_BOARD_KEY) {
    return card.serviceName || 'Без названия'
  }

  return String(card.id)
}

export function createCard(boardId, payload, options = {}) {
  if (!canManageBoardCards(boardId, options)) {
    return null
  }

  const cards = [...getCards(boardId)]
  const cardId = buildCardId(boardId)
  const nextCard = normalizeCardPayload(boardId, { ...payload, id: cardId })
  cards.push(nextCard)
  cardsByBoardId.value[boardId] = cards
  return nextCard
}

export function updateCard(boardId, cardId, payload, options = {}) {
  if (!canManageBoardCards(boardId, options)) {
    return null
  }

  const cards = [...getCards(boardId)]
  const index = cards.findIndex((card) => card.id === cardId)
  if (index === -1) {
    return null
  }

  const previousCard = cards[index]
  const nextCard = normalizeCardPayload(boardId, { ...payload, id: cardId }, previousCard)

  if (previousCard.imageSrc !== nextCard.imageSrc && isBlobUrl(previousCard.imageSrc)) {
    URL.revokeObjectURL(previousCard.imageSrc)
  }

  cards[index] = nextCard
  cardsByBoardId.value[boardId] = cards
  return nextCard
}

export function deleteCard(boardId, cardId, options = {}) {
  if (!canManageBoardCards(boardId, options)) {
    return false
  }

  const cards = [...getCards(boardId)]
  const index = cards.findIndex((card) => card.id === cardId)
  if (index === -1) {
    return false
  }

  const [removedCard] = cards.splice(index, 1)
  cardsByBoardId.value[boardId] = cards

  if (isBlobUrl(removedCard.imageSrc)) {
    URL.revokeObjectURL(removedCard.imageSrc)
  }

  return true
}

export function removeTagFromMainStyleCards(tagId) {
  if (!Number.isInteger(tagId)) {
    return
  }

  let changed = false
  const nextCardsByBoardId = { ...cardsByBoardId.value }

  Object.entries(cardsByBoardId.value).forEach(([boardId, cards]) => {
    if (!isMainStyleBoard(boardId)) {
      return
    }

    const nextCards = cards.map((card) => {
      if (!Array.isArray(card.tagIds) || !card.tagIds.includes(tagId)) {
        return card
      }

      changed = true
      return {
        ...card,
        tagIds: card.tagIds.filter((id) => id !== tagId),
      }
    })

    nextCardsByBoardId[boardId] = nextCards
  })

  if (changed) {
    cardsByBoardId.value = nextCardsByBoardId
  }
}

export function startCardSelection(action, boardId) {
  selectedCardActionEvent.value = null
  pendingCardSelection.value = {
    action,
    boardId,
  }
}

export function clearCardSelection() {
  pendingCardSelection.value = {
    action: null,
    boardId: null,
  }
}

export function pickCardOnBoard(boardId, cardId) {
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
