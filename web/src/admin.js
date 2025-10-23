import Vue from 'vue'
import App from './App.vue'
import router from './router/admin'
import store from './store'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import api from './api'
import CookieManager from './plugins/cookieManager'

Vue.config.productionTip = false

Vue.use(ElementUI, { size: 'mini'})
Vue.use(CookieManager)

Vue.prototype.$api = api

new Vue({
  router,
  store,
  render: (h) => h(App)
}).$mount('#app')
