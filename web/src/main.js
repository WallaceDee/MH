import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import axios from 'axios'

Vue.config.productionTip = false

Vue.use(ElementUI)

// 配置axios
axios.defaults.baseURL = 'http://localhost:5000'
Vue.prototype.$http = axios

new Vue({
  router,
  store,
  render: (h) => h(App)
}).$mount('#app')
