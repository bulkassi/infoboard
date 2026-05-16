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

    <QuillEditor
      v-if="visible"
      :modelValue="draftContent"
      editorStyle="height: 320px"
      @update:modelValue="onEditorUpdate"
      @load="onEditorLoad"
    >
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
    </QuillEditor>

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
import QuillEditor from '../quill/QuillEditor.vue'

const visible = defineModel('visible')

const props = defineProps({
  content: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['save'])

const draftContent = ref('')
const userEdited = ref(false)
const validationError = ref('')
const quillInstance = ref(null)

const htmlToText = (html) =>
  html
    .replace(/<[^>]*>/g, ' ')
    .replaceAll('&nbsp;', ' ')
    .replace(/\s+/g, ' ')
    .trim()

const syncFromProps = () => {
  draftContent.value = props.content ?? ''
  userEdited.value = false
  validationError.value = ''
}

const onEditorUpdate = (value) => {
  draftContent.value = value
  userEdited.value = true
  validationError.value = ''
}

const onEditorLoad = ({ instance }) => {
  quillInstance.value = instance ?? null
}

const getEditorHtml = () => {
  if (!quillInstance.value) {
    return draftContent.value
  }

  const html = quillInstance.value.root?.innerHTML ?? ''
  return html === '<p><br></p>' ? '' : html
}

const resetAndClose = () => {
  syncFromProps()
  visible.value = false
}

const onSubmit = () => {
  const latestContent = getEditorHtml()

  if (!htmlToText(latestContent)) {
    validationError.value = 'Добавьте текст перед сохранением.'
    return
  }

  draftContent.value = latestContent
  emit('save', latestContent)
  visible.value = false
}

watch(
  () => props.content,
  () => {
    if (!visible.value || !userEdited.value) {
      syncFromProps()
    }
  },
)

watch(visible, (isVisible) => {
  if (isVisible) {
    syncFromProps()
    return
  }

  quillInstance.value = null
})
</script>
