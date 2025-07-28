<template>
  <el-button type="primary" @click="goToMoreSimilar">
    查看更多相似装备
  </el-button>
</template>

<script>
import qs from 'qs'

export default {
  name: 'SimilarEquipmentRetry',
  props: {
    message: {
      type: String,
      default: ''
    },
    targetEquipment: {
      type: Object,
      default: () => ({})
    }
  },
  methods: {
    goToMoreSimilar() {
      const { equip_name, large_equip_desc, equip_type_desc, icon, equip_face_img, equip_level, kindid } = this.targetEquipment
      const externalParams = {
        equip_type: 'normal',
        activeTab: 'equip',
        equip_name,
        large_equip_desc,
        equip_type_desc,
        equip_face_img: icon || equip_face_img,
        equip_level,
        kindid
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

      // 使用qs库将参数转换为URL查询字符串
      const queryString = qs.stringify(externalParams)
      const url = `/?${queryString}`

      window.open(url, '_blank')
    }
  }
}
</script>