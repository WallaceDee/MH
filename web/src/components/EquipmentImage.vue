<template>
  <el-popover :close-delay="0" v-if="equipment" :data-equip-sn="equipment.equip_sn" :placement="placement"
    :width="popoverWidth" trigger="hover" :visible-arrow="false" raw-content v-model="visible"
    popper-class="equip-desc-popper" style="position: relative;display: block;">
    <template #reference>
      <el-image v-if="equipment" style="display: block" :style="imageStyle"
        :src="getImageUrl(equipment.equip_face_img, size)" fit="cover" referrerpolicy="no-referrer">
      </el-image>
      <div v-if="rightLock.length > 0" style="position: absolute; width: 14px; right: 0px; top: 0px;">
        <img v-for="l in rightLock" :key="l" :src="require(`../../public/assets/images/time_lock_${l}.webp`)"
          style="height: 14px; width: 14px; display: block;">
      </div>
      <div v-if="leftLock.length > 0" style="position: absolute; width: 14px; left: 0px; top: 0px;">
        <img v-for="l in leftLock" :key="l" :src="require(`../../public/assets/images/time_lock_${l}.webp`)"
          style="height: 14px; width: 14px;display: block;">
      </div>

    </template>
    <div class="equip-desc-content" v-if="visible">
      <div v-if="lock_type.length > 0" style="position: absolute; width: 14px; right: 12px; top: 12px;">
        <img v-for="l in lock_type" :key="l" :src="require(`../../public/assets/images/time_lock_${l}.webp`)"
          style="height: 14px; width: 14px;display: block;">
      </div>
      <el-row type="flex" justify="space-between">
        <el-col v-if="image" style="width: 120px; margin-right: 20px">
          <el-image style="width: 120px; height: 120px" :src="getImageUrl(equipment.equip_face_img, 'big')" fit="cover"
            referrerpolicy="no-referrer">
          </el-image>
        </el-col>
        <el-col>
          <p class="equip_desc_yellow" v-if="equipment.equip_name">{{ equipment.equip_name }}</p>
          <p v-html="parseEquipDesc(equipment.equip_type_desc.replace(/#R/g, '<br />'), '#n')"></p>
          <p v-html="parseEquipDesc(equipment.large_equip_desc)"></p>
        </el-col>
      </el-row>
    </div>
  </el-popover>
</template>

<script>
import { commonMixin } from '@/utils/mixins/commonMixin'

export default {
  name: 'EquipmentImage',
  mixins: [commonMixin],
  props: {
    image: {
      type: Boolean,
      default: true
    },
    equipment: {
      type: [Object, undefined]
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
      type: Number,
      default: 405
    },
    lock_type: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      visible: false,
      features: {}
    }
  },
  computed: {
    rightLock() {
      return this.lock_type.filter(item => item !== 9 && item !== 'protect' && item !== 'huoyue')
    },
    leftLock() {
      return this.lock_type.filter(item => item === 9 || item === 'protect' || item === 'huoyue')
    },
    imageStyle() {
      return {
        display: 'block',
        width: this.width,
        height: this.height,
        cursor: this.cursor
      }
    },
  },
  methods: {
    parseEquipDesc(desc, default_style = '#Y') {
      if (!desc) return ''
      if (typeof window.parse_style_info === 'function') {
        return window.parse_style_info(desc, default_style)
      }
      return desc
    },
  }
}
</script>

<style scoped>
/* 装备描述样式 */
.equip-desc-content {
  overflow-y: auto;
  font-size: 14px;
  font-family: 宋体, tahoma, arial, hiragino sans gb, sans-serif;
  line-height: 22px;
  color: #ecf0f1;
  padding: 10px;
  border-radius: 4px;
}

:global(.equip-desc-popper) {
  background-color: #2c3e50 !important;
  padding: 18px !important;
  border: 2px solid #2782a5 !important;
}
</style>
