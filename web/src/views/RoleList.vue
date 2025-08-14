<template>
  <div class="role-list">
    <div class="filter-bar">
      <el-collapse v-model="activeCollapse">
        <el-collapse-item title="搜索条件" name="1">
          <el-form :model="searchForm" class="search-form">
            <el-form-item label="选择月份">
              <el-date-picker v-model="searchForm.selectedDate" :clearable="false" type="month" placeholder="选择月份"
                format="yyyy-MM" value-format="yyyy-MM" @change="handleDateChange" />
            </el-form-item>
            <el-form-item label="人物等级">
              <el-input-number :controls="false" v-model="searchForm.level_min" :min="0" :max="175"
                style="width: 60px" />
              <span class="mx-2">-</span>
              <el-input-number :controls="false" v-model="searchForm.level_max" :min="0" :max="175"
                style="width: 60px" />
              <div class="level-quick-select">
                <el-button v-for="level in [89, 109, 129, 155, 159, 175]" :key="level"
                  @click="handleQuickLevelSelect(level)">
                  {{ level }}级
                </el-button>
              </div>
            </el-form-item>
            <el-form-item label="师门技能">
              <el-select v-model="searchForm.school_skill_num" placeholder="技能数量" style="width: 80px">
                <el-option label="不限" value="" />
                <el-option v-for="n in 7" :key="n" :label="n" :value="n" />
              </el-select>
              <span class="mx-2">个技能等级≥</span>
              <el-input-number :controls="false" v-model="searchForm.school_skill_level" :min="0" :max="180"
                style="width: 60px" />
            </el-form-item>
            <el-form-item label="角色修炼">
              <div class="cultivation-group">
                <el-row>
                  <el-col :span="6">
                    <span>攻击：</span>
                    <el-input-number placeholder="攻击" :controls="false" v-model="searchForm.expt_gongji" :min="0"
                      :max="25" style="width: 60px" />/<el-input-number placeholder="上限" :controls="false"
                      v-model="searchForm.max_expt_gongji" :min="0" :max="25" style="width: 60px" />
                  </el-col>
                  <el-col :span="6">
                    <span>防御：</span>
                    <el-input-number placeholder="防御" :controls="false" v-model="searchForm.expt_fangyu" :min="0"
                      :max="25" style="width: 60px" />/<el-input-number placeholder="上限" :controls="false"
                      v-model="searchForm.max_expt_fangyu" :min="0" :max="25" style="width: 60px" />
                  </el-col>
                  <el-col :span="6">
                    <span>法术：</span>
                    <el-input-number placeholder="法术" :controls="false" v-model="searchForm.expt_fashu" :min="0"
                      :max="25" style="width: 60px" />/<el-input-number placeholder="上限" :controls="false"
                      v-model="searchForm.max_expt_fashu" :min="0" :max="25" style="width: 60px" /></el-col>
                  <el-col :span="6">
                    <span>抗法：</span>
                    <el-input-number placeholder="抗法" :controls="false" v-model="searchForm.expt_kangfa" :min="0"
                      :max="25" style="width: 60px" />/<el-input-number placeholder="上限" :controls="false"
                      v-model="searchForm.max_expt_kangfa" :min="0" :max="25" style="width: 60px" />
                  </el-col>

                </el-row>
                <el-row>
                  <el-col :span="6">
                    <span>猎术≥</span>
                    <el-input-number :controls="false" v-model="searchForm.expt_lieshu" :min="0" :max="25"
                      style="width: 60px" /> <span class="mx-2 text-gray">（不计入修炼总和）</span>
                  </el-col>
                  <el-col :span="6">
                    <span>总和≥</span>
                    <el-input-number :controls="false" v-model="searchForm.expt_total" :min="0" :max="100"
                      style="width: 60px" />
                  </el-col>
                </el-row>
              </div>
            </el-form-item>
            <el-form-item label="召唤兽修炼">
              <div class="cultivation-group">
                <el-row>
                  <el-col :span="6">
                    <span>攻击控制≥</span>
                    <el-input-number :controls="false" v-model="searchForm.bb_expt_gongji" :min="0" :max="25"
                      style="width: 60px" />
                  </el-col>
                  <el-col :span="6">
                    <span class="mx-2">防御控制≥</span>
                    <el-input-number :controls="false" v-model="searchForm.bb_expt_fangyu" :min="0" :max="25"
                      style="width: 60px" />
                  </el-col>
                  <el-col :span="6">
                    <span class="mx-2">法术控制≥</span>
                    <el-input-number :controls="false" v-model="searchForm.bb_expt_fashu" :min="0" :max="25"
                      style="width: 60px" />
                  </el-col>
                  <el-col :span="6">
                    <span class="mx-2">抗法控制≥</span>
                    <el-input-number :controls="false" v-model="searchForm.bb_expt_kangfa" :min="0" :max="25"
                      style="width: 60px" />
                  </el-col>

                </el-row>

                <el-row>
                  <el-col :span="6"> <span>育兽术≥</span>
                    <el-input-number :controls="false" v-model="searchForm.skill_drive_pet" :min="0" :max="25"
                      style="width: 60px" />
                    <span class="mx-2 text-gray">（不计入宠修总和）</span></el-col>
                  <el-col :span="6">
                    <span class="mx-2">宠修总和≥</span>
                    <el-input-number :controls="false" v-model="searchForm.bb_expt_total" :min="0" :max="100"
                      style="width: 60px" />
                  </el-col>
                </el-row>
              </div>
            </el-form-item>
            <el-form-item label="生活技能">
              <div class="cultivation-group">
                <el-row>
                  <el-col :span="4">
                    <span>强身术≥</span>
                    <el-input v-model.number="searchForm.skill_qiang_shen" style="width: 60px" clearable />
                  </el-col>
                  <el-col :span="4">
                    <span>强壮≥</span>
                    <el-input v-model.number="searchForm.skill_qiang_zhuang" style="width: 60px" clearable />
                  </el-col>
                  <el-col :span="4">
                    <span>神速≥</span>
                    <el-input v-model.number="searchForm.skill_shensu" style="width: 60px" clearable />
                  </el-col>
                  <el-col :span="4">
                    <span>冥想≥</span>
                    <el-input v-model.number="searchForm.skill_ming_xiang" style="width: 60px" clearable />
                  </el-col>
                  <el-col :span="4">
                    <span>暗器技巧≥</span>
                    <el-input v-model.number="searchForm.skill_anqi" style="width: 60px" clearable />
                  </el-col>
                  <el-col :span="4">
                    <span>打造技巧≥</span>
                    <el-input v-model.number="searchForm.skill_dazao" style="width: 60px" clearable />
                  </el-col>
                </el-row>
                <el-row>
                  <el-col :span="4">
                    <span>裁缝技巧≥</span>
                    <el-input v-model.number="searchForm.skill_caifeng" style="width: 60px" clearable />
                  </el-col>
                  <el-col :span="4">
                    <span>巧匠之术≥</span>
                    <el-input v-model.number="searchForm.skill_qiaojiang" style="width: 60px" clearable />
                  </el-col>
                  <el-col :span="4">
                    <span>炼金术≥</span>
                    <el-input v-model.number="searchForm.skill_lianjin" style="width: 60px" clearable />
                  </el-col>
                  <el-col :span="4">
                    <span>养生之道≥</span>
                    <el-input v-model.number="searchForm.skill_yangsheng" style="width: 60px" clearable />
                  </el-col>
                  <el-col :span="4">
                    <span>烹饪技巧≥</span>
                    <el-input v-model.number="searchForm.skill_pengren" style="width: 60px" clearable />
                  </el-col>
                  <el-col :span="4">
                    <span>中药医理≥</span>
                    <el-input v-model.number="searchForm.skill_zhongyao" style="width: 60px" clearable />
                  </el-col>
                </el-row>
                <el-row>
                  <el-col :span="4">
                    <span>灵石技巧≥</span>
                    <el-input v-model.number="searchForm.skill_lingshi" style="width: 60px" clearable />
                  </el-col>
                  <el-col :span="4">
                    <span>健身术≥</span>
                    <el-input v-model.number="searchForm.skill_jianshen" style="width: 60px" clearable />
                  </el-col>
                  <el-col :span="4">
                    <span>逃离技巧≥</span>
                    <el-input v-model.number="searchForm.skill_taoli" style="width: 60px" clearable />
                  </el-col>
                  <el-col :span="4">
                    <span>追捕技巧≥</span>
                    <el-input v-model.number="searchForm.skill_zhuibu" style="width: 60px" clearable />
                  </el-col>
                  <el-col :span="4">
                    <span>熔炼技巧≥</span>
                    <el-input v-model.number="searchForm.skill_ronglian" style="width: 60px" clearable />
                  </el-col>
                  <el-col :span="4">
                    <span>淬灵之术≥</span>
                    <el-input v-model.number="searchForm.skill_cuiling" style="width: 60px" clearable />
                  </el-col>
                </el-row>
                <el-row>
                  <el-col :span="4">
                    <span>风之感应≥</span>
                    <el-input v-model.number="searchForm.skill_wind_sense" style="width: 60px" clearable />
                  </el-col>
                  <el-col :span="4">
                    <span>雨之感应≥</span>
                    <el-input v-model.number="searchForm.skill_rain_sense" style="width: 60px" clearable />
                  </el-col>
                  <el-col :span="4">
                    <span>雪之感应≥</span>
                    <el-input v-model.number="searchForm.skill_snow_sense" style="width: 60px" clearable />
                  </el-col>
                </el-row>
              </div>
            </el-form-item>
            <el-form-item label="其他">
              <div class="cultivation-group">
                <el-row>
                  <el-col :span="4">
                    <span>物品数量≤</span>
                    <el-input v-model.number="searchForm.equip_num" style="width: 60px" clearable />
                  </el-col>
                  <el-col :span="10">
                    <span>宠物 <el-input placeholder="等级大于" v-model.number="searchForm.pet_num_level" style="width: 100px"
                        clearable />的数量≤</span>
                    <el-input placeholder="数量" v-model.number="searchForm.pet_num" style="width: 80px" clearable />
                  </el-col>
                </el-row>
              </div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSearch">搜索</el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>
        </el-collapse-item>
      </el-collapse>
    </div>

    <el-table v-loading="loading" :data="RoleApi" style="width: 100%;border: 1px solid #9ea0bf;" stripe @sort-change="handleSortChange">
      <!-- 基本信息 -->
      <el-table-column width="100" align="center">
        <template slot-scope="scope">
          <RoleImage :other_info="scope.row.other_info" :roleInfo="scope.row.roleInfo" />
          <el-link :href="getCBGLinkByType(scope.row.eid, 'role')" type="danger" target="_blank"
            style="white-space: nowrap;text-overflow: ellipsis;overflow: hidden;display: block;font-size: 12px;"> {{
              scope.row.role_name || scope.row.seller_nickname }}</el-link>
        </template>
      </el-table-column>
      <el-table-column label="等级/门派/飞升" width="160" align="center">
        <template slot-scope="scope">
          <span class="vertical-middle">
            <i class="icon-chai" v-if="scope.row.is_split_independent_role === 1"></i>
            <i class="icon-zheng" v-if="scope.row.is_split_main_role === 1"></i>
            {{ get_school_name(scope.row.school) }}
          </span>
          <div class="js-level cGray">{{ scope.row.level }}级/{{
            scope.row.sum_exp
          }}亿</div>
          {{ scope.row.fly_status }}
        </template>
      </el-table-column>
      <el-table-column prop="highlight" label="亮点" width="100" align="center" sortable="custom">>
        <template slot-scope="scope">
          <span v-html="gen_highlight(scope.row.highlight)"></span>
        </template>
      </el-table-column>
      <el-table-column prop="dynamic_tags" label="动态" width="100" align="center" sortable="custom">
        <template slot-scope="scope">
          <span v-html="gen_dynamic_tags(scope.row.dynamic_tags)"></span>
        </template>
      </el-table-column>
      <el-table-column prop="price" label="价格 (元)" width="140" sortable="custom" align="center">
        <template #default="scope">
          {{ scope.row.server_name }}
          <div v-html="formatFullPrice(scope.row)"></div>
        </template>
      </el-table-column>
      <el-table-column prop="collect_num" label="收藏" width="60" align="center">
      </el-table-column>
      <el-table-column label="装备估价" width="120" align="center">
        <template #default="scope">
          <el-link v-if="get_equip_num(scope.row.roleInfo) > 0" @click="handleEquipPrice(scope.row.roleInfo)"
            type="primary" target="_blank">
            <el-statistic group-separator="," :precision="2" :value="0"
              :title="`⚔️ ${get_equip_num(scope.row.roleInfo)}件`" prefix="￥"
              :value-style="{ fontSize: '14px' }"></el-statistic>
          </el-link>
        </template>
      </el-table-column>
      <el-table-column label="召唤兽估价" width="120" align="center">
        <template #default="scope">
          <el-link v-if="get_pet_num(scope.row.roleInfo) > 0" @click="handlSummonePrice(scope.row)" type="primary"
            target="_blank">
            <el-statistic group-separator="," :precision="2" :value="0"
              :title="`🐲 ${get_pet_num(scope.row.roleInfo)}只`" prefix="￥"
              :value-style="{ fontSize: '14px' }"></el-statistic>
          </el-link>
        </template>
      </el-table-column>
      <!-- 修炼信息 -->
      <el-table-column label="修炼/控制力" width="300" align="center">
        <template slot-scope="scope">
          <span class="ml-10">攻:{{ scope.row.expt_ski1 }}/{{ scope.row.max_expt1 }}</span>
          <span class="ml-10">防:{{ scope.row.expt_ski2 }}/{{ scope.row.max_expt2 }}</span>
          <span class="ml-10">法:{{ scope.row.expt_ski3 }}/{{ scope.row.max_expt3 }}</span>
          <span class="ml-10">抗:{{ scope.row.expt_ski4 }}/{{ scope.row.max_expt4 }}</span>
          <span class="ml-10">猎:{{ scope.row.expt_ski5 }}
            <div>
              <span class="ml-10">攻:{{ scope.row.beast_ski1 }}</span>
              <span class="ml-10">防:{{ scope.row.beast_ski2 }}</span>
              <span class="ml-10">法:{{ scope.row.beast_ski3 }}</span>
              <span class="ml-10">抗:{{ scope.row.beast_ski4 }}</span>
            </div>
          </span>
        </template>
      </el-table-column>
      <!-- 时间信息 -->
      <el-table-column prop="update_time" label="更新时间" width="200" />
      <el-table-column prop="create_time" label="创建时间" width="200" />
      <el-table-column prop="server" label="操作" width="150">
        <template slot-scope="scope">
          <el-link href="javascript:void(0)" type="danger" @click.native="handleDelete(scope.row)">删除</el-link>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container">
      <el-pagination :current-page.sync="currentPage" :page-size.sync="pageSize" :total="total"
        :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next" @size-change="handleSizeChange"
        @current-change="handleCurrentChange" />
    </div>

    <!-- 装备估价结果对话框 -->
    <el-dialog title="装备估价结果" :visible.sync="valuationDialogVisible" width="760px" :close-on-click-modal="false"
      :close-on-press-escape="false" custom-class="batch-valuation-dialog">
      <BatchValuationResult :results="valuationResults" :total-value="valuationTotalValue"
        :equipment-list="valuationEquipmentList" :valuate-params="batchValuateParams" :loading="valuationLoading"
        @close="closeValuationDialog" />
    </el-dialog>

    <!-- 宠物估价结果对话框 -->
    <el-dialog title="宠物估价结果" :visible.sync="petValuationDialogVisible" width="900px" :close-on-click-modal="false"
      :close-on-press-escape="false" custom-class="batch-valuation-dialog">
      <PetBatchValuationResult :results="petValuationResults" :total-value="petValuationTotalValue"
        :pet-list="petValuationList" :valuate-params="batchValuateParams" :loading="petValuationLoading"
        @close="closePetValuationDialog" />
    </el-dialog>
  </div>
