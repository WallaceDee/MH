import Vue from 'vue'
import DevToolsPanel from './DevToolsPanel.vue'
import store from '../store'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import api from '../api'

Vue.config.productionTip = false
Vue.prototype.$api = api

// 使用Element UI
Vue.use(ElementUI, { size: 'mini' })

// 创建Vue应用，注入 Vuex store
new Vue({
  store,
  render: h => h(DevToolsPanel)
}).$mount('#app')
