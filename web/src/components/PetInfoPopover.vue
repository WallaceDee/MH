<template>
  <el-popover placement="right" :width="500" trigger="click" popper-class="pet-info-popover soldDetail tip-for-pet"
    :visible="visible" @show="handleShow" @hide="handleHide">
    <template #reference>
      <div class="pet-trigger" @click="handleClick">
        <slot name="trigger"></slot>
      </div>
    </template>

    <div class="solidPetTip" v-if="petData">
      <div class="col1">
        <div class="thum">
          <div class="time-key-wap">
            <img :src="getImageUrl(equipFaceImg, 'big')" width="120" height="120" alt="大图"
              referrerpolicy="no-referrer" />
            <span v-if="enhanceInfo.time_lock" class="icon-time-key big-time-key"></span>
          </div>
          <p class="f14px cWhite">
            名字：<span class="cYellow">{{ petData.pet_name }}</span> 等级：{{ petData.pet_grade }}
          </p>
        </div>
        <!-- 基础属性表格 -->
        <table width="100%" class="p_table tb02" cellspacing="0" cellpadding="0">
          <tr>
            <th width="28%">气　　血：</th>
            <td width="26%">{{ petData.blood }}/{{ petData.max_blood }}</td>
            <th width="26%">体　　质：</th>
            <td width="20%">
              {{ petData.soma }}
              <span v-if="petData.ti_zhi_add" class="color-pink">+{{ petData.ti_zhi_add }}</span>
            </td>
          </tr>
          <tr>
            <th>魔　　法：</th>
            <td>{{ petData.magic }}/{{ petData.max_magic }}</td>
            <th>法　　力：</th>
            <td>
              {{ petData.magic_powner }}
              <span v-if="petData.fa_li_add" class="color-pink">+{{ petData.fa_li_add }}</span>
            </td>
          </tr>
          <tr>
            <th>攻　　击：</th>
            <td>{{ petData.attack }}</td>
            <th>力　　量：</th>
            <td>
              {{ petData.strength }}
              <span v-if="petData.li_liang_add" class="color-pink">+{{ petData.li_liang_add }}</span>
            </td>
          </tr>
          <tr>
            <th>防　　御：</th>
            <td>{{ petData.defence }}</td>
            <th>耐　　力：</th>
            <td>
              {{ petData.endurance }}
              <span v-if="petData.nai_li_add" class="color-pink">+{{ petData.nai_li_add }}</span>
            </td>
          </tr>
          <tr>
            <th>速　　度：</th>
            <td>{{ petData.speed }}</td>
            <th>敏　　捷：</th>
            <td>
              {{ petData.smartness }}
              <span v-if="petData.min_jie_add" class="color-pink">+{{ petData.min_jie_add }}</span>
            </td>
          </tr>
          <tr v-if="isShowNewLingli">
            <th>法　　伤：</th>
            <td>{{ petData.iMagDam }}</td>
            <th>潜　　能：</th>
            <td>{{ petData.potential }}</td>
          </tr>
          <tr v-else>
            <th>灵　　力：</th>
            <td>{{ petData.wakan }}</td>
            <th>潜　　能：</th>
            <td>{{ petData.potential }}</td>
          </tr>
          <tr v-if="isShowNewLingli">
            <th>法　　防：</th>
            <td>{{ petData.iMagDef }}</td>
          </tr>
        </table>

        <div class="blank12"></div>

        <!-- 资质表格 -->
        <table width="100%" class="p_table tb02 petZiZhiTb" cellpadding="0" cellspacing="0">
          <tr>
            <th width="28%">攻击资质：</th>
            <td width="26%">
              {{ petData.attack_aptitude }}
              <span v-if="petData.attack_ext" class="added_attr">+{{ petData.attack_ext }}</span>
            </td>
            <th width="26%">寿　　命：</th>
            <td width="20%">{{ petData.lifetime }}</td>
          </tr>
          <tr>
            <th>防御资质：</th>
            <td>
              {{ petData.defence_aptitude }}
              <span v-if="petData.defence_ext" class="added_attr">+{{ petData.defence_ext }}</span>
            </td>
            <th>成　　长：</th>
            <td>{{ petData.growth }}</td>
          </tr>
          <tr>
            <th>体力资质：</th>
            <td>
              {{ petData.physical_aptitude }}
              <span v-if="petData.physical_ext" class="added_attr">+{{ petData.physical_ext }}</span>
            </td>
            <th>五　　行：</th>
            <td>{{ getWuxingName(petData.five_aptitude) }}</td>
          </tr>
          <tr v-if="petData.color">
            <th>法力资质：</th>
            <td>
              {{ petData.magic_aptitude }}
              <span v-if="petData.magic_ext" class="added_attr">+{{ petData.magic_ext }}</span>
            </td>
            <th>变异类型：</th>
            <td colspan="3">{{ petData.color }}</td>
          </tr>
          <tr v-else>
            <th>法力资质：</th>
            <td>
              {{ petData.magic_aptitude }}
              <span v-if="petData.magic_ext" class="added_attr">+{{ petData.magic_ext }}</span>
            </td>
            <th :class="{ enhance: enhanceInfo.is_baobao }">是否宝宝：</th>
            <td :class="{ enhance: enhanceInfo.is_baobao }" colspan="3">
              <span :style="{ color: petData.is_baobao === '否' ? '#FF0000' : '#00FF00' }">
                {{ petData.is_baobao }}
              </span>
            </td>
          </tr>
          <tr>
            <th>速度资质：</th>
            <td>
              {{ petData.speed_aptitude }}
              <span v-if="petData.speed_ext" class="added_attr">+{{ petData.speed_ext }}</span>
            </td>
            <th class="nowrap">历史灵性值：</th>
            <td>{{ petData.lx }}</td>
          </tr>
          <tr>
            <th>躲闪资质：</th>
            <td colspan="3">
              {{ petData.avoid_aptitude }}
              <span v-if="petData.avoid_ext" class="added_attr">+{{ petData.avoid_ext }}</span>
            </td>
          </tr>
          <tr v-if="!isShowNewLingli">
            <td colspan="4">
              <p class="cRed">游戏内灵力数值已调整，请以详情页数值为准</p>
            </td>
          </tr>
        </table>

        <p v-if="enhanceInfo.time_lock" class="tips-time-lock-tips">
          请注意，购买该物品将带有{{ enhanceInfo.time_lock_days || '90' }}天转服时间锁
        </p>
      </div>

      <div class="col2">
        <div class="tabCont">
          <div class="p_info">
            <!-- 赐福技能 -->
            <div v-if="evolSkillList && evolSkillList.length > 0">
              <h4>赐福技能</h4>
              <table cellspacing="0" cellpadding="0" class="tb03">
                <tr v-for="(row, rowIndex) in skillRows" :key="rowIndex">
                  <td v-for="(skill, skillIndex) in row" :key="skillIndex" style="position: relative">
                    <img :src="skill.icon" :style="{ filter: skill.hlightLight ? 'none' : 'grayscale(100%)' }"
                      width="40" height="40" referrerpolicy="no-referrer" />
                    <div :class="skill.hlightLight ? 'evol_skill_icon' : ''"
                      :style="{ filter: skill.hlightLight ? 'none' : 'grayscale(100%)' }"></div>
                  </td>
                </tr>
              </table>
              <div class="blank12" style="clear: both"></div>
            </div>

            <!-- v-html="show_pet_skill_in_grade((petData.all_skill, petData.sp_skill, 3, 4, conf, petData))" -->
            <!-- 技能 -->
            <h4>技能</h4>
            <div ref="pet_tip_skill_grid" id="pet_tip_skill_grid" class="textCenter"></div>
            <p ref="pet_tip_notice_msg" class="cYellow textCenter" id="pet_tip_notice_msg"
              style="display: none; margin-top: 5px">
              更多技能查看详细页面&raquo;
            </p>
          </div>

          <!-- 内丹 -->
          <div v-if="petData.neidan && petData.neidan.length > 0" class="p_info">
            <h4>内丹</h4>
            <table width="100%" cellspacing="3" cellpadding="3" id="RolePetNeidan">
              <tr v-for="(item, index) in petData.neidan" :key="index">
                <td>
                  <img :src="item.icon" :data_equip_name="item.name" data_skill_type="neidan"
                    :data_equip_desc="item.desc" :data_equip_level="item.level" data_tip_box="SkillTipsBox"
                    referrerpolicy="no-referrer" />
                </td>
                <th>{{ item.name }}</th>
                <td>{{ item.level }}层</td>
              </tr>
            </table>
          </div>
          <div v-else-if="'neidan' in petData" class="p_info">
            <h4>内丹</h4>
            <p class="textCenter">无</p>
          </div>
        </div>
      </div>
    </div>
  </el-popover>
