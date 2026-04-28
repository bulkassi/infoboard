<template>
  <div class="flex min-h-screen items-center justify-center bg-surface-50 p-4">
    <Card class="w-full max-w-md shadow-lg">
      <template #header>
        <div class="bg-primary-500 p-4 text-center text-white">
          <h1 class="text-2xl font-bold">Вход в систему</h1>
          <p class="text-sm opacity-80">Информационное табло</p>
        </div>
      </template>

      <template #content>
        <div class="flex flex-col gap-6 py-4">
          <Message severity="info" :closable="false">
            Войдите, используя имя пользователя из списка и пароль для этого пользователя.
          </Message>

          <Message v-if="errorMessage" severity="error" :closable="false">
            {{ errorMessage }}
          </Message>

          <div class="flex flex-col gap-2">
            <label for="username" class="text-sm font-semibold text-surface-700"
              >Имя пользователя</label
            >
            <InputText
              id="username"
              v-model.trim="username"
              type="text"
              placeholder="Например, Администратор"
              class="w-full"
              autocomplete="username"
            />
          </div>

          <div class="flex flex-col gap-2">
            <label for="password" class="text-sm font-semibold text-surface-700">Пароль</label>
            <Password
              id="password"
              v-model="password"
              placeholder="Введите пароль"
              class="w-full"
              toggleMask
              fluid
              :feedback="false"
              autocomplete="current-password"
            />
          </div>
        </div>
      </template>

      <template #footer>
        <div class="flex gap-3">
          <Button
            label="Назад"
            icon="pi pi-arrow-left"
            outlined
            class="w-full"
            @click="handleCancel"
          />
          <Button
            label="Войти"
            icon="pi pi-sign-in"
            class="w-full"
            @click="handleLogin"
            :loading="isSubmitting"
            :disabled="isSubmitting"
          />
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Card, Button, Message, InputText, Password } from 'primevue'
import { useAuthStore } from '@/stores/auth'
import { useUsersStore } from '@/stores/users'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const usersStore = useUsersStore()

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const isSubmitting = ref(false)

const handleLogin = async () => {
  errorMessage.value = ''
  isSubmitting.value = true

  try {
    const user = usersStore.findUserByCredentials(username.value, password.value)

    if (!user) {
      errorMessage.value = 'Неверное имя пользователя или пароль.'
      return
    }

    authStore.setAuthenticatedUser(user)

    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/main'
    await router.push(redirect)
  } finally {
    isSubmitting.value = false
  }
}

const handleCancel = () => {
  router.push('/main')
}
</script>
