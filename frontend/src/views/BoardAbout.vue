<script setup>
import { computed, onMounted } from 'vue'

import CardNormal from '@/components/CardNormal.vue'
import { useBoardsStore } from '@/stores/boards'

const boardsStore = useBoardsStore()
const BOARD_ID = 1

const boardName = computed(() => boardsStore.boardsById[BOARD_ID]?.name || 'About')

onMounted(async () => {
  await boardsStore.fetchBoard(BOARD_ID)
})
</script>

<template>
  <div class="board">
    <CardNormal
      image-src="https://img.freepik.com/premium-photo/stunning-mountain-landscape_1048944-30333271.jpg"
      :title="boardName"
      content="Информационная доска раздела About"
    />
  </div>
</template>

<style scoped>
.board {
  display: flex;
  justify-content: center;
  padding: 16px;
}
</style>
