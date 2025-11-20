import { api } from '@/utils/request'

/**
 * 认证相关API
 */
export const authApi = {
  /**
   * 用户登录
   * @param {Object} data - { username, password }
   * @returns {Promise}
   */
  login(data) {
    return api.post('/auth/login', data)
  },

  /**
   * 用户注册
   * @param {Object} data - { username, password }
   * @returns {Promise}
   */
  register(data) {
    return api.post('/auth/register', data)
  },

  /**
   * 用户登出
   * @returns {Promise}
   */
  logout() {
    return api.post('/auth/logout')
  },

  /**
   * 获取当前用户信息
   * @returns {Promise}
   */
  getCurrentUser() {
    return api.get('/auth/me')
  },

  /**
   * 刷新token
   * @returns {Promise}
   */
  refreshToken() {
    return api.post('/auth/refresh-token')
  },

  /**
   * 更新指纹
   * @param {Object} data - { fingerprint }
   * @returns {Promise}
   */
  updateFingerprint(data) {
    return api.post('/auth/update-fingerprint', data)
  }
}

