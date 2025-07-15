<template>
  <el-popover :data-equip-sn="equipment.equip_sn" :placement="placement" :width="popoverWidth" trigger="hover"
    :visible-arrow="false" :content="parseEquipDesc(equipment.large_equip_desc)" raw-content
    popper-class="equip-desc-popper">
    <template #reference>
      <el-image :style="imageStyle" :src="getImageUrl(equipment.equip_face_img, size)" fit="cover"
        referrerpolicy="no-referrer">
      </el-image>
    </template>
    <div class="equip-desc-content">
      <el-row type="flex" justify="space-between">
        <el-col v-if="image" style="width: 120px; margin-right: 20px">
          <el-image style="width: 120px; height: 120px" :src="getImageUrl(equipment.equip_face_img, 'big')" fit="cover"
            referrerpolicy="no-referrer">
          </el-image>
        </el-col>
        <el-col>
          <p class="equip_desc_yellow" v-if="equipment.equip_name">{{ equipment.equip_name }}</p>
          <p v-for="(name_desc, index) in equipment.equip_type_desc.split('#r')" :key="index" style="color: #fff">
            {{ name_desc }}
          </p>
          <div v-html="parseEquipDesc(equipment.large_equip_desc)"></div>
        </el-col>
      </el-row>
    </div>
  </el-popover>
</template>

<script>
export default {
  name: 'EquipmentImage',
  props: {
    image: {
      type: Boolean,
      default: true
    },
    equipment: {
      type: Object,
      required: true
    },
    size: {
      type: String,
      default: 'small'
    },
    width: {
      type: String,
      default: '50px'
    },
    height: {
      type: String,
      default: '50px'
    },
    cursor: {
      type: String,
      default: 'pointer'
    },
    placement: {
      type: String,
      default: 'right'
    },
    popoverWidth: {
      type: String,
      default: '450px'
    }
  },
  computed: {
    imageStyle() {
      return {
        display: 'block',
        width: this.width,
        height: this.height,
        cursor: this.cursor
      }
    }
  },
  methods: {
    getImageUrl(equip_face_img, size = 'small') {
      // 如果已经是全路径（以http或https开头），直接返回
      if (equip_face_img && (equip_face_img.startsWith('http://') || equip_face_img.startsWith('https://'))) {
        return equip_face_img
      }
      // 否则拼接路径
      return `https://cbg-xyq.res.netease.com/images/${size}/${equip_face_img}`
    },
    parseEquipDesc(desc) {
      if (!desc) return ''
      if (typeof window.parse_style_info === 'function') {
        return window.parse_style_info(desc, '#Y')
      }
      return desc
    }
  }
}
</script>

<style scoped>
/* 装备描述样式 */
:deep(.equip-desc-content) {
  overflow-y: auto;
  line-height: 1.6;
  font-size: 14px;
  color: #ecf0f1;
  padding: 10px;
  border-radius: 4px;
}

:global(.equip-desc-popper) {
  background-color: #2c3e50;
  padding: 18px;
  border: 2px solid #2782a5;
}

:deep(.equip_desc_blink) {
  animation: blink 1s infinite;
}

:deep(.equip_desc_underline) {
  text-decoration: underline;
}

@keyframes blink {

  0%,
  50% {
    opacity: 1;
  }

  51%,
  100% {
    opacity: 0.3;
  }
}
</style>