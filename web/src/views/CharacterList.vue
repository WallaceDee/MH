<template>
  <div class="character-list">
    <div class="filter-bar">
      <el-collapse v-model="activeCollapse">
        <el-collapse-item title="搜索条件" name="1">
          <el-form :inline="true" :model="searchForm" class="search-form">
            <el-form-item label="选择月份">
              <el-date-picker v-model="searchForm.selectedDate" :clearable="false" type="month" placeholder="选择月份"
                format="yyyy-MM" value-format="yyyy-MM" @change="handleDateChange" />
            </el-form-item>
            <el-form-item label="人物等级">
              <el-input-number :controls="false" v-model="searchForm.level_min" :min="0" :max="175" style="width: 100px" />
              <span class="mx-2">-</span>
              <el-input-number :controls="false" v-model="searchForm.level_max" :min="0" :max="175" style="width: 100px" />
              <div class="level-quick-select">
                <el-button v-for="level in [89, 109, 129, 155, 159, 175]" :key="level"
                  @click="handleQuickLevelSelect(level)">
                  {{ level }}级
                </el-button>
              </div>
            </el-form-item>
            <el-form-item label="师门技能">
              <el-select v-model="searchForm.school_skill_num" placeholder="技能数量" style="width: 100px">
                <el-option label="不限" value="" />
                <el-option v-for="n in 7" :key="n" :label="n" :value="n" />
              </el-select>
              <span class="mx-2">个技能等级≥</span>
              <el-input-number :controls="false" v-model="searchForm.school_skill_level" :min="0" :max="180"
                style="width: 100px" />
            </el-form-item>
            <el-form-item label="角色修炼">
              <div class="cultivation-group">
                <div class="cultivation-row">
                  <span>攻击修炼≥</span>
                  <el-input-number :controls="false" v-model="searchForm.expt_gongji" :min="0" :max="25"
                    style="width: 80px" />
                  <span class="mx-2">防御修炼≥</span>
                  <el-input-number :controls="false" v-model="searchForm.expt_fangyu" :min="0" :max="25"
                    style="width: 80px" />
                  <span class="mx-2">法术修炼≥</span>
                  <el-input-number :controls="false" v-model="searchForm.expt_fashu" :min="0" :max="25"
                    style="width: 80px" />
                  <span class="mx-2">抗法修炼≥</span>
                  <el-input-number :controls="false" v-model="searchForm.expt_kangfa" :min="0" :max="25"
                    style="width: 80px" />
                  <span class="mx-2">修炼总和≥</span>
                  <el-input-number :controls="false" v-model="searchForm.expt_total" :min="0" :max="100"
                    style="width: 80px" />
                </div>
                <div class="cultivation-row">
                  <span>攻击上限≥</span>
                  <el-input-number :controls="false" v-model="searchForm.max_expt_gongji" :min="0" :max="25"
                    style="width: 80px" />
                  <span class="mx-2">防御上限≥</span>
                  <el-input-number :controls="false" v-model="searchForm.max_expt_fangyu" :min="0" :max="25"
                    style="width: 80px" />
                  <span class="mx-2">法术上限≥</span>
                  <el-input-number :controls="false" v-model="searchForm.max_expt_fashu" :min="0" :max="25"
                    style="width: 80px" />
                  <span class="mx-2">抗法上限≥</span>
                  <el-input-number :controls="false" v-model="searchForm.max_expt_kangfa" :min="0" :max="25"
                    style="width: 80px" />
                </div>
                <div class="cultivation-row">
                  <span>猎术修炼≥</span>
                  <el-input-number :controls="false" v-model="searchForm.expt_lieshu" :min="0" :max="25"
                    style="width: 80px" />
                  <span class="mx-2 text-gray">（不计入修炼总和）</span>
                </div>
              </div>
            </el-form-item>
            <el-form-item label="召唤兽修炼">
              <div class="cultivation-group">
                <div class="cultivation-row">
                  <span>攻击控制≥</span>
                  <el-input-number :controls="false" v-model="searchForm.bb_expt_gongji" :min="0" :max="25"
                    style="width: 80px" />
                  <span class="mx-2">防御控制≥</span>
                  <el-input-number :controls="false" v-model="searchForm.bb_expt_fangyu" :min="0" :max="25"
                    style="width: 80px" />
                  <span class="mx-2">法术控制≥</span>
                  <el-input-number :controls="false" v-model="searchForm.bb_expt_fashu" :min="0" :max="25"
                    style="width: 80px" />
                  <span class="mx-2">抗法控制≥</span>
                  <el-input-number :controls="false" v-model="searchForm.bb_expt_kangfa" :min="0" :max="25"
                    style="width: 80px" />
                  <span class="mx-2">宠修总和≥</span>
                  <el-input-number :controls="false" v-model="searchForm.bb_expt_total" :min="0" :max="100"
                    style="width: 80px" />
                </div>
                <div class="cultivation-row">
                  <span>育兽术≥</span>
                  <el-input-number :controls="false" v-model="searchForm.skill_drive_pet" :min="0" :max="25"
                    style="width: 80px" />
                  <span class="mx-2 text-gray">（不计入宠修总和）</span>
                </div>
              </div>
            </el-form-item>
            <el-form-item label="生活技能">
              <div class="cultivation-group">
                <div class="cultivation-row">
                  <span class="mx-2">强身≥</span>
                  <el-input v-model.number="searchForm.skill_qiang_shen" style="width: 100px;" clearable />
                  <span class="mx-2">强壮≥</span>
                  <el-input v-model.number="searchForm.skill_qiang_zhuang" style="width: 100px;" clearable />
                  <span class="mx-2">神速≥</span>
                  <el-input v-model.number="searchForm.skill_shensu" style="width: 100px;" clearable />
                  <span class="mx-2">冥想≥</span>
                  <el-input v-model.number="searchForm.skill_ming_xiang" style="width: 100px;" clearable />
                  <span class="mx-2">暗器技巧≥</span>
                  <el-input v-model.number="searchForm.skill_anqi" style="width: 100px;" clearable />
                </div>
                <div class="cultivation-row">
                  <span class="mx-2">打造技巧≥</span>
                  <el-input v-model.number="searchForm.skill_dazao" style="width: 100px;" clearable />
                  <span class="mx-2">裁缝技巧≥</span>
                  <el-input v-model.number="searchForm.skill_caifeng" style="width: 100px;" clearable />
                  <span class="mx-2">巧匠之术≥</span>
                  <el-input v-model.number="searchForm.skill_qiaojiang" style="width: 100px;" clearable />
                  <span class="mx-2">炼金术≥</span>
                  <el-input v-model.number="searchForm.skill_lianjin" style="width: 100px;" clearable />
                  <span class="mx-2">养生之道≥</span>
                  <el-input v-model.number="searchForm.skill_yangsheng" style="width: 100px;" clearable />
                </div>
                <div class="cultivation-row">
                  <span class="mx-2">烹饪技巧≥</span>
                  <el-input v-model.number="searchForm.skill_pengren" style="width: 100px;" clearable />
                  <span class="mx-2">中药医理≥</span>
                  <el-input v-model.number="searchForm.skill_zhongyao" style="width: 100px;" clearable />
                  <span class="mx-2">灵石技巧≥</span>
                  <el-input v-model.number="searchForm.skill_lingshi" style="width: 100px;" clearable />
                  <span class="mx-2">健身术≥</span>
                  <el-input v-model.number="searchForm.skill_jianshen" style="width: 100px;" clearable />
                  <span class="mx-2">逃离技巧≥</span>
                  <el-input v-model.number="searchForm.skill_taoli" style="width: 100px;" clearable />
                </div>
                <div class="cultivation-row">
                  <span class="mx-2">追捕技巧≥</span>
                  <el-input v-model.number="searchForm.skill_zhuibu" style="width: 100px;" clearable />
                  <span class="mx-2">熔炼技巧≥</span>
                  <el-input v-model.number="searchForm.skill_ronglian" style="width: 100px;" clearable />
                  <span class="mx-2">淬灵之术≥</span>
                  <el-input v-model.number="searchForm.skill_cuiling" style="width: 100px;" clearable />
                  <span class="mx-2">风之感应≥</span>
                  <el-input v-model.number="searchForm.skill_wind_sense" style="width: 100px;" clearable />
                  <span class="mx-2">雨之感应≥</span>
                  <el-input v-model.number="searchForm.skill_rain_sense" style="width: 100px;" clearable />
                </div>
                <div class="cultivation-row">
                  <span class="mx-2">雪之感应≥</span>
                  <el-input v-model.number="searchForm.skill_snow_sense" style="width: 100px;" clearable />
                </div>
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

    <el-table v-loading="loading" :data="characterList" border style="width: 100%">
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
          {{ scope.row.level }}/{{ scope.row.school_desc }}/{{ scope.row.fly_status }}/{{ scope.row.sum_exp }}亿
        </template>
      </el-table-column>
      <el-table-column prop="price" label="价格" width="80" />
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
        skill_snow_sense: undefined
      },
      activeCollapse: ['1']
    }
  },

  created() {
    this.fetchData()
  },

  methods: {
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
        if (this.searchForm.max_expt_gongji) params.append('max_expt_gongji', this.searchForm.max_expt_gongji)
        if (this.searchForm.max_expt_fangyu) params.append('max_expt_fangyu', this.searchForm.max_expt_fangyu)
        if (this.searchForm.max_expt_fashu) params.append('max_expt_fashu', this.searchForm.max_expt_fashu)
        if (this.searchForm.max_expt_kangfa) params.append('max_expt_kangfa', this.searchForm.max_expt_kangfa)
        if (this.searchForm.expt_lieshu) params.append('expt_lieshu', this.searchForm.expt_lieshu)
        // 召唤兽修炼参数
        if (this.searchForm.bb_expt_gongji) params.append('bb_expt_gongji', this.searchForm.bb_expt_gongji)
        if (this.searchForm.bb_expt_fangyu) params.append('bb_expt_fangyu', this.searchForm.bb_expt_fangyu)
        if (this.searchForm.bb_expt_fashu) params.append('bb_expt_fashu', this.searchForm.bb_expt_fashu)
        if (this.searchForm.bb_expt_kangfa) params.append('bb_expt_kangfa', this.searchForm.bb_expt_kangfa)
        if (this.searchForm.bb_expt_total) params.append('bb_expt_total', this.searchForm.bb_expt_total)
        if (this.searchForm.skill_drive_pet) params.append('skill_drive_pet', this.searchForm.skill_drive_pet)
        if (this.searchForm.skill_qiang_shen) params.append('skill_qiang_shen', this.searchForm.skill_qiang_shen)
        if (this.searchForm.skill_qiang_zhuang) params.append('skill_qiang_zhuang', this.searchForm.skill_qiang_zhuang)
        if (this.searchForm.skill_shensu) params.append('skill_shensu', this.searchForm.skill_shensu)
        if (this.searchForm.skill_ming_xiang) params.append('skill_ming_xiang', this.searchForm.skill_ming_xiang)
        if (this.searchForm.skill_anqi) params.append('skill_anqi', this.searchForm.skill_anqi)
        if (this.searchForm.skill_dazao) params.append('skill_dazao', this.searchForm.skill_dazao)
        if (this.searchForm.skill_caifeng) params.append('skill_caifeng', this.searchForm.skill_caifeng)
        if (this.searchForm.skill_qiaojiang) params.append('skill_qiaojiang', this.searchForm.skill_qiaojiang)
        if (this.searchForm.skill_lianjin) params.append('skill_lianjin', this.searchForm.skill_lianjin)
        if (this.searchForm.skill_yangsheng) params.append('skill_yangsheng', this.searchForm.skill_yangsheng)
        if (this.searchForm.skill_pengren) params.append('skill_pengren', this.searchForm.skill_pengren)
        if (this.searchForm.skill_zhongyao) params.append('skill_zhongyao', this.searchForm.skill_zhongyao)
        if (this.searchForm.skill_lingshi) params.append('skill_lingshi', this.searchForm.skill_lingshi)
        if (this.searchForm.skill_jianshen) params.append('skill_jianshen', this.searchForm.skill_jianshen)
        if (this.searchForm.skill_taoli) params.append('skill_taoli', this.searchForm.skill_taoli)
        if (this.searchForm.skill_zhuibu) params.append('skill_zhuibu', this.searchForm.skill_zhuibu)
        if (this.searchForm.skill_ronglian) params.append('skill_ronglian', this.searchForm.skill_ronglian)
        if (this.searchForm.skill_cuiling) params.append('skill_cuiling', this.searchForm.skill_cuiling)
        if (this.searchForm.skill_wind_sense) params.append('skill_wind_sense', this.searchForm.skill_wind_sense)
        if (this.searchForm.skill_rain_sense) params.append('skill_rain_sense', this.searchForm.skill_rain_sense)
        if (this.searchForm.skill_snow_sense) params.append('skill_snow_sense', this.searchForm.skill_snow_sense)

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
        skill_snow_sense: undefined
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
    }
  }
}
</script>

<style scoped>
.character-list {
  padding: 20px;
}

.filter-bar {
  margin-bottom: 20px;
}

.search-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
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
  color: #409EFF;
  text-decoration: none;
}

.character-link:hover {
  text-decoration: underline;
}
</style>