</template>

<script>
import dayjs from 'dayjs'
import BatchValuationResult from '@/components/BatchValuationResult.vue'
import PetBatchValuationResult from '@/components/PetBatchValuationResult.vue'
import RoleImage from '@/components/RoleInfo/RoleImage.vue'
import { commonMixin } from '@/utils/mixins/commonMixin'
export default {
  name: 'RoleApi',
  mixins: [commonMixin],
  components: {
    RoleImage,
    BatchValuationResult,
    PetBatchValuationResult
  },
  data() {
    return {
      valuationLoading: false,
      batchValuateParams: {
        similarity_threshold: 0.8,
        max_anchors: 30
      },
      valuationResults: [],
      valuationTotalValue: 0,
      valuationEquipmentList: [],
      valuationDialogVisible: false,
      // 宠物估价相关
      petValuationResults: [],
      petValuationTotalValue: 0,
      petValuationList: [],
      petValuationDialogVisible: false,
      petValuationLoading: false,
      loading: false,
      RoleApi: [],
      currentPage: 1,
      pageSize: 20,
      total: 0,
      searchForm: {
        selectedDate: dayjs().format('YYYY-MM'),
        level_min: undefined,
        level_max: undefined,
        school_skill_num: '',
        school_skill_level: undefined,
        // 角色修炼
        expt_gongji: undefined,
        expt_fangyu: undefined,
        expt_fashu: undefined,
        expt_kangfa: undefined,
        expt_total: undefined,
        max_expt_gongji: undefined,
        max_expt_fangyu: undefined,
        max_expt_fashu: undefined,
        max_expt_kangfa: undefined,
        expt_lieshu: undefined,
        // 召唤兽修炼
        bb_expt_gongji: undefined,
        bb_expt_fangyu: undefined,
        bb_expt_fashu: undefined,
        bb_expt_kangfa: undefined,
        bb_expt_total: undefined,
        skill_drive_pet: undefined,
        skill_qiang_shen: undefined,
        skill_qiang_zhuang: undefined,
        skill_shensu: undefined,
        skill_ming_xiang: undefined,
        skill_anqi: undefined,
        skill_dazao: undefined,
        skill_caifeng: undefined,
        skill_qiaojiang: undefined,
        skill_lianjin: undefined,
        skill_yangsheng: undefined,
        skill_pengren: undefined,
        skill_zhongyao: undefined,
        skill_lingshi: undefined,
        skill_jianshen: undefined,
        skill_taoli: undefined,
        skill_zhuibu: undefined,
        skill_ronglian: undefined,
        skill_cuiling: undefined,
        skill_wind_sense: undefined,
        skill_rain_sense: undefined,
        skill_snow_sense: undefined,
        equip_num: undefined,
        pet_num: undefined,
        pet_num_level: undefined
      },
      activeCollapse: [],
      sortState: {
        price: null,
        level: null,
        create_time: null
      }
    }
  },

  mounted() {
    this.fetchData()
  },

  methods: {
    // 关闭装备估价结果对话框
    closeValuationDialog() {
      this.valuationDialogVisible = false
      this.valuationResults = []
      this.valuationTotalValue = 0
      this.valuationEquipmentList = []
      this.valuationLoading = false
      this.valuationDialogTitle = ''
    },
    // 关闭宠物估价结果对话框
    closePetValuationDialog() {
      this.petValuationDialogVisible = false
      this.petValuationResults = []
      this.petValuationTotalValue = 0
      this.petValuationList = []
      this.petValuationLoading = false
    },
    async handlSummonePrice(summone) {
      const pet_list_desc = [...summone.roleInfo.pet_info, ...summone.roleInfo.split_pets]
      let pet_list = JSON.parse(summone.all_summon_json)
      if (!pet_list || pet_list.length === 0) {
        this.$message.warning('没有可估价的宠物')
        return
      }
      pet_list = pet_list.map((item) => {
        //TODO:等级
        const role_grade_limit = window.CBG_GAME_CONFIG.pet_equip_type_to_grade_mapping[item.iType]
        const all_skill = []
        for (var typeid in item.all_skills) {
          all_skill.push('' + typeid)
        }
        // 根据JavaScript逻辑计算evol_skill_list
        const evol_skill_list = this.calculateEvolSkillList(item)
        const texing = JSON.stringify(item.jinjie?.core)
        const lx = item.jinjie?.lx || 0
        const equip_list = []
        for (var i = 0; i < 3; i++) {
          var equip = item['summon_equip' + (i + 1)]
          if (equip) {
            equip_list.push({
              type: equip.iType,
              desc: equip.cDesc,
            })
          } else {
            equip_list.push(null)
          }
        }
        const neidan = []
        if (item.summon_core != undefined) {
          for (var p in item.summon_core) {
            var p_core = item.summon_core[p]
            neidan.push({
              name: window.CBG_GAME_CONFIG.pet_neidans[p] || '',
              level: p_core[0],
              isNeiDan: true
            })
          }
        }
        const pet_detail = pet_list_desc.find(pet => pet.equip_sn === item.equip_sn)
        //召唤兽特征提取必传参数
        return {
          pet_detail,
          equip_sn: item.equip_sn,
          role_grade_limit,
          equip_level: item.iGrade,
          growth: item.grow / 1000,
          is_baobao: item.iBaobao == 1 ? '是' : '否',
          all_skill: all_skill.join('|'),
          evol_skill_list,
          texing,
          lx,
          equip_list: JSON.stringify(equip_list),
          neidan: JSON.stringify(neidan),
        }
      })
      try {
        // 先显示弹窗和骨架屏
        this.petValuationDialogVisible = true
        this.petValuationLoading = true
        this.petValuationResults = []
        this.petValuationTotalValue = 0
        this.petValuationList = pet_list

        // 调用批量宠物估价API
        const response = await this.$api.pet.batchPetValuation({
          pet_list: pet_list.map(({ pet_detail, ...item }) => {
            console.log(pet_detail)
            return item
          }),
          strategy: 'fair_value',
          similarity_threshold: this.batchValuateParams.similarity_threshold,
          max_anchors: this.batchValuateParams.max_anchors
        })

        if (response.code === 200) {
          const data = response.data
          const results = data.results || []
          const totalValue = results.reduce((sum, result) => {
            return sum + (result.estimated_price || 0)
          }, 0)

          // 更新弹窗内容，显示实际数据
          this.petValuationResults = results
          this.petValuationTotalValue = totalValue
          this.petValuationLoading = false
        } else {
          this.$notify.error({
            title: '错误',
            message: response.message || '宠物估价失败'
          })
          this.closePetValuationDialog()
        }
      } catch (error) {
        console.error('宠物估价失败:', error)
        this.$notify.error({
          title: '错误',
          message: '宠物估价失败'
        })
        this.closePetValuationDialog()
      } finally {
        this.petValuationLoading = false
      }
    },
    calculateEvolSkillList(pet) {
      const evol_skill_list = []

      if (!pet.EvolSkill || !window.CBG_GAME_CONFIG.pet_skill_high_to_other_level_mapping) {
        return evol_skill_list
      }

      // 解析进化技能ID
      const cifu = pet.EvolSkill.split('|').map(Number)
      const cifuObj = {}
      cifu.forEach(function (number) {
        cifuObj[number] = 1
      })

      const evol_skills = cifuObj
      if (!evol_skills) {
        return evol_skill_list
      }

      const evol_skill_str = []
      for (const typeid in evol_skills) {
        evol_skill_str.push('' + typeid)
      }

      for (let i = 0, max = evol_skill_str.length; i < max; i++) {
        const typeid = evol_skill_str[i]
        const evol_skill_hash = window.CBG_GAME_CONFIG.pet_skill_high_to_other_level_mapping[typeid]

        if (!evol_skill_hash) {
          continue
        }

        const evol_skill_item = {
          skill_type: typeid,
          level: evol_skills[typeid],
          evol_type: typeid
        }

        if (pet.all_skills) {
          const isHighSkill = pet.all_skills[String(evol_skill_hash.high_skill)]
          const isLowSkill = pet.all_skills[String(evol_skill_hash.low_skill)]

          if (isHighSkill || isLowSkill) {
            evol_skill_item.hlightLight = true
            if (!isHighSkill) {
              evol_skill_item.evol_type = evol_skill_hash.low_skill
            }
          } else {
            evol_skill_item.hlightLight = false
          }
        }
        evol_skill_list.push(evol_skill_item)
      }

      return evol_skill_list
    },
    get_pet_num(roleInfo) {
      return roleInfo.pet_info.length + roleInfo.split_pets.length
    },
    get_equip_num(roleInfo) {
      return roleInfo.using_equips.length + roleInfo.not_using_equips.length + roleInfo.split_equips.length
    },
    async handleEquipPrice({ using_equips, not_using_equips, split_equips }) {
      const equip_list = [...using_equips, ...not_using_equips, ...split_equips].map((item) => ({ ...item, iType: item.type, cDesc: item.desc }))
      try {
        // 先显示弹窗和骨架屏
        this.valuationDialogVisible = true
        this.valuationLoading = true
        this.valuationResults = []
        this.valuationTotalValue = 0
        this.valuationEquipmentList = equip_list
        console.log(equip_list)
        // 调用批量估价API
        const response = await this.$api.equipment.batchEquipmentValuation({
          equipment_list: equip_list,
          strategy: 'fair_value',
          similarity_threshold: this.batchValuateParams.similarity_threshold,
          max_anchors: this.batchValuateParams.max_anchors
        })

        if (response.code === 200) {
          const data = response.data
          const results = data.results || []
          const totalValue = results.reduce((sum, result) => {
            return sum + (result.estimated_price || 0)
          }, 0)
          // 更新弹窗内容，显示实际数据
          this.valuationResults = results
          this.valuationTotalValue = totalValue
          this.valuationLoading = false
        } else {
          this.$notify.error({
            title: '错误',
            message: response.message || '装备估价失败'
          })
          this.closeValuationDialog()
        }
      } catch (error) {
        console.error('装备估价失败:', error)
        this.$notify.error({
          title: '错误',
          message: '装备估价失败'
        })
        this.closeValuationDialog()
      } finally {
        this.valuationLoading = false
      }
    },
    get_school_name: window.get_school_name,
    getExAvtJsonDesc(ex_avt_json) {
      const ex_avt_json_obj = eval(`(${ex_avt_json})`)
      const exAvtJsonDesc = []
      for (const key in ex_avt_json_obj) {
        const item = ex_avt_json_obj[key]
        exAvtJsonDesc.push(item.cName)
      }
      return exAvtJsonDesc
    },
    handleSortChange({ prop, order }) {
      this.sortState[prop] = order

      const sortFields = []
      const sortOrders = []
      for (const [field, order] of Object.entries(this.sortState)) {
        if (order) {
          sortFields.push(field)
          sortOrders.push(order === 'ascending' ? 'ASC' : 'DESC')
        }
      }

      this.$set(this.searchForm, 'sort_by', sortFields.join(','))
      this.$set(this.searchForm, 'sort_order', sortOrders.join(','))
      this.handleSearch()
    },
    async fetchData() {
      this.loading = true
      try {
        const [year, month] = this.searchForm.selectedDate.split('-')
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          year,
          month
        }

        // 添加搜索条件
        if (this.searchForm.level_min) {
          params.level_min = this.searchForm.level_min
        }
        if (this.searchForm.level_max) {
          params.level_max = this.searchForm.level_max
        }
        if (this.searchForm.school_skill_num) {
          params.school_skill_num = this.searchForm.school_skill_num
        }
        if (this.searchForm.school_skill_level) {
          params.school_skill_level = this.searchForm.school_skill_level
        }
        // 角色修炼参数
        if (this.searchForm.expt_gongji) params.expt_gongji = this.searchForm.expt_gongji
        if (this.searchForm.expt_fangyu) params.expt_fangyu = this.searchForm.expt_fangyu
        if (this.searchForm.expt_fashu) params.expt_fashu = this.searchForm.expt_fashu
        if (this.searchForm.expt_kangfa) params.expt_kangfa = this.searchForm.expt_kangfa
        if (this.searchForm.expt_total) params.expt_total = this.searchForm.expt_total
        if (this.searchForm.max_expt_gongji) params.max_expt_gongji = this.searchForm.max_expt_gongji
        if (this.searchForm.max_expt_fangyu) params.max_expt_fangyu = this.searchForm.max_expt_fangyu
        if (this.searchForm.max_expt_fashu) params.max_expt_fashu = this.searchForm.max_expt_fashu
        if (this.searchForm.max_expt_kangfa) params.max_expt_kangfa = this.searchForm.max_expt_kangfa
        if (this.searchForm.expt_lieshu) params.expt_lieshu = this.searchForm.expt_lieshu
        // 召唤兽修炼参数
        if (this.searchForm.bb_expt_gongji) params.bb_expt_gongji = this.searchForm.bb_expt_gongji
        if (this.searchForm.bb_expt_fangyu) params.bb_expt_fangyu = this.searchForm.bb_expt_fangyu
        if (this.searchForm.bb_expt_fashu) params.bb_expt_fashu = this.searchForm.bb_expt_fashu
        if (this.searchForm.bb_expt_kangfa) params.bb_expt_kangfa = this.searchForm.bb_expt_kangfa
        if (this.searchForm.bb_expt_total) params.bb_expt_total = this.searchForm.bb_expt_total
        if (this.searchForm.skill_drive_pet) params.skill_drive_pet = this.searchForm.skill_drive_pet
        // 排序参数
        if (this.searchForm.sort_by) params.sort_by = this.searchForm.sort_by
        if (this.searchForm.sort_order) params.sort_order = this.searchForm.sort_order

        // 使用新的API
        const response = await this.$api.role.getRoleApi(params)

        if (response.code === 200) {
          // 现在直接使用response.data和response.items
          this.RoleApi = response.data.data.map(item => {
            const roleInfo = new window.RoleInfoParser(item.large_equip_desc, { equip_level: item.equip_level })
            if (roleInfo.result) {
              item.roleInfo = roleInfo.result
            }
            return item
          }) || []
          this.total = response.data.total || 0
        } else {
          this.$notify.error({
            title: '错误',
            message: response.message || '获取数据失败'
          })
        }
      } catch (error) {
        this.$notify.error({
          title: '错误',
          message: '获取数据失败：' + error.message
        })
      } finally {
        this.loading = false
      }
    },

    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
      this.fetchData()
    },

    handleCurrentChange(val) {
      this.currentPage = val
      this.fetchData()
    },

    handleDateChange() {
      this.currentPage = 1
      this.fetchData()
    },

    handleQuickLevelSelect(level) {
      this.searchForm.level_min = level
      this.searchForm.level_max = level
    },

    handleSearch() {
      this.currentPage = 1
      this.fetchData()
    },

    handleReset() {
      this.searchForm = {
        selectedDate: dayjs().format('YYYY-MM'),
        level_min: undefined,
        level_max: undefined,
        school_skill_num: '',
        school_skill_level: undefined,
        // 角色修炼
        expt_gongji: undefined,
        expt_fangyu: undefined,
        expt_fashu: undefined,
        expt_kangfa: undefined,
        expt_total: undefined,
        max_expt_gongji: undefined,
        max_expt_fangyu: undefined,
        max_expt_fashu: undefined,
        max_expt_kangfa: undefined,
        expt_lieshu: undefined,
        // 召唤兽修炼
        bb_expt_gongji: undefined,
        bb_expt_fangyu: undefined,
        bb_expt_fashu: undefined,
        bb_expt_kangfa: undefined,
        bb_expt_total: undefined,
        //生活技能 TODO:
        skill_drive_pet: undefined,
        skill_qiang_shen: undefined,
        skill_qiang_zhuang: undefined,
        skill_shensu: undefined,
        skill_ming_xiang: undefined,
        skill_anqi: undefined,
        skill_dazao: undefined,
        skill_caifeng: undefined,
        skill_qiaojiang: undefined,
        skill_lianjin: undefined,
        skill_yangsheng: undefined,
        skill_pengren: undefined,
        skill_zhongyao: undefined,
        skill_lingshi: undefined,
        skill_jianshen: undefined,
        skill_taoli: undefined,
        skill_zhuibu: undefined,
        skill_ronglian: undefined,
        skill_cuiling: undefined,
        skill_wind_sense: undefined,
        skill_rain_sense: undefined,
        skill_snow_sense: undefined,
        sort_by: undefined,
        sort_order: undefined
      }
      this.currentPage = 1
      this.fetchData()
    },

    extractServerId(equipId) {
      // 从equip_id中提取服务器ID
      // 格式通常是: 服务器ID_其他信息
      const parts = equipId.split('-')
      return parts[1] || null
    },
  }
}
</script>

<style scoped>
.filter-bar {
  margin-bottom: 20px;
}

.search-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.ml-10 {
  margin-left: 10px;
}

/* 设置表格行高 */
.el-table>>>td {
  padding: 5px 0;
}

.mx-2 {
  margin: 0 8px;
}

.level-quick-select {
  margin-left: 16px;
  display: inline-block;
}

.level-quick-select .el-button {
  margin-right: 8px;
  margin-bottom: 8px;
}

.cultivation-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cultivation-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.text-gray {
  color: #909399;
  font-size: 12px;
}

.role-link {
  color: #409eff;
  text-decoration: none;
}

.role-link:hover {
  text-decoration: underline;
}

.equip-desc {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
