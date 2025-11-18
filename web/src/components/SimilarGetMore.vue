<template>
  <span>
    <el-button type="success" @click="goToMoreSimilar">
      查看更多相似
    </el-button>

    <!-- AutoParams Modal -->
    <!-- 
      Bug原因分析：
      1. 事件冒泡：点击内层对话框内容时，事件会冒泡到外层对话框的遮罩层
      2. Element UI 关闭机制：外层对话框接收到点击遮罩事件，即使设置了 close-on-click-modal="false"，
         但如果事件路径包含遮罩层，仍可能触发关闭
      3. 嵌套对话框的特殊情况：当对话框嵌套时，DOM层级和事件传播路径更复杂，
         容易导致误判点击位置
      
      解决方案：
      - @click.native.stop: 阻止原生DOM事件冒泡，防止事件传播到外层
      - @mousedown.native.stop: 阻止鼠标按下事件冒泡
      - @click.stop: 阻止Vue事件冒泡
      - before-close: 完全控制关闭逻辑，只允许通过明确的方法关闭
    -->
    <el-dialog :visible.sync="autoParamsDialogVisible" width="720px" :close-on-click-modal="false"
      :close-on-press-escape="false" custom-class="auto-params-dialog" append-to-body @click.native.stop
      @mousedown.native.stop>
      <AutoParams v-if="autoParamsDialogVisible" :external-params="autoParamsExternalParams" :log="false"
        :server-id="modalServerId" :server-name="modalServerName" @close="closeAutoParamsDialog" />

      <!-- 显示搜索回来的结果 - 装备和召唤兽数据列表 -->
      <div v-if="shouldShowEquipsAndPetsData" class="equips-pets-data-section">
        <el-divider content-position="left">搜索结果</el-divider>
        <div v-for="(item, index) in equipsAndPetsData" :key="item.requestId || `equip-${index}`" class="data-item">
          <div class="data-item-header">
            <span class="status" :class="item.status">
              <template v-if="item.status === 'parsing'">
                <i class="el-icon-loading"></i> 解析中...
              </template>
              <template v-else-if="item.status === 'completed'">
                <i class="el-icon-success"></i> 解析完成
              </template>
              <template v-else>
                <i class="el-icon-error"></i> 解析失败
              </template>
            </span>
            <el-tag v-if="item.dataType || item.requestCategory" size="mini" type="info" style="margin-left: 5px;">
              {{ getDataTypeLabel(item.dataType || item.requestCategory) }}
            </el-tag>
          </div>

          <!-- 装备数据渲染 -->
          <el-row :gutter="4" v-if="(item.dataType || item.requestCategory) === 'equipment'">
            <el-col v-for="equip in parseListData(item.responseData)?.equip_list" :key="equip.eid"
              style="width: 20%;margin-bottom: 2px;margin-top: 2px;">
              <el-card class="result-card">
                <EquipmentImage :equipment="equip" />
                <el-link :href="getCBGLinkByType(equip.eid, 'equip')" type="danger" target="_blank"
                  style="white-space: nowrap;text-overflow: ellipsis;overflow: hidden;display: block;font-size: 12px;">
                  {{ equip.equip_name }}
                </el-link>
                <div style="padding: 5px 0;">
                  <span v-html="formatFullPrice(equip)"></span>
                </div>
                <div v-if="equip.highlight" class="equip-desc-content" v-html="gen_highlight(equip.highlight)"></div>
                <div v-if="equip.equip_level" style="font-size: 12px;">
                  等级: {{ equip.equip_level }}
                </div>
                <div v-if="equip.server_name" style="font-size: 12px; color: #909399;">
                  {{ equip.server_name }}
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 召唤兽数据渲染 -->
          <el-row :gutter="4" v-else-if="(item.dataType || item.requestCategory) === 'pet'">
            <el-col v-for="pet in parseListData(item.responseData)?.equip_list" :key="pet.eid"
              style="width: 20%;margin-bottom: 2px;margin-top: 2px;">
              <el-card class="result-card">
                <el-row type="flex" justify="space-between">
                  <el-col style="width:50px;flex-shrink: 0;margin-right: 4px;">
                    <el-image v-if="pet.avatar_url" :src="pet.avatar_url" style="width: 50px;height: 50px;"
                      fit="cover"></el-image>
                    <el-link :href="getCBGLinkByType(pet.eid, 'pet')" type="danger" target="_blank"
                      style="white-space: nowrap;text-overflow: ellipsis;overflow: hidden;display: block;font-size: 12px;">
                      {{ pet.seller_nickname || pet.name || pet.nickname }}
                    </el-link>
                  </el-col>
                  <el-col>
                    <div style="padding: 5px 0;">
                      <span v-html="formatFullPrice(pet.price, true)"></span>
                    </div>
                    <div v-if="pet.grade" style="font-size: 12px;">
                      等级: {{ pet.grade }}
                    </div>
                    <div v-if="pet.server_name" style="font-size: 12px; color: #909399;">
                      {{ pet.server_name }}
                    </div>
                  </el-col>
                </el-row>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-dialog>
  </span>
