<template>
    <!-- 召唤兽详细信息 -->
    <div class="hasLayout">
        <h4>
            详细信息
            <span v-if="
                current_pet.other &&
                current_pet.other.color_str &&
                current_pet.other.current_on_avt
            ">(已包含梦影穿戴属性)</span>
        </h4>
        <div class="blank9"></div>
        <table v-if="current_pet.is_child && current_pet.isnew" class="tb02" width="100%" cellspacing="0"
            cellpadding="0">
            <tr>
                <td width="152"><strong>类型：</strong>{{ current_pet.kind }}</td>
                <td width="150"><strong>气血：</strong>{{ current_pet.blood_max }}</td>
                <td width="150"><strong>根骨：</strong>{{ current_pet.gg }}</td>
            </tr>
            <tr>
                <td><strong>等级：</strong>{{ current_pet.pet_grade }}</td>
                <td><strong>魔法：</strong>{{ current_pet.magic_max }}</td>
                <td><strong>智力：</strong>{{ current_pet.zl }}</td>
            </tr>
            <tr>
                <td><strong>悟性：</strong>{{ current_pet.child_sixwx }}</td>
                <td><strong>攻击：</strong>{{ current_pet.attack }}</td>
                <td><strong>武力：</strong>{{ current_pet.wl }}</td>
            </tr>
            <tr>
                <td><strong>门派：</strong>{{ current_pet.school }}</td>
                <td><strong>防御：</strong>{{ current_pet.defence }}</td>
                <td><strong>定力：</strong>{{ current_pet.dl }}</td>
            </tr>
            <tr>
                <td><strong>五行：</strong>{{ current_pet.wu_xing }}</td>
                <td><strong>速度：</strong>{{ current_pet.speed }}</td>
                <td><strong>念力：</strong>{{ current_pet.nl }}</td>
            </tr>
            <tr>
                <td><strong>结局：</strong>{{ current_pet.ending }}</td>
                <td><strong>法伤：</strong>{{ current_pet.iMagDam_all }}</td>
                <td><strong>灵敏：</strong>{{ current_pet.lm }}</td>
            </tr>
            <tr>
                <td></td>
                <td><strong>法防：</strong>{{ current_pet.ling_li }}</td>
                <td></td>
            </tr>
        </table>
        <table v-else class="tb02 petZiZhiTb" width="100%" cellspacing="0" cellpadding="0">
            <tr>
                <td><strong>类型：</strong>{{ current_pet.kind }}</td>
                <td><strong>等级：</strong>{{ current_pet.pet_grade }}</td>
                <td v-if="current_pet.color">
                    <strong>变异类型：</strong>{{ current_pet.color }}
                </td>
                <td v-else>
                    <strong>是否宝宝：</strong>
                    <span :style="{ color: current_pet.is_baobao === '否' ? '#FF0000' : '#00FF00' }">
                        {{ current_pet.is_baobao }}
                    </span>
                </td>
            </tr>
            <tr>
                <td><strong>气血：</strong>{{ current_pet.blood_max }}</td>
                <td>
                    <strong>体质：</strong>
                    {{ current_pet.ti_zhi }}
                    <span v-if="current_pet.ti_zhi_add" class="color-pink">+{{ current_pet.ti_zhi_add }}</span>
                </td>
                <td>
                    <strong>攻击资质：</strong>
                    {{ current_pet.gong_ji_zz }}
                    <span v-if="current_pet.gong_ji_ext" class="added_attr">+{{ current_pet.gong_ji_ext }}</span>
                </td>
            </tr>
            <tr>
                <td><strong>魔法：</strong>{{ current_pet.magic_max }}</td>
                <td>
                    <strong>法力：</strong>
                    {{ current_pet.fa_li }}
                    <span v-if="current_pet.fa_li_add" class="color-pink">+{{ current_pet.fa_li_add }}</span>
                </td>
                <td>
                    <strong>防御资质：</strong>
                    {{ current_pet.fang_yu_zz }}
                    <span v-if="current_pet.fang_yu_ext" class="added_attr">+{{ current_pet.fang_yu_ext }}</span>
                </td>
            </tr>
            <tr>
                <td><strong>攻击：</strong>{{ current_pet.attack }}</td>
                <td>
                    <strong>力量：</strong>
                    {{ current_pet.li_liang }}
                    <span v-if="current_pet.li_liang_add" class="color-pink">+{{ current_pet.li_liang_add }}</span>
                </td>
                <td>
                    <strong>体力资质：</strong>
                    {{ current_pet.ti_li_zz }}
                    <span v-if="current_pet.ti_li_ext" class="added_attr">+{{ current_pet.ti_li_ext }}</span>
                </td>
            </tr>
            <tr>
                <td><strong>防御：</strong>{{ current_pet.defence }}</td>
                <td>
                    <strong>耐力：</strong>
                    {{ current_pet.nai_li }}
                    <span v-if="current_pet.nai_li_add" class="color-pink">+{{ current_pet.nai_li_add }}</span>
                </td>
                <td>
                    <strong>法力资质：</strong>
                    {{ current_pet.fa_li_zz }}
                    <span v-if="current_pet.fa_li_ext" class="added_attr">+{{ current_pet.fa_li_ext }}</span>
                </td>
            </tr>
            <tr>
                <td><strong>速度：</strong>{{ current_pet.speed }}</td>
                <td>
                    <strong>敏捷：</strong>
                    {{ current_pet.min_jie }}
                    <span v-if="current_pet.min_jie_add" class="color-pink">+{{ current_pet.min_jie_add }}</span>
                </td>
                <td>
                    <strong>速度资质：</strong>
                    {{ current_pet.su_du_zz }}
                    <span v-if="current_pet.su_du_ext" class="added_attr">+{{ current_pet.su_du_ext }}</span>
                </td>
            </tr>
            <tr>
                <td v-if="isShowNewLingli"><strong>法伤：</strong>{{ current_pet.iMagDam }}</td>
                <td v-else><strong>灵力：</strong>{{ current_pet.ling_li }}</td>
                <td><strong>潜能：</strong>{{ current_pet.qian_neng }}</td>
                <td>
                    <strong>躲闪资质：</strong>
                    {{ current_pet.duo_shan_zz }}
                    <span v-if="current_pet.duo_shan_ext" class="added_attr">+{{ current_pet.duo_shan_ext }}</span>
                </td>
            </tr>
            <tr>
                <td v-if="isShowNewLingli"><strong>法防：</strong>{{ current_pet.iMagDef }}</td>
                <td v-else><strong>寿命：</strong>{{ current_pet.lifetime }}</td>
                <td><strong>成长：</strong>{{ current_pet.cheng_zhang }}</td>
                <td><strong>五行：</strong>{{ current_pet.wu_xing }}</td>
            </tr>
            <tr>
                <td><strong>已用元宵：</strong>{{ current_pet.used_yuanxiao }}</td>
                <td><strong>已用千金露：</strong>{{ current_pet.used_qianjinlu }}</td>
            </tr>
            <tr>
                <td>
                    <strong v-if="current_pet.is_child">悟性：</strong>
                    <span v-if="current_pet.is_child && current_pet.child_sixwx !== undefined">{{
                        current_pet.child_sixwx
                        }}</span>
                    <span v-else-if="current_pet.is_child">无</span>
                    <strong v-else>已用炼兽珍经：</strong>
                    <span v-if="!current_pet.is_child">{{ current_pet.used_lianshou }}</span>
                </td>
                <td>
                    <strong>已使用幻色丹：</strong>{{ getSummonColorDesc(current_pet.summon_color, current_pet.type_id) }}
                </td>
                <td>
                    <strong>历史灵性值：</strong>{{ getDictValue(current_pet.jinjie, 'lx', 0) }}
                </td>
            </tr>
            <tr>
                <td>
                    <strong>已用清灵仙露：</strong>{{ getDictValue(current_pet.jinjie, 'cnt', 0) }}
                </td>
                <td v-if="isShowNewLingli"><strong>寿命：</strong>{{ current_pet.lifetime }}</td>
                <td></td>
            </tr>
        </table>

        <div class="blank9"></div>
        <div class="hasLayout">
            <div class="soldDetail" id="RoleSkillTipsBox" ref="RoleSkillTipsBox" style="width: 320px; display: none">
            </div>
            <div class="cols" style="width: 210px; margin: 0">
                <!-- 赐福技能 -->
                <h4 v-if="current_pet.evol_skill_list">赐福技能</h4>
                <div class="blank9"></div>
                <table v-if="current_pet.evol_skill_list" cellspacing="0" cellpadding="0" class="tb03" id="RolePetCifu">
                    <tr v-for="(row, rowIndex) in evolSkillRows" :key="rowIndex">
                        <td v-for="(skill, colIndex) in row" :key="colIndex" style="position: relative">
                            <img referrerpolicy="no-referrer" v-if="skill.hlightLight" :src="skill.icon" width="40"
                                height="40" :data_equip_name="skill.name" data_skill_type="cifu"
                                :data_equip_desc="skill.desc" data_tip_box="RoleSkillTipsBox"
                                :data_cifu_icon="skill.cifuIcon" :data_height_icon="skill.heightCifuIcon"
                                @mouseenter="showSkillTip($event, skill)" @mouseleave="hideSkillTip" />
                            <img referrerpolicy="no-referrer" v-else style="filter: grayscale(100%)" :src="skill.icon"
                                width="40" height="40" :data_equip_name="skill.name" data_skill_type="cifu"
                                :data_equip_desc="skill.desc" data_tip_box="RoleSkillTipsBox"
                                :data_cifu_icon="skill.cifuIcon" :data_height_icon="skill.heightCifuIcon"
                                @mouseenter="showSkillTip($event, skill)" @mouseleave="hideSkillTip" />
                            <div v-if="skill.hlightLight" :data_src="skill.icon" class="evol_skill_icon"
                                :data_equip_name="skill.name" data_skill_type="cifu" :data_equip_desc="skill.desc"
                                data_tip_box="RoleSkillTipsBox" :data_cifu_icon="skill.cifuIcon"
                                :data_height_icon="skill.heightCifuIcon"></div>
                            <div v-else style="filter: grayscale(100%)" :data_src="skill.icon" class="evol_skill_icon"
                                :data_equip_name="skill.name" data_skill_type="cifu" :data_equip_desc="skill.desc"
                                data_tip_box="RoleSkillTipsBox" :data_cifu_icon="skill.cifuIcon"
                                :data_height_icon="skill.heightCifuIcon"></div>
                        </td>
                    </tr>
                </table>
                <div v-if="current_pet.evol_skill_list" class="blank12" style="clear: both"></div>

                <!-- 技能 -->
                <h4>技能</h4>
                <div class="blank9"></div>
                <table cellspacing="0" cellpadding="0" class="tb03" id="RolePetSkill">
                    <tr v-for="(row, rowIndex) in petSkillRows" :key="rowIndex">
                        <td v-for="(skill, colIndex) in row" :key="colIndex" style="position: relative">
                            <img referrerpolicy="no-referrer" :src="skill.icon" width="40" height="40"
                                :data_equip_name="skill.name" data_skill_type="cifu" :data_equip_desc="skill.desc"
                                data_tip_box="RoleSkillTipsBox" :data_is_super_skill="skill.isSuperSkill"
                                @mouseenter="showSkillTip($event, skill)" @mouseleave="hideSkillTip" />
                            <div v-if="skill.hashEvol" :data_src="skill.icon" class="evol_skill_icon"
                                :data_equip_name="skill.name" data_skill_type="cifu" :data_equip_desc="skill.desc"
                                data_tip_box="RoleSkillTipsBox" :data_is_super_skill="skill.isSuperSkill"></div>
                        </td>
                        <template v-for="i in 4 - row.length">
                            <td v-if="
                                i === 4 - row.length &&
                                rowIndex === petSkillRows.length - 1 &&
                                current_pet.genius
                            " :key="'genius-' + i">
                                <img referrerpolicy="no-referrer" class="on" :src="current_pet.genius_skill.icon"
                                    :data_equip_name="current_pet.genius_skill.name" data_skill_type="cifu"
                                    :data_equip_desc="current_pet.genius_skill.desc" data_tip_box="RoleSkillTipsBox"
                                    :data_is_super_skill="current_pet.genius_skill.isSuperSkill"
                                    @mouseenter="showSkillTip($event, current_pet.genius_skill)"
                                    @mouseleave="hideSkillTip" />
                            </td>
                            <td v-else :key="'empty-' + i"></td>
                        </template>
                    </tr>
                </table>

                <template v-if="!current_pet.is_child">
                    <div class="blank9"></div>
                    <h4 v-if="
                        current_pet.core_close &&
                        getDictValue(current_pet.jinjie, 'core', {}).id !== undefined
                    ">
                        特性:{{ current_pet.core_close }}
                    </h4>
                    <h4 v-else>特性</h4>
                    <div v-if="getDictValue(current_pet.jinjie, 'core', {}).id !== undefined" style="text-align: left">
                        <span>{{ getDictValue(current_pet.jinjie, 'core', {}).name }}：<span v-html="parseStyleInfo(getDictValue(current_pet.jinjie, 'core', {}).effect)
                            "></span></span>
                    </div>
                    <div v-else style="text-align: center">无</div>
                </template>
            </div>

            <div class="cols" style="float: right; width: 232px; margin: 0">
                <div v-if="!current_pet.is_child" class="cols" style="width: 160px; margin: 0">
                    <h4>装备</h4>
                    <div class="blank6"></div>
                    <table cellspacing="0" cellpadding="0" class="tb03 size50" id="RolePetEquips">
                        <tr>
                            <td v-for="(equip, index) in current_pet.equip_list" :key="index">
                                <ItemPopover v-if="equip" :equipment="{
                                    equip_face_img: equip.icon,
                                    equip_name: equip.name,
                                    large_equip_desc: equip.desc,
                                    equip_type_desc: equip.static_desc
                                }" placement="top" />
                                <span v-else>&nbsp;</span>
                            </td>
                        </tr>
                    </table>
                </div>

                <div v-if="!current_pet.is_child" class="cols" style="float: right; width: 60px; margin: 0">
                    <h4>饰品</h4>
                    <div class="blank6"></div>
                    <table cellspacing="0" cellpadding="0" class="tb03 size50" id="RolePetShipin">
                        <tr>
                            <td>
                                <img referrerpolicy="no-referrer"
                                    v-if="current_pet.shipin_list && current_pet.shipin_list[0]" style="
                              max-width: 50px;
                              max-height: 50px;
                              background: #fff;
                              border-radius: 5px;
                            " :src="current_pet.shipin_list[0].icon" :data_equip_name="current_pet.shipin_list[0].name"
                                    :data_equip_type="current_pet.shipin_list[0].type"
                                    :data_equip_desc="current_pet.shipin_list[0].desc" data_equip_type_desc=""
                                    :lock_types="current_pet.shipin_list[0].lock_type" />
                                <span v-else>&nbsp;</span>
                            </td>
                        </tr>
                    </table>
                </div>
                <template v-if="!current_pet.is_child">
                    <div class="blank12" style="clear: both"></div>
                    <h4>内丹</h4>
                    <div class="blank9"></div>
                    <p v-if="current_pet.neidan.length === 0" class="textCenter">无</p>
                    <table v-else width="100%" cellspacing="3" cellpadding="3" id="RolePetNeidan">
                        <tr v-for="(item, index) in current_pet.neidan" :key="index">
                            <td>
                                <img referrerpolicy="no-referrer" :src="item.icon" :data_equip_name="item.name"
                                    data_skill_type="neidan" :data_equip_desc="item.desc" :data_equip_level="item.level"
                                    data_tip_box="SkillTipsBox" @mouseenter="showNeidanTip($event, item)"
                                    @mouseleave="hideSkillTip" />
                            </td>
                            <th>{{ item.name }}</th>
                            <td>{{ item.level }}层</td>
                        </tr>
                    </table>
                </template>

                <!-- 梦影 -->
                <div v-if="
                    current_pet.other &&
                    current_pet.other.avt_list &&
                    current_pet.other.avt_list.length
                " class="blank12"></div>
                <h4 v-if="
                    current_pet.other &&
                    current_pet.other.avt_list &&
                    current_pet.other.avt_list.length
                ">
                    梦影
                </h4>
                <table v-if="
                    current_pet.other &&
                    current_pet.other.avt_list &&
                    current_pet.other.avt_list.length
                " class="tb02" width="100%" cellspacing="0" cellpadding="0">
                    <tr>
                        <th width="40%">梦影数量：</th>
                        <td>
                            <p class="fl" style="line-height: 24px">
                                {{ current_pet.other.avt_list.length }}
                            </p>
                            <button v-if="current_pet.other.color_str" class="identify-pet-btn fr" id="identify-pet-btn"
                                @click="window.petClothEffect.display()">
                                穿戴效果
                            </button>
                        </td>
                    </tr>
                    <tr v-if="current_pet.other.color_str && current_pet.other.current_on_avt">
                        <th width="40%" style="vertical-align: top">当前穿戴：</th>
                        <td style="vertical-align: top">
                            <p>{{ current_pet.other.current_on_avt.name }}</p>
                            <p v-if="current_pet.other.current_on_avt.sumavt_propsk" style="color: #00ff00">
                                ({{ current_pet.other.current_on_avt.sumavt_propsk }}+1)
                            </p>
                        </td>
                    </tr>
                    <tr v-else>
                        <th width="40%" style="padding-right: 20px">未穿戴</th>
                        <td></td>
                    </tr>
                </table>
            </div>
        </div>
    </div>
