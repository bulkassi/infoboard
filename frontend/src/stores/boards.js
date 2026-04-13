import { defineStore } from 'pinia'
import { ref } from 'vue'

const API_BASE = import.meta.env.VITE_API_URL

export const useBoardsStore = defineStore('boards', () => {
  const boardsById = ref({})
  const loadingById = ref({})
  const errorById = ref({})

  async function fetchBoard(boardId) {
    loadingById.value[boardId] = true
    errorById.value[boardId] = null

    try {
      const response = await fetch(`${API_BASE}/api/boards/${boardId}`)
      if (!response.ok) {
        throw new Error(`Failed to load board ${boardId}: ${response.status}`)
      }
      const board = await response.json()
      boardsById.value[boardId] = board
      return board
    } catch (error) {
      errorById.value[boardId] = error instanceof Error ? error.message : 'Unknown error'
      throw error
    } finally {
      loadingById.value[boardId] = false
    }
  }

  return {
    boardsById,
    loadingById,
    errorById,
    fetchBoard,
  }
})
