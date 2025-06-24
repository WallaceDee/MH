import { api } from '@/utils/request'

/**
 * 角色相关API
 */
export const characterApi = {
  /**
   * 获取角色列表
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  getCharacterList(params = {}) {
    return api.get('/character/', params)
  },

  /**
   * 获取角色详情
   * @param {string} equipId - 角色装备ID
   * @param {Object} params - 额外参数（如年月）
   * @returns {Promise}
   */
  getCharacterDetail(equipId, params = {}) {
    return api.get(`/character/${equipId}`, params)
  },

  /**
   * 导出角色数据为JSON
   * @param {Object} data - 导出参数
   * @returns {Promise}
   */
  exportCharactersJson(data = {}) {
    return api.post('/character/export/json', data)
  },

  /**
   * 导出单个角色数据为JSON
   * @param {string} equipId - 角色装备ID
   * @param {Object} params - 额外参数
   * @returns {Promise}
   */
  exportSingleCharacterJson(equipId, params = {}) {
    return api.download(`/character/${equipId}/export/json`, params, `character_${equipId}.json`)
  },

  /**
   * 健康检查
   * @returns {Promise}
   */
  healthCheck() {
    return api.get('/character/health')
  }
} 