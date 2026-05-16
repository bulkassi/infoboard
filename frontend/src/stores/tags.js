import { ref } from 'vue'
import { defineStore } from 'pinia'
import { useAuthStore } from '@/stores/auth'

export const useTagsStore = defineStore('tags', () => {
  const authStore = useAuthStore()
  const tags = ref([])

  function normalizeTag(payload) {
    return {
      id: payload.id,
      name: payload.text,
      textColor: String(payload.text_color ?? '').replace('#', ''),
      bgColor: String(payload.background_color ?? '').replace('#', ''),
      isGlobal: Boolean(payload.global_),
      ownerUserId: payload.owner_id ?? null,
    }
  }

  function serializeTag(payload) {
    return {
      text: payload.name,
      text_color: `#${payload.textColor}`,
      background_color: `#${payload.bgColor}`,
      global_: Boolean(payload.isGlobal),
    }
  }

  async function fetchTags() {
    const response = await authStore.authorizedRequest('/tags')
    tags.value = Array.isArray(response) ? response.map(normalizeTag) : []
    return tags.value
  }

  async function createTag(payload) {
    const response = await authStore.authorizedRequest('/tags', {
      method: 'POST',
      body: serializeTag(payload),
    })
    const tag = normalizeTag(response)
    tags.value = [...tags.value, tag]
    return tag
  }

  async function updateTag(tagId, payload) {
    const response = await authStore.authorizedRequest(`/tags/${tagId}`, {
      method: 'PATCH',
      body: serializeTag(payload),
    })
    const tag = normalizeTag(response)
    const index = tags.value.findIndex((item) => item.id === tagId)
    if (index !== -1) {
      tags.value[index] = tag
      tags.value = [...tags.value]
    }
    return tag
  }

  async function deleteTag(tagId) {
    await authStore.authorizedRequest(`/tags/${tagId}`, {
      method: 'DELETE',
    })
    tags.value = tags.value.filter((item) => item.id !== tagId)
  }

  return {
    tags,
    fetchTags,
    createTag,
    updateTag,
    deleteTag,
  }
})
