// 统一API入口
export { characterApi } from './character'
export { equipmentApi } from './equipment'

// 也可以作为默认导出
import { characterApi } from './character'
import { equipmentApi } from './equipment'

export default {
  character: characterApi,
  equipment: equipmentApi
} 