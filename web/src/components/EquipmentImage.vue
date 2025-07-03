<template>
  <el-popover
    :data-equip-sn="equipment.equip_sn"
    placement="right"
    :width="450"
    trigger="hover"
    :visible-arrow="false"
    :content="parseEquipDesc(equipment.large_equip_desc)"
    raw-content
    popper-class="equip-desc-popper"
  >
    <template #reference>
      <el-image
        :style="imageStyle"
        :src="getImageUrl(equipment.equip_face_img, size)"
        fit="cover"
        referrerpolicy="no-referrer"
      >
      </el-image>
    </template>
    <div class="equip-desc-content">
      <el-row type="flex" justify="space-between">
        <el-col style="width: 120px; margin-right: 20px">
          <el-image
            style="width: 120px; height: 120px"
            :src="getImageUrl(equipment.equip_face_img, 'big')"
            fit="cover"
            referrerpolicy="no-referrer"
          >
          </el-image>
        </el-col>
        <el-col>
          <p class="equip_desc_yellow">{{ equipment.equip_name }}</p>
          <p
            v-for="(name_desc, index) in equipment.equip_type_desc.split('#r')"
            :key="index"
            style="color: #fff"
          >
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
    }
  },
  computed: {
    imageStyle() {
      return {
        width: this.width,
        height: this.height,
        cursor: this.cursor
      }
    }
  },
  methods: {
    getImageUrl(equip_face_img, size = 'small') {
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

/* 装备描述颜色样式 */
:deep(.equip_desc_red) {
  color: #e74c3c;
}

:deep(.equip_desc_green) {
  color: #2ecc71;
}

:deep(.equip_desc_blue) {
  color: #3498db;
}

:deep(.equip_desc_black) {
  color: #34495e;
}

:deep(.equip_desc_yellow) {
  color: #f1c40f;
}

:deep(.equip_desc_white) {
  color: #ecf0f1;
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