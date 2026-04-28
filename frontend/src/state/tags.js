import { ref } from 'vue'

const initialTags = [
  {
    id: 0,
    name: 'Важная информация',
    textColor: 'ffffff',
    bgColor: 'ef4444',
    isGlobal: true,
    ownerUserId: 1,
  },
  {
    id: 1,
    name: 'Срочно',
    textColor: 'ffffff',
    bgColor: 'f59e0b',
    isGlobal: true,
    ownerUserId: 1,
  },
  {
    id: 2,
    name: 'На рассмотрении',
    textColor: 'ffffff',
    bgColor: '3b82f6',
    isGlobal: false,
    ownerUserId: 100,
  },
]

export const tags = ref(initialTags)

let nextTagId = initialTags.reduce((maxId, tag) => Math.max(maxId, tag.id), -1) + 1

export function getNextTagId() {
  const tagId = nextTagId
  nextTagId += 1
  return tagId
}

export function reserveTagId(tagId) {
  if (!Number.isInteger(tagId)) {
    return
  }

  if (tagId >= nextTagId) {
    nextTagId = tagId + 1
  }
}
