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
    class="w-[42rem]"
  >
    <template #header>
      <div class="inline-flex items-center justify-center gap-1">
        <PhCards :size="24" weight="duotone" />
        <span class="text-lg font-bold">{{ dialogTitle }}</span>
      </div>
    </template>

    <Fieldset pt:root:class="mt-0" pt:content:class="flex flex-col gap-4">
      <template #legend>
        <span class="text-brand-500 text-md font-medium">Параметры карточки</span>
      </template>

      <form @submit.prevent="onSubmit" class="flex flex-col gap-4">
        <div v-if="isMainBoard" class="flex flex-col gap-2">
          <InputText
            v-model="formState.title"
            type="text"
            placeholder="Заголовок карточки"
            class="w-full"
            :invalid="isSubmitAttempted && !formState.title.trim()"
          />
          <Textarea
            v-model="formState.content"
            autoResize
            rows="4"
            placeholder="Описание"
            class="w-full"
          />

          <Fieldset pt:root:class="flex flex-col gap-2">
            <template #legend>
              <span class="text-brand-500 text-md font-medium">Теги карточки</span>
            </template>

            <Listbox
              v-model="formState.tagIds"
              :options="tags"
              optionLabel="name"
              optionValue="id"
              multiple
              checkmark
              class="w-full"
              :pt="{
                option: { class: 'w-full !justify-end' },
              }"
            >
              <template #option="slotProps">
                <div class="flex w-full items-center justify-end gap-2">
                  <span class="inline-flex w-4 justify-center">
                    <i
                      v-if="formState.tagIds.includes(slotProps.option.id)"
                      class="pi pi-check text-brand-500"
                      aria-hidden="true"
                    />
                  </span>
                  <InfoTag
                    :text="slotProps.option.name"
                    :textColor="slotProps.option.textColor"
                    :bgColor="slotProps.option.bgColor"
                  />
                </div>
              </template>
            </Listbox>
          </Fieldset>
        </div>

        <div v-else-if="isEmployeesBoard" class="grid grid-cols-1 gap-2 md:grid-cols-2">
          <InputText
            v-model="formState.surname"
            type="text"
            placeholder="Фамилия"
            :invalid="isSubmitAttempted && !formState.surname.trim()"
          />
          <InputText
            v-model="formState.name"
            type="text"
            placeholder="Имя"
            :invalid="isSubmitAttempted && !formState.name.trim()"
          />
          <InputText v-model="formState.patronymic" type="text" placeholder="Отчество" />
          <InputText
            v-model="formState.position"
            type="text"
            placeholder="Должность"
            :invalid="isSubmitAttempted && !formState.position.trim()"
          />
        </div>

        <div v-else-if="isServicesBoard" class="flex flex-col gap-2">
          <InputText
            v-model="formState.serviceName"
            type="text"
            placeholder="Название сервиса"
            :invalid="isSubmitAttempted && !formState.serviceName.trim()"
          />
          <InputText
            v-model="formState.link"
            type="text"
            placeholder="Ссылка на сервис"
            :invalid="isSubmitAttempted && !formState.link.trim()"
          />
          <Textarea
            v-model="formState.serviceDesc"
            autoResize
            rows="4"
            placeholder="Описание сервиса"
            class="w-full"
          />
        </div>

        <Fieldset pt:root:class="flex flex-col gap-4">
          <template #legend>
            <span class="text-brand-500 text-md font-medium">Изображение</span>
          </template>

          <FileUploader
            name="cardImage[]"
            acceptPattern="image/*"
            :maxFileSize="2000000"
            :fileLimit="1"
            :autoProcess="true"
            chooseLabel="Выбрать изображение"
            removeLabel="Удалить файл"
            emptyLabel="Файл не выбран"
            @files-selected="onImageFilesSelected"
            @files-cleared="onImageFilesCleared"
          />
        </Fieldset>

        <Message v-if="validationError" severity="error" size="small">
          {{ validationError }}
        </Message>

        <div class="flex justify-end gap-2">
          <Button type="button" severity="secondary" @click="onCancel">Отменить</Button>
          <Button type="submit">Сохранить</Button>
        </div>
      </form>
    </Fieldset>
  </Dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Button, Dialog, Fieldset, InputText, Listbox, Message, Textarea } from 'primevue'
