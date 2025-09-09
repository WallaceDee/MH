import Vue from 'vue'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import DevToolsPanel from './DevToolsPanel.vue'

// 使用Element UI
Vue.use(ElementUI)

// 创建Vue应用
new Vue({
  el: '#app',
  render: h => h(DevToolsPanel)
})
