<template>
  <Popover ref="popoverRef" class="profile-popover" @show="onPopoverShow">
    <div class="flex w-[340px] flex-col gap-4 p-2">
      <div class="flex items-center gap-3">
        <Avatar shape="circle" size="large" />
        <div class="min-w-0">
          <div class="truncate text-sm font-semibold text-brand-500">Ваш профиль</div>
          <div class="truncate text-xs text-color-secondary">{{ currentUserLabel }}</div>
        </div>
      </div>

      <div class="flex flex-col gap-3">
        <div class="flex flex-col gap-1">
          <label class="text-xs font-medium text-slate-600" for="profile-name">Имя</label>
          <InputText
            id="profile-name"
            v-model="nameDraft"
            type="text"
            class="w-full"
            :invalid="Boolean(nameError)"
          />
        </div>

        <div class="flex flex-col gap-1">
          <label class="text-xs font-medium text-slate-600" for="profile-password"
            >Новый пароль (опционально)</label
          >
          <InputText
            id="profile-password"
            v-model="passwordDraft"
            type="password"
            class="w-full"
            placeholder="Оставьте пустым, если не хотите менять"
          />
        </div>

        <Message v-if="nameError" severity="error" size="small" variant="simple">
          {{ nameError }}
        </Message>
      </div>

      <div class="flex justify-end gap-2">
        <Button size="small" severity="secondary" variant="outlined" @click="onCancel">
          Отмена
        </Button>
        <Button size="small" @click="onSave">Сохранить</Button>
      </div>
    </div>
  </Popover>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Avatar, Button, InputText, Message, Popover } from 'primevue'
import { useAuthStore } from '@/stores/auth'

const popoverRef = ref(null)
const authStore = useAuthStore()

const nameDraft = ref('')
const passwordDraft = ref('')
const nameError = ref('')

const currentUserLabel = computed(() => {
  return authStore.currentUser?.name || 'Пользователь'
})

const syncFormState = () => {
  nameDraft.value = authStore.currentUser?.name ?? ''
  passwordDraft.value = ''
  nameError.value = ''
}

const onPopoverShow = () => {
  syncFormState()
}

const open = (event) => {
  syncFormState()
  popoverRef.value?.toggle(event)
}

const hide = () => {
  popoverRef.value?.hide()
}

const onCancel = () => {
  syncFormState()
  hide()
}

const onSave = async () => {
  const nextName = nameDraft.value.trim()
  if (!nextName) {
    nameError.value = 'Введите имя пользователя.'
    return
  }

  await authStore.updateProfile({
    name: nextName,
    password: passwordDraft.value,
  })

  hide()
}

defineExpose({
  open,
})
</script>

<style scoped>
.profile-popover :deep(.p-popover-content) {
  padding: 0;
}
</style>
