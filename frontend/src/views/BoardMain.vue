<template>
  <div class="w-full overflow-x-auto p-[2px]">
    <div
      ref="gridRef"
      class="board-grid min-w-[960px]"
      :class="{ 'board-grid--editable': canEdit }"
      :style="gridStyle"
      @dragover="onGridDragOver"
      @dragleave="onGridDragLeave"
      @drop="onGridDrop"
    >
      <div
        v-for="card in cards"
        :key="card.id"
        class="board-card"
        :class="{
          'board-card--editable': canEdit,
          'board-card--selectable': isCardSelectionMode,
        }"
        :style="getCardStyle(card.id)"
        :draggable="canEdit"
        @dragstart="onCardDragStart(card.id, $event)"
        @dragend="onCardDragEnd"
        @click="onCardClick(card.id)"
      >
        <CardNormal
          :image-src="card.imageSrc"
          :title="card.title"
          :content="card.content"
          :tags="resolveCardTags(card)"
        />

        <button
          v-if="canEdit"
          type="button"
          class="resize-handle"
          @pointerdown="onResizePointerDown(card.id, $event)"
          aria-label="Изменить размер карточки"
        />
      </div>

      <div v-if="canEdit" class="board-grid-overlay" :style="overlayStyle" aria-hidden="true">
        <div v-for="cell in overlayCells" :key="cell" class="board-grid-overlay__cell" />
      </div>

      <div
        v-if="canEdit && hasTargetPreview"
        class="drag-target-shadow"
        :class="{ 'drag-target-shadow--invalid': !dragPreviewIsValid }"
        :style="dragPreviewStyle"
        aria-hidden="true"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import CardNormal from '@/components/CardNormal.vue'
import { useBoardsStore } from '@/stores/boards'
import { useBoardCardsStore, MAIN_BOARD_KEY, INVALID_BOARD_ID } from '@/stores/boardCards'
import { useTagsStore } from '@/stores/tags'
import { useAuthStore } from '@/stores/auth'

const boardsStore = useBoardsStore()
const boardCardsStore = useBoardCardsStore()
const tagsStore = useTagsStore()
const authStore = useAuthStore()
const { pendingCardSelection, systemBoardIdsByKind } = storeToRefs(boardCardsStore)
const { tags } = storeToRefs(tagsStore)
const boardId = computed(() => systemBoardIdsByKind.value[MAIN_BOARD_KEY] ?? INVALID_BOARD_ID)
const DEFAULT_CARD_LAYOUT = { col: 1, row: 1, colSpan: 1, rowSpan: 1 }
const DEFAULT_DYNAMIC_LAYOUT_SPAN = { colSpan: 4, rowSpan: 3 }
const gridRef = ref(null)
const draggedCardId = ref(null)
const resizeState = ref(null)
const dragPreviewLayout = ref(null)
const resizePreviewLayout = ref(null)
const isDesktop = ref(false)
const transientLayouts = ref({})

const cards = computed(() => boardCardsStore.getCards(boardId.value))
const tagById = computed(() => new Map(tags.value.map((tag) => [tag.id, tag])))

const resolveCardTags = (card) => {
  if (!Array.isArray(card.tagIds) || card.tagIds.length === 0) {
    return []
  }

  return card.tagIds.map((tagId) => tagById.value.get(tagId)).filter(Boolean)
}

const defaultLayouts = {}

const canEdit = computed(() => boardsStore.isLayoutEditMode && isDesktop.value)
const isCardSelectionMode = computed(() => {
  return (
    pendingCardSelection.value.action !== null &&
    pendingCardSelection.value.boardId === boardId.value &&
    !canEdit.value
  )
})

const gridSettings = computed(() => boardsStore.getActiveGridSettings(boardId.value))
const activeLayouts = computed(() => boardsStore.getActiveBoardLayouts(boardId.value))

const gridStyle = computed(() => {
  const settings = gridSettings.value
  return {
    display: 'grid',
    gridTemplateColumns: `repeat(${settings.columns}, minmax(0, 1fr))`,
    gridTemplateRows: `repeat(${settings.rows}, ${settings.rowHeight}px)`,
    gap: '1.25rem',
  }
})

