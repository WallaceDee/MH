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
   * 批量召唤兽估价
   * @param {Object} data - 召唤兽列表和估价参数
   * @returns {Promise}
   */
  batchPetValuation(data) {
    return api.post('/pet/batch-valuation', data)
  },

  /**
   * 更新召唤兽装备价格
   * @param {Object} data - 召唤兽数据和估价参数
   * @returns {Promise}
   */
  updatePetEquipmentsPrice(data) {
    return api.post('/pet/update-equipments-price', data)
  },

  /**
   * 获取当前年月携带装备但未估价的召唤兽数量
   * @param {Object} params - 查询参数（年月）
   * @returns {Promise}
   */
  getUnvaluedPetsCount(params = {}) {
    return api.get('/pet/unvalued-count', params)
  },

  /**
   * 批量更新未估价召唤兽的装备价格
   * @param {Object} data - 请求数据（年月）
   * @returns {Promise}
   */
  batchUpdateUnvaluedPets(data = {}) {
    return api.post('/pet/batch-update-unvalued', data)
  },

  /**
   * 获取任务状态
   * @param {string} taskId - 任务ID
   * @returns {Promise}
   */
  getTaskStatus(taskId) {
    return api.get(`/pet/task-status/${taskId}`)
  },

  /**
   * 获取活跃任务列表
   * @returns {Promise}
   */
  getActiveTasks() {
    return api.get('/pet/active-tasks')
  },

  /**
   * 停止任务
   * @param {string} taskId - 任务ID
   * @returns {Promise}
   */
  stopTask(taskId) {
    return api.post(`/pet/stop-task/${taskId}`)
  },

  /**
   * 删除召唤兽
   * @param {string} petSn - 召唤兽序列号
   * @param {Object} params - 查询参数（年月）
   * @returns {Promise}
   */
  deletePet(petSn, params = {}) {
    return api.delete(`/pet/${petSn}`, params)
  },

  /**
   * 通过equip_sn获取召唤兽详情
   * @param {string} year - 年份
   * @param {string} month - 月份
   * @param {string} equipSn - 召唤兽序列号
   * @returns {Promise}
   */
  getPetByEquipSn(year, month, equipSn) {
    return api.get(`/pet/${year}/${month}/${equipSn}`)
  }
} 