</template>
<script>
import ItemPopover from './ItemPopover.vue'
export default {
    name: 'PetDetail',
    props: {
        current_pet: {
            type: Object,
            required: true
        }
    },
    components: {
        ItemPopover
    },
    computed: {
        // 召唤兽详细信息相关计算属性
        isShowNewLingli() {
            return (
                this.current_pet &&
                this.current_pet.iMagDam !== undefined &&
                this.current_pet.iMagDef !== undefined
            )
        },
        evolSkillRows() {
            if (!this.current_pet || !this.current_pet.evol_skill_list) return []
            const numPerLine = 4
            const skills = this.current_pet.evol_skill_list
            const skillNum = skills.length
            let loopTimes = parseInt(skillNum / numPerLine) + (skillNum % numPerLine ? 1 : 0)
            loopTimes = loopTimes < 3 ? 3 : loopTimes

            const rows = []
            for (let i = 0; i < loopTimes; i++) {
                const items = skills.slice(i * numPerLine, (i + 1) * numPerLine)
                rows.push(items)
            }
            return rows
        },
        petSkillRows() {
            if (!this.current_pet || !this.current_pet.skill_list) return []
            const numPerLine = 4
            const skills = this.current_pet.skill_list
            const skillNum = skills.length
            let loopTimes = parseInt(skillNum / numPerLine) + (skillNum % numPerLine ? 1 : 0)
            loopTimes = loopTimes < 3 ? 3 : loopTimes

            if (this.current_pet.genius) {
                if (skillNum === numPerLine * loopTimes) {
                    loopTimes = loopTimes + 1
                }
            }

            const rows = []
            for (let i = 0; i < loopTimes; i++) {
                const items = skills.slice(i * numPerLine, (i + 1) * numPerLine)
                rows.push(items)
            }
            return rows
        },

    },
    methods: {


        // 解析样式信息
        parseStyleInfo(text) {
            if (!text) return ''
            // 这里可以添加样式解析逻辑，暂时直接返回文本
            return window.parse_style_info(text, '#Y')
        },

        // 技能提示相关方法
        showSkillTip(event, skill) {
            // 组装tip内容
            const tipData = {
                name: skill.name,
                desc: skill.desc || '',
                icon: skill.cifuIcon || skill.heightCifuIcon || skill.icon,
                isCifu: skill.cifuIcon || skill.heightCifuIcon ? true : false
            }
            // 渲染内容
            const box = this.$refs.RoleSkillTipsBox
            if (!box) return
            box.innerHTML = `<img class="tip-skill-icon" src="${tipData.icon
                }" referrerpolicy="no-referrer"><div class="skill-text"><p class="cYellow${tipData.isCifu ? ' cifu-name' : ''
                }">${tipData.name}</p>${window.parse_style_info ? window.parse_style_info(tipData.desc, '#Y') : tipData.desc
                }`
            // 定位
            box.style.display = 'block'
            box.style.position = 'fixed'

            // 获取图标元素的位置信息
            const iconRect = event.target.getBoundingClientRect()

            // 计算tooltip的位置（图标正下方）
            let left = iconRect.left
            let top = iconRect.bottom + 5 // 图标下方5px的位置

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
            const box = this.$refs.RoleSkillTipsBox
            if (box) box.style.display = 'none'
        },

        // 专门处理内丹的tooltip
        showNeidanTip(event, item) {
            this.showSkillTip(event, item)
        },
        // 召唤兽详细信息相关方法
        getDictValue(obj, key, defaultValue) {
            if (!obj || typeof obj !== 'object') return defaultValue
            return obj[key] !== undefined ? obj[key] : defaultValue
        },

        getSummonColorDesc(summonColor) {
            // 这里需要实现get_summon_color_desc的逻辑
            // 暂时返回原值，实际项目中需要根据具体逻辑实现
            return summonColor || '无'
        },

    }
}
</script>