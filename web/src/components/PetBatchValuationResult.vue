<template>
  <div class="pet-batch-valuation-result">
    <!-- Loading骨架屏 -->
    <div v-if="loading" class="skeleton-container">
      <el-skeleton :rows="12" animated />
    </div>
    <!-- 实际结果 -->
    <template v-else>
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-statistic group-separator="," :precision="2" :value="totalValue / 100" title="估价总值" prefix="¥"
            :value-style="{ fontSize: '28px', fontWeight: 'bold', color: '#67c23a' }">
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic group-separator="," :precision="0" :value="successCount" title="成功估价"
            :value-style="{ fontSize: '28px', fontWeight: 'bold', color: '#67c23a' }">
            <template slot="suffix">
              <span style="color: #909399; font-size: 16px">/ {{ totalCount }}</span>
            </template>
          </el-statistic>
        </el-col>
      </el-row>
      <el-row type="flex" style="flex-wrap: wrap;">
        <el-col :span="8" v-for="(result, index) in results" :key="index" class="result-item"
          :class="{ error: result.error, success: !result.error }">
          <div class="result-header">
            <span class="item-index">{{ petList[index].pet_detail.pet_name || `宠物 ${index + 1}` }}-{{
              petList[index].equip_level
              }}级</span>
            <span v-if="!result.error" class="confidence-badge">
              置信度: {{ (result.confidence * 100).toFixed(1) }}%
            </span>
            <span v-else class="error-badge" :title="result.error">估价失败</span>
          </div>
          <el-row type="flex" align="middle" justify="space-between">
            <el-col style="width: 50px;">
              <PetImage placement="top" :pet="petList[index].pet_detail" size="small"
                :equip_sn="petList[index].equip_sn" :equipFaceImg="petList[index].pet_detail.icon" />
              <SimilarPetModal
                :pet="genPetData(petList[index])"
                :similar-data="similarData" :valuation="result" @show="loadSimilarPets" />
            </el-col>
            <el-col class="price-info" :span="12">
              <el-statistic group-separator="," :precision="2" :value="result.estimated_price_yuan" title="估价"
                prefix="¥" :value-style="{ color: '#f56c6c', fontSize: '18px', fontWeight: 'bold' }">
              </el-statistic>
            </el-col>
          </el-row>

          <!-- 宠物详细信息 -->
          <div class="pet-details" v-if="petList[index]">
            <div class="pet-info">
              <el-tag size="mini" :type="petList[index].is_baobao === '是' ? 'success' : 'danger'">{{
                petList[index].is_baobao === '是' ?'宝宝':'野生'}}</el-tag>
              <el-tag size="mini">{{ petList[index].equip_level }}级</el-tag>
              <el-tag size="mini" type="success">{{ petList[index].growth }}</el-tag>
            </div>
            <div class="pet-skills">
              <span class="skill-label">技能:</span>
              <span class="mini-icon"
                v-html="formatSkills({ petData: { ...petList[index].pet_detail, sp_skill: petList[index].pet_detail.genius } })"></span>
            </div>
            <div class="pet-equips">
              <span class="skill-label">装备:</span>
              <table cellspacing="0" cellpadding="0" class="tb03 size50" style="margin: unset;">
            <tr>
              <!-- {{ petList[index] }} -->
              <td v-for="(eItem, index) in JSON.parse(petList[index].equip_list).splice(0, 3)" :key="index">
                <EquipmentImage v-if="eItem" :placement="'bottom'" :image="false" :equipment="getEquipImageProps(eItem)"
                  size="small" :popoverWidth="300" width="40px" height="40px"/>
                <span v-else>&nbsp;</span>
              </td>
            </tr>
          </table>
            </div>
 
          </div>
        </el-col>
      </el-row>
    </template>
    <!-- 关闭按钮 -->
    <div class="dialog-footer" style="text-align: center; margin-top: 20px;">
      <el-button @click="$emit('close')" type="primary">关闭</el-button>
    </div>
  </div>
</template>

