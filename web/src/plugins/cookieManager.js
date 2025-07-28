// Cookie管理插件 - 简化版本
const CookieManager = {
  install(Vue) {
    // 添加全局属性
    Vue.prototype.$cookieManager = {
      // 获取缓存状态
      getCache() {
        return this.$store.state.cookie.cookieValidationCache
      },

      // 设置缓存状态
      setCache(cache) {
        this.$store.commit('cookie/updateCookieCache', cache)
      },

      // 重置插件状态
      reset() {
        this.$store.dispatch('cookie/clearCookieCache')
      }
    }
  }
}

export default CookieManager 