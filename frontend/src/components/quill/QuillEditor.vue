<template>
  <div class="quill-editor">
    <div v-if="showToolbar" ref="toolbarEl" class="quill-editor__toolbar">
      <slot name="toolbar" />
    </div>
    <div ref="editorEl" class="quill-editor__content" :style="editorStyle"></div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, useSlots, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  readonly: {
    type: Boolean,
    default: false,
  },
  placeholder: {
    type: String,
    default: '',
  },
  formats: {
    type: Array,
    default: null,
  },
  modules: {
    type: Object,
    default: null,
  },
  editorStyle: {
    type: [String, Object, Array],
    default: null,
  },
})

const emit = defineEmits(['update:modelValue', 'load'])

const editorEl = ref(null)
const toolbarEl = ref(null)
const quill = ref(null)
const slots = useSlots()
const showToolbar = computed(() => !props.readonly && Boolean(slots.toolbar))

const renderValue = (value) => {
  if (!quill.value) {
    return
  }

  if (value) {
    // Set HTML directly and let Quill's mutation observer sync the Blot tree.
    // Avoid calling update() as it triggers selection tracking on mismatched DOM/Blot state.
    quill.value.root.innerHTML = value
  } else {
    quill.value.root.innerHTML = ''
  }
}

const initializeQuill = async () => {
  if (!editorEl.value || quill.value) {
    return
  }

  const module = await import('quill')
  const QuillCtor = module.default ?? module

  const configuration = {
    modules: {
      ...(props.modules ?? {}),
      toolbar: props.readonly ? false : (toolbarEl.value ?? props.modules?.toolbar),
    },
    readOnly: props.readonly,
    theme: 'snow',
    placeholder: props.placeholder,
  }

  // Quill treats a provided formats list as a strict whitelist.
  // Passing null disables formatting from the toolbar, so only pass formats when defined.
  if (Array.isArray(props.formats) && props.formats.length > 0) {
    configuration.formats = props.formats
  }

  quill.value = new QuillCtor(editorEl.value, configuration)
  renderValue(props.modelValue)

  quill.value.on('text-change', (...args) => {
    const source = args[2]
    if (source !== 'user') {
      return
    }

    let html = quill.value.getSemanticHTML()
    const text = quill.value.getText().trim()

    if (html === '<p><br></p>') {
      html = ''
    }

    emit('update:modelValue', html)
  })

  emit('load', { instance: quill.value })
}

watch(
  () => props.modelValue,
  (newValue, oldValue) => {
    if (newValue !== oldValue && quill.value && !quill.value.hasFocus()) {
      renderValue(newValue)
    }
  },
)

watch(
  () => props.readonly,
  (isReadonly) => {
    if (quill.value) {
      quill.value.enable(!isReadonly)
    }
  },
)

onMounted(() => {
  initializeQuill()
})

onBeforeUnmount(() => {
  quill.value = null
})
</script>
