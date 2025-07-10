import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/HomeView.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/characters',
    name: 'CharacterList',
    component: () => import('../views/CharacterList.vue'),
    meta: {
      title: '角色列表'
    }
  },
  {
    path: '/equipments',
    name: 'EquipmentList',
    component: () => import('../views/EquipmentList.vue'),
    meta: {
      title: '装备列表'
    }
  },
  {
    path: '/pets',
    name: 'PetList',
    component: () => import('../views/PetList.vue'),
    meta: {
      title: '召唤兽列表'
    }
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'CBG数据'
  next()
})

export default router
