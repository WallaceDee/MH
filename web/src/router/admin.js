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
      showHeader: true
    }
  },
  {
    path: '/auto-params',
    name: 'AutoParams',
    component: AutoParams,
    meta: {
      title: ''
    }
  },
  {
    path: '/roles/:type/:levelRange/:page?',
    name: 'RoleList',
    component: () => import('../views/RoleList.vue'),
    meta: {
      title: '角色列表',
      showHeader: true
    }
  },
  {
    path: '/equipments',
    name: 'EquipmentList',
    component: () => import('../views/EquipmentList.vue'),
    meta: {
      title: '装备列表',
      showHeader: true
    }
  },
  {
    path: '/equipments/:equip_sn',
    name: 'EquipmentDetail',
    component: () => import('../views/EquipmentDetail.vue'),
    meta: {
      title: '装备详情',
      showHeader: true
    }
  },
  {
    path: '/pets',
    name: 'PetList',
    component: () => import('../views/PetList.vue'),
    meta: {
      title: '召唤兽列表',
      showHeader: true
    }
  },
  {
    path: '/equipment-desc-creator',
    name: 'EquipmentDescCreator',
    component: () => import('../views/EquipmentDescCreator.vue'),
    meta: {
      title: '装备模拟',
      showHeader: true
    }
  },
  {
    path: '/market-data-status',
    name: 'MarketDataStatus',
    component: () => import('../views/MarketDataStatus.vue'),
    meta: {
      title: '市场数据状态',
      showHeader: true
    }
  }
]

const router = new VueRouter({
  base: process.env.BASE_URL,
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '👁️梦幻灵瞳'
  next()
})

export default router
