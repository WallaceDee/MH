<template>
  <el-button type="success" @click="goToMoreSimilar">
    查看更多相似
  </el-button>
</template>

<script>
import qs from 'qs'

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
    goToMoreSimilar() {
      let externalParams = {}
      if (this.type === 'equip') {
        console.log(this.targetEquipment, 'this.targetEquipment')
        const { equip_name, large_equip_desc, equip_type_desc, icon, equip_face_img, equip_level, kindid,equip_type,iType } = this.targetEquipment
         externalParams = {
          action: 'similar_equip',
          equip_type: 'normal',
          activeTab: 'equip',
          equip_name,
          large_equip_desc,
          equip_type_desc,
          equip_face_img:  equip_face_img||icon,
          equip_level,
          kindid,
          type:iType||equip_type||undefined,
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
        const { equip_sn, role_grade_limit, equip_level, growth, is_baobao, all_skill,sp_skill, evol_skill_list, texing, lx, equip_list, neidan,equip_face_img } = this.targetEquipment
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
          neidan
        }
        console.log(externalParams, 'externalParams')
      }

      // 使用qs库将参数转换为URL查询字符串
      const queryString = qs.stringify(externalParams)
      const url = `/?${queryString}`

      window.open(url, '_blank')
    }
  },
  mounted() {
    console.log(this.targetEquipment, 'this.targetEquipment')
  }
}
</script>