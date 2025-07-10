import { api } from '@/utils/request'

/**
 * 召唤兽相关API
 */
export const petApi = {
  /**
   * 获取召唤兽列表
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  getPetList(params = {}) {
    return api.get('/pet/', params)
  },

  /**
   * 获取召唤兽详情
   * @param {string} petSn - 召唤兽序列号
   * @param {Object} params - 额外参数（如年月）
   * @returns {Promise}
   */
  getPetDetail(petSn, params = {}) {
    return api.get(`/pet/${petSn}`, params)
  },

  /**
   * 寻找召唤兽市场锚点
   * @param {Object} data - 召唤兽数据和查询参数
   * @returns {Promise}
   */
  findPetAnchors(data) {
    return api.post('/pet/anchors', data)
  },

  /**
   * 获取召唤兽估价
   * @param {Object} data - 召唤兽数据和估价参数
   * @returns {Promise}
   */
  getPetValuation(data) {
    return api.post('/pet/valuation', data)
  },

  /**
   * 通过召唤兽SN查找锚点（便捷接口）
   * @param {string} petSn - 召唤兽序列号
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  findAnchorsBySn(petSn, params = {}) {
    return api.get(`/pet/anchors/${petSn}`, params)
  },

  /**
   * 通过召唤兽SN获取估价（便捷接口）
   * @param {string} petSn - 召唤兽序列号
   * @param {Object} params - 估价参数
   * @returns {Promise}
   */
  getValuationBySn(petSn, params = {}) {
    return api.get(`/pet/valuation/${petSn}`, params)
  },

  /**
   * 导出召唤兽数据为JSON
   * @param {Object} data - 导出参数
   * @returns {Promise}
   */
  exportPetsJson(data = {}) {
    return api.post('/pet/export/json', data)
  },

  /**
   * 导出单个召唤兽数据为JSON
   * @param {string} petSn - 召唤兽序列号
   * @param {Object} params - 额外参数
   * @returns {Promise}
   */
  exportSinglePetJson(petSn, params = {}) {
    return api.download(`/pet/${petSn}/export/json`, params, `pet_${petSn}.json`)
  },

  /**
   * 健康检查
   * @returns {Promise}
   */
  healthCheck() {
    return api.get('/pet/health')
  }
} 