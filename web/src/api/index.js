// 统一API入口
export { roleApi } from './role'
export { equipmentApi } from './equipment'
export { petApi } from './pet'
export { spiderApi } from './spider'
export { configApi } from './config'

// 也可以作为默认导出
import { roleApi } from './role'
import { equipmentApi } from './equipment'
import { petApi } from './pet'
import { spiderApi } from './spider'
import { configApi } from './config'

export default {
  role: roleApi,
  equipment: equipmentApi,
  pet: petApi,
  spider: spiderApi,
  config: configApi
} 