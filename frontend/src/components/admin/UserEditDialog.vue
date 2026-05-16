<template>
  <Dialog
    v-model:visible="visible"
    modal
    :header="dialogTitle"
    :pt="{
      header: { class: 'text-brand-500' },
      title: { class: 'text-brand-500' },
      content: { class: 'flex flex-col gap-4' },
      closeButtonIcon: { class: 'text-brand-500' },
    }"
  >
    <template #header>
      <div class="inline-flex items-center justify-center gap-1">
        <PhUserCircle :size="24" weight="duotone" />
        <span class="text-lg font-bold">{{ dialogTitle }}</span>
      </div>
    </template>

    <Fieldset pt:root:class="mt-0" pt:content:class="flex flex-col gap-4">
      <template #legend>
        <span class="text-brand-500 text-md font-medium">Параметры пользователя</span>
      </template>

      <form @submit.prevent="onUserFormSubmit" class="flex flex-col gap-4">
        <div class="flex flex-col gap-2">
          <InputText
            v-model="formState.userName"
            type="text"
            placeholder="Имя пользователя"
            class="w-full"
            :invalid="!formState.userName.trim()"
          />

          <InputText
            v-model="formState.userPassword"
            type="password"
            placeholder="Пароль пользователя"
            class="w-full"
          />

          <div class="flex flex-row items-center justify-between">
            <label for="userIsAdmin">Администратор</label>
            <Checkbox v-model="formState.userIsAdmin" inputId="userIsAdmin" binary />
          </div>

          <Message size="small" severity="secondary" variant="simple">
            Аватары пользователей отключены в серверной версии.
          </Message>
        </div>
      </form>

      <div class="flex justify-end gap-2">
        <Button type="button" severity="secondary" @click="resetUserForm">Отменить</Button>
        <Button type="button" @click="onUserFormSubmit">Сохранить</Button>
      </div>
    </Fieldset>
  </Dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

import { Button, Checkbox, Dialog, Fieldset, InputText, Message } from 'primevue'
import { PhUserCircle } from '@phosphor-icons/vue'

const visible = defineModel('visible')

const props = defineProps({
  user: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['save'])

const getDefaultFormState = () => ({
  id: null,
  userName: '',
  userPassword: '',
  userIsAdmin: false,
})

const formState = ref(getDefaultFormState())

const dialogTitle = computed(() =>
  formState.value.id === null ? 'Создание пользователя' : 'Редактирование пользователя',
)

const applyUserToForm = (user) => {
  if (!user) {
    formState.value = getDefaultFormState()
    return
  }

  formState.value = {
    id: user.id ?? null,
    userName: user.name ?? '',
    userPassword: user.password ?? '',
    userIsAdmin: Boolean(user.isAdmin),
  }
}

const resetUserForm = () => {
  applyUserToForm(props.user)
  visible.value = false
}

const onUserFormSubmit = () => {
  const userName = formState.value.userName.trim()
  if (!userName) {
    return
  }

  emit('save', {
    id: formState.value.id,
    userName,
    userPassword: formState.value.userPassword,
    userIsAdmin: formState.value.userIsAdmin,
  })
  visible.value = false
}

watch(
  () => props.user,
  (user) => {
    applyUserToForm(user)
  },
  { immediate: true },
)

watch(visible, (isVisible) => {
  if (isVisible) {
    applyUserToForm(props.user)
  }
})
</script>
