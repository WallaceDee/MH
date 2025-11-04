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
    <el-dialog 
      :visible.sync="autoParamsDialogVisible" 
      width="720px" 
      :close-on-click-modal="false"
      :close-on-press-escape="false" 
      custom-class="auto-params-dialog" 
      append-to-body
      @click.native.stop 
      @mousedown.native.stop>
        <AutoParams v-if="autoParamsDialogVisible" :external-params="autoParamsExternalParams" :log="false"
          :server-id="modalServerId" :server-name="modalServerName"
          @close="closeAutoParamsDialog" />
    </el-dialog>
  </span>
</template>

<script>
import qs from 'qs'
import windowReuseManager from '@/utils/windowReuseManager'
import AutoParams from '@/components/AutoParams.vue'

export default {
  name: 'SimilarGetMore',
  components: {
    AutoParams
  },
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
        console.log(externalParams, 'externalParams')
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
      const isChromeExtension =true|| typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id

      if (isChromeExtension) {
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
    }
  },
  mounted() {
    console.log(this.targetEquipment, 'this.targetEquipment')
  }
}
</script>