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
   * @param {number} params.pet_num - 宠物数量限制
   * @param {number} params.pet_num_level - 宠物等级限制
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
   * 健康检查
   * @returns {Promise}
   */
  healthCheck() {
    return api.get('/role/health')
  },

} 