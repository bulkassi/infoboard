<template>
  <Tag
    :value="props.text"
    :pt="{
      root: {
        class:
          'inline-flex items-center justify-center text-[0.875rem] font-medium px-[0.5rem] py-[0.25rem] rounded-md gap-[0.25rem]',
        style: {
          backgroundColor: `#${props.bgColor}`,
          color: `#${props.textColor}`,
        },
      },
    }"
    unstyled
  />
</template>

<script setup>
import Tag from 'primevue/tag'

const props = defineProps(['text', 'textColor', 'bgColor'])
</script>
