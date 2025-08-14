<template>
  <PetInfoPopover v-bind="$attrs" :pet="pet" :equipFaceImg="equipFaceImg" :enhanceInfo="enhanceInfo" style="position: relative;display: block;">
    <template #trigger>
      <el-image :src="imageUrl" fit="cover" :style="imageStyle" referrerpolicy="no-referrer">
        <div slot="error" class="image-slot">
          <i class="el-icon-picture-outline"></i>
        </div>
      </el-image>
    </template>
  </PetInfoPopover>
</template>

<script>
import PetInfoPopover from './PetInfoPopover.vue'
import { commonMixin } from '@/utils/mixins/commonMixin'

export default {
  name: 'PetImage',
  components: { PetInfoPopover },
  mixins: [commonMixin],
  props: {
    size: { type: String, default: 'small' },
    width: { type: String, default: '50px' },
    height: { type: String, default: '50px' },
    cursor: { type: String, default: 'pointer' },
    placement: { type: String, default: 'right' },
    popoverWidth: { type: String, default: '400px' },
    pet: Object,
    enhanceInfo: {
      type: Object,
      default: () => ({})
    },
    equipFaceImg: {
      type: String,
      default: ''
    }
  },
  computed: {
    imageUrl() {
      const petId = this.equipFaceImg
      return this.getImageUrl(`${petId}`)
    },
    imageStyle() {
      return {
        display: 'inline-block',
        width: this.width,
        height: this.height,
        cursor: this.cursor
      }
    },
  },
  mounted() {
    console.log(this.pet)
  }
}
</script>

<style scoped>
.pet-info-content {
  padding: 10px;
  min-width: 320px;
  max-width: 400px;
}

.pet-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.pet-basic {
  margin-left: 12px;
}

.pet-name {
  color: #ffd700;
  font-weight: bold;
  font-size: 16px;
}

.pet-attrs {
  font-size: 13px;
  color: #eee;
  margin-bottom: 8px;
}

.pet-skills,
.pet-texing {
  margin-bottom: 8px;
}
</style>