const overlayStyle = computed(() => {
  const settings = gridSettings.value
  return {
    gridTemplateColumns: `repeat(${settings.columns}, minmax(0, 1fr))`,
    gridTemplateRows: `repeat(${settings.rows}, ${settings.rowHeight}px)`,
    gap: '1.25rem',
  }
})

const overlayCells = computed(() => {
  const settings = gridSettings.value
  return Array.from({ length: settings.columns * settings.rows }, (_, index) => index)
})

const dragPreviewStyle = computed(() => {
  const targetLayout = dragPreviewLayout.value ?? resizePreviewLayout.value
  if (!targetLayout) {
    return {}
  }

  return {
    gridColumn: `${targetLayout.col} / span ${targetLayout.colSpan}`,
    gridRow: `${targetLayout.row} / span ${targetLayout.rowSpan}`,
  }
})

const dragPreviewIsValid = computed(() => {
  if (draggedCardId.value && dragPreviewLayout.value) {
    return boardsStore.canPlaceCardLayout(
      boardId.value,
      draggedCardId.value,
      dragPreviewLayout.value,
    )
  }

  if (resizeState.value?.cardId && resizePreviewLayout.value) {
    return boardsStore.canPlaceCardLayout(
      boardId.value,
      resizeState.value.cardId,
      resizePreviewLayout.value,
    )
  }

  return true
})

const hasTargetPreview = computed(() => {
  return Boolean(dragPreviewLayout.value || resizePreviewLayout.value)
})

const updateViewportState = () => {
  isDesktop.value = window.matchMedia('(min-width: 1024px)').matches
}

const getCardLayout = (cardId) => {
  return (
    activeLayouts.value[cardId] ??
    defaultLayouts[cardId] ??
    transientLayouts.value[cardId] ??
    DEFAULT_CARD_LAYOUT
  )
}

const getCardStyle = (cardId) => {
  const layout = getCardLayout(cardId)
  return {
    gridColumn: `${layout.col} / span ${layout.colSpan}`,
    gridRow: `${layout.row} / span ${layout.rowSpan}`,
  }
}

const clamp = (value, min, max) => {
  return Math.min(Math.max(value, min), max)
}

const getGridMetrics = () => {
  const gridElement = gridRef.value
  if (!gridElement) {
    return null
  }

  const rect = gridElement.getBoundingClientRect()
  const styles = window.getComputedStyle(gridElement)
  const colGap = Number.parseFloat(styles.columnGap) || 0
  const rowGap = Number.parseFloat(styles.rowGap) || 0
  const settings = gridSettings.value
  const cellWidth = (rect.width - (settings.columns - 1) * colGap) / settings.columns

  return {
    rect,
    colGap,
    rowGap,
    cellWidth,
    cellHeight: settings.rowHeight,
    columns: settings.columns,
    rows: settings.rows,
  }
}

const getCellFromPointer = (event, metrics) => {
  const x = event.clientX - metrics.rect.left
  const y = event.clientY - metrics.rect.top
  const col = Math.floor(x / (metrics.cellWidth + metrics.colGap)) + 1
  const row = Math.floor(y / (metrics.cellHeight + metrics.rowGap)) + 1

  return {
    col: clamp(col, 1, metrics.columns),
    row: clamp(row, 1, metrics.rows),
  }
}

const getPreviewPlacement = (event, cardLayout) => {
  const metrics = getGridMetrics()
  if (!metrics) {
    return null
  }

  const cell = getCellFromPointer(event, metrics)
  return {
    col: clamp(cell.col, 1, metrics.columns - cardLayout.colSpan + 1),
    row: clamp(cell.row, 1, metrics.rows - cardLayout.rowSpan + 1),
    colSpan: cardLayout.colSpan,
    rowSpan: cardLayout.rowSpan,
  }
}

const clearDragPreview = () => {
  dragPreviewLayout.value = null
}

const clearResizePreview = () => {
  resizePreviewLayout.value = null
}

const onCardDragStart = (cardId, event) => {
  if (!canEdit.value) {
    return
  }

  draggedCardId.value = cardId
  dragPreviewLayout.value = getCardLayout(cardId)
  event.dataTransfer?.setData('text/plain', cardId)
  event.dataTransfer?.setDragImage(event.currentTarget, 24, 24)
}

