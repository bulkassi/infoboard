<template>
  <div
    class="box-border flex flex-wrap justify-center items-center content-center gap-4 overflow-y-auto p-4"
  >
    <div
      v-for="card in cards"
      :key="card.id"
      class="rounded-md"
      :class="{ 'card-selectable': isCardSelectionMode }"
      @click="onCardClick(card.id)"
    >
      <CardEmployee
        :image-src="card.imageSrc"
        :surname="card.surname"
        :name="card.name"
        :patronymic="card.patronymic"
        :position="card.position"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import CardEmployee from '@/components/CardEmployee.vue'
import { EMPLOYEES_BOARD_KEY, INVALID_BOARD_ID } from '@/stores/boardCards'
import { useBoardCardsStore } from '@/stores/boardCards'

const boardCardsStore = useBoardCardsStore()
const { pendingCardSelection, systemBoardIdsByKind } = storeToRefs(boardCardsStore)
const boardId = computed(() => systemBoardIdsByKind.value[EMPLOYEES_BOARD_KEY] ?? INVALID_BOARD_ID)
const cards = computed(() => boardCardsStore.getCards(boardId.value))
const isCardSelectionMode = computed(() => {
  return (
    pendingCardSelection.value.action !== null &&
    pendingCardSelection.value.boardId === boardId.value
  )
})

const onCardClick = (cardId) => {
  if (!isCardSelectionMode.value) {
    return
  }

  boardCardsStore.pickCardOnBoard(boardId.value, cardId)
}

const loadBoard = async () => {
  await boardCardsStore.loadBoards()
  if (boardId.value !== INVALID_BOARD_ID) {
    await boardCardsStore.fetchCards(boardId.value)
  }
}

onMounted(() => {
  loadBoard()
})

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
.card-selectable {
  cursor: pointer;
  outline: 2px solid rgba(2, 94, 161, 0.45);
  border-radius: 0.5rem;
}

.card-selectable:hover {
  outline-color: rgba(2, 94, 161, 0.8);
}
</style>
