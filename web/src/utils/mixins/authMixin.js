/**
 * 认证相关方法Mixin
 * 提供统一的登录检查功能
 */
export const authMixin = {
  methods: {
    /**
     * 检查登录状态
     * @returns {Promise<boolean>} 是否已登录
     */
    async checkAuthStatus() {
      // 先检查 userInfo（最快的方式）
      if (this.userInfo !== null && this.userInfo !== undefined) {
        return true
      }
      
      // 如果没有 userInfo，从 chrome.storage 检查 token
      if (typeof chrome !== 'undefined' && chrome.storage) {
        try {
          const result = await new Promise((resolve) => {
            chrome.storage.local.get(['auth_token', 'user_info'], (result) => {
              resolve(result)
            })
          })
          return !!(result.auth_token || result.user_info)
        } catch (error) {
          console.error('检查登录状态失败:', error)
          return false
        }
      }
      
      return false
    },
    
    /**
     * 检查登录状态，如果未登录则提示并返回 false
     * 用于在方法开始处快速检查
     * @returns {Promise<boolean>} 是否已登录
     */
    async $requireAuth() {
      const isAuthenticated = await this.checkAuthStatus()
      
      if (!isAuthenticated) {
        this.$notify.warning({
          title: '需要登录',
          message: '此功能需要登录后才能使用，请先登录',
          duration: 3000
        })
        return false
      }
      
      return true
    },
    
    /**
     * 包装需要登录的方法
     * 使用方式: @click="$auth(handleEquipPrice, role)"
     * @param {Function} fn 需要登录的方法
     * @param {...any} args 方法参数
     * @returns {Promise<any>} 方法返回值
     */
    async $auth(fn, ...args) {
      const isAuthenticated = await this.checkAuthStatus()
      
      if (!isAuthenticated) {
        this.$notify.warning({
          title: '需要登录',
          message: '此功能需要登录后才能使用，请先登录',
          duration: 3000
        })
        return false
      }
      
      return fn.apply(this, args)
    }
  }
}

