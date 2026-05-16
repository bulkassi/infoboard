<template>
  <div class="flex flex-col items-center justify-center w-1/2">
    <DataTable
      :value="users"
      paginator
      :rows="5"
      dataKey="id"
      removableSort
      rowHover
      stripedRows
      showGridlines="true"
      pt:root:class="w-full"
    >
      <template #header>
        <div class="flex flex-row items-center justify-between">
          <span class="text-brand-500 text-lg">Список пользователей приложения</span>
          <Button @click="openCreateUserDialog">Добавить пользователя</Button>
        </div>
      </template>
      <template #empty>Пользователи не найдены</template>
      <template #loading>Список пользователей загружается. Пожалуйста, подождите...</template>

      <Column field="id" header="ID" sortable> </Column>
      <Column field="name" header="Имя пользователя" sortable>
        <template #body="{ data }">
          <div class="flex flex-row items-center justify-start gap-2">
            {{ data.name }}
          </div>
        </template>
      </Column>
      <Column field="isAdmin" header="Роль" sortable>
        <template #body="{ data }">
          <Tag severity="success" v-if="data.isAdmin">Администратор</Tag>
          <Tag v-else>Пользователь</Tag>
        </template>
      </Column>
      <Column pt:header:class="flex flex-row items-center" header="Действия">
        <template #body="{ data }">
          <div class="flex items-center justify-center gap-2">
            <Button rounded variant="outlined" @click="openEditUserDialog(data)">
              <PhPencilSimple :size="16" weight="duotone" />
            </Button>
            <Button
              rounded
              variant="outlined"
              severity="danger"
              :disabled="isCurrentUser(data)"
              @click="onUserDelete(data)"
            >
              <PhTrash :size="16" weight="duotone" />
            </Button>
          </div>
        </template>
      </Column>
    </DataTable>

    <UserEditDialog
      v-model:visible="userEditDialogVisible"
      :user="editingUser"
      @save="onUserSave"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'

import { PhPencilSimple, PhTrash } from '@phosphor-icons/vue'
import { Column, DataTable, Button, Tag } from 'primevue'
import UserEditDialog from '@/components/admin/UserEditDialog.vue'
import { useAuthStore } from '@/stores/auth'
import { useUsersStore } from '@/stores/users'

const userEditDialogVisible = ref(false)
const editingUser = ref(null)
const authStore = useAuthStore()
const usersStore = useUsersStore()
const { users } = storeToRefs(usersStore)

const openCreateUserDialog = () => {
  editingUser.value = null
  userEditDialogVisible.value = true
}

const openEditUserDialog = (user) => {
  editingUser.value = { ...user }
  userEditDialogVisible.value = true
}

const onUserSave = async (payload) => {
  const normalizedUser = {
    name: payload.userName,
    password: payload.userPassword ?? '',
    isAdmin: payload.userIsAdmin,
  }

  if (payload.id === null || payload.id === undefined) {
    await usersStore.createUser(normalizedUser)
  } else {
    await usersStore.updateUser(payload.id, normalizedUser)
  }

  editingUser.value = null
}

const isCurrentUser = (user) => {
  return user.id === authStore.currentUser.id
}

const onUserDelete = async (user) => {
  if (isCurrentUser(user)) {
    return
  }

  await usersStore.deleteUser(user.id)
}

onMounted(() => {
  usersStore.fetchUsers()
})
</script>