const onCardDragEnd = () => {
  draggedCardId.value = null
  clearDragPreview()
}

const onCardClick = (cardId) => {
  if (!isCardSelectionMode.value) {
    return
  }

  boardCardsStore.pickCardOnBoard(boardId.value, cardId)
}

const onGridDragOver = (event) => {
  if (!canEdit.value) {
    return
  }

  event.preventDefault()

  if (!draggedCardId.value) {
    return
  }

  const cardLayout = getCardLayout(draggedCardId.value)
  const preview = getPreviewPlacement(event, cardLayout)
  if (!preview) {
    return
  }

  dragPreviewLayout.value = preview
}

const onGridDragLeave = (event) => {
  if (!canEdit.value || !draggedCardId.value) {
    return
  }

  if (event.currentTarget.contains(event.relatedTarget)) {
    return
  }

  clearDragPreview()
}

const onGridDrop = (event) => {
  if (!canEdit.value) {
    return
  }

  event.preventDefault()
  const droppedCardId = draggedCardId.value || event.dataTransfer?.getData('text/plain')
  if (!droppedCardId) {
    return
  }

  const droppedCardLayout = getCardLayout(droppedCardId)
  const preview = dragPreviewLayout.value ?? getPreviewPlacement(event, droppedCardLayout)
  if (!preview) {
    return
  }

  if (dragPreviewIsValid.value) {
    boardsStore.updateDraftCardLayout(boardId.value, droppedCardId, {
      col: preview.col,
      row: preview.row,
      colSpan: preview.colSpan,
      rowSpan: preview.rowSpan,
    })
  }

  draggedCardId.value = null
  clearDragPreview()
}

const onResizePointerMove = (event) => {
  const state = resizeState.value
  if (!state || !canEdit.value) {
    return
  }

  const currentLayout = getCardLayout(state.cardId)
  const maxColSpan = gridSettings.value.columns - currentLayout.col + 1
  const maxRowSpan = gridSettings.value.rows - currentLayout.row + 1
  const deltaX = event.clientX - state.startX
  const deltaY = event.clientY - state.startY
  const nextColSpan = state.startColSpan + Math.round(deltaX / state.colStep)
  const nextRowSpan = state.startRowSpan + Math.round(deltaY / state.rowStep)

  resizePreviewLayout.value = {
    ...currentLayout,
    colSpan: clamp(nextColSpan, 1, maxColSpan),
    rowSpan: clamp(nextRowSpan, 1, maxRowSpan),
  }
}

const cleanupResize = () => {
  resizeState.value = null
  clearResizePreview()
  window.removeEventListener('pointermove', onResizePointerMove)
  window.removeEventListener('pointerup', stopResize)
}

const stopResize = () => {
  const state = resizeState.value
  if (state && resizePreviewLayout.value && dragPreviewIsValid.value) {
    boardsStore.updateDraftCardLayout(boardId.value, state.cardId, {
      colSpan: resizePreviewLayout.value.colSpan,
      rowSpan: resizePreviewLayout.value.rowSpan,
    })
  }

  cleanupResize()
}

const onResizePointerDown = (cardId, event) => {
  if (!canEdit.value) {
    return
  }

  event.preventDefault()
  event.stopPropagation()
  const metrics = getGridMetrics()
  if (!metrics) {
    return
  }

  const layout = getCardLayout(cardId)
  resizeState.value = {
    cardId,
    startX: event.clientX,
    startY: event.clientY,
    startColSpan: layout.colSpan,
    startRowSpan: layout.rowSpan,
    colStep: metrics.cellWidth + metrics.colGap,
    rowStep: metrics.cellHeight + metrics.rowGap,
  }
  resizePreviewLayout.value = {
    ...layout,
  }

  window.addEventListener('pointermove', onResizePointerMove)
  window.addEventListener('pointerup', stopResize)
}