<script>
import PetImage from '@/components/PetImage.vue'
import EquipmentImage from '@/components/EquipmentImage.vue'
import SimilarPetModal from '@/components/SimilarPetModal.vue'
import { petMixin } from '@/utils/mixins/petMixin'
import { equipmentMixin } from '@/utils/mixins/equipmentMixin'
export default {
  name: 'PetBatchValuationResult',
  props: {
    results: {
      type: Array,
      required: true
    },
    petList: {
      type: Array,
      required: true
    },
    totalValue: {
      type: Number,
      default: 0
    },
    valuateParams: {
      type: Object,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      similarData: null
    }
  },
  mixins: [petMixin,equipmentMixin],
  computed: {
    totalCount() {
      return this.results.length
    },
    successCount() {
      return this.results.filter((result) => !result.error).length
    }
  },
  components: {
    PetImage,
    EquipmentImage,
    SimilarPetModal
  },
  methods: {
    genPetData(pet) {
      return { ...pet, petData: pet.pet_detail, equip_face_img: pet.pet_detail.icon }
    },
    // 加载相似宠物
    async loadSimilarPets(pet) {
      this.similarData = null
      await this.loadPetValuation(pet)
    },
    // 统一的宠物估价加载方法
    async loadPetValuation(pet) {
      try {
        // 获取估价信息（包含相似宠物）
        const valuationResponse = await this.$api.pet.getPetValuation({
          pet_data: pet,
          strategy: 'fair_value',
          similarity_threshold: this.valuateParams.similarity_threshold,
          max_anchors: this.valuateParams.max_anchors
        })
        const { data: { anchors:allAnchors } } = await this.$api.pet.findPetAnchors({
          pet_data: pet,
          similarity_threshold: this.valuateParams.similarity_threshold,
          max_anchors: this.valuateParams.max_anchors
        })

        // 处理估价响应
        if (valuationResponse.code === 200) {
          const data = valuationResponse.data
          // 从估价结果中提取相似宠物信息
          if (data.anchors && data.anchors.length > 0) {
            this.similarData = {
              anchor_count: data.anchor_count,
              similarity_threshold: data.similarity_threshold,
              anchors: allAnchors.map((item) => ({ ...item, petData: this.parsePetInfo(item.desc) })),
              statistics: {
                price_range: {
                  min: Math.min(...allAnchors.map((a) => a.price || 0)),
                  max: Math.max(...allAnchors.map((a) => a.price || 0))
                },
                similarity_range: {
                  min: Math.min(...allAnchors.map((a) => a.similarity || 0)),
                  max: Math.max(...allAnchors.map((a) => a.similarity || 0)),
                  avg:
                    allAnchors.reduce((sum, a) => sum + (a.similarity || 0), 0) /
                    allAnchors.length
                }
              }
            }
          } else {
            this.similarData = {
              anchor_count: 0,
              similarity_threshold: data.similarity_threshold || this.valuateParams.similarity_threshold,
              anchors: [],
              statistics: {
                price_range: { min: 0, max: 0 },
                similarity_range: { min: 0, max: 0, avg: 0 }
              },
              message: '未找到符合条件的市场锚点，建议降低相似度阈值',
              canRetry: true,
              pet: pet
            }
          }
        } else if (valuationResponse.code === 400) {
          // 400错误也要显示界面，只是没有锚点数据
          this.similarData = {
            anchor_count: 0,
            similarity_threshold: this.valuateParams.similarity_threshold,
            anchors: [],
            statistics: {
              price_range: { min: 0, max: 0 },
              similarity_range: { min: 0, max: 0, avg: 0 }
            },
            message: valuationResponse.message || '未找到符合条件的市场锚点，建议降低相似度阈值',
            canRetry: true,
            pet: pet
          }
        }

        console.log('估价和相似宠物数据:', valuationResponse.data)
      } catch (error) {
        console.error('加载相似宠物或估价失败:', error)
      }
    }
  }
}
</script>

<style scoped>
.pet-batch-valuation-result {
  width: 860px;
  margin: 0 auto;
}

.result-item {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #e4e7ed;
  background: #fff;
  transition: all 0.3s;
  min-height: 100px;
}

.result-item:hover {
  background-color: #f5f7fa;
}

.result-item.success {
  border-left: 4px solid #67c23a;
}

.result-item.error {
  border-left: 4px solid #f56c6c;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.item-index {
  font-weight: bold;
  color: #303133;
}

.confidence-badge {
  background: #67c23a;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.error-badge {
  background: #f56c6c;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.price-info {
  text-align: right;
}

.pet-details {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
}
.pet-details .size50 td{
width: 40px;
height: 40px;
}
.pet-info {
  margin-bottom: 5px;
  font-size: 12px;
  color: #606266;
}

.pet-info>* {
  margin-right: 5px;
}

.pet-skills {
  font-size: 12px;
  color: #606266;
}

.skill-label {
  font-weight: bold;
  margin-right: 5px;
}

.skill-text {
  color: #409eff;
}

.skeleton-container {
  padding: 20px;
}

/* 滚动条样式 */
.results-list::-webkit-scrollbar {
  width: 6px;
}

.results-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.results-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.results-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

:global(.mini-icon .tb03 td) {
  width: 28px !important;
  height: 28px !important;
}

:global(.mini-icon .tb03 td img) {
  width: 24px !important;
  height: 24px !important;
}
</style>