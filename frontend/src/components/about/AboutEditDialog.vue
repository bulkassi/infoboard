<template>
  <Dialog
    v-model:visible="visible"
    modal
    class="w-[60rem] max-w-[95vw]"
    :pt="{
      header: { class: 'text-brand-500' },
      title: { class: 'text-brand-500' },
      content: { class: 'flex flex-col gap-4' },
      closeButtonIcon: { class: 'text-brand-500' },
    }"
  >
    <template #header>
      <div class="inline-flex items-center justify-center gap-1">
        <PhPencilSimple :size="24" weight="duotone" />
        <span class="text-lg font-bold">Редактирование About</span>
      </div>
    </template>

    <Editor v-model="draftContent" editorStyle="height: 320px">
      <template #toolbar>
        <span class="ql-formats">
          <select class="ql-header">
            <option selected></option>
            <option value="1"></option>
            <option value="2"></option>
            <option value="3"></option>
          </select>
          <select class="ql-font"></select>
          <select class="ql-size"></select>
        </span>

        <span class="ql-formats">
          <button class="ql-bold"></button>
          <button class="ql-italic"></button>
          <button class="ql-underline"></button>
        </span>

        <span class="ql-formats">
          <button class="ql-list" value="ordered"></button>
          <button class="ql-list" value="bullet"></button>
          <select class="ql-align"></select>
        </span>

        <span class="ql-formats">
          <button class="ql-link"></button>
          <button class="ql-image"></button>
          <button class="ql-clean"></button>
        </span>
      </template>
    </Editor>

    <Message v-if="validationError" severity="error" size="small">{{ validationError }}</Message>

    <div class="flex justify-end gap-2">
      <Button type="button" severity="secondary" @click="resetAndClose">Отменить</Button>
      <Button type="button" @click="onSubmit">Сохранить</Button>
    </div>
  </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

import { PhPencilSimple } from '@phosphor-icons/vue'
import { Button, Dialog, Message } from 'primevue'
import Editor from 'primevue/editor'

const visible = defineModel('visible')

const props = defineProps({
  content: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['save'])

const draftContent = ref('')
const validationError = ref('')

const htmlToText = (html) =>
  html
    .replace(/<[^>]*>/g, ' ')
    .replaceAll('&nbsp;', ' ')
    .replace(/\s+/g, ' ')
    .trim()

const syncFromProps = () => {
  draftContent.value = props.content ?? ''
  validationError.value = ''
}

const resetAndClose = () => {
  syncFromProps()
  visible.value = false
}

const onSubmit = () => {
  if (!htmlToText(draftContent.value)) {
    validationError.value = 'Добавьте текст перед сохранением.'
    return
  }

  emit('save', draftContent.value)
  visible.value = false
}

watch(
  () => props.content,
  () => {
    if (!visible.value) {
      syncFromProps()
    }
  },
)

watch(visible, (isVisible) => {
  if (isVisible) {
    syncFromProps()
  }
})
</script>
