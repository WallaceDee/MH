<template>
  <EquipmentImage v-if="equipment.large_equip_desc||equipment.equip_desc" :image="false" :popover-width="200" :placement="placement" :equipment="equipment"
    :lock-type="lock_type" />
</template>
<script>
import EquipmentImage from '../EquipmentImage.vue'

export default {
  name: 'ItemPopover',
  components: {
    EquipmentImage
  },
  props: {
    placement: {
      type: String,
      default: 'right-start'
    },
    equipment: {
      type: Object,
      default: () => ({})
    }
  },
  computed: {
    lock_type() {
      return this.equipment?.lock_type || []
    }
  }
}
</script>