import { ref } from 'vue'
import { defineStore } from 'pinia'

const DEFAULT_USERS = [
  {
    id: 1,
    name: 'Администратор',
    password: 'admin123',
    avatar: 'https://i.pravatar.cc/150?img=1',
    isAdmin: true,
  },
  {
    id: 100,
    name: 'Обычный пользователь',
    password: 'user123',
    avatar: 'https://i.pravatar.cc/150?img=2',
    isAdmin: false,
  },
  {
    id: 101,
    name: 'Анна Волкова',
    password: 'anna123',
    avatar: 'https://i.pravatar.cc/150?img=3',
    isAdmin: true,
  },
  {
    id: 102,
    name: 'Дмитрий Соколов',
    password: 'dmitry123',
    avatar: 'https://i.pravatar.cc/150?img=4',
    isAdmin: false,
  },
  {
    id: 103,
    name: 'Екатерина Морозова',
    password: 'ekaterina123',
    avatar: 'https://i.pravatar.cc/150?img=5',
    isAdmin: false,
  },
]

export const useUsersStore = defineStore('users', () => {
  const users = ref(DEFAULT_USERS.map((user) => ({ ...user })))

  function listUsers() {
    return users.value
  }

  function getUserById(userId) {
    return users.value.find((user) => user.id === userId) ?? null
  }

  function findUserByCredentials(username, password) {
    const normalizedUsername = String(username ?? '').trim().toLowerCase()
    const normalizedPassword = String(password ?? '')

    return (
      users.value.find(
        (user) =>
          user.name.trim().toLowerCase() === normalizedUsername && user.password === normalizedPassword,
      ) ?? null
    )
  }

  function createUser(payload) {
    const maxId = users.value.length > 0 ? Math.max(...users.value.map((user) => user.id)) : 0
    const nextUser = {
      id: maxId + 1,
      name: String(payload.name ?? '').trim(),
      password: String(payload.password ?? ''),
      avatar: String(payload.avatar ?? ''),
      isAdmin: Boolean(payload.isAdmin),
    }

    users.value = [...users.value, nextUser]
    return nextUser
  }

  function updateUser(userId, payload) {
    const index = users.value.findIndex((user) => user.id === userId)
    if (index === -1) {
      return null
    }

    const previous = users.value[index]
    const nextUser = {
      ...previous,
      name: String(payload.name ?? previous.name).trim() || previous.name,
      password: payload.password ?? previous.password,
      avatar: payload.avatar ?? previous.avatar,
      isAdmin: typeof payload.isAdmin === 'boolean' ? payload.isAdmin : previous.isAdmin,
    }

    if (
      typeof previous.avatar === 'string' &&
      previous.avatar.startsWith('blob:') &&
      previous.avatar !== nextUser.avatar
    ) {
      URL.revokeObjectURL(previous.avatar)
    }

    users.value[index] = nextUser
    users.value = [...users.value]
    return nextUser
  }

  function deleteUser(userId) {
    const index = users.value.findIndex((user) => user.id === userId)
    if (index === -1) {
      return false
    }

    const [removed] = users.value.splice(index, 1)
    users.value = [...users.value]

    if (removed.avatar?.startsWith('blob:')) {
      URL.revokeObjectURL(removed.avatar)
    }

    return true
  }

  return {
    users,
    listUsers,
    getUserById,
    findUserByCredentials,
    createUser,
    updateUser,
    deleteUser,
  }
})
