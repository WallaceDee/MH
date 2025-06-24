import { api } from '@/utils/request'

/**
 * 装备相关API
 */
export const equipmentApi = {
  /**
   * 获取装备列表
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  getEquipmentList(params = {}) {
    return api.get('/equipment/', params)
  },

  /**
   * 获取装备详情
   * @param {string} equipSn - 装备序列号
   * @param {Object} params - 额外参数（如年月）
   * @returns {Promise}
   */
  getEquipmentDetail(equipSn, params = {}) {
    return api.get(`/equipment/${equipSn}`, params)
  },

  /**
   * 寻找装备市场锚点
   * @param {Object} data - 装备数据和查询参数
   * @returns {Promise}
   */
  findEquipmentAnchors(data) {
    return api.post('/equipment/anchors', data)
  },

  /**
   * 获取装备估价
   * @param {Object} data - 装备数据和估价参数
   * @returns {Promise}
   */
  getEquipmentValuation(data) {
    return api.post('/equipment/valuation', data)
  },

  /**
   * 通过装备SN查找锚点（便捷接口）
   * @param {string} equipSn - 装备序列号
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  findAnchorsBySn(equipSn, params = {}) {
    return api.get(`/equipment/anchors/${equipSn}`, params)
  },

  /**
   * 通过装备SN获取估价（便捷接口）
   * @param {string} equipSn - 装备序列号
   * @param {Object} params - 估价参数
   * @returns {Promise}
   */
  getValuationBySn(equipSn, params = {}) {
    return api.get(`/equipment/valuation/${equipSn}`, params)
  },

  /**
   * 健康检查
   * @returns {Promise}
   */
  healthCheck() {
    return api.get('/equipment/health')
  }
} 