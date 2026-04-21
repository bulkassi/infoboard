import { ref } from 'vue'

const aboutTitle = ref('О нас')
const aboutContent = ref(`
  <h2>Добро пожаловать</h2>
  <p>Этот раздел поддерживает форматирование текста с помощью редактора.</p>
  <p>Откройте боковую панель и выберите пункт редактирования, чтобы изменить содержимое.</p>
`)

export function useAboutBoardState() {
  return {
    aboutTitle,
    aboutContent,
  }
}