</template>

<script>
export default {
  name: 'PetInfoPopover',
  props: {
    petData: {
      type: Object,
      required: true
    },
    equipFaceImg: {
      type: String,
      default: ''
    },
    enhanceInfo: {
      type: Object,
      default: () => ({})
    },
    visible: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      conf: {
        pet_skill_url: 'https://cbg-xyq.res.netease.com/images/skill/',
        notice_node_name: 'pet_tip_notice_msg',
        skill_panel_name: 'pet_tip_skill_grid',
        table_class: 'tb03',
        enhance_skills: this.enhanceInfo.skill_id_list || []
      }
    }
  },
  emits: ['show', 'hide', 'click'],
  computed: {
    // 判断是否显示新版灵力
    isShowNewLingli() {
      return this.petData.iMagDam !== undefined && this.petData.iMagDef !== undefined
    },

    // 赐福技能列表
    evolSkillList() {
      return this.petData.evol_skill_list || []
    },

    // 技能网格布局
    skillRows() {
      const numPerLine = 4
      const skillNum = this.evolSkillList.length
      let loopTimes = Math.floor(skillNum / numPerLine) + (skillNum % numPerLine ? 1 : 0)
      loopTimes = loopTimes < 3 ? 3 : loopTimes

      // 如果是天才宝宝且技能数量正好填满，增加一行
      if (this.petData.genius && skillNum === numPerLine * loopTimes) {
        loopTimes += 1
      }

      const rows = []
      for (let i = 0; i < loopTimes; i++) {
        const items = this.evolSkillList.slice(i * numPerLine, (i + 1) * numPerLine)
        rows.push(items)
      }

      return rows
    }
  },
  methods: {
    show_pet_skill_in_grade: window.show_pet_skill_in_grade,
    getImageUrl(imageName, size = 'small') {
      return `https://cbg-xyq.res.netease.com/images/${size}/${imageName}`
    },
    // 获取五行名称
    getWuxingName(fiveAptitude) {
      const wuxingInfo = {
        0: '未知',
        1: '金',
        2: '木',
        4: '土',
        8: '水',
        16: '火'
      }
      return wuxingInfo[fiveAptitude] || '未知'
    },

    // 处理点击事件
    handleClick() {
      this.$emit('click')
    },

    // 处理显示事件
    handleShow() {
      this.$emit('show')
    },

    // 处理隐藏事件
    handleHide() {
      this.$emit('hide')
    }
  },
  mounted() {
    this.$nextTick(() => {
      const skillNode = this.show_pet_skill_in_grade(this.petData.all_skill, this.petData.sp_skill, 4, 4, this.conf, this.petData)
      const { skill_panel_name, notice_node_name } = this.conf
      const skillPanelNode = skillNode[skill_panel_name]
      const noticeNode = skillNode[notice_node_name]
      skillPanelNode.forEach(node => {
        if (node) {
          this.$refs.pet_tip_skill_grid.appendChild(node)
        }
      })
      if (noticeNode) {
        this.$refs.pet_tip_notice_msg.style.display = 'block'
      }
    })
  }
}
</script>

<style scoped>
/* 触发器样式 */
.pet-trigger {
  cursor: pointer;
}

.default-trigger {
  display: inline-block;
}
:global(.pet-info-popover .popper__arrow::after){
  border-right-color: #184a5e!important;
}
</style>
