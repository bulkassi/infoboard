import { ref } from 'vue'
import { defineStore } from 'pinia'
import { useAuthStore } from '@/stores/auth'

export const useShareLinksStore = defineStore('shareLinks', () => {
  const authStore = useAuthStore()
  const linksByBoardId = ref({})

  function getLinks(boardId) {
    return linksByBoardId.value[boardId] ?? []
  }

  async function fetchLinks(boardId) {
    const response = await authStore.authorizedRequest(`/boards/${boardId}/share-links`)
    const links = Array.isArray(response) ? response : []
    linksByBoardId.value = {
      ...linksByBoardId.value,
      [boardId]: links,
    }
    return links
  }

  async function createLink(boardId) {
    const response = await authStore.authorizedRequest(`/boards/${boardId}/share-links`, {
      method: 'POST',
      body: {},
    })
    const next = [...getLinks(boardId), response]
    linksByBoardId.value = {
      ...linksByBoardId.value,
      [boardId]: next,
    }
    return response
  }

  async function deleteLink(token) {
    await authStore.authorizedRequest(`/share-links/${token}`, {
      method: 'DELETE',
    })

    const nextByBoard = { ...linksByBoardId.value }
    Object.keys(nextByBoard).forEach((boardId) => {
      nextByBoard[boardId] = nextByBoard[boardId].filter((link) => link.token !== token)
    })
    linksByBoardId.value = nextByBoard
  }

  return {
    linksByBoardId,
    getLinks,
    fetchLinks,
    createLink,
    deleteLink,
  }
})
