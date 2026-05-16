import { ref } from 'vue'
import { defineStore } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { apiRequest } from '@/api/client'

export const useAboutStore = defineStore('about', () => {
  const authStore = useAuthStore()
  const title = ref('О нас')
  const content = ref('')

  async function fetchAbout() {
    const payload = authStore.accessToken
      ? await authStore.authorizedRequest('/boards/about')
      : await apiRequest('/boards/about')
    content.value = payload?.content ?? ''
    return content.value
  }

  async function updateAbout(nextContent) {
    const payload = await authStore.authorizedRequest('/boards/about', {
      method: 'PATCH',
      body: { content: nextContent },
    })
    content.value = payload?.content ?? ''
    return content.value
  }

  return {
    title,
    content,
    fetchAbout,
    updateAbout,
  }
})
