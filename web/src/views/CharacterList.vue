<template>
  <div class="character-list">
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
              <el-button type="success" @click="handleExportJSON" :loading="exportLoading">导出JSON</el-button>
            </el-form-item>
          </el-form>
        </el-collapse-item>
      </el-collapse>
    </div>

    <el-table v-loading="loading" :data="characterList" border style="width: 100%" @sort-change="handleSortChange">
      <!-- 基本信息 -->
      <el-table-column prop="character_name" label="角色名" width="120">
        <template slot-scope="scope">
          <a :href="getCBGLink(scope.row.equip_id)" target="_blank" class="character-link">
            {{ scope.row.character_name || scope.row.seller_nickname }}
          </a>
        </template>
      </el-table-column>
      <el-table-column label="等级/门派/飞升" width="160">
        <template slot-scope="scope">
          {{ scope.row.level }}/{{ scope.row.school_desc }}/{{ scope.row.fly_status }}/{{
            scope.row.sum_exp
          }}亿
        </template>
      </el-table-column>
      <el-table-column prop="price" label="价格" width="80" sortable="custom"/>
      <!-- 修炼信息 -->
      <el-table-column label="修炼/控制力" width="300">
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

      <el-table-column label="师门技能" width="220" prop="school_skills">
        <template slot-scope="scope">
          <span v-for="(val, key, index) in JSON.parse(scope.row.school_skills)" :key="index"><em
              v-if="index > 0">/</em>{{ val }}</span>
        </template>
      </el-table-column>
      <!-- 物品 -->
      <el-table-column label="物品" width="120">
        <template slot-scope="scope">
          <el-popover placement="top" width="400" trigger="click" :content="scope.row.all_equip_json_desc">
            <div class="equip-desc" slot="reference" @click="copyText(scope.row.all_equip_json_desc)">{{
              scope.row.all_equip_json_desc }}</div>
          </el-popover>
        </template>
      </el-table-column>
      <!-- 宠物 -->
      <el-table-column label="宠物" width="120">
        <template slot-scope="scope">
          <el-popover placement="top" width="400" trigger="click" :content="scope.row.all_pets_json">
            <div class="equip-desc" slot="reference" @click="copyText(scope.row.all_pets_json)">{{
              scope.row.all_pets_json }}</div>
          </el-popover>
        </template>
      </el-table-column>
      <!-- 资产信息 -->
      <el-table-column label="资产" width="200">
        <template slot-scope="scope">
          <span>现金:{{ scope.row.cash }}</span>
          <span class="ml-10">存款:{{ scope.row.saving }}</span>
        </template>
      </el-table-column>

      <!-- 评分信息 -->
      <el-table-column label="积分" width="200">
        <template slot-scope="scope">
          <span class="ml-10">神器:{{ scope.row.shenqi_score }}</span>
          <span class="ml-10">副本:{{ scope.row.dup_score }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="server" label="服务器" width="150">
        <template slot-scope="scope">
          {{ scope.row.area_name }}/{{ scope.row.server_name }}
        </template>
      </el-table-column>
      <!-- 时间信息 -->
      <el-table-column prop="create_time" label="创建时间" width="200" />
      <el-table-column prop="server" label="操作" width="150">
        <template slot-scope="scope">
          <el-button 
            size="mini" 
            type="primary" 
            @click="handleExportSingleJSON(scope.row)"
            :loading="scope.row.exportLoading">
            导出JSON
          </el-button> 
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination :current-page.sync="currentPage" :page-size.sync="pageSize" :total="total"
        :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next" @size-change="handleSizeChange"
        @current-change="handleCurrentChange" />
    </div>
  </div>
</template>

<script>
import dayjs from 'dayjs'

export default {
  name: 'CharacterList',

  data() {
    return {
      loading: false,
      exportLoading: false,
      characterList: [],
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
      activeCollapse: ['1'],
      sortState: {
        price: null,
        level: null,
        create_time: null
      }
    }
  },

  created() {
    this.fetchData()
  },

  methods: {
    handleSortChange({ prop, order }) {
      this.sortState[prop] = order
      
      const sortFields = []
      const sortOrders = []
      for (const [field, order] of Object.entries(this.sortState)) {
        if (order) {
          sortFields.push(field)
          sortOrders.push(order==='ascending'?'ASC':'DESC')
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
        const params = new URLSearchParams({
          page: this.currentPage,
          page_size: this.pageSize,
          year,
          month
        })

        if (this.searchForm.level_min) {
          params.append('level_min', this.searchForm.level_min)
        }
        if (this.searchForm.level_max) {
          params.append('level_max', this.searchForm.level_max)
        }
        if (this.searchForm.school_skill_num) {
          params.append('school_skill_num', this.searchForm.school_skill_num)
        }
        if (this.searchForm.school_skill_level) {
          params.append('school_skill_level', this.searchForm.school_skill_level)
        }
        // 角色修炼参数
        if (this.searchForm.expt_gongji) params.append('expt_gongji', this.searchForm.expt_gongji)
        if (this.searchForm.expt_fangyu) params.append('expt_fangyu', this.searchForm.expt_fangyu)
        if (this.searchForm.expt_fashu) params.append('expt_fashu', this.searchForm.expt_fashu)
        if (this.searchForm.expt_kangfa) params.append('expt_kangfa', this.searchForm.expt_kangfa)
        if (this.searchForm.expt_total) params.append('expt_total', this.searchForm.expt_total)
        if (this.searchForm.max_expt_gongji)
          params.append('max_expt_gongji', this.searchForm.max_expt_gongji)
        if (this.searchForm.max_expt_fangyu)
          params.append('max_expt_fangyu', this.searchForm.max_expt_fangyu)
        if (this.searchForm.max_expt_fashu)
          params.append('max_expt_fashu', this.searchForm.max_expt_fashu)
        if (this.searchForm.max_expt_kangfa)
          params.append('max_expt_kangfa', this.searchForm.max_expt_kangfa)
        if (this.searchForm.expt_lieshu) params.append('expt_lieshu', this.searchForm.expt_lieshu)
        // 召唤兽修炼参数
        if (this.searchForm.bb_expt_gongji)
          params.append('bb_expt_gongji', this.searchForm.bb_expt_gongji)
        if (this.searchForm.bb_expt_fangyu)
          params.append('bb_expt_fangyu', this.searchForm.bb_expt_fangyu)
        if (this.searchForm.bb_expt_fashu)
          params.append('bb_expt_fashu', this.searchForm.bb_expt_fashu)
        if (this.searchForm.bb_expt_kangfa)
          params.append('bb_expt_kangfa', this.searchForm.bb_expt_kangfa)
        if (this.searchForm.bb_expt_total)
          params.append('bb_expt_total', this.searchForm.bb_expt_total)
        if (this.searchForm.skill_drive_pet)
          params.append('skill_drive_pet', this.searchForm.skill_drive_pet)
        if (this.searchForm.skill_qiang_shen)
          params.append('skill_qiang_shen', this.searchForm.skill_qiang_shen)
        if (this.searchForm.skill_qiang_zhuang)
          params.append('skill_qiang_zhuang', this.searchForm.skill_qiang_zhuang)
        if (this.searchForm.skill_shensu)
          params.append('skill_shensu', this.searchForm.skill_shensu)
        if (this.searchForm.skill_ming_xiang)
          params.append('skill_ming_xiang', this.searchForm.skill_ming_xiang)
        if (this.searchForm.skill_anqi) params.append('skill_anqi', this.searchForm.skill_anqi)
        if (this.searchForm.skill_dazao) params.append('skill_dazao', this.searchForm.skill_dazao)
        if (this.searchForm.skill_caifeng)
          params.append('skill_caifeng', this.searchForm.skill_caifeng)
        if (this.searchForm.skill_qiaojiang)
          params.append('skill_qiaojiang', this.searchForm.skill_qiaojiang)
        if (this.searchForm.skill_lianjin)
          params.append('skill_lianjin', this.searchForm.skill_lianjin)
        if (this.searchForm.skill_yangsheng)
          params.append('skill_yangsheng', this.searchForm.skill_yangsheng)
        if (this.searchForm.skill_pengren)
          params.append('skill_pengren', this.searchForm.skill_pengren)
        if (this.searchForm.skill_zhongyao)
          params.append('skill_zhongyao', this.searchForm.skill_zhongyao)
        if (this.searchForm.skill_lingshi)
          params.append('skill_lingshi', this.searchForm.skill_lingshi)
        if (this.searchForm.skill_jianshen)
          params.append('skill_jianshen', this.searchForm.skill_jianshen)
        if (this.searchForm.skill_taoli) params.append('skill_taoli', this.searchForm.skill_taoli)
        if (this.searchForm.skill_zhuibu)
          params.append('skill_zhuibu', this.searchForm.skill_zhuibu)
        if (this.searchForm.skill_ronglian)
          params.append('skill_ronglian', this.searchForm.skill_ronglian)
        if (this.searchForm.skill_cuiling)
          params.append('skill_cuiling', this.searchForm.skill_cuiling)
        if (this.searchForm.skill_wind_sense)
          params.append('skill_wind_sense', this.searchForm.skill_wind_sense)
        if (this.searchForm.skill_rain_sense)
          params.append('skill_rain_sense', this.searchForm.skill_rain_sense)
        if (this.searchForm.skill_snow_sense)
          params.append('skill_snow_sense', this.searchForm.skill_snow_sense)
        if (this.searchForm.equip_num !== undefined)
          params.append('equip_num', this.searchForm.equip_num)
        if (this.searchForm.pet_num !== undefined)
          params.append('pet_num', this.searchForm.pet_num)
        if (this.searchForm.pet_num_level !== undefined)
          params.append('pet_num_level', this.searchForm.pet_num_level)
        if (this.searchForm.sort_by){
          params.append('sort_by', this.searchForm.sort_by)
          params.append('sort_order', this.searchForm.sort_order)
        }
        const response = await fetch(`/api/characters?${params.toString()}`)
        const data = await response.json()

        if (data.error) {
          this.$message.error(data.error)
          return
        }

        this.characterList = data.data
        this.total = data.total
      } catch (error) {
        this.$message.error('获取数据失败：' + error.message)
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

    formatPrice(price) {
      return price ? `¥${(price / 100).toFixed(2)}` : '-'
    },

    formatDate(timestamp) {
      return timestamp ? dayjs(timestamp * 1000).format('YYYY-MM-DD HH:mm:ss') : '-'
    },

    formatMoney(money) {
      return money ? `¥${(money / 100).toFixed(2)}` : '-'
    },

    getCBGLink(equipId) {
      if (!equipId) return '#'
      // 从equip_id中提取服务器ID
      const serverId = this.extractServerId(equipId)
      if (!serverId) return '#'

      // 构建CBG链接
      return `https://xyq.cbg.163.com/equip?s=${serverId}&eid=${equipId}`
    },

    extractServerId(equipId) {
      // 从equip_id中提取服务器ID
      // 格式通常是: 服务器ID_其他信息
      const parts = equipId.split('-')
      return parts[1] || null
    },

    copyText(text) {
      navigator.clipboard.writeText(text).then(() => {
        this.$message({
          message: '复制成功',
          type: 'success',
          duration: 1500
        })
      }).catch(() => {
        this.$message({
          message: '复制失败',
          type: 'error',
          duration: 1500
        })
      })
    },

    async handleExportJSON() {
      this.exportLoading = true
      try {
        const [year, month] = this.searchForm.selectedDate.split('-')
        const params = new URLSearchParams({
          year,
          month,
          export_all: 'true' // 导出所有匹配的数据，不分页
        })

        // 添加所有搜索条件参数
        if (this.searchForm.level_min) {
          params.append('level_min', this.searchForm.level_min)
        }
        if (this.searchForm.level_max) {
          params.append('level_max', this.searchForm.level_max)
        }
        if (this.searchForm.school_skill_num) {
          params.append('school_skill_num', this.searchForm.school_skill_num)
        }
        if (this.searchForm.school_skill_level) {
          params.append('school_skill_level', this.searchForm.school_skill_level)
        }
        // 角色修炼参数
        if (this.searchForm.expt_gongji) params.append('expt_gongji', this.searchForm.expt_gongji)
        if (this.searchForm.expt_fangyu) params.append('expt_fangyu', this.searchForm.expt_fangyu)
        if (this.searchForm.expt_fashu) params.append('expt_fashu', this.searchForm.expt_fashu)
        if (this.searchForm.expt_kangfa) params.append('expt_kangfa', this.searchForm.expt_kangfa)
        if (this.searchForm.expt_total) params.append('expt_total', this.searchForm.expt_total)
        if (this.searchForm.max_expt_gongji)
          params.append('max_expt_gongji', this.searchForm.max_expt_gongji)
        if (this.searchForm.max_expt_fangyu)
          params.append('max_expt_fangyu', this.searchForm.max_expt_fangyu)
        if (this.searchForm.max_expt_fashu)
          params.append('max_expt_fashu', this.searchForm.max_expt_fashu)
        if (this.searchForm.max_expt_kangfa)
          params.append('max_expt_kangfa', this.searchForm.max_expt_kangfa)
        if (this.searchForm.expt_lieshu) params.append('expt_lieshu', this.searchForm.expt_lieshu)
        // 召唤兽修炼参数
        if (this.searchForm.bb_expt_gongji)
          params.append('bb_expt_gongji', this.searchForm.bb_expt_gongji)
        if (this.searchForm.bb_expt_fangyu)
          params.append('bb_expt_fangyu', this.searchForm.bb_expt_fangyu)
        if (this.searchForm.bb_expt_fashu)
          params.append('bb_expt_fashu', this.searchForm.bb_expt_fashu)
        if (this.searchForm.bb_expt_kangfa)
          params.append('bb_expt_kangfa', this.searchForm.bb_expt_kangfa)
        if (this.searchForm.bb_expt_total)
          params.append('bb_expt_total', this.searchForm.bb_expt_total)
        if (this.searchForm.skill_drive_pet)
          params.append('skill_drive_pet', this.searchForm.skill_drive_pet)
        // 生活技能参数
        if (this.searchForm.skill_qiang_shen)
          params.append('skill_qiang_shen', this.searchForm.skill_qiang_shen)
        if (this.searchForm.skill_qiang_zhuang)
          params.append('skill_qiang_zhuang', this.searchForm.skill_qiang_zhuang)
        if (this.searchForm.skill_shensu)
          params.append('skill_shensu', this.searchForm.skill_shensu)
        if (this.searchForm.skill_ming_xiang)
          params.append('skill_ming_xiang', this.searchForm.skill_ming_xiang)
        if (this.searchForm.skill_anqi) params.append('skill_anqi', this.searchForm.skill_anqi)
        if (this.searchForm.skill_dazao) params.append('skill_dazao', this.searchForm.skill_dazao)
        if (this.searchForm.skill_caifeng)
          params.append('skill_caifeng', this.searchForm.skill_caifeng)
        if (this.searchForm.skill_qiaojiang)
          params.append('skill_qiaojiang', this.searchForm.skill_qiaojiang)
        if (this.searchForm.skill_lianjin)
          params.append('skill_lianjin', this.searchForm.skill_lianjin)
        if (this.searchForm.skill_yangsheng)
          params.append('skill_yangsheng', this.searchForm.skill_yangsheng)
        if (this.searchForm.skill_pengren)
          params.append('skill_pengren', this.searchForm.skill_pengren)
        if (this.searchForm.skill_zhongyao)
          params.append('skill_zhongyao', this.searchForm.skill_zhongyao)
        if (this.searchForm.skill_lingshi)
          params.append('skill_lingshi', this.searchForm.skill_lingshi)
        if (this.searchForm.skill_jianshen)
          params.append('skill_jianshen', this.searchForm.skill_jianshen)
        if (this.searchForm.skill_taoli) params.append('skill_taoli', this.searchForm.skill_taoli)
        if (this.searchForm.skill_zhuibu)
          params.append('skill_zhuibu', this.searchForm.skill_zhuibu)
        if (this.searchForm.skill_ronglian)
          params.append('skill_ronglian', this.searchForm.skill_ronglian)
        if (this.searchForm.skill_cuiling)
          params.append('skill_cuiling', this.searchForm.skill_cuiling)
        if (this.searchForm.skill_wind_sense)
          params.append('skill_wind_sense', this.searchForm.skill_wind_sense)
        if (this.searchForm.skill_rain_sense)
          params.append('skill_rain_sense', this.searchForm.skill_rain_sense)
        if (this.searchForm.skill_snow_sense)
          params.append('skill_snow_sense', this.searchForm.skill_snow_sense)
        // 其他参数
        if (this.searchForm.equip_num !== undefined)
          params.append('equip_num', this.searchForm.equip_num)
        if (this.searchForm.pet_num !== undefined)
          params.append('pet_num', this.searchForm.pet_num)
        if (this.searchForm.pet_num_level !== undefined)
          params.append('pet_num_level', this.searchForm.pet_num_level)
        if (this.searchForm.sort_by){
          params.append('sort_by', this.searchForm.sort_by)
          params.append('sort_order', this.searchForm.sort_order)
        }

        const response = await fetch(`/api/characters/export/json?${params.toString()}`)
        
        if (!response.ok) {
          throw new Error(`导出失败: ${response.status} ${response.statusText}`)
        }

        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `cbg_characters_${this.searchForm.selectedDate.replace('-', '')}_${new Date().getTime()}.json`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        this.$message({
          message: 'JSON导出成功',
          type: 'success',
          duration: 2000
        })
      } catch (error) {
        this.$message.error('导出失败：' + error.message)
      } finally {
        this.exportLoading = false
      }
    },

    async handleExportSingleJSON(character) {
      // 设置单个角色的loading状态
      this.$set(character, 'exportLoading', true)
      
      try {
        const [year, month] = this.searchForm.selectedDate.split('-')
        const params = new URLSearchParams({
          year,
          month,
          equip_id: character.equip_id
        })

        const response = await fetch(`/api/characters/export/single/json?${params.toString()}`)
        
        if (!response.ok) {
          throw new Error(`导出失败: ${response.status} ${response.statusText}`)
        }

        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        
        // 使用角色名和服务器名作为文件名
        const characterName = character.seller_nickname || '未知角色'
        const serverName = (character.area_name + '_' + character.server_name).replace(/[/\\:*?"<>|]/g, '_')
        const timestamp = new Date().getTime()
        link.download = `${characterName}_${serverName}_${timestamp}.json`
        
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        this.$message({
          message: '角色JSON导出成功',
          type: 'success',
          duration: 2000
        })
      } catch (error) {
        this.$message.error('导出失败：' + error.message)
      } finally {
        this.$set(character, 'exportLoading', false)
      }
    }
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

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
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

.character-link {
  color: #409eff;
  text-decoration: none;
}

.character-link:hover {
  text-decoration: underline;
}

.equip-desc {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
