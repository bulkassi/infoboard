<template>
  <section class="about-reader w-full max-w-[1100px] px-4 py-2">
    <div class="flex flex-col gap-8 border-none bg-white p-4 md:p-6">
      <h1 class="flex justify-center mb-4 text-3xl font-semibold text-brand-500">
        {{ aboutTitle }}
      </h1>

      <QuillEditor
        v-model="aboutContent"
        readonly
        editorStyle="min-height: 50vh"
        class="about-reader-editor"
      />
    </div>
  </section>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useAboutStore } from '@/stores/about'
import QuillEditor from '@/components/quill/QuillEditor.vue'

const aboutStore = useAboutStore()
const { title: aboutTitle, content: aboutContent } = storeToRefs(aboutStore)

aboutStore.fetchAbout()
</script>

<style scoped>
.about-reader :deep(.ql-editor) {
  font-size: 1.05rem;
  line-height: 1.75;
}

.about-reader :deep(.quill-editor__content),
.about-reader :deep(.ql-container) {
  border: none !important;
  box-shadow: none !important;
}

.about-reader :deep(.ql-editor h1),
.about-reader :deep(.ql-editor h2),
.about-reader :deep(.ql-editor h3) {
  color: var(--p-primary-500);
  font-weight: 600;
}
</style>
