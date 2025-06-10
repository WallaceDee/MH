<template>
  <div class="spider-search">
    <!-- 基础信息搜索 -->
    <div class="divGride searchForm js_search_form">
      <div class="title">
        <span><a href="#" class="fB f14px" @click="resetBasicInfo">重置</a></span>
        <h3 class="f14px textLeft fB js_form_title" data-title="基础信息">基础信息</h3>
      </div>
      <div class="grideCont">
        <table width="99%" cellspacing="0" cellpadding="0" class="searcTb" id="role_basic_panel">
          <col width="130" />
          <tr>
            <th class="fB js_sub_title" data-title="门派">门派：</th>
            <td>
              <ul class="btnList js_selected_li" style="width:960px;float:left;" id="school_list">
                <li v-for="(name, id) in schoolInfo" :key="id" 
                    :class="{on: selectedSchools.includes(id)}"
                    @click="toggleSchool(id)">
                  <span>{{name}}</span>
                </li>
              </ul>
            </td>
          </tr>
          <tr>
            <th class="fB js_sub_title" data-title="历史门派">历史门派：</th>
            <td>
              <ul class="btnList js_selected_li" style="width:960px;float:left;" id="school_change_list">
                <li v-for="(name, id) in historySchoolInfo" :key="id"
                    :class="{on: selectedHistorySchools.includes(id)}"
                    @click="toggleHistorySchool(id)">
                  <span>{{name}}</span>
                </li>
              </ul>
            </td>
          </tr>
          <tr>
            <th class="fB js_sub_title" data-title="角色">角色：</th>
            <td>
              <ul class="btnList js_selected_li" style="width:960px;float:left;" id="race_list">
                <li v-for="(name, id) in raceInfo" :key="id"
                    :class="{on: selectedRaces.includes(id)}"
                    @click="toggleRace(id)">
                  <span>{{name}}</span>
                </li>
              </ul>
            </td>
          </tr>
          <tr>
            <th class="fB js_sub_title" data-title="原始种族">原始种族：</th>
            <td>
              <ul class="btnList js_selected_li" style="width:960px;float:left;" id="ori_race_list">
                <li v-for="(name, id) in oriRaceInfo" :key="id"
                    :class="{on: selectedOriRaces.includes(id)}"
                    @click="toggleOriRace(id)">
                  <span>{{name}}</span>
                </li>
              </ul>
            </td>
          </tr>
          <tr>
            <th class="js_sub_title" data-title="人物等级">人物等级：</th>
            <td id="role_level">
              <div class="fl">
                <input type="text" v-model="levelMin" class="txt1" size="6"> - 
                <input type="text" v-model="levelMax" class="txt1" size="6">
              </div>
              <ul class="btnList" style="float:left;margin-left:20px;">
                <li v-for="level in levelShortcuts" :key="level"
                    :class="{on: levelMin == level && levelMax == level}"
                    @click="setLevel(level)">
                  <span>{{level}}级</span>
                </li>
              </ul>
            </td>
          </tr>
          <tr>
            <th class="js_sub_title" data-title="价格">价格：</th>
            <td>
              <input type="text" v-model="priceMin" class="txt1" size="7"> - 
              <input type="text" v-model="priceMax" class="txt1" size="7">
            </td>
          </tr>
          <tr>
            <th class="js_sub_title" data-title="角色总经验">角色总经验：</th>
            <td>
              <input type="text" v-model="expMin" class="txt1" size="6" />亿 - 
              <input type="text" v-model="expMax" class="txt1" size="6" />亿
            </td>
          </tr>
          <tr>
            <th class="js_sub_title" data-title="飞升/渡劫/化圣">飞升/渡劫/化圣：</th>
            <td>
              <label><input class="zhuang_zhi" type="radio" v-model="zhuangZhi" value="">不限</label>&nbsp;&nbsp;&nbsp;&nbsp;
              <label><input class="zhuang_zhi" type="radio" v-model="zhuangZhi" value="1">已飞升</label>&nbsp;&nbsp;&nbsp;&nbsp;
              <label><input class="zhuang_zhi" type="radio" v-model="zhuangZhi" value="2">已渡劫</label>&nbsp;&nbsp;&nbsp;&nbsp;
              <label><input class="zhuang_zhi" type="radio" v-model="zhuangZhi" value="10,20,30,40,50,60,70,80,90">已化圣</label>
              <label class="disabled" :class="{active: zhuangZhi === '10,20,30,40,50,60,70,80,90'}">
                <span>&nbsp;化圣境界&ge;</span>
                <select v-model="huaShengLevel" :disabled="zhuangZhi !== '10,20,30,40,50,60,70,80,90'">
                  <option value="10,20,30,40,50,60,70,80,90">不限</option>
                  <option value="10,20,30,40,50,60,70,80,90">化圣一</option>
                  <option value="20,30,40,50,60,70,80,90">化圣二</option>
                  <option value="30,40,50,60,70,80,90">化圣三</option>
                  <option value="40,50,60,70,80,90">化圣四</option>
                  <option value="50,60,70,80,90">化圣五</option>
                  <option value="60,70,80,90">化圣六</option>
                  <option value="70,80,90">化圣七</option>
                  <option value="80,90">化圣八</option>
                  <option value="90">化圣九</option>
                </select>
              </label>
            </td>
          </tr>
        </table>
      </div>
    </div>
    
    <!-- 角色属性搜索 -->
    <div class="divGride searchForm js_search_form">
      <div class="title">
        <span><a href="#" class="fB f14px" @click="resetAttributes">重置</a></span>
        <h3 class="f14px textLeft fB js_form_title" data-title="角色属性">角色属性</h3>
      </div>
      <div class="grideCont">
        <table width="99%" cellspacing="0" cellpadding="0" class="searcTb" id="role_attr_panel">
          <col width="130" />
          <tr>
            <th class="fB js_sub_title" data-title="基本属性">基本属性：</th>
            <td>
              伤害&ge; <input id="shang_hai" type="text" v-model="attributes.damage" size="6" class="txt1" />
              命中&ge; <input id="ming_zhong" type="text" v-model="attributes.hit" size="6" class="txt1" />
              灵力&ge; <input id="ling_li" type="text" v-model="attributes.magic" size="6" class="txt1" />
              防御&ge; <input id="fang_yu" type="text" v-model="attributes.defense" size="6" class="txt1" />
              气血&ge; <input id="hp" type="text" v-model="attributes.hp" size="6" class="txt1" />
              速度&ge; <input id="speed" type="text" v-model="attributes.speed" size="6" class="txt1" />
              法伤&ge; <input id="fa_shang" type="text" v-model="attributes.magicDamage" size="6" class="txt1" />
              法防&ge; <input id="fa_fang" type="text" v-model="attributes.magicDefense" size="6" class="txt1" />
            </td>
          </tr>
          <tr>
            <th class="fB js_sub_title" data-title="额外属性">额外属性：</th>
            <td>
              <div class="fl">
                潜能果数&ge; <input id="qian_neng_guo" type="text" v-model="attributes.potentialPoints" size="6" class="txt1" />
                &nbsp;
              </div>
              <ul class="btnList js_selected_li fl" id="jiyuan_and_addpoint_panel">
                <li :class="{on: attributes.hasJiYuan}" @click="toggleJiYuan">
                  <span>机缘属性</span>
                </li>
                <li :class="{on: attributes.hasAddon}" @click="toggleAddon">
                  <span>月饼粽子</span>
                </li>
              </ul>
              <div class="fl">
                &nbsp;属性总和&ge;<input type="text" v-model="attributes.totalPoints" size="6" class="txt1" id="jiyuan_and_addpoint">
              </div>
            </td>
          </tr>
          <tr>
            <th class="fB js_sub_title" data-title="属性点保存方案">属性点保存方案：</th>
            <td>
              <select v-model="attributes.pointStrategy">
                <option v-for="(name, id) in attrPointStrategy" :key="id" :value="id">{{name}}</option>
              </select>
            </td>
          </tr>
        </table>
      </div>
    </div>

    <!-- 角色修炼搜索 -->
    <div class="divGride searchForm js_search_form">
      <div class="title">
        <span><a href="#" class="fB f14px" @click="resetPractice">重置</a></span>
        <h3 class="f14px textLeft fB js_form_title" data-title="角色修炼">角色修炼</h3>
      </div>
      <div class="grideCont" style="position:relative;">
        <table width="99%" cellspacing="0" cellpadding="0" class="searcTb" id="role_expt_panel">
          <col width="130" />
          <tr>
            <th class="fB js_sub_title" data-title="角色自身修炼">角色自身修炼：</th>
            <td>
              攻击修炼&ge; <input id="expt_gongji" type="text" v-model="practice.attack" size="6" class="txt1" />&nbsp;&nbsp;&nbsp;
              防御修炼&ge; <input id="expt_fangyu" type="text" v-model="practice.defense" size="6" class="txt1" />&nbsp;&nbsp;&nbsp;
              法术修炼&ge; <input id="expt_fashu" type="text" v-model="practice.magic" size="6" class="txt1" />&nbsp;&nbsp;&nbsp;
              抗法修炼&ge; <input id="expt_kangfa" type="text" v-model="practice.magicDefense" size="6" class="txt1" />&nbsp;&nbsp;
              修炼总和&ge; <input id="expt_total" type="text" v-model="practice.total" size="6" class="txt1" />

              <div class="blank9"></div>

              攻击上限&ge; <input id="max_expt_gongji" type="text" v-model="practice.maxAttack" size="6" class="txt1" />&nbsp;&nbsp;&nbsp;
              防御上限&ge; <input id="max_expt_fangyu" type="text" v-model="practice.maxDefense" size="6" class="txt1" />&nbsp;&nbsp;&nbsp;
              法术上限&ge; <input id="max_expt_fashu" type="text" v-model="practice.maxMagic" size="6" class="txt1" />&nbsp;&nbsp;&nbsp;
              抗法上限&ge; <input id="max_expt_kangfa" type="text" v-model="practice.maxMagicDefense" size="6" class="txt1" />&nbsp;&nbsp;&nbsp;
            
              <div style="position:absolute;top:16px;right:20px;">
                猎术修炼&ge; <input id="expt_lieshu" type="text" v-model="practice.hunting" size="6" class="txt1" />
                <p class="f12px cGray textCenter">（不计入修炼总和）</p>
              </div>
            </td>
          </tr>
          <tr>
            <th class="fB js_sub_title" data-title="召唤兽控制修炼">召唤兽控制修炼：</th>
            <td style="position:relative">
              攻击控制&ge; <input id="bb_expt_gongji" type="text" v-model="practice.petAttack" size="6" class="txt1" />&nbsp;&nbsp;&nbsp;
              防御控制&ge; <input id="bb_expt_fangyu" type="text" v-model="practice.petDefense" size="6" class="txt1" />&nbsp;&nbsp;&nbsp;
              法术控制&ge; <input id="bb_expt_fashu" type="text" v-model="practice.petMagic" size="6" class="txt1" />&nbsp;&nbsp;&nbsp;
              抗法控制&ge; <input id="bb_expt_kangfa" type="text" v-model="practice.petMagicDefense" size="6" class="txt1" />&nbsp;&nbsp;
              宠修总和&ge; <input id="bb_expt_total" type="text" v-model="practice.petTotal" size="6" class="txt1" />
              <div style="position:absolute;top:16px;right:20px;">
                育兽术&ge; <input id="skill_drive_pet" type="text" v-model="practice.petTraining" size="6" class="txt1" />
                <p class="f12px cGray textCenter">（不计入宠修总和）</p>
              </div>
            </td>
          </tr>
        </table>
      </div>
    </div>

    <!-- 高级搜索按钮 -->
    <div class="blank12"></div>
    <div class="textCenter">
      <input type="button" class="btn1 btn1-more" :value="showAdvanced ? '收起高级搜索' : '高级搜索'" @click="toggleAdvanced" id="btn_advance_search_fold"/>
    </div>
    <div class="blank12"></div>

    <!-- 高级搜索内容 -->
    <div v-show="showAdvanced" id="advance_search_box">
      <!-- 角色技能 -->
      <div class="divGride searchForm js_search_form">
        <div class="title">
          <span><a href="#" class="fB f14px" @click="resetSkills">重置</a></span>
          <h3 class="f14px textLeft fB js_form_title" data-title="角色技能">角色技能</h3>
        </div>
        <div class="grideCont">
          <table width="99%" cellspacing="0" cellpadding="0" class="searcTb" id="role_skills_panel">
            <col width="100" />
            <tr>
              <th class="fB js_sub_title" data-title="师门技能">师门技能：</th>
              <td>
                任意&nbsp;
                <select v-model="skills.schoolSkillNum">
                  <option value="">不限</option>
                  <option v-for="n in 7" :key="n" :value="n">{{n}}</option>
                </select>
                &nbsp;个技能等级≥&nbsp;<input id="school_skill_level" type="text" v-model="skills.schoolSkillLevel" size="6" class="txt1" />
                &nbsp;&nbsp;
                包含符石、法宝影响:
                <label><input type="radio" v-model="skills.includeOriginal" value="1" checked> 是</label>&nbsp;&nbsp;
                <label><input type="radio" v-model="skills.includeOriginal" value="0"> 否</label>
              </td>
            </tr>
          </table>
        </div>
      </div>
    </div>

    <!-- 添加提交按钮 -->
    <div class="search-buttons">
      <el-button type="primary" @click="handleSubmit">搜索</el-button>
      <el-button @click="resetForm">重置</el-button>
    </div>

    <!-- 添加搜索结果展示区域 -->
    <el-card v-if="searchResult.length > 0" class="search-result">
      <template #header>
        <div class="card-header">
          <span>搜索结果</span>
        </div>
      </template>
      <div v-for="(item, index) in searchResult" :key="index" class="result-item">
        <pre>{{ JSON.stringify(item, null, 2) }}</pre>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'SpiderSearch',
  data() {
    return {
      // 基础信息
      selectedSchools: [],
      selectedHistorySchools: [],
      selectedRaces: [],
      selectedOriRaces: [],
      levelMin: '',
      levelMax: '',
      priceMin: '',
      priceMax: '',
      expMin: '',
      expMax: '',
      zhuangZhi: '',
      huaShengLevel: '10,20,30,40,50,60,70,80,90',

      // 角色属性
      attributes: {
        damage: '',
        hit: '',
        magic: '',
        defense: '',
        hp: '',
        speed: '',
        magicDamage: '',
        magicDefense: '',
        potentialPoints: '',
        hasJiYuan: false,
        hasAddon: false,
        totalPoints: '',
        pointStrategy: ''
      },

      // 角色修炼
      practice: {
        attack: '',
        defense: '',
        magic: '',
        magicDefense: '',
        total: '',
        maxAttack: '',
        maxDefense: '',
        maxMagic: '',
        maxMagicDefense: '',
        hunting: '',
        petAttack: '',
        petDefense: '',
        petMagic: '',
        petMagicDefense: '',
        petTotal: '',
        petTraining: ''
      },

      // 角色技能
      skills: {
        schoolSkillNum: '',
        schoolSkillLevel: '',
        includeOriginal: '1'
      },

      // 高级搜索
      showAdvanced: false,

      // 数据
      schoolInfo: window.CBG_GAME_CONFIG?.school_info || {},
      historySchoolInfo: Object.assign({}, window.CBG_GAME_CONFIG?.school_info || {}, {'99999': '无历史门派'}),
      raceInfo: window.CBG_GAME_CONFIG?.race_info || {},
      oriRaceInfo: window.AUTO_SEARCH_CONFIG?.ori_race_info || {},
      levelShortcuts: [59, 69, 89, 109, 129, 155, 159, 175],
      attrPointStrategy: window.AUTO_SEARCH_CONFIG?.attr_point_strategy || {},
      searchResult: [], // 添加搜索结果数组
    }
  },
  methods: {
    // 基础信息方法
    toggleSchool(id) {
      const index = this.selectedSchools.indexOf(id)
      if(index > -1) {
        this.selectedSchools.splice(index, 1)
      } else {
        this.selectedSchools.push(id)
      }
    },
    toggleHistorySchool(id) {
      const index = this.selectedHistorySchools.indexOf(id)
      if(index > -1) {
        this.selectedHistorySchools.splice(index, 1)
      } else {
        this.selectedHistorySchools.push(id)
      }
    },
    toggleRace(id) {
      const index = this.selectedRaces.indexOf(id)
      if(index > -1) {
        this.selectedRaces.splice(index, 1)
      } else {
        this.selectedRaces.push(id)
      }
    },
    toggleOriRace(id) {
      const index = this.selectedOriRaces.indexOf(id)
      if(index > -1) {
        this.selectedOriRaces.splice(index, 1)
      } else {
        this.selectedOriRaces.push(id)
      }
    },
    setLevel(level) {
      this.levelMin = level
      this.levelMax = level
    },
    resetBasicInfo() {
      this.selectedSchools = []
      this.selectedHistorySchools = []
      this.selectedRaces = []
      this.selectedOriRaces = []
      this.levelMin = ''
      this.levelMax = ''
      this.priceMin = ''
      this.priceMax = ''
      this.expMin = ''
      this.expMax = ''
      this.zhuangZhi = ''
      this.huaShengLevel = '10,20,30,40,50,60,70,80,90'
    },

    // 角色属性方法
    toggleJiYuan() {
      this.attributes.hasJiYuan = !this.attributes.hasJiYuan
    },
    toggleAddon() {
      this.attributes.hasAddon = !this.attributes.hasAddon
    },
    resetAttributes() {
      this.attributes = {
        damage: '',
        hit: '',
        magic: '',
        defense: '',
        hp: '',
        speed: '',
        magicDamage: '',
        magicDefense: '',
        potentialPoints: '',
        hasJiYuan: false,
        hasAddon: false,
        totalPoints: '',
        pointStrategy: ''
      }
    },

    // 角色修炼方法
    resetPractice() {
      this.practice = {
        attack: '',
        defense: '',
        magic: '',
        magicDefense: '',
        total: '',
        maxAttack: '',
        maxDefense: '',
        maxMagic: '',
        maxMagicDefense: '',
        hunting: '',
        petAttack: '',
        petDefense: '',
        petMagic: '',
        petMagicDefense: '',
        petTotal: '',
        petTraining: ''
      }
    },

    // 角色技能方法
    resetSkills() {
      this.skills = {
        schoolSkillNum: '',
        schoolSkillLevel: '',
        includeOriginal: '1'
      }
    },

    // 高级搜索方法
    toggleAdvanced() {
      this.showAdvanced = !this.showAdvanced
    },

    // 添加提交方法
    handleSubmit() {
      const formData = {}
      
      // 基本信息
      if (this.selectedSchools.length > 0) formData.school = this.selectedSchools.join(',')
      if (this.selectedHistorySchools.length > 0) formData.school_change_list = this.selectedHistorySchools.join(',')
      if (this.selectedRaces.length > 0) formData.race = this.selectedRaces.join(',')
      if (this.selectedOriRaces.length > 0) formData.ori_race = this.selectedOriRaces.join(',')
      if (this.levelMin && this.levelMax) formData.level = `${this.levelMin}-${this.levelMax}`
      if (this.priceMin && this.priceMax) formData.price = `${this.priceMin}-${this.priceMax}`
      if (this.expMin && this.expMax) formData.total_exp = `${this.expMin}-${this.expMax}亿`
      if (this.zhuangZhi) formData.role_status = this.zhuangZhi

      // 角色属性
      if (this.attributes.damage) formData.damage = this.attributes.damage
      if (this.attributes.hit) formData.hit = this.attributes.hit
      if (this.attributes.defense) formData.defense = this.attributes.defense
      if (this.attributes.speed) formData.speed = this.attributes.speed
      if (this.attributes.magic) formData.magic = this.attributes.magic
      if (this.attributes.hp) formData.hp = this.attributes.hp
      if (this.attributes.potentialPoints) formData.potential_points = this.attributes.potentialPoints
      if (this.attributes.pointStrategy) formData.attr_point_strategy = this.attributes.pointStrategy

      // 角色修炼
      if (this.practice.attack) formData.attack_cultivation = this.practice.attack
      if (this.practice.defense) formData.defense_cultivation = this.practice.defense
      if (this.practice.magic) formData.magic_cultivation = this.practice.magic
      if (this.practice.magicDefense) formData.anti_magic_cultivation = this.practice.magicDefense
      if (this.practice.maxAttack) formData.max_attack_cultivation = this.practice.maxAttack
      if (this.practice.maxDefense) formData.max_defense_cultivation = this.practice.maxDefense
      if (this.practice.maxMagic) formData.max_magic_cultivation = this.practice.maxMagic
      if (this.practice.maxMagicDefense) formData.max_anti_magic_cultivation = this.practice.maxMagicDefense
      if (this.practice.hunting) formData.hunting_cultivation = this.practice.hunting
      if (this.practice.petAttack) formData.pet_attack_cultivation = this.practice.petAttack
      if (this.practice.petDefense) formData.pet_defense_cultivation = this.practice.petDefense
      if (this.practice.petMagic) formData.pet_magic_cultivation = this.practice.petMagic
      if (this.practice.petMagicDefense) formData.pet_anti_magic_cultivation = this.practice.petMagicDefense
      if (this.practice.petTotal) formData.pet_cultivation = this.practice.petTotal
      if (this.practice.petTraining) formData.pet_training_cultivation = this.practice.petTraining

      // 角色技能
      if (this.skills.schoolSkillNum) formData.school_skill_num = this.skills.schoolSkillNum
      if (this.skills.schoolSkillLevel) formData.school_skill_level = this.skills.schoolSkillLevel
      if (this.skills.includeOriginal === '1') formData.school_skills = this.skills.schoolSkills

      // 将收集到的数据添加到搜索结果中
      this.searchResult = [formData]
    },

    // 添加重置方法
    resetForm() {
      this.selectedSchools = []
      this.selectedHistorySchools = []
      this.selectedRaces = []
      this.selectedOriRaces = []
      this.levelMin = ''
      this.levelMax = ''
      this.priceMin = ''
      this.priceMax = ''
      this.expMin = ''
      this.expMax = ''
      this.zhuangZhi = ''
      this.huaShengLevel = '10,20,30,40,50,60,70,80,90'
      this.attributes = {
        damage: '',
        hit: '',
        magic: '',
        defense: '',
        hp: '',
        speed: '',
        magicDamage: '',
        magicDefense: '',
        potentialPoints: '',
        hasJiYuan: false,
        hasAddon: false,
        totalPoints: '',
        pointStrategy: ''
      }
      this.practice = {
        attack: '',
        defense: '',
        magic: '',
        magicDefense: '',
        total: '',
        maxAttack: '',
        maxDefense: '',
        maxMagic: '',
        maxMagicDefense: '',
        hunting: '',
        petAttack: '',
        petDefense: '',
        petMagic: '',
        petMagicDefense: '',
        petTotal: '',
        petTraining: ''
      }
      this.skills = {
        schoolSkillNum: '',
        schoolSkillLevel: '',
        includeOriginal: '1'
      }
      this.showAdvanced = false
      this.searchResult = []
    }
  }
}
</script>

