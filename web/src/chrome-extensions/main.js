import Vue from 'vue'
import DevToolsPanel from './DevToolsPanel.vue'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

Vue.config.productionTip = false

// 使用Element UI
Vue.use(ElementUI, { size: 'mini' })

// 创建Vue应用
new Vue({
  render: h => h(DevToolsPanel)
}).$mount('#app')