</template>

<script>
import qs from 'qs'
import windowReuseManager from '@/utils/windowReuseManager'
import AutoParams from '@/components/AutoParams.vue'
import EquipmentImage from '@/components/EquipmentImage/EquipmentImage.vue'
import { commonMixin } from '@/utils/mixins/commonMixin'
import { equipmentMixin } from '@/utils/mixins/equipmentMixin'

export default {
  name: 'SimilarGetMore',
  components: {
    AutoParams,
    EquipmentImage
  },
  mixins: [commonMixin, equipmentMixin],
  data() {
    return {
      // AutoParams Modal相关数据
      autoParamsDialogVisible: false,
      autoParamsExternalParams: {},
      // 服务器信息（从externalParams中提取）
      modalServerId: undefined,
      modalServerName: undefined,
      // 标记是否允许关闭对话框
      allowDialogClose: false
    }
  },
  computed: {
    // 判断是否为 Chrome 插件环境
    isChromeExtension() {
      return 1||typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id
    },
    // 从 Vuex 获取装备和召唤兽数据（仅在 Chrome 插件环境下）
    equipsAndPetsData() {
      if (this.isChromeExtension) {
        return this.$store.getters['chromeDevtools/getEquipsAndPetsData']
      }
      return []
    },
    // 判断是否显示装备和召唤兽数据列表
    shouldShowEquipsAndPetsData() {
      return this.isChromeExtension && this.autoParamsDialogVisible && this.equipsAndPetsData.length > 0
    }
  },
  props: {
    message: {
      type: String,
      default: ''
    },
    targetEquipment: {
      type: Object,
      default: () => ({})
    },
    type: {
      type: String,
      default: 'equip'
    }
  },
  methods: {
    async goToMoreSimilar() {
      let externalParams = {}
      if (this.type === 'equip') {
        console.log(this.targetEquipment, 'this.targetEquipment')
        const { equip_name, large_equip_desc, equip_type_desc, icon, equip_face_img, equip_level, kindid, equip_type, iType, serverid, server_name } = this.targetEquipment
        externalParams = {
          action: 'similar_equip',
          equip_type: 'normal',
          activeTab: 'equip',
          equip_name,
          large_equip_desc,
          equip_type_desc,
          equip_face_img: equip_face_img || icon,
          equip_level,
          kindid,
          type: iType || equip_type || undefined,
          serverid,
          server_name
        }

        if (window.is_pet_equip(externalParams.kindid)) {
          externalParams.equip_type = 'pet'
          //TODO:sssssssssssssssssssss
        } else if (window.lingshiKinds.some(([kId]) => kId === externalParams.kindid)) {
          externalParams.equip_type = 'lingshi'
        }

        if (!externalParams.equip_name) {
          externalParams.equip_name = this.targetEquipment.name
        }
        if (!externalParams.equip_type_desc) {
          externalParams.equip_type_desc = this.targetEquipment.static_desc
        }
      } else if (this.type === 'pet') {
        //TODO: RoleList跳转的参数需要处理
        console.log('SimilarGetMore - targetEquipment:', this.targetEquipment)
        
        const { equip_sn, role_grade_limit, equip_level, growth, is_baobao, all_skill, sp_skill, evol_skill_list, texing, lx, equip_list, neidan, equip_face_img, serverid, server_name } = this.targetEquipment
        
        externalParams = {
          action: 'similar_pet',
          activeTab: 'pet',
          equip_face_img,
          equip_sn,
          role_grade_limit,
          equip_level,
          growth,
          is_baobao,
          all_skill,
          sp_skill,
          evol_skill_list,
          texing,
          lx,
          equip_list,
          neidan,
          serverid,
          server_name
        }
        
        console.log('SimilarGetMore - 提取的宠物参数:', externalParams)
        console.log('SimilarGetMore - 关键字段检查:', {
          role_grade_limit,
          equip_level,
          growth,
          texing,
          lx,
          sp_skill,
          evol_skill_list
        })
      }

      // 尝试复用已存在的窗口
      console.log('🔍 开始检查可复用的窗口，参数:', externalParams)
      const existingWindow = await windowReuseManager.checkForExistingWindow(externalParams, 1000)

      if (existingWindow) {
        console.log('✅ 找到可复用的窗口:', existingWindow.windowId)

        // 聚焦到已存在的窗口
        windowReuseManager.requestFocus(existingWindow.windowId)

        // 直接更新窗口参数，强制刷新页面
        console.log('🔄 直接更新窗口参数，强制刷新页面...')
        windowReuseManager.requestUpdateParams(existingWindow.windowId, externalParams)

        console.log('🎯 复用已存在的窗口:', existingWindow.windowId)
        return
      }

      console.log('❌ 没有找到可复用的窗口，创建新窗口')

      // 判断是否为Chrome插件环境
      if (this.isChromeExtension) {
        // 如果是Chrome插件环境，则打开Modal加载AutoParams组件，并传递参数
        this.openAutoParamsModal(externalParams)
      } else {
        // 如果不是Chrome插件环境，则打开新窗口
        this.createNewWindow(externalParams)
      }
    },

    openAutoParamsModal(params) {
      // 直接在当前页面打开AutoParams Modal
      console.log('打开AutoParams Modal，参数:', params)

      // 先提取服务器信息（在设置visible之前）
      this.modalServerId = params.serverid || params.server_id || null
      this.modalServerName = params.server_name || null

      console.log('提取的服务器信息:', {
        modalServerId: this.modalServerId,
        modalServerName: this.modalServerName,
        paramsServerid: params.serverid,
        paramsServer_id: params.server_id,
        paramsServer_name: params.server_name
      })

      // 先设置externalParams
      this.autoParamsExternalParams = params

      // 使用$nextTick确保props值已经更新后再显示组件
      this.$nextTick(() => {
        this.autoParamsDialogVisible = true
      })
    },

    closeAutoParamsDialog() {
      this.autoParamsDialogVisible = false
      this.autoParamsExternalParams = {}
      this.modalServerId = null
      this.modalServerName = null
    },

    createNewWindow(params) {
      // 使用qs库将参数转换为URL查询字符串
      const queryString = qs.stringify(params)
      const url = `/admin/#/auto-params?${queryString}`

      // 计算窗口位置，使其显示在右下角
      const screenWidth = window.screen.availWidth
      const screenHeight = window.screen.availHeight
      const windowWidth = 1000
      const windowHeight = 700
      const left = screenWidth - windowWidth - 20  // 距离右边缘20px
      const top = screenHeight - windowHeight - 20  // 距离下边缘20px

      const newWindow = window.open(url, '_blank', `popup=1,location=no,width=${windowWidth},height=${windowHeight},left=${left},top=${top}`)

      if (newWindow) {
        console.log('创建新窗口:', url)
      }
    },

    // 获取数据类型标签
    getDataTypeLabel(dataType) {
      const labels = {
        'role': '角色',
        'equipment': '装备',
        'pet': '召唤兽'
      }
      return labels[dataType] || '未知'
    },

    // 解析列表数据
    parseListData(responseDataStr) {
      // 解析响应数据 Request.JSONP.request_map.request_数字(xxxx) 中的xxxx
      const match = responseDataStr.match(/Request\.JSONP\.request_map\.request_\d+\((.*)\)/)
      let templateJSONStr = '{}'
      if (match) {
        templateJSONStr = match[1]
      } else {
        templateJSONStr = responseDataStr
      }
      try {
        let templateJSON = {}
        if (typeof templateJSONStr === 'string') {
          templateJSON = JSON.parse(templateJSONStr)
        } else {
          // h5
          templateJSON = templateJSONStr
        }
        return templateJSON
      } catch (error) {
        console.error('解析响应数据失败:', error)
        return {}
      }
    }
  },
  mounted() {
    console.log(this.targetEquipment, 'this.targetEquipment')
  }
}
</script>

<style scoped>
.equips-pets-data-section {
  margin-top: 20px;
  padding: 10px;
  max-height: 500px;
  overflow-y: auto;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.data-item {
  margin-bottom: 16px;
  padding: 12px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.data-item-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.status {
  padding: 2px 6px;
  border-radius: 2px;
  font-weight: bold;
  font-size: 12px;
}

.status.completed {
  background: #52c41a;
  color: white;
}

.status.parsing {
  background: #1890ff;
  color: white;
}

.status.failed {
  background: #ff4d4f;
  color: white;
}

.status.parsing .el-icon-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.result-card {
  height: 100%;
}

.result-card /deep/ .el-card__body {
  padding: 8px;
}

.equip-desc-content {
  font-size: 12px;
  color: #666;
  margin: 4px 0;
}
</style>