import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { ApiError, apiRequest } from '@/api/client'

const USER_ROLE = {
  EMPLOYEE: 'employee',
  ADMIN: 'admin',
  ANONYMOUS: 'anonymous',
}

const ANONYMOUS_USER = {
  id: null,
  name: 'Гость',
  role: USER_ROLE.ANONYMOUS,
}

export const useAuthStore = defineStore('auth', () => {
  const currentUser = ref({ ...ANONYMOUS_USER })
  const accessToken = ref('')
  const isBootstrapped = ref(false)

  const role = computed(() => currentUser.value?.role ?? USER_ROLE.ANONYMOUS)
  const isAdmin = computed(() => role.value === USER_ROLE.ADMIN)
  const isAuthenticated = computed(() => role.value !== USER_ROLE.ANONYMOUS)
  const currentUserProfile = computed(() => ({
    id: currentUser.value?.id ?? null,
    name: currentUser.value?.name ?? '',
  }))

  function setUserFromApiPayload(payload = {}) {
    currentUser.value = {
      id: Number.isInteger(payload.id) ? payload.id : null,
      name: String(payload.username ?? payload.name ?? '').trim() || 'Пользователь',
      role: [USER_ROLE.ADMIN, USER_ROLE.EMPLOYEE].includes(payload.role)
        ? payload.role
        : USER_ROLE.ANONYMOUS,
    }
  }

  function setAccessToken(token) {
    accessToken.value = String(token ?? '').trim()
  }

  function clearSession() {
    accessToken.value = ''
    currentUser.value = { ...ANONYMOUS_USER }
  }

  async function fetchCurrentUser() {
    if (!accessToken.value) {
      clearSession()
      return null
    }

    const payload = await apiRequest('/users/me', {
      token: accessToken.value,
    })
    setUserFromApiPayload(payload)
    return currentUser.value
  }

  async function refreshAccessToken() {
    const payload = await apiRequest('/auth/refresh', {
      method: 'POST',
    })
    setAccessToken(payload.access_token)
    return payload.access_token
  }

  async function bootstrapSession() {
    if (isBootstrapped.value) {
      return
    }

    isBootstrapped.value = true
    if (accessToken.value) {
      await fetchCurrentUser()
      return
    }

    try {
      await refreshAccessToken()
      await fetchCurrentUser()
    } catch {
      clearSession()
    }
  }

  async function login(username, password) {
    const payload = await apiRequest('/auth/login', {
      method: 'POST',
      form: {
        username,
        password,
      },
    })

    setAccessToken(payload.access_token)
    await fetchCurrentUser()
    return currentUser.value
  }

  async function logout() {
    try {
      await apiRequest('/auth/logout', {
        method: 'POST',
        token: accessToken.value || undefined,
      })
    } finally {
      clearSession()
    }
  }

  async function updateProfile({ name, password }) {
    if (!accessToken.value) {
      return null
    }

    const updates = {}
    if (typeof name === 'string' && name.trim()) {
      updates.username = name.trim()
    }
    if (typeof password === 'string' && password.trim()) {
      updates.password = password
    }

    const payload = await apiRequest('/users/me', {
      method: 'PATCH',
      body: updates,
      token: accessToken.value,
    })
    setUserFromApiPayload(payload)
    return currentUser.value
  }

  async function authorizedRequest(path, options = {}) {
    try {
      return await apiRequest(path, { ...options, token: accessToken.value })
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        await refreshAccessToken()
        return apiRequest(path, { ...options, token: accessToken.value })
      }
      throw error
    }
  }

  return {
    USER_ROLE,
    currentUser,
    accessToken,
    role,
    isAdmin,
    isAuthenticated,
    currentUserProfile,
    setUserFromApiPayload,
    setAccessToken,
    clearSession,
    fetchCurrentUser,
    refreshAccessToken,
    bootstrapSession,
    login,
    logout,
    updateProfile,
    authorizedRequest,
  }
})
