<template>
  <div
    class="box-border flex flex-wrap justify-center items-center content-center gap-4 overflow-y-auto p-4"
  >
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
import { onMounted } from 'vue'
import CardService from '@/components/CardService.vue'
import { useBoardsStore } from '@/stores/boards'

const boardsStore = useBoardsStore()
const BOARD_ID = 3

onMounted(async () => {
  await boardsStore.fetchBoard(BOARD_ID)
})
</script>
