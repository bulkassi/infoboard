import { createRouter, createWebHistory } from 'vue-router'
import BoardMain from '@/views/BoardMain.vue'
import BoardEmployees from '@/views/BoardEmployees.vue'
import BoardServices from '@/views/BoardServices.vue'
import BoardAbout from '@/views/BoardAbout.vue'
import AdminPage from '@/views/AdminPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: {
        name: 'board-main',
      },
    },
    {
      path: '/main',
      name: 'board-main',
      component: BoardMain,
    },
    {
      path: '/about',
      name: 'board-about',
      component: BoardAbout,
    },
    {
      path: '/employees',
      name: 'board-employees',
      component: BoardEmployees,
    },
    {
      path: '/services',
      name: 'board-services',
      component: BoardServices,
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminPage,
    },
  ],
})

export default router
