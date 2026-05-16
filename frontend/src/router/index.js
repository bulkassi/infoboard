import { createRouter, createWebHistory } from 'vue-router'
import BoardMain from '@/views/BoardMain.vue'
import BoardEmployees from '@/views/BoardEmployees.vue'
import BoardServices from '@/views/BoardServices.vue'
import BoardAbout from '@/views/BoardAbout.vue'
import BoardUser from '@/views/BoardUser.vue'
import AdminPage from '@/views/AdminPage.vue'
import LoginPage from '@/views/LoginPage.vue'
import { useAuthStore } from '@/stores/auth'

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
      path: '/login',
      name: 'login',
      component: LoginPage,
    },
    {
      path: '/board/:boardId(\\d+)',
      name: 'board-user',
      component: BoardUser,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminPage,
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
      },
    },
  ],
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  await authStore.bootstrapSession()

  const hasShareToken = typeof to.query.share_token === 'string'

  if (to.meta.requiresAuth && !authStore.isAuthenticated && !hasShareToken) {
    return {
      path: '/login',
      query: { redirect: to.fullPath },
    }
  }

  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    return {
      path: '/main',
    }
  }

  return true
})

export default router
