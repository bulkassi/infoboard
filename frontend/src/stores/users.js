import { ref } from 'vue'
import { defineStore } from 'pinia'
import { useAuthStore } from '@/stores/auth'

const ROLE = {
  ADMIN: 'admin',
  EMPLOYEE: 'employee',
}

export const useUsersStore = defineStore('users', () => {
  const authStore = useAuthStore()
  const users = ref([])

  function listUsers() {
    return users.value
  }

  function getUserById(userId) {
    return users.value.find((user) => user.id === userId) ?? null
  }

  function normalizeUser(payload) {
    return {
      id: payload.id,
      name: payload.username ?? payload.name ?? 'Пользователь',
      role: payload.role ?? ROLE.EMPLOYEE,
      isAdmin: payload.role === ROLE.ADMIN,
    }
  }

  async function fetchUsers() {
    const response = await authStore.authorizedRequest('/users')
    users.value = Array.isArray(response) ? response.map(normalizeUser) : []
    return users.value
  }

  async function createUser(payload) {
    const response = await authStore.authorizedRequest('/users', {
      method: 'POST',
      body: {
        username: String(payload.name ?? '').trim(),
        password: String(payload.password ?? ''),
        role: payload.isAdmin ? ROLE.ADMIN : ROLE.EMPLOYEE,
      },
    })

    const user = normalizeUser(response)
    users.value = [...users.value, user]
    return user
  }

  async function updateUser(userId, payload) {
    const response = await authStore.authorizedRequest(`/users/${userId}`, {
      method: 'PATCH',
      body: {
        username: payload.name ? String(payload.name).trim() : undefined,
        password: payload.password ? String(payload.password) : undefined,
        role:
          typeof payload.isAdmin === 'boolean'
            ? payload.isAdmin
              ? ROLE.ADMIN
              : ROLE.EMPLOYEE
            : undefined,
      },
    })

    const updated = normalizeUser(response)
    const index = users.value.findIndex((user) => user.id === userId)
    if (index !== -1) {
      users.value[index] = updated
      users.value = [...users.value]
    }
    return updated
  }

  async function deleteUser(userId) {
    await authStore.authorizedRequest(`/users/${userId}`, {
      method: 'DELETE',
    })
    users.value = users.value.filter((user) => user.id !== userId)
    return true
  }

  function clearUsers() {
    users.value = []
  }

  return {
    users,
    listUsers,
    getUserById,
    fetchUsers,
    createUser,
    updateUser,
    deleteUser,
    clearUsers,
  }
})
