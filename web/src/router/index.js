import Vue from 'vue'
import VueRouter from 'vue-router'
Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Index',
    component: () => import('../views/Index.vue'),
    meta: {
      title: '梦幻灵瞳 - CBG数据分析平台',
      hideHeader: true
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
