import { api } from '@/utils/request'

/**
 * 宠物相关API
 */
export const petApi = {
  /**
   * 获取宠物列表
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  getPetList(params = {}) {
    return api.get('/pet/', params)
  },

  /**
   * 获取宠物详情
   * @param {string} petSn - 宠物序列号
   * @param {Object} params - 额外参数（如年月）
   * @returns {Promise}
   */
  getPetDetail(petSn, params = {}) {
    return api.get(`/pet/${petSn}`, params)
  },

  /**
   * 寻找宠物市场锚点
   * @param {Object} data - 宠物数据和查询参数
   * @returns {Promise}
   */
  findPetAnchors(data) {
    return api.post('/pet/anchors', data)
  },

  /**
   * 获取宠物估价
   * @param {Object} data - 宠物数据和估价参数
   * @returns {Promise}
   */
  getPetValuation(data) {
    return api.post('/pet/valuation', data)
  },

  /**
   * 通过宠物SN查找锚点（便捷接口）
   * @param {string} petSn - 宠物序列号
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  findAnchorsBySn(petSn, params = {}) {
    return api.get(`/pet/anchors/${petSn}`, params)
  },

  /**
   * 通过宠物SN获取估价（便捷接口）
   * @param {string} petSn - 宠物序列号
   * @param {Object} params - 估价参数
   * @returns {Promise}
   */
  getValuationBySn(petSn, params = {}) {
    return api.get(`/pet/valuation/${petSn}`, params)
  },

  /**
   * 健康检查
   * @returns {Promise}
   */
  healthCheck() {
    return api.get('/pet/health')
  }
} 