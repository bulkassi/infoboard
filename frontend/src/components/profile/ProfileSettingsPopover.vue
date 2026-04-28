<template>
  <Popover ref="popoverRef" class="profile-popover" @show="onPopoverShow">
    <div class="flex w-[340px] flex-col gap-4 p-2">
      <div class="flex items-center gap-3">
        <Avatar :image="previewAvatar" shape="circle" size="large" />
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

        <Fieldset pt:root:class="flex flex-col gap-4">
          <template #legend>
            <span class="text-brand-500 text-xs font-medium">Аватар</span>
          </template>
          <FileUploader
            name="profileAvatar[]"
            acceptPattern="image/*"
            :maxFileSize="1000000"
            :fileLimit="1"
            :autoProcess="true"
            chooseLabel="Выбрать изображение"
            removeLabel="Удалить файл"
            emptyLabel="Файл не выбран"
            @files-selected="onAvatarSelected"
            @files-cleared="onAvatarCleared"
          />
          <small class="text-xs text-color-secondary">Разрешены изображения до 1MB.</small>
        </Fieldset>

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
import { Avatar, Button, Fieldset, InputText, Message, Popover } from 'primevue'
import FileUploader from '@/components/FileUploader.vue'
import { useAuthStore } from '@/stores/auth'
import { useUsersStore } from '@/stores/users'

const popoverRef = ref(null)
const authStore = useAuthStore()
const usersStore = useUsersStore()

const nameDraft = ref('')
const passwordDraft = ref('')
const avatarPreviewUrl = ref('')
const nameError = ref('')

const currentUserRecord = computed(() => {
  const userId = authStore.currentUser?.id
  return Number.isInteger(userId) ? usersStore.getUserById(userId) : null
})

const currentUserLabel = computed(() => {
  return authStore.currentUser?.name || 'Пользователь'
})

const previewAvatar = computed(() => {
  if (avatarPreviewUrl.value) {
    return avatarPreviewUrl.value
  }

  return currentUserRecord.value?.avatar || authStore.currentUser?.avatar || ''
})

const syncFormState = () => {
  nameDraft.value = authStore.currentUser?.name ?? ''
  passwordDraft.value = ''
  avatarPreviewUrl.value = ''
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

const onAvatarSelected = (files) => {
  if (!Array.isArray(files) || files.length === 0) {
    avatarPreviewUrl.value = ''
    return
  }

  const first = files[0]
  avatarPreviewUrl.value = first.previewUrl || ''
}

const onAvatarCleared = () => {
  avatarPreviewUrl.value = ''
}

const onCancel = () => {
  syncFormState()
  hide()
}

const onSave = () => {
  const nextName = nameDraft.value.trim()
  if (!nextName) {
    nameError.value = 'Введите имя пользователя.'
    return
  }

  const avatarPayload = avatarPreviewUrl.value || currentUserRecord.value?.avatar || ''

  if (currentUserRecord.value?.id != null) {
    usersStore.updateUser(currentUserRecord.value.id, {
      name: nextName,
      password: passwordDraft.value || currentUserRecord.value.password,
      avatar: avatarPayload,
    })
  }

  authStore.updateCurrentUserProfile({
    name: nextName,
    avatar: avatarPayload,
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