import { PhCards } from '@phosphor-icons/vue'
import FileUploader from '@/components/FileUploader.vue'
import InfoTag from '@/components/tags/InfoTag.vue'
import { EMPLOYEES_BOARD_KEY, SERVICES_BOARD_KEY, isMainStyleCardBoard } from '@/state/boardCards'
import { tags } from '@/state/tags'

const visible = defineModel('visible')

const props = defineProps({
  boardId: {
    type: Number,
    required: true,
  },
  card: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['save'])

const isSubmitAttempted = ref(false)
const validationError = ref('')

const getDefaultFormState = () => ({
  id: null,
  title: '',
  content: '',
  surname: '',
  name: '',
  patronymic: '',
  position: '',
  link: '',
  serviceName: '',
  serviceDesc: '',
  tagIds: [],
  imageFile: null,
})

const formState = ref(getDefaultFormState())

const isMainBoard = computed(() => isMainStyleCardBoard(props.boardId))
const isEmployeesBoard = computed(() => props.boardId === EMPLOYEES_BOARD_KEY)
const isServicesBoard = computed(() => props.boardId === SERVICES_BOARD_KEY)

const dialogTitle = computed(() =>
  formState.value.id === null ? 'Создание карточки' : 'Редактирование карточки',
)

const normalizeTagIds = (tagIds) => {
  if (!Array.isArray(tagIds)) {
    return []
  }

  const availableTagIds = new Set(tags.value.map((tag) => tag.id))

  return [
    ...new Set(tagIds.filter((tagId) => Number.isInteger(tagId) && availableTagIds.has(tagId))),
  ]
}

const applyCardToForm = (card) => {
  if (!card) {
    formState.value = getDefaultFormState()
    return
  }

  formState.value = {
    id: card.id ?? null,
    title: card.title ?? '',
    content: card.content ?? '',
    surname: card.surname ?? '',
    name: card.name ?? '',
    patronymic: card.patronymic ?? '',
    position: card.position ?? '',
    link: card.link ?? '',
    serviceName: card.serviceName ?? '',
    serviceDesc: card.serviceDesc ?? '',
    tagIds: normalizeTagIds(card.tagIds),
    imageFile: null,
  }
}

const onImageFilesSelected = (files) => {
  formState.value.imageFile = files.length > 0 ? files[0].file : null
}

const onImageFilesCleared = () => {
  formState.value.imageFile = null
}

const validate = () => {
  validationError.value = ''

  if (isMainBoard.value && !formState.value.title.trim()) {
    validationError.value = 'Укажите заголовок карточки.'
    return false
  }

  if (isEmployeesBoard.value) {
    if (!formState.value.surname.trim() || !formState.value.name.trim()) {
      validationError.value = 'Укажите фамилию и имя сотрудника.'
      return false
    }

    if (!formState.value.position.trim()) {
      validationError.value = 'Укажите должность сотрудника.'
      return false
    }
  }

  if (isServicesBoard.value) {
    if (!formState.value.serviceName.trim()) {
      validationError.value = 'Укажите название сервиса.'
      return false
    }

    if (!formState.value.link.trim()) {
      validationError.value = 'Укажите ссылку на сервис.'
      return false
    }
  }

  return true
}

const onCancel = () => {
  isSubmitAttempted.value = false
  validationError.value = ''
  applyCardToForm(props.card)
  visible.value = false
}

const onSubmit = () => {
  isSubmitAttempted.value = true
  if (!validate()) {
    return
  }

  emit('save', {
    id: formState.value.id,
    title: formState.value.title,
    content: formState.value.content,
    surname: formState.value.surname,
    name: formState.value.name,
    patronymic: formState.value.patronymic,
    position: formState.value.position,
    link: formState.value.link,
    serviceName: formState.value.serviceName,
    serviceDesc: formState.value.serviceDesc,
    tagIds: normalizeTagIds(formState.value.tagIds),
    imageFile: formState.value.imageFile,
  })

  visible.value = false
}

watch(
  () => props.card,
  (card) => {
    applyCardToForm(card)
  },
  { immediate: true },
)

watch(visible, (isVisible) => {
  if (isVisible) {
    isSubmitAttempted.value = false
    validationError.value = ''
    applyCardToForm(props.card)
  }
})

watch(
  tags,
  () => {
    formState.value.tagIds = normalizeTagIds(formState.value.tagIds)
  },
  { deep: true },
)
</script>
