<template>
  <el-popover :data-equip-sn="equipment.equip_sn" :placement="placement" :width="popoverWidth" trigger="hover"
    :visible-arrow="false" raw-content v-model="visible" popper-class="equip-desc-popper">
    <template #reference>
      <el-image style="display: block;" :style="imageStyle" :src="getImageUrl(equipment.equip_face_img, size)"
        fit="cover" referrerpolicy="no-referrer">
      </el-image>
      <template v-if="searchInCBG">
        <el-cascader :options="server_data" size="mini" filterable v-model="server_data_value" />
        <el-link @click="openCBGSearch" type="danger">藏宝阁</el-link>
      </template>
    </template>
    <div class="equip-desc-content" v-if="visible">
      <el-row type="flex" justify="space-between">
        <el-col v-if="image" style="width: 120px; margin-right: 20px">
          <el-image style="width: 120px; height: 120px" :src="getImageUrl(equipment.equip_face_img, 'big')" fit="cover"
            referrerpolicy="no-referrer">
          </el-image>
        </el-col>
        <el-col>
          <p class="equip_desc_yellow" v-if="equipment.equip_name">{{ equipment.equip_name }}</p>
          <p v-for="(name_desc, index) in equipment.equip_type_desc?.split('#r')" :key="index" style="color: #fff">
            {{ name_desc }}
          </p>
          <div v-html="parseEquipDesc(equipment.large_equip_desc)"></div>
        </el-col>
      </el-row>
    </div>
  </el-popover>
</template>

<script>
import { commonMixin } from '@/utils/mixins/commonMixin'
import str2gbk from 'str2gbk'
import qs from 'qs'
const server_data_list = []
for (let key in window.server_data) {
  let [parent, children] = window.server_data[key]
  const [label, , , , value] = parent
  children = children.map(([value, label]) => ({ value, label }))
  server_data_list.push({
    label, value, children
  })
}
export default {
  name: 'EquipmentImage',
  mixins: [commonMixin],
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
      type: Number,
      default: 450
    },
    extractFeatures: {
      type: Boolean,
      default: false
    },
    searchInCBG: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      visible: false,
      server_data: server_data_list,
      features: {}
    }
  },
  computed: {
    imageStyle() {
      return {
        display: this.searchInCBG ? 'inline-block' : 'block',
        width: this.width,
        height: this.height,
        cursor: this.cursor
      }
    },
    // 从Vuex store获取server_data_valueTODO:::::
    server_data_value: {
      get() {
        return this.$store?.state.server_data_value || {}
      },
      set(value) {
        this.$store.dispatch('setServerDataValue', value)
      }
    }
  },
  watch: {
    // 监听server_data_value变化，同步到Vuex store
    server_data_value: {
      handler(newValue) {
        console.log(newValue, 'newValue')
        if (Array.isArray(newValue) && newValue.length >= 2) {
          this.$store.dispatch('setServerDataValue', newValue)
          const { server_id, areaid, server_name } = this.$store.getters.getCurrentServerData
          this.$emit('onExtractQuery', { ...this.genarateSearchParams(this.features), server_id, areaid, server_name })
        }
      },
      deep: true
    }
  },
  methods: {
    /**
     * GBK编码的URL编码
     * @param {string} str - 要编码的字符串
     * @returns {Promise<string>} - GBK编码的URL编码字符串
     */
    encodeGBK(str) {
      if (!str) return ''

      try {
        const gbkBytes = str2gbk(str)
        // 将字节数组转换为URL编码格式
        return Array.from(gbkBytes).map(b => `%${b.toString(16).toUpperCase().padStart(2, '0')}`).join('')
      } catch (error) {
        console.warn('GBK编码失败，使用UTF-8编码作为降级方案:', error)
        // 降级到UTF-8编码
        return window.encodeURI(str)
      }
    },

    parseEquipDesc(desc) {
      if (!desc) return ''
      if (typeof window.parse_style_info === 'function') {
        return window.parse_style_info(desc, '#Y')
      }
      return desc
    },
    genarateSearchParams({ kindid, ...features }) {
      const searchParams = {}
      if (kindid * 1 === 29) {
        searchParams.level = features.equip_level
        searchParams.speed = features.speed > 0 ? features.speed : undefined
        searchParams.shanghai = features.shanghai > 0 ? features.shanghai : undefined
        searchParams.hp = features.qixue > 0 ? features.qixue : undefined
        searchParams.fangyu = features.fangyu > 0 ? features.fangyu : undefined
        let addon_sum = 0;
        ['fali', 'liliang', 'lingli', 'minjie', 'naili'].forEach(item => {
          searchParams[`addon_${item}`] = this.features[`addon_${item}`] > 0 ? 1 : undefined
          if (item === 'minjie' && this.features[`addon_${item}`] < 0) {
            searchParams.addon_minjie_reduce = this.features[`addon_${item}`] * -1
          } else {
            addon_sum += this.features[`addon_${item}`]
          }
        })
        searchParams.addon_sum = addon_sum > 0 ? addon_sum : undefined
        searchParams.addon_sum_min = searchParams.addon_sum
        searchParams.addon_status = features.addon_status
        if (features.fangyu > 0) {
          searchParams.equip_pos = 1
        } else if (features.speed > 0) {
          searchParams.equip_pos = 2
        } else {
          searchParams.equip_pos = 3
        }
      }
      return searchParams
    },
    async openCBGSearch() {
      let prefix = ''
      console.log(this.features)
      if (this.features.kindid === 29) {
        // 使用Vuex store中的服务器数据
        const serverData = this.$store.getters.getCurrentServerData
        prefix = `https://xyq.cbg.163.com/cgi-bin/recommend.py?callback=Request.JSONP.request_map.request_0&_=${new Date().getTime()}&act=recommd_by_role&server_id=${serverData.server_id}&areaid=${serverData.areaid}&server_name=${serverData.server_name}&page=1&query_order=price%20ASC&view_loc=search_cond&count=15&search_type=search_pet_equip&`
      }
      const query = this.genarateSearchParams(this.features)
      let target_url = prefix + qs.stringify(query)

      console.log(target_url, 'target_url')
      this.$api.spider.startPlaywright({
        headless: false,
        target_url
      })
    }
  },
  mounted() {
    // 初始化时设置默认的server_data_value（如果store中没有的话）
    if (this.searchInCBG && (!this.$store?.state.server_data_value || this.$store?.state.server_data_value.length === 0)  ) {
      this.$store.dispatch('setServerDataValue', [43, 77])
    }

    if (this.extractFeatures) {
      this.$api.equipment.extractFeatures({
        equipment_data: {
          kindid: this.equipment.kindid * 1,
          large_equip_desc: this.equipment.large_equip_desc
        },
        data_type: 'equipment'
      }).then(res => {
        if (res.code === 200 && res.data.features) {
          this.features = res.data.features
          this.$emit('onExtractFeatures', res.data.features)
          const { server_id, areaid, server_name } = this.$store.getters.getCurrentServerData
          this.$emit('onExtractQuery', { ...this.genarateSearchParams(res.data.features), server_id, areaid, server_name })
        }
      })
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
  background-color: #2c3e50 !important;
  padding: 18px !important;
  border: 2px solid #2782a5 !important;
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