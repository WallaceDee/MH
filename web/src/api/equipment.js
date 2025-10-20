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
   * 批量装备估价
   * @param {Object} data - 装备列表和估价参数
   * @returns {Promise}
   */
  batchEquipmentValuation(data) {
    return api.post('/equipment/batch-valuation', data)
  },





  /**
   * 删除装备
   * @param {string} equipSn - 装备序列号
   * @param {Object} params - 额外参数（如年月）
   * @returns {Promise}
   */
  deleteEquipment(equipSn, params = {}) {
    return api.delete(`/equipment/${equipSn}`, params)
  },

  /**
   * 获取灵饰数据
   * @returns {Promise}
   */
  getLingshiConfig() {
    return api.get('/equipment/lingshi-config')
  },

  /**
   * 获取武器数据
   * @returns {Promise}
   */
  getWeaponConfig() {
    return api.get('/equipment/weapon-config')
  },

  /**
   * 获取召唤兽装备数据
   * @returns {Promise}
   */
  getPetEquipConfig() {
    return api.get('/equipment/pet-equip-config')
  },

  /**
   * 获取装备数据
   * @returns {Promise}
   */
  getEquipConfig() {
    return api.get('/equipment/equip-config')
  },
  /**
   * 标记装备为异常
   * @param {Object} data - 装备数据和标记原因
   * @returns {Promise}
   */
  markEquipmentAsAbnormal(data) {
    return api.post('/equipment/mark-abnormal', data)
  },

  /**
   * 获取异常装备列表
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  getAbnormalEquipmentList(params = {}) {
    return api.get('/equipment/abnormal', params)
  },

  /**
   * 更新异常装备状态
   * @param {string} equipSn - 装备序列号
   * @param {Object} data - 更新数据
   * @returns {Promise}
   */
  updateAbnormalEquipmentStatus(equipSn, data) {
    return api.put(`/equipment/abnormal/${equipSn}`, data)
  },

  /**
   * 删除异常装备记录
   * @param {string} equipSn - 装备序列号
   * @returns {Promise}
   */
  deleteAbnormalEquipment(equipSn) {
    return api.delete(`/equipment/abnormal/${equipSn}`)
  }
} 