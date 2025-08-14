<template>
  <el-popover :data-equip-sn="$attrs.equip_sn" placement="right" :trigger="trigger" popper-class="pet-info-popover"
    v-model="visible" @show="handleShow" @hide="handleHide">
    <template #reference>
      <div class="pet-trigger" @click="handleClick">
        <slot name="trigger"></slot>
      </div>
    </template>

    <div class="tabCont" v-if="pet && visible&&pet.icon">
      <PetDetail :current_pet="pet" />
    </div>
    <div class="tabCont" v-else-if="pet && visible&&!pet.icon">
      <div class="soldDetail" id="SkillTipsBox" ref="SkillTipsBox" style="width: 320px; display: none"></div>
      <div class="cols" style="width: 280px; margin-left: -2px; margin-right: 2px">
        <template v-if="pet.action">
          <div class="thum" style="text-align: center;">
          <div class="time-key-wap"><el-image :src="getImageUrl(equipFaceImg, 'big')"
              style="width: 100px; height: 100px" referrerpolicy="no-referrer"></el-image></div>
          <p class="f14px cWhite">等级：<span class="cYellow">{{ pet.equip_level }}</span> 携带等级：{{ pet.role_grade_limit }}</p>
        </div>
        <div class="blank12"></div>
        <h4>资质</h4>
        <table class="tb02 petZiZhiTb petAttrInfo" width="100%" cellspacing="0" cellpadding="0">
          <tr>
            <th>历史灵性值：</th>
            <td>{{ pet.lx }}</td>
            <th>成长：</th>
            <td>{{ pet.growth }}</td>
          </tr>
          <tr>
            <th :class="{ enhance: enhanceInfo.is_baobao }">是否宝宝：</th>
              <td :class="{ enhance: enhanceInfo.is_baobao }">
                <span :style="`color:${pet.is_baobao === '否' ? '#FF0000' : '#00FF00'}`">
                  {{ pet.is_baobao }}
                </span>
              </td>
          </tr>
        </table>
        </template>
        <template v-else>
          <div class="thum" style="text-align: center;">
          <div class="time-key-wap"><el-image :src="getImageUrl(equipFaceImg, 'big')"
              style="width: 100px; height: 100px" referrerpolicy="no-referrer"></el-image></div>
          <p class="f14px cWhite">名字：<span class="cYellow">{{ pet.pet_name }}</span> 等级：{{ pet.pet_grade }}</p>
        </div>
        <h4>
          属性<span v-if="pet.other.color_str && pet.other.current_on_avt">(已包含梦影穿戴属性)</span>
        </h4>
        <table class="tb02" width="100%" cellspacing="0" cellpadding="0">
          <tr>
            <th>气血：</th>
            <td>{{ pet.blood }}/{{ pet.max_blood }}</td>
            <th>体质：</th>
            <td>
              {{ pet.soma }}
              <span v-if="pet.ti_zhi_add" class="color-pink">+{{ pet.ti_zhi_add }}</span>
            </td>
          </tr>
          <tr>
            <th>魔法：</th>
            <td>{{ pet.magic }}/{{ pet.max_magic }}</td>
            <th>法力：</th>
            <td>
              {{ pet.magic_powner }}
              <span v-if="pet.fa_li_add" class="color-pink">+{{ pet.fa_li_add }}</span>
            </td>
          </tr>
          <tr>
            <th>攻击：</th>
            <td>{{ pet.attack }}</td>
            <th>力量：</th>
            <td>
              {{ pet.strength }}
              <span v-if="pet.li_liang_add" class="color-pink">+{{ pet.li_liang_add }}</span>
            </td>
          </tr>
          <tr>
            <th>防御：</th>
            <td>{{ pet.defence }}</td>
            <th>耐力：</th>
            <td>
              {{ pet.endurance }}
              <span v-if="pet.nai_li_add" class="color-pink">+{{ pet.nai_li_add }}</span>
            </td>
          </tr>
          <tr>
            <th>速度：</th>
            <td>{{ pet.speed }}</td>
            <th>敏捷：</th>
            <td>
              {{ pet.smartness }}
              <span v-if="pet.min_jie_add" class="color-pink">+{{ pet.min_jie_add }}</span>
            </td>
          </tr>
          <tr>
            <template v-if="isShowNewLingli">
              <th>法伤：</th>
              <td>{{ pet.iMagDam }}</td>
            </template>
            <template v-else>
              <th>灵力：</th>
              <td>{{ pet.wakan }}</td>
            </template>
            <th>潜能：</th>
            <td>{{ pet.potential }}</td>
          </tr>
          <tr v-if="isShowNewLingli">
            <th>法防：</th>
            <td>{{ pet.iMagDef }}</td>
          </tr>
        </table>
        <div class="blank12"></div>
        <h4>资质</h4>
        <!-- <button v-if="!is_shenshou" class="identify-pet-btn" id="identify-pet-btn"
          onclick="window.petCalcInstance.display()">鉴定召唤兽</button> -->
        <table class="tb02 petZiZhiTb petAttrInfo" width="100%" cellspacing="0" cellpadding="0">
          <tr>
            <th>攻击资质：</th>
            <td>
              <span class="added_attr_wrap">
                {{ pet.attack_aptitude }}
                <span class="added_attr" v-if="pet.attack_ext">+{{ pet.attack_ext }}</span>
              </span>
            </td>
            <th>寿命：</th>
            <td>{{ pet.lifetime }}</td>
          </tr>
          <tr>
            <th>防御资质：</th>
            <td>
              <span class="added_attr_wrap">
                {{ pet.defence_aptitude }}
                <span v-if="pet.defence_ext" class="added_attr">+{{ pet.defence_ext }}</span>
              </span>
            </td>
            <th>成长：</th>
            <td>{{ pet.growth }}</td>
          </tr>
          <tr>
            <th>体力资质：</th>
            <td>
              <span class="added_attr_wrap">
                {{ pet.physical_aptitude }}
                <span v-if="pet.physical_ext" class="added_attr">+{{ pet.physical_ext }}</span>
              </span>
            </td>
            <th>五行：</th>
            <td>{{ getWuxingName(pet.five_aptitude) }}</td>
          </tr>
          <tr>
            <th>法力资质：</th>
            <td>
              <span class="added_attr_wrap">
                {{ pet.magic_aptitude }}
                <span v-if="pet.magic_ext" class="added_attr">+{{ pet.magic_ext }}</span>
              </span>
            </td>
            <th>已用元宵：</th>
            <td>{{ pet.used_yuanxiao }}</td>
          </tr>
          <tr>
            <th>速度资质：</th>
            <td>
              <span class="added_attr_wrap">
                {{ pet.speed_aptitude }}
                <span v-if="pet.speed_ext" class="added_attr">+{{ pet.speed_ext }}</span>
              </span>
            </td>
            <th>已用千金露：</th>
            <td>{{ pet.used_qianjinlu }}</td>
          </tr>
          <tr>
            <th>躲闪资质：</th>
            <td>
              <span class="added_attr_wrap">
                {{ pet.avoid_aptitude }}
                <span v-if="pet.avoid_ext" class="added_attr">+{{ pet.avoid_ext }}</span>
              </span>
            </td>
            <th>已用炼兽珍经：</th>
            <td>{{ pet.used_lianshou }}</td>
          </tr>
          <tr data-enhance='{"dir":"top","x":"auto","y":-6}' data-enhance-index="2">
            <template v-if="pet.color">
              <th>变异类型：</th>
              <td>{{ pet.color }}</td>
            </template>
            <template v-else>
              <th :class="{ enhance: enhanceInfo.is_baobao }">是否宝宝：</th>
              <td :class="{ enhance: enhanceInfo.is_baobao }">
                <span :style="`color:${pet.is_baobao === '否' ? '#FF0000' : '#00FF00'}`">
                  {{ pet.is_baobao }}
                </span>
              </td>
            </template>
            <th>已用清灵仙露：</th>
            <td>{{ pet.jinjie_cnt }}</td>
          </tr>
          <tr>
            <th>历史灵性值：</th>
            <td>{{ pet.lx }}</td>
          </tr>
        </table>
        </template>
      </div>

      <!-- 技能和特性部分 -->
      <div class="cols" style="width: 182px" data-enhance='{"dir":"top","x":"auto","y":-34}' data-enhance-index="1">
        <!-- 赐福技能 -->
        <div v-if="evolSkillList.length > 0">
          <h4>赐福技能</h4>
          <table cellspacing="0" cellpadding="0" class="tb03" id="evol_skill_grid">
            <tr v-for="(row, rowIndex) in skillRows" :key="rowIndex">
              <td v-for="(skill, skillIndex) in row" :key="skillIndex" style="position: relative">
                <template v-if="skill.hlightLight">
                  <img :src="skill.icon" width="40" height="40" :data_equip_name="skill.name"
                    :data_equip_desc="skill.desc" data_tip_box="SkillTipsBox" :data_cifu_icon="skill.cifuIcon"
                    :data_height_icon="skill.heightCifuIcon" referrerpolicy="no-referrer"
                    @mouseenter="showSkillTip($event, skill)" @mouseleave="hideSkillTip" />
                  <div class="evol_skill_icon" :data_equip_name="skill.name" :data_equip_desc="skill.desc"
                    data_tip_box="SkillTipsBox" :data_cifu_icon="skill.cifuIcon"
                    :data_height_icon="skill.heightCifuIcon"></div>
                </template>
                <template v-else>
                  <img style="filter: grayscale(100%)" :src="skill.icon" width="40" height="40"
                    :data_equip_name="skill.name" :data_equip_desc="skill.desc" data_tip_box="SkillTipsBox"
                    :data_cifu_icon="skill.cifuIcon" :data_height_icon="skill.heightCifuIcon"
                    referrerpolicy="no-referrer" @mouseenter="showSkillTip($event, skill)" @mouseleave="hideSkillTip" />
                  <div style="filter: grayscale(100%)" class="evol_skill_icon" :data_equip_name="skill.name"
                    :data_equip_desc="skill.desc" data_tip_box="SkillTipsBox" :data_cifu_icon="skill.cifuIcon"
                    :data_height_icon="skill.heightCifuIcon"></div>
                </template>
              </td>
            </tr>
          </table>
          <div class="blank12" style="clear: both"></div>
        </div>

        <!-- 技能 -->
        <h4>技能</h4>
        <div class="blank6"></div>
        <div id="pet_skill_grid_con" ref="pet_skill_grid_con"></div>
        <table cellspacing="0" cellpadding="0" class="tb03"></table>

        <!-- 特性 -->
        <div class="blank12"></div>
        <h4 v-if="pet.core_close && pet.texing && pet.texing.id !== undefined">
          特性:{{ pet.core_close }}
        </h4>
        <h4 v-else>特性</h4>

        <div v-if="pet.texing && pet.texing.id !== undefined" style="text-align: left; font-size: 12px">
          <span>{{ pet.texing.name }}：<span v-html="parseStyleInfo(pet.texing.effect)"></span></span>
        </div>
        <div v-else style="text-align: center">无</div>
      </div>

      <!-- 装备和内丹部分 -->
      <div class="cols" style="width: 218px; margin-right: -2px; margin-left: 2px">
        <div class="cols" style="width: 158px; margin: 0">
          <h4>装备</h4>
          <div class="blank6"></div>
          <table cellspacing="0" cellpadding="0" class="tb03 size50" id="pet_equip_con">
            <tr>
              <td v-for="(eItem, index) in pet.equip_list" :key="index">
                <EquipmentImage v-if="eItem && index < 3" :placement="'bottom'" :image="false"
                  :equipment="getEquipImageProps(eItem)" size="small" :popoverWidth="300" />
                <span v-else>&nbsp;</span>
              </td>
            </tr>
          </table>
        </div>
        <div class="cols" style="float: right; width: 58px; margin: 0">
          <h4>饰品</h4>
          <div class="blank6"></div>
          <table cellspacing="0" cellpadding="0" class="tb03 size50" id="pet_shipin_con">
            <tr>
              <td>
                <EquipmentImage v-if="pet.equip_list && pet.equip_list[3]" :placement="'bottom'" :image="false"
                  :equipment="getEquipImageProps(pet.equip_list[3])" :size="'small'" />
                <span v-else>&nbsp;</span>
              </td>
            </tr>
          </table>
        </div>

        <div class="blank12" style="clear: both"></div>
        <h4>内丹</h4>
        <div class="blank6"></div>
        <p v-if="!pet.neidan || pet.neidan.length === 0" class="textCenter">无</p>
        <table v-else width="100%" cellspacing="3" cellpadding="3" id="RolePetNeidan">
          <tr v-for="(item, index) in pet.neidan" :key="index">
            <td>
              <img :src="item.icon" :data_equip_name="item.name" data_skill_type="neidan" :data_equip_desc="item.desc"
                :data_equip_level="item.level" data_tip_box="SkillTipsBox" referrerpolicy="no-referrer"
                @mouseenter="showNeidanTip($event, item)" @mouseleave="hideSkillTip" />
            </td>
            <th>{{ item.name }}</th>
            <td>{{ item.level }}层</td>
          </tr>
        </table>

        <div class="blank12"></div>
        <!-- 梦影部分 -->
        <div v-if="pet.other && pet.other.avt_list && pet.other.avt_list.length">
          <h4>梦影</h4>
          <table class="tb02" width="100%" cellspacing="0" cellpadding="0">
            <tr>
              <th width="40%">梦影数量：</th>
              <td>
                <p class="fl" style="line-height: 24px">{{ pet.other.avt_list.length }}</p>
                <!-- <button v-if="pet.other.color_str" class="identify-pet-btn fr" id="identify-pet-btn"
                  @click="window.petClothEffect && window.petClothEffect.display()">穿戴效果</button> -->
              </td>
            </tr>
            <tr v-if="pet.other.color_str && pet.other.current_on_avt">
              <th width="40%" style="vertical-align: top">当前穿戴：</th>
              <td style="vertical-align: top">
                <p>{{ pet.other.current_on_avt.name }}</p>
                <p v-if="pet.other.current_on_avt.sumavt_propsk" style="color: #00ff00">
                  ({{ pet.other.current_on_avt.sumavt_propsk }}+1)
                </p>
              </td>
            </tr>
            <tr v-else>
              <th width="40%" style="padding-right: 20px">未穿戴</th>
            </tr>
          </table>
          <div class="blank12"></div>
        </div>

        <template v-if="!pet.action">
          <h4>其它</h4>
        <div class="blank6"></div>
        <table class="tb02" width="100%" cellspacing="0" cellpadding="0">
          <tr>
            <th width="50%">已用幻色丹：</th>
            <td>{{ getSummonColorDesc(pet.summon_color, pet.type_id) }}</td>
          </tr>
        </table>
        </template>
      </div>
    </div>
  </el-popover>
