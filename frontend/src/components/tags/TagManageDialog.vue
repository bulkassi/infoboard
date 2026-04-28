<template>
  <Dialog
    v-model:visible="visible"
    modal
    :pt="{
      header: { class: 'text-brand-500' },
      title: { class: 'text-brand-500' },
      content: { class: 'flex flex-col gap-4' },
      closeButtonIcon: { class: 'text-brand-500' },
    }"
    class="w-[40rem]"
  >
    <template #header>
      <div class="inline-flex items-center justify-center gap-1">
        <PhBookmark :size="24" weight="duotone" />
        <span class="text-lg font-bold">Управление тегами</span>
      </div>
    </template>

    <div class="flex flex-col gap-2">
      <Listbox
        v-model="selectedTagId"
        :options="visibleTags"
        optionLabel="name"
        :pt="{
          option: { class: 'w-full flex justify-between' },
        }"
        striped
        fluid
      >
        <template #option="slotProps">
          <div class="flex w-full justify-between items-center gap-1">
            <InfoTag
              :text="slotProps.option.name"
              :textColor="slotProps.option.textColor"
              :bgColor="slotProps.option.bgColor"
            />

            <div class="flex gap-2">
              <Button
                class="flex-none"
                @click.stop="tagEdit(slotProps.option)"
                :disabled="!canEditTag(slotProps.option)"
                raised
                rounded
              >
                <PhPencilSimple :size="16" />
              </Button>
              <Button
                class="flex-none"
                @click.stop="tagDelete(slotProps.option)"
                :disabled="!canDeleteTag(slotProps.option)"
                severity="danger"
                raised
                rounded
              >
                <PhTrash :size="16" />
              </Button>
            </div>
          </div>
        </template>
      </Listbox>

      <Button @click="tagCreate" class="w-auto" :disabled="!canManageTags">
        <PhPlus :size="16" />
        Добавить тег
      </Button>
    </div>

    <Message size="small" severity="secondary" variant="simple">
      <span>
        Выберите тег из списка, измените его параметры и нажмите "Сохранить". Для сброса изменений
        нажмите кнопку "Отменить".
      </span>
      <span class="block mt-1">
        Для добавления нового тега нажмите кнопку "Добавить тег". Добавленные Вами теги будут
        доступны только на досках, созданных Вами. Для доступности тега на любых досках поставьте
        галочку "Глобальность тега".
      </span>
    </Message>
  </Dialog>

  <TagEditDialog v-model:visible="tagEditDialogVisible" :tag="editingTag" @save="onTagSave" />
</template>

<script setup>
import { computed, ref, watch } from 'vue'

import { Dialog, Button, Listbox, Message } from 'primevue'
import { PhBookmark, PhPencilSimple, PhPlus, PhTrash } from '@phosphor-icons/vue'

import InfoTag from './InfoTag.vue'
import TagEditDialog from './TagEditDialog.vue'
import { useAuthStore } from '@/stores/auth'
import { usePermissions } from '@/composables/usePermissions'
import { removeTagFromMainStyleCards } from '@/state/boardCards'
import { getNextTagId, reserveTagId, tags } from '@/state/tags'

const visible = defineModel('visible')
const tagEditDialogVisible = ref(false)
const returnToManageAfterEdit = ref(false)
const selectedTagId = ref(null)
const editingTag = ref(null)
const authStore = useAuthStore()
const { canManageTags, canSetTagGlobal, canEditTag, canDeleteTag } = usePermissions()
const visibleTags = computed(() => tags.value)

const getNewTagTemplate = () => ({
  id: null,
  name: '',
  textColor: 'ffffff',
  bgColor: 'ef4444',
  isGlobal: false,
})

const openTagEditDialog = () => {
  returnToManageAfterEdit.value = true
  visible.value = false
  tagEditDialogVisible.value = true
}

const tagCreate = () => {
  if (!canManageTags.value) {
    return
  }

  editingTag.value = getNewTagTemplate()
  openTagEditDialog()
}

const tagEdit = (tag) => {
  if (!canEditTag(tag)) {
    return
  }

  editingTag.value = { ...tag }
  openTagEditDialog()
}

const tagDelete = (tag) => {
  if (!canDeleteTag(tag)) {
    return
  }

  tags.value = tags.value.filter((item) => item.id !== tag.id)
  removeTagFromMainStyleCards(tag.id)
  if (selectedTagId.value === tag.id) {
    selectedTagId.value = null
  }
}

const onTagSave = (payload) => {
  const existingTag = tags.value.find((tag) => tag.id === payload.id)
  if (existingTag && !canEditTag(existingTag)) {
    return
  }

  if (!existingTag && !canManageTags.value) {
    return
  }

  const normalizedTag = {
    id: payload.id,
    name: payload.tagName,
    textColor: payload.tagTextColor,
    bgColor: payload.tagBgColor,
    isGlobal: canSetTagGlobal.value ? payload.tagIsGlobal : Boolean(existingTag?.isGlobal),
    ownerUserId: existingTag?.ownerUserId ?? authStore.currentUser.id,
  }

  if (normalizedTag.id === null || normalizedTag.id === undefined) {
    normalizedTag.id = getNextTagId()
    tags.value.push(normalizedTag)
  } else {
    reserveTagId(normalizedTag.id)
    const index = tags.value.findIndex((tag) => tag.id === normalizedTag.id)
    if (index !== -1) {
      tags.value[index] = normalizedTag
    }
  }

  selectedTagId.value = normalizedTag.id
}

watch(tagEditDialogVisible, (isVisible) => {
  if (!isVisible && returnToManageAfterEdit.value) {
    visible.value = true
    returnToManageAfterEdit.value = false
  }
})
</script>
