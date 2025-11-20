// 统一API入口
export { roleApi } from './role'
export { equipmentApi } from './equipment'
export { petApi } from './pet'
export { spiderApi } from './spider'
export { systemApi } from './system'
export { adminApi } from './admin'
export { authApi } from './auth'

// 也可以作为默认导出
import { roleApi } from './role'
import { equipmentApi } from './equipment'
import { petApi } from './pet'
import { spiderApi } from './spider'
import { systemApi } from './system'
import { adminApi } from './admin'
import { authApi } from './auth'

export default {
  role: roleApi,
  equipment: equipmentApi,
  pet: petApi,
  spider: spiderApi,
  system: systemApi,
  admin: adminApi,
  auth: authApi
} 