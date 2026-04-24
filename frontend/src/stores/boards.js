import { defineStore } from 'pinia'
import { ref } from 'vue'

const API_BASE = import.meta.env.VITE_API_URL
const DEFAULT_GRID_SETTINGS = {
  columns: 12,
  rows: 8,
  rowHeight: 100,
}
const MIN_GRID_ROWS = 4
const MAX_GRID_ROWS = 24

function cloneValue(value) {
  return JSON.parse(JSON.stringify(value))
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max)
}

function isOverlapping(a, b) {
  const aRight = a.col + a.colSpan
  const bRight = b.col + b.colSpan
  const aBottom = a.row + a.rowSpan
  const bBottom = b.row + b.rowSpan

  return a.col < bRight && aRight > b.col && a.row < bBottom && aBottom > b.row
}

function hasOverlapForCard(layouts, cardId) {
  const target = layouts[cardId]
  if (!target) {
    return false
  }

  return Object.entries(layouts).some(([otherId, otherLayout]) => {
    if (otherId === cardId) {
      return false
    }

    return isOverlapping(target, otherLayout)
  })
}

function hasAnyOverlap(layouts) {
  const ids = Object.keys(layouts)

  for (let index = 0; index < ids.length; index += 1) {
    const left = layouts[ids[index]]

    for (let nextIndex = index + 1; nextIndex < ids.length; nextIndex += 1) {
      const right = layouts[ids[nextIndex]]
      if (isOverlapping(left, right)) {
        return true
      }
    }
  }

  return false
}

