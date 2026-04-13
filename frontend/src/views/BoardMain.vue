<template>
  <div class="board">
    <CardNormal
      class="card-1"
      image-src="https://i.pinimg.com/originals/19/fc/fb/19fcfbb5debcb7d95a5f73a556a54b39.webp?nii=t"
      title="Карточка 1"
      content="Горы горы горы горы горы горы"
    />
    <CardNormal
      class="card-2"
      image-src="https://img.freepik.com/premium-photo/stunning-4k-hd-wallpaper-majestic-mountain_1193781-9607.jpg?semt=ais_hybrid"
      title="Карточка 2"
      content="Еще горы"
    />
    <CardNormal
      class="card-3"
      image-src="https://img.freepik.com/premium-photo/majestic-mountain-range-sunset-with-fiery-sky_63085-5917.jpg?semt=ais_hybrid&w=740"
      title="Карточка 3"
      content="А вот еще горы"
    />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import CardNormal from '@/components/CardNormal.vue'
import { useBoardsStore } from '@/stores/boards'

const boardsStore = useBoardsStore()
const BOARD_ID = 0

const boardName = computed(() => boardsStore.boardsById[BOARD_ID]?.name || 'Main')

onMounted(async () => {
  await boardsStore.fetchBoard(BOARD_ID)
})
</script>

<style scoped>
.board {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-template-rows: repeat(8, 100px);
  gap: 20px;
}

.board-title {
  grid-column: 1 / span 12;
  margin: 0;
}

.card-1 {
  grid-column: 1 / span 4;
  grid-row: 1 / span 4;
}

.card-2 {
  grid-column: 5 / span 5;
  grid-row: 1 / span 5;
}

.card-3 {
  grid-column: 10 / span 2;
  grid-row: 1 / span 3;
}
</style>
