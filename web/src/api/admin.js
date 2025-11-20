import { api } from '@/utils/request'

/**
 * 管理员相关API
 */
export const adminApi = {
  /**
   * 获取用户列表
   * @param {Object} params - 查询参数 { page, page_size, is_active }
   * @returns {Promise}
   */
  getUserList(params = {}) {
    return api.get('/admin/users', params)
  },

  /**
   * 获取用户详情
   * @param {number} userId - 用户ID
   * @returns {Promise}
   */
  getUserDetail(userId) {
    return api.get(`/admin/users/${userId}`)
  },

  /**
   * 激活用户
   * @param {number} userId - 用户ID
   * @returns {Promise}
   */
  activateUser(userId) {
    return api.post(`/admin/users/${userId}/activate`)
  },

  /**
   * 禁用用户
   * @param {number} userId - 用户ID
   * @returns {Promise}
   */
  deactivateUser(userId) {
    return api.post(`/admin/users/${userId}/deactivate`)
  },

  /**
   * 设置/取消高级用户
   * @param {number} userId - 用户ID
   * @param {boolean} isPremium - 是否高级用户
   * @returns {Promise}
   */
  setPremium(userId, isPremium = true) {
    return api.post(`/admin/users/${userId}/set-premium`, {
      is_premium: isPremium
    })
  },

  /**
   * 删除用户
   * @param {number} userId - 用户ID
   * @returns {Promise}
   */
  deleteUser(userId) {
    return api.delete(`/admin/users/${userId}`)
  },

  /**
   * 重置用户fingerprint
   * @param {number} userId - 用户ID
   * @returns {Promise}
   */
  resetFingerprint(userId) {
    return api.post(`/admin/users/${userId}/reset-fingerprint`)
  }
}

