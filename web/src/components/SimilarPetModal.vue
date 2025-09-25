<template>
  <el-popover :data-equip-sn="pet.equip_sn" :placement="placement" width="860" trigger="click"
    popper-class="similar-pet-popper" v-model="visible" @show="handleShow">
    <template #reference>
      <slot>
        <el-link type="primary" style="font-size: 12px;">查看相似</el-link>
      </slot>
    </template>

    <!-- 相似召唤兽内容 -->
    <div v-if="visible">
      <!-- 加载状态 -->
      <div v-if="valuationLoading" class="loading-info">
        <el-skeleton :rows="12" animated />
      </div>
      <div v-else-if="similarData">
        <div class="similar-header">
          <h4>相似召唤兽 (共{{ similarData.anchor_count }}个) <el-divider direction="vertical" />
            <el-tag type="info" size="mini">相似度阈值: {{ similarData.similarity_threshold }}</el-tag>
            <el-divider direction="vertical" />
            <el-tag type="info" size="mini">最大锚点数: {{ similarData.max_anchors }}</el-tag>
          </h4>
          <!-- 召唤兽估价信息 -->
          <PetValuation :valuation="petValuation" :target-pet="pet" :equip_sn="pet.equip_sn" @refresh="refresh" />
          <div v-if="similarData.statistics" class="stats">
            <span>
              价格范围:
              <span v-html="formatPrice(similarData.statistics.price_range.min)"></span>
              -
              <span v-html="formatPrice(similarData.statistics.price_range.max)"></span>
            </span>
            <span> 平均相似度: {{ similarData.statistics.similarity_range.avg.toFixed(3) }} </span>
          </div>
        </div>

        <!-- 相似召唤兽表格 -->
        <el-empty v-if="!anchorsLoading && !similarData?.anchors?.length" description="暂无数据"></el-empty>
        <SimilarPetTable v-else :anchors="similarData.anchors" v-loading="anchorsLoading" element-loading-text="正在加载相似召唤兽" :target-pet="pet" />
      </div>
    </div>
  </el-popover>
</template>

<script>
import PetValuation from './PetValuation.vue'
import SimilarPetTable from './SimilarPetTable.vue'
import { commonMixin } from '@/utils/mixins/commonMixin'
import { petMixin } from '@/utils/mixins/petMixin'
export default {
  name: 'SimilarPetModal',
  components: {
    PetValuation,
    SimilarPetTable
  },
  mixins: [commonMixin, petMixin],
  props: {
    pet: {
      type: Object,
      required: true
    },
    placement: {
      type: String,
      default: 'left-end'
    },
    similarityThreshold: {
      type: Number,
      default: 0.8
    },
    maxAnchors: {
      type: Number,
      default: 30
    },
  },
  data() {
    return {
      visible: false,
      valuationLoading: false,  // 召唤兽估价接口加载状态
      anchorsLoading: false,    // 相似召唤兽锚点接口加载状态
      error: false,
      similarData: null,
      petValuation: {}
    }
  },
  computed: {
    // 整体加载状态
    loading() {
      return this.valuationLoading || this.anchorsLoading
    }
  },
  methods: {
    async handleShow() {
      if (!this.similarData) {
        await this.loadSimilarPets()
      }
    },

    async refresh() {
      await this.loadSimilarPets()
    },

    // 加载相似召唤兽
    async loadSimilarPets() {
      this.error = false
      this.petValuation = {}
      this.similarData = null

      try {
        await this.loadPetValuation(this.pet, this.similarityThreshold)
      } catch (error) {
        console.error('加载相似召唤兽失败:', error)
        this.error = true
      }
    },

    // 统一的召唤兽估价加载方法
    async loadPetValuation({ petData, ...pet }, similarityThreshold) {
      try {
        // 第一个接口：获取召唤兽估价信息
        this.valuationLoading = true
        const response = await this.$api.pet.getPetValuation({
          pet_data: pet,
          strategy: 'fair_value',
          similarity_threshold: similarityThreshold,
          max_anchors: this.maxAnchors
        })

        const result = response.data
        this.petValuation = result

        // 向父组件发出估价结果更新事件
        this.$emit('valuation-updated', result)

        // 初始化相似召唤兽数据
        this.similarData = {
          anchor_count: result.anchor_count,
          similarity_threshold: result.similarity_threshold || similarityThreshold,
          max_anchors: result.max_anchors || this.maxAnchors,
          anchors: [],
          statistics: {
            price_range: result.anchor_count?{
              min: Math.min(...result.anchors.map((a) => a.price || 0)),
              max: Math.max(...result.anchors.map((a) => a.price || 0)),
              avg: result.anchors.reduce((sum, a) => sum + (a.price || 0), 0) / result.anchors.length
            }:{
              min:0,
              max:0,
              avg:0
            },
            similarity_range: result.anchor_count?{
              min: Math.min(...result.anchors.map((a) => a.similarity || 0)),
              max: Math.max(...result.anchors.map((a) => a.similarity || 0)),
              avg: result.anchors.reduce((sum, a) => sum + (a.similarity || 0), 0) / result.anchors.length
            }:{
              min:0,
              max:0,
              avg:0
            }
          }
        }

        this.valuationLoading = false

        // 处理估价响应，如果有锚点数据则加载详细信息
        if (result?.anchor_count > 0 && result?.anchors?.length > 0) {
          // 第二个接口：获取相似召唤兽锚点详细数据
          this.anchorsLoading = true

          try {
            // 使用估价结果中的equip_sn_list直接获取相似召唤兽列表，避免重复计算
            const anchorsResponse = await this.$api.pet.getPetList({
              page_size: 99,
              equip_sn_list: result.anchors.map(item => item.equip_sn)
            })

            this.anchorsLoading = false
            // 合并相似度和数据
            if (anchorsResponse.code === 200 && anchorsResponse.data?.data) {
              const anchorsData = anchorsResponse.data.data
              const parsedAnchors = anchorsData.map((item, index) => {
                const petData = this.parsePetInfo(item.desc)
                // 添加相似度信息
                item.similarity = result.anchors[index].similarity
                item.features = result.anchors[index].features
                item.petData = petData
                return item
              })

              // 更新相似召唤兽数据
              this.$set(this.similarData, 'anchors', parsedAnchors)
            } else {
              console.warn('未获取到相似召唤兽锚点数据:', anchorsResponse.message)
            }
          } catch (error) {
            console.error('查询相似召唤兽锚点失败:', error)
            // 锚点查询失败不影响估价结果显示
          }
        }

      } catch (error) {
        console.error('召唤兽估价失败:', error)
        this.$notify.error({
          title: '估价请求失败',
          message: '网络请求异常，请稍后重试',
          duration: 3000
        })
        throw error
      } finally {
        // 确保在出现异常时也重置加载状态
        this.valuationLoading = false
        this.anchorsLoading = false
      }
    }
  }
}
</script>

<style scoped>
.similar-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.similar-header h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
}

.similar-header p {
  margin: 0 0 8px 0;
  color: #606266;
  font-size: 14px;
}

.stats {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #909399;
}

.error-info {
  padding: 20px 0;
}

.loading-info {
  padding: 20px;
}
</style>