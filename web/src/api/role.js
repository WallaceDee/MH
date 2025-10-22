import { api } from '@/utils/request'

/**
 * 角色相关API
 */
export const roleApi = {
  /**
   * 获取角色列表
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.page_size - 每页大小
   * @param {number} params.year - 年份
   * @param {number} params.month - 月份
   * @param {number} params.level_min - 最低等级
   * @param {number} params.level_max - 最高等级
   * @param {number} params.equip_num - 装备数量限制
   * @param {number} params.pet_num - 召唤兽数量限制
   * @param {number} params.pet_num_level - 召唤兽等级限制
   * @param {string} params.sort_by - 排序字段
   * @param {string} params.sort_order - 排序方向
   * @param {string} params.role_type - 角色类型，'normal' 表示正常角色，'empty' 表示空号角色
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
   * 删除角色
   * @param {string} eid - 角色订单号
   * @param {Object} params - 额外参数（如年月、role_type）
   * @returns {Promise}
   */
  deleteRole(eid, params = {}) {
    return api.delete(`/role/${eid}`, params)
  },

  /**
   * 切换角色类型（数据迁移）
   * @param {string} eid - 角色订单号
   * @param {Object} params - 查询参数（如年月、role_type/target_role_type）
   * @returns {Promise}
   */
  switchRoleType(eid, params = {}) {
    return api.post(`/role/${eid}/switch-type`, params)
  },

  /**
   * 角色估价
   * @param {Object} params - 估价参数
   * @param {string} params.eid - 角色唯一标识符
   * @param {number} params.year - 年份（可选）
   * @param {number} params.month - 月份（可选）
   * @param {string} params.role_type - 角色类型（可选，默认normal）
   * @param {string} params.strategy - 估价策略（可选，默认fair_value）
   * @param {number} params.similarity_threshold - 相似度阈值（可选，默认0.7）
   * @param {number} params.max_anchors - 最大锚点数量（可选，默认30）
   * @returns {Promise}
   */
  getRoleValuation(params = {}) {
    return api.post('/role/valuation', params)
  },

  /**
   * 批量角色估价
   * @param {Object} params - 批量估价参数
   * @param {Array} params.eid_list - 角色eid列表
   * @param {number} params.year - 年份（可选）
   * @param {number} params.month - 月份（可选）
   * @param {string} params.role_type - 角色类型（可选，默认normal）
   * @param {string} params.strategy - 估价策略（可选，默认fair_value）
   * @param {number} params.similarity_threshold - 相似度阈值（可选，默认0.7）
   * @param {number} params.max_anchors - 最大锚点数量（可选，默认30）
   * @param {boolean} params.verbose - 是否详细日志（可选，默认false）
   * @returns {Promise}
   */
  batchRoleValuation(params = {}) {
    return api.post('/role/batch-valuation', params)
  },

  /**
   * 更新角色裸号价格
   * @param {Object} params - 更新参数
   * @param {string} params.eid - 角色唯一标识符
   * @param {number} params.base_price - 裸号价格（分）
   * @param {number} params.year - 年份（可选）
   * @param {number} params.month - 月份（可选）
   * @param {string} params.role_type - 角色类型（可选，默认normal）
   * @returns {Promise}
   */
  updateRoleBasePrice(params = {}) {
    return api.post(`/role/${params.eid}/update-base-price`, params)
  },

  /**
   * 查找相似角色锚点
   * @param {Object} params - 查询参数
   * @param {string} params.eid - 角色唯一标识符
   * @param {number} params.year - 年份
   * @param {number} params.month - 月份
   * @param {string} params.role_type - 角色类型（可选，默认normal）
   * @param {number} params.similarity_threshold - 相似度阈值（可选，默认0.7）
   * @param {number} params.max_anchors - 最大锚点数量（可选，默认30）
   * @returns {Promise}
   */
  findRoleAnchors(params = {}) {
    return api.post('/role/find-anchors', params)
  },

  /**
   * 健康检查
   * @returns {Promise}
   */
  healthCheck() {
    return api.get('/role/health')
  },

  /**
   * 获取角色统计数据
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  getRoleStats(params = {}) {
    return api.get('/role/stats', params)
  }

} 