const findFirstAvailableLayout = (layouts) => {
  const settings = gridSettings.value
  const candidateSpan = DEFAULT_DYNAMIC_LAYOUT_SPAN

  for (let row = 1; row <= settings.rows - candidateSpan.rowSpan + 1; row += 1) {
    for (let col = 1; col <= settings.columns - candidateSpan.colSpan + 1; col += 1) {
      const candidate = {
        col,
        row,
        colSpan: candidateSpan.colSpan,
        rowSpan: candidateSpan.rowSpan,
      }

      const overlaps = Object.values(layouts).some((layout) => {
        const aRight = layout.col + layout.colSpan
        const bRight = candidate.col + candidate.colSpan
        const aBottom = layout.row + layout.rowSpan
        const bBottom = candidate.row + candidate.rowSpan

        return (
          layout.col < bRight &&
          aRight > candidate.col &&
          layout.row < bBottom &&
          aBottom > candidate.row
        )
      })

      if (!overlaps) {
        return candidate
      }
    }
  }

  return {
    col: 1,
    row: 1,
    colSpan: candidateSpan.colSpan,
    rowSpan: candidateSpan.rowSpan,
  }
}

const syncTransientLayouts = () => {
  const nextTransient = { ...transientLayouts.value }
  const knownLayouts = {
    ...defaultLayouts,
    ...activeLayouts.value,
    ...nextTransient,
  }
  const activeIds = new Set(cards.value.map((card) => String(card.id)))

  Object.keys(nextTransient).forEach((cardId) => {
    if (!activeIds.has(cardId) || activeLayouts.value[cardId]) {
      delete nextTransient[cardId]
      delete knownLayouts[cardId]
    }
  })

  cards.value.forEach((card) => {
    if (knownLayouts[card.id]) {
      return
    }

    const layout = findFirstAvailableLayout(knownLayouts)
    nextTransient[card.id] = layout
    knownLayouts[card.id] = layout
  })

  transientLayouts.value = nextTransient
}

const loadBoardData = async () => {
  await boardCardsStore.loadBoards()
  if (authStore.isAuthenticated) {
    tagsStore.fetchTags()
  }
  if (boardId.value !== INVALID_BOARD_ID) {
    await boardCardsStore.fetchCards(boardId.value)
  }
}

onMounted(() => {
  updateViewportState()
  window.addEventListener('resize', updateViewportState)
  loadBoardData()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateViewportState)
  cleanupResize()
})

watch(canEdit, (editable) => {
  if (!editable) {
    draggedCardId.value = null
    clearDragPreview()
    cleanupResize()
  }
})

watch(
  [cards, activeLayouts, gridSettings],
  () => {
    syncTransientLayouts()
  },
  { immediate: true, deep: true },
)

watch(
  boardId,
  (nextBoardId) => {
    if (nextBoardId !== INVALID_BOARD_ID) {
      boardCardsStore.fetchCards(nextBoardId)
    }
  },
  { immediate: true },
)
</script>

<style scoped>
.board-grid {
  position: relative;
}

.board-card {
  min-height: 0;
  position: relative;
  z-index: 2;
}

.board-card--editable {
  cursor: grab;
}

.board-card--editable:active {
  cursor: grabbing;
}

.board-card--selectable {
  cursor: pointer;
  outline: 2px solid rgba(2, 94, 161, 0.45);
  border-radius: 0.5rem;
}

.board-card--selectable:hover {
  outline-color: rgba(2, 94, 161, 0.8);
}

.resize-handle {
  border: 0;
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 0.375rem;
  background: linear-gradient(135deg, transparent 0%, transparent 45%, #025ea1 45%, #025ea1 100%);
  position: absolute;
  right: 0.375rem;
  bottom: 0.375rem;
  cursor: nwse-resize;
}

.board-grid-overlay {
  position: absolute;
  inset: 0;
  display: grid;
  pointer-events: none;
  z-index: 1;
}

.board-grid-overlay__cell {
  border: 1px dashed rgba(2, 94, 161, 0.25);
  border-radius: 0.375rem;
  background: rgba(2, 94, 161, 0.04);
}

.drag-target-shadow {
  z-index: 3;
  pointer-events: none;
  border-radius: 0.5rem;
  border: 2px solid rgba(2, 94, 161, 0.5);
  background: rgba(2, 94, 161, 0.15);
  box-shadow: 0 6px 18px rgba(2, 94, 161, 0.2);
}

.drag-target-shadow--invalid {
  border-color: rgba(220, 38, 38, 0.75);
  background: rgba(220, 38, 38, 0.16);
  box-shadow: 0 6px 18px rgba(220, 38, 38, 0.24);
}
</style>
