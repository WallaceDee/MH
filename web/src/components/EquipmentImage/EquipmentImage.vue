<template>
  <el-popover :close-delay="0" v-if="equipment" :data-equip-sn="equipment.equip_sn" :placement="placement"
    :width="popoverWidth" trigger="hover" :visible-arrow="false" raw-content v-model="visible"
    popper-class="equip-desc-popper" style="position: relative;display: block;">
    <template #reference>
      <div :style="imageStyle" style="position: relative;overflow: hidden;"> <el-image v-if="equipment"
          style="display: block" :style="imageStyle" :src="getImageUrl(equipment.equip_face_img, size)" fit="cover"
          referrerpolicy="no-referrer">
        </el-image>
        <div v-if="isBinding" class="icon-binding">
          专用
        </div>
        <div v-if="rightLock.length > 0" style="position: absolute; width: 14px; right: 0px; top: 0px;">
          <img v-for="l in rightLock" :key="l" :src="require(`../../../public/assets/images/time_lock_${l}.webp`)"
            style="height: 14px; width: 14px; display: block;">
        </div>
        <div v-if="leftLock.length > 0" style="position: absolute; width: 14px; left: 0px; top: 0px;">
          <img v-for="l in leftLock" :key="l" :src="require(`../../../public/assets/images/time_lock_${l}.webp`)"
            style="height: 14px; width: 14px;display: block;">
        </div>
      </div>
    </template>
    <EquipmentDesc :equipment="equipment" :lock-type="lockType" :image="image" v-if="visible" :isBinding="isBinding"/>
  </el-popover>
</template>

<script>
import { commonMixin } from '@/utils/mixins/commonMixin'
import EquipmentDesc from './EquipmentDesc.vue'
export default {
  name: 'EquipmentImage',
  mixins: [commonMixin],
  components: {
    EquipmentDesc
  },
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
    lockType: {
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
    isBinding() {
      // 玩家(\d+)专用
      const bindingPattern = /玩家(\d+)专用/
      const match = this.equipment.large_equip_desc.match(bindingPattern)
      return Boolean(match)
    },
    rightLock() {
      return this.lockType.filter(item => item !== 9 && item !== 'protect' && item !== 'huoyue')
    },
    leftLock() {
      return this.lockType.filter(item => item === 9 || item === 'protect' || item === 'huoyue')
    },
    imageStyle() {
      return {
        display: 'block',
        width: this.width,
        height: this.height,
        cursor: this.cursor
      }
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

.icon-binding {
  position: absolute;
  right: -9px;
  top: -9px;
  color: red;
  border: 3px solid red;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  line-height: 40px;
  font-weight: bold !important;
  font-size: 16px;
  transform: rotate(45deg);
  background-color: rgb(245 108 108 / 20%);
  user-select: none;
}
</style>
