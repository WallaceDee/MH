import { api } from '@/utils/request'

/**
 * 角色相关API
 */
export const roleApi = {
  /**
   * 获取角色列表
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  getRoleApi(params = {}) {
    return api.get('/role/', params)
  },

  /**
   * 获取角色详情
   * @param {string} equipId - 角色装备ID
   * @param {Object} params - 额外参数（如年月）
   * @returns {Promise}
   */
  getRoleDetail(equipId, params = {}) {
    return api.get(`/role/${equipId}`, params)
  },

  /**
   * 健康检查
   * @returns {Promise}
   */
  healthCheck() {
    return api.get('/role/health')
  }
} 