export const useBoardsStore = defineStore('boards', () => {
  const boardsById = ref({})
  const loadingById = ref({})
  const errorById = ref({})
  const boardLayoutsById = ref({})
  const boardGridSettingsById = ref({})
  const draftLayoutsById = ref({})
  const draftGridSettingsById = ref({})
  const isLayoutEditMode = ref(false)

  function resetDraftState() {
    draftLayoutsById.value = {}
    draftGridSettingsById.value = {}
  }

  function getGridSettings(boardId) {
    const existing = boardGridSettingsById.value[boardId]
    if (existing) {
      return existing
    }

    boardGridSettingsById.value[boardId] = cloneValue(DEFAULT_GRID_SETTINGS)
    return boardGridSettingsById.value[boardId]
  }

  function getDraftGridSettings(boardId) {
    const existing = draftGridSettingsById.value[boardId]
    if (existing) {
      return existing
    }

    draftGridSettingsById.value[boardId] = cloneValue(getGridSettings(boardId))
    return draftGridSettingsById.value[boardId]
  }

  function initializeBoardLayout(boardId, initialLayouts = {}) {
    if (!boardLayoutsById.value[boardId]) {
      boardLayoutsById.value[boardId] = cloneValue(initialLayouts)
    }

    getGridSettings(boardId)
  }

  function removeBoardLayoutState(boardId) {
    const nextLayouts = { ...boardLayoutsById.value }
    const nextGridSettings = { ...boardGridSettingsById.value }
    const nextDraftLayouts = { ...draftLayoutsById.value }
    const nextDraftGridSettings = { ...draftGridSettingsById.value }

    delete nextLayouts[boardId]
    delete nextGridSettings[boardId]
    delete nextDraftLayouts[boardId]
    delete nextDraftGridSettings[boardId]

    boardLayoutsById.value = nextLayouts
    boardGridSettingsById.value = nextGridSettings
    draftLayoutsById.value = nextDraftLayouts
    draftGridSettingsById.value = nextDraftGridSettings
  }

  function getActiveBoardLayouts(boardId) {
    return isLayoutEditMode.value
      ? (draftLayoutsById.value[boardId] ?? boardLayoutsById.value[boardId] ?? {})
      : (boardLayoutsById.value[boardId] ?? {})
  }

  function getActiveGridSettings(boardId) {
    return isLayoutEditMode.value ? getDraftGridSettings(boardId) : getGridSettings(boardId)
  }

  function normalizeCardLayout(layout, gridSettings) {
    const nextLayout = { ...layout }
    nextLayout.colSpan = clamp(nextLayout.colSpan ?? 1, 1, gridSettings.columns)
    nextLayout.rowSpan = clamp(nextLayout.rowSpan ?? 1, 1, gridSettings.rows)
    nextLayout.col = clamp(nextLayout.col ?? 1, 1, gridSettings.columns - nextLayout.colSpan + 1)
    nextLayout.row = clamp(nextLayout.row ?? 1, 1, gridSettings.rows - nextLayout.rowSpan + 1)
    return nextLayout
  }

  function canPlaceCardLayout(boardId, cardId, layout) {
    const gridSettings = getDraftGridSettings(boardId)
    const nextLayouts = {
      ...getActiveBoardLayouts(boardId),
      [cardId]: normalizeCardLayout(layout, gridSettings),
    }

    return !hasOverlapForCard(nextLayouts, cardId)
  }

  function beginLayoutEdit(boardId) {
    draftLayoutsById.value[boardId] = cloneValue(boardLayoutsById.value[boardId] ?? {})
    draftGridSettingsById.value[boardId] = cloneValue(getGridSettings(boardId))
    isLayoutEditMode.value = true
  }

  function cancelLayoutEdit() {
    isLayoutEditMode.value = false
    resetDraftState()
  }

  function saveLayoutEdit(boardId) {
    if (!isLayoutEditMode.value) {
      return
    }

    boardLayoutsById.value[boardId] = cloneValue(draftLayoutsById.value[boardId] ?? {})
    boardGridSettingsById.value[boardId] = cloneValue(getDraftGridSettings(boardId))
    isLayoutEditMode.value = false
    resetDraftState()
  }

  function setDraftRowCount(boardId, rowCount) {
    if (!isLayoutEditMode.value) {
      return false
    }

    const gridSettings = getDraftGridSettings(boardId)
    const targetRows = clamp(Number(rowCount) || DEFAULT_GRID_SETTINGS.rows, MIN_GRID_ROWS, MAX_GRID_ROWS)
    const currentLayouts = { ...getActiveBoardLayouts(boardId) }
    const testGridSettings = {
      ...gridSettings,
      rows: targetRows,
    }

    const nextLayouts = {}
    for (const [cardId, layout] of Object.entries(currentLayouts)) {
      if (layout.rowSpan > targetRows) {
        return false
      }

      nextLayouts[cardId] = normalizeCardLayout(layout, testGridSettings)
    }

    if (hasAnyOverlap(nextLayouts)) {
      return false
    }

    gridSettings.rows = targetRows
    draftLayoutsById.value[boardId] = nextLayouts
    return true
  }

  function updateDraftCardLayout(boardId, cardId, patch) {
    if (!isLayoutEditMode.value) {
      return false
    }

    const existingLayouts = { ...getActiveBoardLayouts(boardId) }
    const currentLayout = existingLayouts[cardId] ?? { col: 1, row: 1, colSpan: 1, rowSpan: 1 }
    const nextLayout = normalizeCardLayout(
      {
        ...currentLayout,
        ...patch,
      },
      getDraftGridSettings(boardId),
    )

    existingLayouts[cardId] = nextLayout

    if (hasOverlapForCard(existingLayouts, cardId)) {
      return false
    }

    draftLayoutsById.value[boardId] = existingLayouts
    return true
  }

  function resetDraftLayoutOverlap(boardId) {
    const gridSettings = getDraftGridSettings(boardId)
    const nextLayouts = { ...getActiveBoardLayouts(boardId) }

    Object.keys(nextLayouts).forEach((cardId) => {
      nextLayouts[cardId] = normalizeCardLayout(nextLayouts[cardId], gridSettings)
    })

    if (!hasAnyOverlap(nextLayouts)) {
      draftLayoutsById.value[boardId] = nextLayouts
      return true
    }

    return false
  }

  async function fetchBoard(boardId) {
    loadingById.value[boardId] = true
    errorById.value[boardId] = null

    try {
      const response = await fetch(`${API_BASE}/api/boards/${boardId}`)
      if (!response.ok) {
        throw new Error(`Failed to load board ${boardId}: ${response.status}`)
      }
      const board = await response.json()
      boardsById.value[boardId] = board
      return board
    } catch (error) {
      errorById.value[boardId] = error instanceof Error ? error.message : 'Unknown error'
      throw error
    } finally {
      loadingById.value[boardId] = false
    }
  }

  return {
    boardsById,
    loadingById,
    errorById,
    boardLayoutsById,
    boardGridSettingsById,
    isLayoutEditMode,
    fetchBoard,
    initializeBoardLayout,
    removeBoardLayoutState,
    getActiveBoardLayouts,
    getActiveGridSettings,
    beginLayoutEdit,
    saveLayoutEdit,
    cancelLayoutEdit,
    setDraftRowCount,
    updateDraftCardLayout,
    canPlaceCardLayout,
    resetDraftLayoutOverlap,
    MIN_GRID_ROWS,
    MAX_GRID_ROWS,
  }
})