<style scoped>
.spider-search {
  padding: 20px;
}
.divGride {
  margin-bottom: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.title {
  padding: 10px;
  background: #f5f5f5;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title h3 {
  margin: 0;
  font-size: 16px;
}
.fB {
  font-weight: bold;
}
.f14px {
  font-size: 14px;
}
.textLeft {
  text-align: left;
}
.grideCont {
  padding: 15px;
}
.searcTb {
  width: 100%;
  border-collapse: collapse;
}
.searcTb th {
  width: 130px;
  text-align: right;
  padding-right: 15px;
  font-weight: bold;
}
.searcTb td {
  padding: 5px 0;
}
.btnList {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.btnList li {
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 3px;
  cursor: pointer;
}
.btnList li.on {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
}
.txt1 {
  border: 1px solid #ddd;
  border-radius: 3px;
  padding: 2px 5px;
}
.fl {
  float: left;
}
.blank9 {
  height: 9px;
  clear: both;
}
.blank12 {
  height: 12px;
  clear: both;
}
.f12px {
  font-size: 12px;
}
.cGray {
  color: #999;
}
.textCenter {
  text-align: center;
}
.btn1 {
  padding: 8px 20px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.btn1:hover {
  background: #40a9ff;
}
.btn1-more {
  background: #fff;
  color: #1890ff;
  border: 1px solid #1890ff;
}
.btn1-more:hover {
  background: #e6f7ff;
}
.search-buttons {
  margin-top: 20px;
  text-align: center;
}
.search-result {
  margin-top: 20px;
}
.result-item {
  margin-bottom: 10px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}
.result-item pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style> 