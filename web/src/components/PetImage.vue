<template>
  <div class="pet-image-container">
    <el-image 
      :src="imageUrl" 
      :alt="petName"
      fit="cover"
      style="width: 50px; height: 50px; cursor: pointer;"
      @click="showPetDetail"
      referrerpolicy="no-referrer">
      <div slot="error" class="image-slot">
        <i class="el-icon-picture-outline"></i>
      </div>
    </el-image>
  </div>
</template>

<script>
export default {
  name: 'PetImage',
  props: {
    pet: {
      type: Object,
      required: true
    }
  },
  computed: {
    imageUrl() {
      // 根据召唤兽ID获取图片URL
      const petId = this.pet.equip_face_img || 'default'
      return this.getImageUrl(`${petId}`)
    },
    petName() {
      return this.pet.pet_name || this.pet.name || '召唤兽'
    }
  },
  methods: {
    getImageUrl(imageName, size = 'small') {
      return `https://cbg-xyq.res.netease.com/images/${size}/${imageName}`
    },
    showPetDetail() {
      // 显示召唤兽详细信息
      this.$emit('show-detail', this.pet)
    }
  }
}
</script>

<style scoped>
.pet-image-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  font-size: 14px;
}
</style> 