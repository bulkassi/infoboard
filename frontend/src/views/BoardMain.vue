<template>
  <div class="grid grid-cols-12 grid-rows-[repeat(8,100px)] gap-5">
    <CardNormal
      class="col-span-4 row-span-4"
      image-src="https://i.pinimg.com/originals/19/fc/fb/19fcfbb5debcb7d95a5f73a556a54b39.webp?nii=t"
      title="Карточка 1"
      content="Горы горы горы горы горы горы"
    />
    <CardNormal
      class="col-start-5 col-span-5 row-span-5"
      image-src="https://img.freepik.com/premium-photo/stunning-4k-hd-wallpaper-majestic-mountain_1193781-9607.jpg?semt=ais_hybrid"
      title="Карточка 2"
      content="Еще горы"
    />
    <CardNormal
      class="col-start-10 col-span-2 row-span-3"
      image-src="https://img.freepik.com/premium-photo/majestic-mountain-range-sunset-with-fiery-sky_63085-5917.jpg?semt=ais_hybrid&w=740"
      title="Карточка 3"
      content="А вот еще горы"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import CardNormal from '@/components/CardNormal.vue'
import { useBoardsStore } from '@/stores/boards'

const boardsStore = useBoardsStore()
const BOARD_ID = 0

onMounted(async () => {
  await boardsStore.fetchBoard(BOARD_ID)
})
</script>
