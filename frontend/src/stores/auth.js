import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

const DEV_USER_ROLE = {
  USER: 'user',
  ADMIN: 'admin',
  ANONYMOUS: 'anonymous',
}

const DEV_USERS = {
  anonymous: {
    id: null,
    name: 'Гость',
    role: DEV_USER_ROLE.ANONYMOUS,
    accessToken: null,
    avatar: '',
  },
  user: {
    id: 100,
    name: 'Обычный пользователь',
    role: DEV_USER_ROLE.USER,
    accessToken: 'dev-token-user',
    avatar: 'https://i.pravatar.cc/150?img=2',
  },
  admin: {
    id: 1,
    name: 'Администратор',
    role: DEV_USER_ROLE.ADMIN,
    accessToken: 'dev-token-admin',
    avatar: 'https://i.pravatar.cc/150?img=1',
  },
}

// Переключайте this key для проверки интерфейса под разными ролями.
const ACTIVE_DEV_USER_KEY = 'anonymous'

function resolveDevUser(userKey) {
  return DEV_USERS[userKey] ?? DEV_USERS.anonymous
}

export const useAuthStore = defineStore('auth', () => {
  const initialUser = resolveDevUser(ACTIVE_DEV_USER_KEY)
  const currentUser = ref({ ...initialUser })
  const accessToken = ref(initialUser.accessToken)

  const role = computed(() => currentUser.value?.role ?? DEV_USER_ROLE.ANONYMOUS)
  const isAdmin = computed(() => role.value === DEV_USER_ROLE.ADMIN)
  const isAuthenticated = computed(() => role.value !== DEV_USER_ROLE.ANONYMOUS)
  const currentUserProfile = computed(() => ({
    id: currentUser.value?.id ?? null,
    name: currentUser.value?.name ?? '',
    avatar: currentUser.value?.avatar ?? '',
  }))

  function setUserFromApiPayload(payload = {}) {
    currentUser.value = {
      id: Number.isInteger(payload.id) ? payload.id : null,
      name: String(payload.name ?? payload.username ?? '').trim() || 'Пользователь',
      role: [DEV_USER_ROLE.ADMIN, DEV_USER_ROLE.USER].includes(payload.role) ? payload.role : DEV_USER_ROLE.ANONYMOUS,
      accessToken: accessToken.value,
      avatar: String(payload.avatar ?? '').trim(),
    }
  }

  function setAuthenticatedUser(user = {}) {
    currentUser.value = {
      id: Number.isInteger(user.id) ? user.id : null,
      name: String(user.name ?? '').trim() || 'Пользователь',
      role: user.isAdmin ? DEV_USER_ROLE.ADMIN : DEV_USER_ROLE.USER,
      accessToken: accessToken.value,
      avatar: String(user.avatar ?? '').trim(),
    }
  }

  function updateCurrentUserProfile(payload = {}) {
    currentUser.value = {
      ...currentUser.value,
      name: String(payload.name ?? currentUser.value?.name ?? '').trim() || currentUser.value?.name,
      avatar: payload.avatar ?? currentUser.value?.avatar ?? '',
    }
  }

  function setAccessToken(token) {
    accessToken.value = String(token ?? '').trim()
  }

  function clearSession() {
    accessToken.value = ''
    currentUser.value = { ...DEV_USERS.anonymous }
  }

  return {
    DEV_USER_ROLE,
    currentUser,
    accessToken,
    role,
    isAdmin,
    isAuthenticated,
    currentUserProfile,
    setUserFromApiPayload,
    setAuthenticatedUser,
    updateCurrentUserProfile,
    setAccessToken,
    clearSession,
  }
})