</template>

<script>
import EquipmentImage from './EquipmentImage.vue'
import { commonMixin } from '@/utils/mixins/commonMixin'
import { equipmentMixin } from '@/utils/mixins/equipmentMixin'
import PetDetail from './RoleInfo/PetDetail.vue'

export default {
  name: 'PetInfoPopover',
  mixins: [commonMixin, equipmentMixin],
  components: {
    EquipmentImage,
    PetDetail
  },
  props: {
    trigger: {
      type: String,
      default: 'click'
    },
    equipFaceImg: {
      type: String,
      default: ''
    },
    pet: {
      type: Object,
      required: true
    },
    enhanceInfo: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      visible: false,
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
      return this.pet.iMagDam !== undefined && this.pet.iMagDef !== undefined
    },

    // 赐福技能列表
    evolSkillList() {
      return this.pet.evol_skill_list || []
    },

    // 技能网格布局
    skillRows() {
      const numPerLine = 4
      const skillNum = this.evolSkillList.length
      let loopTimes = Math.floor(skillNum / numPerLine) + (skillNum % numPerLine ? 1 : 0)
      loopTimes = loopTimes < 3 ? 3 : loopTimes

      // 如果是天才宝宝且技能数量正好填满，增加一行
      if (this.pet.genius && skillNum === numPerLine * loopTimes) {
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
  beforeDestroy() {
    // 清理动态绑定的事件监听器
    this.cleanupDynamicEvents()
  },
  methods: {
    show_pet_skill_in_grade: window.show_pet_skill_in_grade,
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

    // 解析样式信息
    parseStyleInfo(text) {
      if (!text) return ''
      // 这里可以添加样式解析逻辑，暂时直接返回文本
      return window.parse_style_info(text, '#Y')
    },

    // 获取召唤兽颜色描述
    getSummonColorDesc(summonColor) {
      if (!summonColor) return '无'
      // 这里可以添加颜色描述逻辑，暂时直接返回颜色值
      return summonColor.toString()
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
    },
    showSkillTip(event, skill) {
      // 组装tip内容
      const tipData = {
        name: skill.name,
        desc: skill.desc || '',
        icon: skill.cifuIcon || skill.heightCifuIcon || skill.icon,
        isCifu: (skill.cifuIcon || skill.heightCifuIcon) ? true : false
      }
      // 渲染内容
      const box = this.$refs.SkillTipsBox
      if (!box) return
      box.innerHTML = `<img class="tip-skill-icon" src="${tipData.icon}" referrerpolicy="no-referrer"><div class="skill-text"><p class="cYellow${tipData.isCifu ? ' cifu-name' : ''}">${tipData.name}</p>${window.parse_style_info ? window.parse_style_info(tipData.desc, '#Y') : tipData.desc}`
      // 定位
      box.style.display = 'block'
      box.style.position = 'fixed'

      // 获取图标元素的位置信息
      const iconRect = event.target.getBoundingClientRect()

      // 计算tooltip的位置（图标正下方）
      let left = iconRect.left
      let top = iconRect.bottom + 5  // 图标下方5px的位置

      // 处理超出窗口情况
      const boxWidth = 320
      const boxHeight = 120

      // 右边界检查
      if (left + boxWidth > window.innerWidth) {
        left = window.innerWidth - boxWidth - 10
      }

      // 下边界检查，如果超出则显示在图标上方
      if (top + boxHeight > window.innerHeight) {
        top = iconRect.top - boxHeight - 5
      }

      // 左边界检查
      if (left < 0) {
        left = 10
      }

      // 上边界检查
      if (top < 0) {
        top = 10
      }

      box.style.left = left + 'px'
      box.style.top = top + 'px'
      box.style.zIndex = 9999
    },
    hideSkillTip() {
      const box = this.$refs.SkillTipsBox
      if (box) box.style.display = 'none'
    },

    // 专门处理内丹的tooltip
    showNeidanTip(event, item) {
      const neidanData = {
        name: item.name,
        desc: item.desc + (item.level ? `<br/><span style="color: #ccc; font-size: 12px;">${item.level}层</span>` : ''),
        icon: item.icon,
        isCifu: false
      }
      this.showSkillTip(event, neidanData)
    },

    // 为动态生成的技能节点绑定事件
    bindEventsForDynamicNodes() {
      const container = this.$refs.pet_skill_grid_con
      if (!container) return

      // 查找所有带有技能数据的img元素
      const skillImages = container.querySelectorAll('img[data_store_name]')
      skillImages.forEach((img) => {
        // 检查是否已经绑定过事件
        if (img.dataset.eventBound) return

        const skillName = img.getAttribute('data_store_name')
        const skillDesc = img.getAttribute('data_store_desc')
        const skillIcon = img.src

        if (skillName) {
          // 创建技能对象，模拟原有的skill结构
          const skillData = {
            name: skillName,
            desc: skillDesc,
            icon: skillIcon,
            isCifu: false
          }

          // 绑定鼠标事件
          img.addEventListener('mouseenter', (event) => {
            this.showSkillTip(event, skillData)
          })

          img.addEventListener('mouseleave', () => {
            this.hideSkillTip()
          })

          // 标记已绑定事件
          img.dataset.eventBound = 'true'
        }
      })
    },

    // 清理动态绑定的事件监听器
    cleanupDynamicEvents() {
      // 当组件销毁时，DOM节点也会被销毁，事件监听器会自动被清理
      // 这里主要是为了防止内存泄漏，将引用置空
      const container = this.$refs.pet_skill_grid_con
      if (container) {
        container.innerHTML = ''
      }
    }
  },
  watch: {
    visible(val) {
      if (val) {
        this.$nextTick(() => {
          if (this.pet.all_skill && this.show_pet_skill_in_grade ) {
            const skillNode = this.show_pet_skill_in_grade(
              this.pet.all_skill,
              this.pet.sp_skill,
              6,
              4,
              this.conf,
              this.pet
            )
            const { skill_panel_name, notice_node_name } = this.conf
            const skillPanelNode = skillNode[skill_panel_name]
            const noticeNode = skillNode[notice_node_name]

            if (skillPanelNode && this.$refs.pet_skill_grid_con) {
              skillPanelNode.forEach((node) => {
                if (node) {
                  this.$refs.pet_skill_grid_con.appendChild(node)
                }
              })

              // 为动态生成的技能节点绑定事件
              this.$nextTick(() => {
                this.bindEventsForDynamicNodes()
              })
            }

            if (noticeNode && this.$refs.pet_tip_notice_msg) {
              this.$refs.pet_tip_notice_msg.style.display = 'block'
            }
          }
        })
      }
    }

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

:global(.pet-info-popover) {
  padding: 0 !important;
  border: 2px solid #184a5e !important;
}

:global(.pet-info-popover .popper__arrow::after) {
  border-right-color: #184a5e !important;
}

/* 技能tooltip样式 */
.soldDetail {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px;
  background: #303133;
  color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  font-size: 12px;
  line-height: 1.4;
}

.tip-skill-icon {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
}

.skill-text {
  flex: 1;
}

.cYellow {
  color: #ffff00;
}

.cifu-name {
  margin: 0 0 4px 0;
  font-weight: bold;
}
</style>
