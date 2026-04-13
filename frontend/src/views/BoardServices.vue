<template>
  <div class="board">
    <CardService
      link="https://ya.ru/"
      image-src="https://img.icons8.com/external-others-inmotus-design/1200/external-Yandex-browser-others-inmotus-design-2.jpg"
      service-name="Яндекс"
      service-desc="Партнер предприятия"
    />
    <CardService
      link="https://1c.ru/"
      image-src="https://online-kassa.ru/wp-content/uploads/2023/12/1S_LOGO_PNG.webp"
      service-name="1С"
      service-desc="Официальный партнер предприятия уже на протяжении долгого времени!"
    />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import CardService from '@/components/CardService.vue'
import { useBoardsStore } from '@/stores/boards'

const boardsStore = useBoardsStore()
const BOARD_ID = 3

const boardName = computed(() => boardsStore.boardsById[BOARD_ID]?.name || 'Services')

onMounted(async () => {
  await boardsStore.fetchBoard(BOARD_ID)
})
</script>

<style scoped>
.board {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 16px;

  overflow-y: auto; /* vertical scroll when too tall */
  padding: 16px;
  box-sizing: border-box;
}

.board-title {
  width: 100%;
  margin: 0;
}
</style>
