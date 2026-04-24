<template>
  <div
    class="box-border flex flex-wrap justify-center items-center content-center gap-4 overflow-y-auto p-4"
  >
    <div
      v-for="card in cards"
      :key="card.id"
      class="rounded-md"
      :class="{ 'card-selectable': isCardSelectionMode }"
      @click="onCardClick(card.id, $event)"
    >
      <CardService
        :link="card.link"
        :image-src="card.imageSrc"
        :service-name="card.serviceName"
        :service-desc="card.serviceDesc"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import CardService from '@/components/CardService.vue'
import {
  SERVICES_BOARD_KEY,
  getCards,
  pendingCardSelection,
  pickCardOnBoard,
} from '@/state/boardCards'

const BOARD_ID = SERVICES_BOARD_KEY
const cards = computed(() => getCards(BOARD_ID))
const isCardSelectionMode = computed(() => {
  return (
    pendingCardSelection.value.action !== null && pendingCardSelection.value.boardId === BOARD_ID
  )
})

const onCardClick = (cardId, event) => {
  if (!isCardSelectionMode.value) {
    return
  }

  event.preventDefault()
  event.stopPropagation()

  pickCardOnBoard(BOARD_ID, cardId)
}
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
