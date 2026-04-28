<template>
  <Dialog
    v-model:visible="visible"
    modal
    :header="dialogTitle"
    :pt="{
      header: { class: 'text-brand-500' },
      title: { class: 'text-brand-500' },
      content: { class: 'flex flex-col gap-4' },
      closeButtonIcon: { class: 'text-brand-500' },
    }"
  >
    <template #header>
      <div class="inline-flex items-center justify-center gap-1">
        <PhBookmark :size="24" weight="duotone" />
        <span class="text-lg font-bold">{{ dialogTitle }}</span>
      </div>
    </template>
    <Fieldset pt:root:class="mt-0">
      <template #legend>
        <span class="text-brand-500 text-md font-medium">Параметры тега</span>
      </template>

      <form @submit.prevent="onTagFormSubmit" class="flex flex-col gap-4">
        <div class="flex flex-col gap-2">
          <div class="flex flex-col">
            <InputText
              v-model="formState.tagName"
              type="text"
              placeholder="Имя тега"
              class="w-full"
              :invalid="!formState.tagName"
            />
          </div>

          <div class="flex flex-row items-center justify-between">
            <label for="tagTextColor">Цвет текста</label>
            <ColorPicker v-model="formState.tagTextColor" inputId="tagTextColor" format="hex" />
          </div>

          <div class="flex flex-row items-center justify-between">
            <label for="tagBgColor">Цвет фона</label>
            <ColorPicker v-model="formState.tagBgColor" inputId="tagBgColor" format="hex" />
          </div>

          <div class="flex flex-row items-center justify-between">
            <label for="tagIsGlobal">Глобальность тега</label>
            <Checkbox
              v-model="formState.tagIsGlobal"
              inputId="tagIsGlobal"
              binary
              :disabled="!canSetTagGlobal"
            />
          </div>

          <div class="flex gap-2">
            <Button type="button" severity="secondary" @click="resetTagForm">Отменить</Button>
            <Button type="submit">Сохранить</Button>
          </div>
        </div>
      </form>
    </Fieldset>
  </Dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

import { Button, Checkbox, ColorPicker, Dialog, Fieldset, InputText } from 'primevue'
import { PhBookmark } from '@phosphor-icons/vue'
import { usePermissions } from '@/composables/usePermissions'

const visible = defineModel('visible')

const props = defineProps({
  tag: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['save'])
const { canSetTagGlobal } = usePermissions()

const getDefaultFormState = () => ({
  id: null,
  tagName: '',
  tagTextColor: 'ffffff',
  tagBgColor: 'ef4444',
  tagIsGlobal: false,
})

const formState = ref(getDefaultFormState())

const dialogTitle = computed(() =>
  formState.value.id === null ? 'Создание тега' : 'Редактирование тега',
)

const applyTagToForm = (tag) => {
  if (!tag) {
    formState.value = getDefaultFormState()
  } else {
    formState.value = {
      id: tag.id ?? null,
      tagName: tag.name ?? '',
      tagTextColor: tag.textColor ?? 'ffffff',
      tagBgColor: tag.bgColor ?? 'ef4444',
      tagIsGlobal: Boolean(tag.isGlobal),
    }
  }
}

watch(
  () => props.tag,
  (tag) => {
    applyTagToForm(tag)
  },
  { immediate: true },
)

const resetTagForm = () => {
  applyTagToForm(props.tag)
  visible.value = false
}

const onTagFormSubmit = () => {
  const tagName = formState.value.tagName.trim()
  if (!tagName) {
    return
  }

  emit('save', {
    id: formState.value.id,
    tagName,
    tagTextColor: formState.value.tagTextColor,
    tagBgColor: formState.value.tagBgColor,
    tagIsGlobal: canSetTagGlobal.value ? formState.value.tagIsGlobal : false,
  })
  visible.value = false
}

watch(visible, (isVisible) => {
  if (isVisible) {
    applyTagToForm(props.tag)
  }
})
</script>
