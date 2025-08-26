<template>
    <div class="equip-desc-content">
        <div v-if="lockType.length > 0"
            style="position: absolute; width: 100px; right: 12px; top: 12px; display: flex;justify-content: flex-end;">
            <img v-for="l in lockType" :key="l" :src="require(`../../../public/assets/images/time_lock_${l}.webp`)"
                style="height: 14px; width: 14px;display: block;">
        </div>
        <el-row type="flex" justify="space-between">
            <el-col v-if="image" style="width: 120px; margin-right: 20px;position: relative;">
                <el-image style="width: 120px; height: 120px" :src="getImageUrl(equipment.equip_face_img, 'big')"
                    fit="cover" referrerpolicy="no-referrer">
                </el-image>
                <div v-if="isBinding" class="icon-binding">
                    专用
                </div>
            </el-col>
            <el-col>
                <p class="equip_desc_yellow" v-if="equipment.equip_name">{{ equipment.equip_name }}</p>
                <p v-html="parseEquipDesc(equipment.equip_type_desc?.replace(/#R/g, '<br />'), '#n')"></p>
                <p v-html="parseEquipDesc(equipment.large_equip_desc)"></p>
            </el-col>
        </el-row>
    </div>
</template>
<script>
import { commonMixin } from '@/utils/mixins/commonMixin'

export default {
    name: 'EquipmentDesc',
    mixins: [commonMixin],
    props: {
        equipment: {
            type: Object,
            required: true
        },
        image: {
            type: Boolean,
            default: true
        },
        lockType: {
            type: Array,
            default: () => []
        },
        isBinding: {
            type: Boolean,
            default: false
        }
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