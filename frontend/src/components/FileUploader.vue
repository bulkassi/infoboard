<template>
  <div class="flex flex-col gap-2">
    <FileUpload
      ref="fileUploadRef"
      :name="name"
      :fileLimit="fileLimit"
      :accept="acceptPattern"
      :maxFileSize="maxFileSize"
      customUpload
      :auto="false"
      :showUploadButton="false"
      :showCancelButton="false"
      @select="onSelect"
      @clear="onClear"
      @error="onError"
      :invalidFileLimitMessage="fileLimitMessage"
      :invalidFileSizeMessage="fileSizeMessage"
      :invalidFileTypeMessage="fileTypeMessage"
    >
      <template #header="{ chooseCallback, clearCallback, files }">
        <div class="flex flex-wrap items-center gap-2">
          <Button type="button" @click="chooseCallback()" size="small">
            {{ chooseLabel }}
          </Button>
          <Button
            type="button"
            severity="danger"
            variant="outlined"
            size="small"
            :disabled="!files || files.length === 0"
            @click="clearFiles(clearCallback)"
          >
            {{ removeLabel }}
          </Button>
        </div>
      </template>

      <template #content="{ files, removeFileCallback, messages }">
        <div class="flex flex-col gap-3 pt-2">
          <Message
            v-for="message in messages"
            :key="message"
            severity="error"
            size="small"
            variant="simple"
          >
            {{ message }}
          </Message>

          <div v-if="showPreview && files.length > 0" class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <div
              v-for="(file, index) in files"
              :key="file.name + file.size + index"
              class="border border-surface-200 rounded-md p-2 flex items-center gap-2"
            >
              <img
                v-if="canPreviewImage(file)"
                :src="file.objectURL"
                :alt="file.name"
                class="h-12 w-12 rounded object-cover"
              />
              <div
                v-else
                class="h-12 w-12 rounded bg-surface-100 flex items-center justify-center text-xs"
              >
                FILE
              </div>

              <div class="min-w-0 flex-1">
                <div class="truncate text-sm">{{ file.name }}</div>
                <div class="text-xs text-color-secondary">{{ formatFileSize(file.size) }}</div>
              </div>

              <Button
                type="button"
                icon="pi pi-times"
                severity="danger"
                variant="text"
                rounded
                @click="removeSingleFile(file, index, removeFileCallback)"
              />
            </div>
          </div>
        </div>
      </template>

      <template #empty>
        <span class="text-brand-500">{{ emptyLabel }}</span>
      </template>
    </FileUpload>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

import { Button, FileUpload, Message } from 'primevue'

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  fileLimit: {
    type: Number,
    default: 1,
  },
  acceptPattern: {
    type: String,
    default: '*/*',
  },
  maxFileSize: {
    type: Number,
    default: undefined,
  },
  autoProcess: {
    type: Boolean,
    default: true,
  },
  showPreview: {
    type: Boolean,
    default: true,
  },
  previewOnlyImages: {
    type: Boolean,
    default: true,
  },
  chooseLabel: {
    type: String,
    default: 'Выбрать файл',
  },
  removeLabel: {
    type: String,
    default: 'Удалить файлы',
  },
  emptyLabel: {
    type: String,
    default: 'Файл не выбран',
  },
})

const emit = defineEmits([
  'files-selected',
  'files-cleared',
  'file-removed',
  'upload-requested',
  'validation-error',
])

const fileUploadRef = ref(null)
const selectedFiles = ref([])
const lastInvalidFileSize = ref(null)

const canPreviewImage = (file) => {
  if (!props.showPreview) {
    return false
  }
  if (!props.previewOnlyImages) {
    return true
  }
  return Boolean(file?.type?.startsWith('image/'))
}

const formatFileSize = (bytes) => {
  if (!bytes || bytes <= 0) {
    return '0 B'
  }

  const units = ['B', 'KB', 'MB', 'GB']
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1)
  const size = bytes / 1024 ** index
  return `${size.toFixed(index === 0 ? 0 : 1)} ${units[index]}`
}

const normalizeFiles = (files) =>
  files.map((file) => ({
    file,
    name: file.name,
    size: file.size,
    type: file.type,
    isImage: Boolean(file.type?.startsWith('image/')),
    previewUrl: file.objectURL ?? null,
  }))

const onSelect = (event) => {
  selectedFiles.value = event.files ? [...event.files] : []
  const normalized = normalizeFiles(selectedFiles.value)

  emit('files-selected', normalized)

  if (props.autoProcess) {
    emit('upload-requested', normalized)
  }
}

const onClear = () => {
  selectedFiles.value = []
  lastInvalidFileSize.value = null
  emit('files-cleared')
}

const extractFileSizeFromErrorEvent = (event) => {
  const filesFromEvent = Array.isArray(event?.files)
    ? event.files
    : event?.files
      ? Array.from(event.files)
      : []

  if (filesFromEvent.length > 0 && Number.isFinite(filesFromEvent[0]?.size)) {
    return filesFromEvent[0].size
  }

  const filesFromOriginalEvent = event?.originalEvent?.target?.files
    ? Array.from(event.originalEvent.target.files)
    : []

  if (filesFromOriginalEvent.length > 0 && Number.isFinite(filesFromOriginalEvent[0]?.size)) {
    return filesFromOriginalEvent[0].size
  }

  return null
}

const onError = (event) => {
  const invalidSize = extractFileSizeFromErrorEvent(event)
  if (invalidSize !== null) {
    lastInvalidFileSize.value = invalidSize
  }

  const message = event?.message || 'Ошибка валидации файла'
  emit('validation-error', [message])
}

const removeSingleFile = (file, index, removeFileCallback) => {
  removeFileCallback(index)

  selectedFiles.value = selectedFiles.value.filter((_, fileIndex) => fileIndex !== index)
  emit('file-removed', {
    index,
    file: {
      name: file.name,
      size: file.size,
      type: file.type,
      isImage: Boolean(file.type?.startsWith('image/')),
      previewUrl: file.objectURL ?? null,
    },
  })
  emit('files-selected', normalizeFiles(selectedFiles.value))
}

const clearFiles = (clearCallback) => {
  clearCallback()
}

const fileLimitMessage = computed(() => `Вы можете выбрать не более ${props.fileLimit} файла(ов).`)
const fileSizeMessage = computed(() => {
  const maxSize = formatFileSize(props.maxFileSize)

  if (lastInvalidFileSize.value !== null) {
    return `Размер выбранного файла (${formatFileSize(lastInvalidFileSize.value)}) превышает лимит в ${maxSize}.`
  }

  return `Размер выбранного файла превышает лимит в ${maxSize}.`
})
const fileTypeMessage = computed(
  () => `Выбранный файл не соответствует допустимому формату (${props.acceptPattern}).`,
)

defineExpose({
  clearFiles: () => {
    fileUploadRef.value?.clear()
  },
})
</script>
