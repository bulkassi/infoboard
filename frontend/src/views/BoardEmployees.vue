<template>
  <div
    class="box-border flex flex-wrap justify-center items-center content-center gap-4 overflow-y-auto p-4"
  >
    <CardEmployee
      image-src="https://yt3.googleusercontent.com/zqWZEp5yBw-Ap3B5ljLA5y66MnJTWAMuGH0T-8usRA0jUA-Y4il0jcqrSHGOa0XX8zYeHr0yF_w=s900-c-k-c0x00ffffff-no-rj"
      surname="Walter"
      name="White"
      patronymic="Sergeevich"
      position="Project Manager"
    />
    <CardEmployee
      image-src="https://i.pinimg.com/736x/e0/17/a5/e017a591f196802929bea1e013a083d6.jpg"
      surname="Pinkman"
      name="Jesse"
      patronymic="Antonovich"
      position="Software Tester"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import CardEmployee from '@/components/CardEmployee.vue'
import { useBoardsStore } from '@/stores/boards'

const boardsStore = useBoardsStore()
const BOARD_ID = 2

onMounted(async () => {
  await boardsStore.fetchBoard(BOARD_ID)
})
</script>
