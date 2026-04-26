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
            <Avatar class="p-overlay-badge" :image="data.avatar" shape="circle" size="large" />
            {{ data.name }}
          </div>
        </template></Column
      >
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
            <Button rounded variant="outlined" severity="danger">
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
import { ref } from 'vue'

import { PhPencilSimple, PhTrash } from '@phosphor-icons/vue'
import { Avatar, Column, DataTable, Button, Tag } from 'primevue'
import UserEditDialog from '@/components/admin/UserEditDialog.vue'

const userEditDialogVisible = ref(false)
const editingUser = ref(null)

const defaultUsers = [
  { name: 'Анна Волкова', isAdmin: true },
  { name: 'Дмитрий Соколов', isAdmin: false },
  { name: 'Екатерина Морозова', isAdmin: false },
  { name: 'Алексей Федоров', isAdmin: false },
  { name: 'Марина Кузнецова', isAdmin: true },
  { name: 'Илья Орлов', isAdmin: false },
  { name: 'Ольга Павлова', isAdmin: false },
  { name: 'Никита Воронов', isAdmin: false },
  { name: 'Татьяна Белова', isAdmin: false },
  { name: 'Павел Зайцев', isAdmin: false },
  { name: 'Светлана Новикова', isAdmin: true },
  { name: 'Роман Громов', isAdmin: false },
  { name: 'Юлия Титова', isAdmin: false },
  { name: 'Андрей Лебедев', isAdmin: false },
  { name: 'Виктория Смирнова', isAdmin: false },
  { name: 'Кирилл Николаев', isAdmin: false },
  { name: 'Наталья Сидорова', isAdmin: true },
  { name: 'Константин Мельников', isAdmin: false },
  { name: 'Елена Васильева', isAdmin: false },
  { name: 'Михаил Ковалев', isAdmin: false },
  { name: 'Алина Романова', isAdmin: false },
  { name: 'Владислав Емельянов', isAdmin: false },
  { name: 'Дарья Андреева', isAdmin: false },
  { name: 'Сергей Павлов', isAdmin: false },
  { name: 'Полина Захарова', isAdmin: true },
  { name: 'Вадим Александров', isAdmin: false },
  { name: 'Ксения Фролова', isAdmin: false },
  { name: 'Олег Комаров', isAdmin: false },
  { name: 'Евгения Калинина', isAdmin: false },
  { name: 'Глеб Киселев', isAdmin: false },
]

const users = ref(
  defaultUsers.map((user, index) => ({
    id: index,
    name: user.name,
    password: '',
    avatar: `https://i.pravatar.cc/150?img=${index + 1}`,
    isAdmin: user.isAdmin,
  })),
)

const openCreateUserDialog = () => {
  editingUser.value = null
  userEditDialogVisible.value = true
}

const openEditUserDialog = (user) => {
  editingUser.value = { ...user }
  userEditDialogVisible.value = true
}

const onUserSave = (payload) => {
  const normalizedUser = {
    id: payload.id,
    name: payload.userName,
    password: payload.userPassword ?? '',
    isAdmin: payload.userIsAdmin,
    avatar: payload.avatarUrl,
  }

  if (payload.avatarFile) {
    normalizedUser.avatar = URL.createObjectURL(payload.avatarFile)
  }

  if (normalizedUser.id === null || normalizedUser.id === undefined) {
    const maxId = users.value.length > 0 ? Math.max(...users.value.map((user) => user.id)) : -1
    normalizedUser.id = maxId + 1
    users.value.push(normalizedUser)
  } else {
    const index = users.value.findIndex((user) => user.id === normalizedUser.id)
    if (index !== -1) {
      const previousAvatar = users.value[index].avatar
      if (previousAvatar?.startsWith('blob:') && previousAvatar !== normalizedUser.avatar) {
        URL.revokeObjectURL(previousAvatar)
      }
      users.value[index] = normalizedUser
    }
  }

  editingUser.value = null
}
</script>
