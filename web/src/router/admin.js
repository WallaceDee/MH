import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/HomeView.vue'
import AutoParams from '@/components/AutoParams.vue'
Vue.use(VueRouter)

const routes = [

  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      showHeader: true,
      requiresAuth: true
    }
  },
  {
    path: '/auto-params',
    name: 'AutoParams',
    component: AutoParams,
    meta: {
      title: '',
      requiresAuth: true
    }
  },
  {
    path: '/roles/:type/:levelRange/:page?',
    name: 'RoleList',
    component: () => import('../views/RoleList.vue'),
    meta: {
      title: '角色列表',
      showHeader: true,
      requiresAuth: true
    }
  },
  {
    path: '/equipments',
    name: 'EquipmentList',
    component: () => import('../views/EquipmentList.vue'),
    meta: {
      title: '装备列表',
      showHeader: true,
      requiresAuth: true
    }
  },
  {
    path: '/equipments/:equip_sn',
    name: 'EquipmentDetail',
    component: () => import('../views/EquipmentDetail.vue'),
    meta: {
      title: '装备详情',
      showHeader: true,
      requiresAuth: true
    }
  },
  {
    path: '/pets',
    name: 'PetList',
    component: () => import('../views/PetList.vue'),
    meta: {
      title: '召唤兽列表',
      showHeader: true,
      requiresAuth: true
    }
  },
  {
    path: '/equipment-desc-creator',
    name: 'EquipmentDescCreator',
    component: () => import('../views/EquipmentDescCreator.vue'),
    meta: {
      title: '装备模拟',
      showHeader: true,
      requiresAuth: true
    }
  },
  {
    path: '/market-data-status',
    name: 'MarketDataStatus',
    component: () => import('../views/MarketDataStatus.vue'),
    meta: {
      title: '市场数据状态',
      showHeader: true,
      requiresAuth: true
    }
  },
  {
    path: '/admin/users',
    name: 'UserManagement',
    component: () => import('../views/UserManagement.vue'),
    meta: {
      title: '用户管理',
      showHeader: true,
      requiresAuth: true
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: {
      title: '登录',
      showHeader: false
    }
  }
]

const router = new VueRouter({
  base: process.env.BASE_URL,
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '👁️梦幻灵瞳'
  
  // 检查路由是否需要认证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查是否已登录
    const token = localStorage.getItem('auth_token')
    const userInfoStr = localStorage.getItem('user_info')
    
    if (!token || !userInfoStr) {
      // 未登录，重定向到登录页
      console.log('未登录，重定向到登录页:', to.fullPath)
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      // 验证用户信息的有效性
      try {
        const userInfo = JSON.parse(userInfoStr)
        if (userInfo && userInfo.username) {
          // 检查是否是管理员（后台管理需要管理员权限）
          if (!userInfo.is_admin) {
            // 非管理员用户，清除登录信息并重定向到登录页
            console.warn('非管理员用户，无法访问后台管理')
            localStorage.removeItem('auth_token')
            localStorage.removeItem('user_info')
            next({
              path: '/login',
              query: { redirect: to.fullPath }
            })
            return
          }
          // 用户信息有效且是管理员，允许访问
          next()
        } else {
          // 用户信息无效，清除并重定向到登录页
          console.warn('用户信息无效，清除并重定向到登录页')
          localStorage.removeItem('auth_token')
          localStorage.removeItem('user_info')
          next({
            path: '/login',
            query: { redirect: to.fullPath }
          })
        }
      } catch (error) {
        // 解析用户信息失败，清除并重定向到登录页
        console.error('解析用户信息失败:', error)
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user_info')
        next({
          path: '/login',
          query: { redirect: to.fullPath }
        })
      }
    }
  } else {
    // 不需要认证的路由（如登录页），直接放行
    next()
  }
})

export default router
