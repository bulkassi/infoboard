<template>
  <Dialog v-model:visible="visible" modal class="w-[40rem] max-w-[95vw]">
    <template #header>
      <div class="inline-flex items-center gap-2">
        <PhShareFat :size="20" weight="duotone" />
        <span class="text-lg font-semibold">Ссылки для доступа</span>
      </div>
    </template>

    <div class="flex flex-col gap-3">
      <div class="flex justify-between items-center">
        <span class="text-sm text-surface-700">
          Доска: <strong>{{ boardTitle }}</strong>
        </span>
        <Button size="small" @click="createLink" :disabled="isBusy || !canCreate">
          Создать ссылку
        </Button>
      </div>

      <Message v-if="errorMessage" severity="error" size="small">
        {{ errorMessage }}
      </Message>

      <div v-if="links.length === 0" class="text-sm text-surface-500">Нет активных ссылок.</div>

      <ul v-else class="flex flex-col gap-2">
        <li
          v-for="link in links"
          :key="link.token"
          class="flex flex-col gap-2 rounded-md border border-surface-200 p-2"
        >
          <div class="text-xs text-surface-500">Действует до {{ formatDate(link.expires_at) }}</div>
          <div class="flex items-center gap-2">
            <InputText class="flex-1" :modelValue="buildShareUrl(link.token)" readonly />
            <Button size="small" severity="secondary" @click="copyLink(link.token)">
              Копировать
            </Button>
            <Button size="small" severity="danger" @click="deleteLink(link.token)">
              Отозвать
            </Button>
          </div>
        </li>
      </ul>
    </div>
  </Dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Button, Dialog, InputText, Message } from 'primevue'
import { PhShareFat } from '@phosphor-icons/vue'
import { useShareLinksStore } from '@/stores/shareLinks'
import { useBoardCardsStore } from '@/stores/boardCards'

const visible = defineModel('visible')

const props = defineProps({
  boardId: {
    type: Number,
    required: true,
  },
})

const shareLinksStore = useShareLinksStore()
const boardCardsStore = useBoardCardsStore()
const isBusy = ref(false)
const errorMessage = ref('')

const links = computed(() => shareLinksStore.getLinks(props.boardId))
const boardTitle = computed(() => boardCardsStore.getBoardDisplayName(props.boardId))
const canCreate = computed(() => Number.isInteger(props.boardId))

const formatDate = (iso) => {
  const date = iso ? new Date(iso) : null
  if (!date || Number.isNaN(date.getTime())) {
    return 'неизвестно'
  }
  return date.toLocaleString()
}

const buildShareUrl = (token) => {
  const base = window.location.origin
  const route = boardCardsStore.getBoardRoute(props.boardId)
  return `${base}${route}?share_token=${encodeURIComponent(token)}`
}

const copyLink = async (token) => {
  const link = buildShareUrl(token)
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(link)
  } else {
    window.prompt('Скопируйте ссылку:', link)
  }
}

const createLink = async () => {
  errorMessage.value = ''
  isBusy.value = true
  try {
    await shareLinksStore.createLink(props.boardId)
  } catch (error) {
    errorMessage.value = 'Не удалось создать ссылку.'
  } finally {
    isBusy.value = false
  }
}

const deleteLink = async (token) => {
  errorMessage.value = ''
  isBusy.value = true
  try {
    await shareLinksStore.deleteLink(token)
  } catch (error) {
    errorMessage.value = 'Не удалось удалить ссылку.'
  } finally {
    isBusy.value = false
  }
}

const loadLinks = async () => {
  if (!Number.isInteger(props.boardId)) {
    return
  }

  errorMessage.value = ''
  isBusy.value = true
  try {
    await shareLinksStore.fetchLinks(props.boardId)
  } catch (error) {
    errorMessage.value = 'Не удалось загрузить ссылки.'
  } finally {
    isBusy.value = false
  }
}

watch(
  () => visible.value,
  (isVisible) => {
    if (isVisible) {
      loadLinks()
    }
  },
)
</script>
