<template>
  <el-button type="success" @click="goToMoreSimilar">
    查看更多相似
  </el-button>
</template>

<script>
import qs from 'qs'
import windowReuseManager from '@/utils/windowReuseManager'

export default {
  name: 'SimilarGetMore',
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
      // 如果没有可复用的窗口，则创建新窗口
      this.createNewWindow(externalParams)
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