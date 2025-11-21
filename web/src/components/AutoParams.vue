<template>
    <el-card class="spider-system-card" shadow="never">
        <el-row slot="header" class="card-header" type="flex" justify="space-between" align="middle">
            <div><span class="emoji-icon">⚙️</span> 搜索配置</div>
            <div class="tool-buttons">
                <el-dropdown split-button type="danger" @click="stopTask" v-if="!isChromeExtension">
                    🛑 停止
                    <el-dropdown-menu slot="dropdown">
                        <el-dropdown-item @click.native="resetTask">🛑 重置任务</el-dropdown-item>
                    </el-dropdown-menu>
                </el-dropdown>
                <el-button type="danger" @click="stopTask" v-else>🛑 停止</el-button>
            </div>
        </el-row>
        <el-row type="flex">
            <div style="width: 140px;text-align: center;">
                <template v-if="externalParamsState.action">
                    <el-col :span="24">
                        <p class="cBlue" style="margin-bottom: 5px;">🎯目标：</p>
                    </el-col>
                    <EquipmentImage v-if="externalParamsState.action === 'similar_equip'"
                        :equipment="externalParamsState" :popoverWidth="450"
                        style="display: flex;flex-direction: column;height: 50px;width: 100%;align-items: center;" />
                    <PetImage v-if="externalParamsState.action === 'similar_pet'" :pet="externalParamsState"
                        :equipFaceImg="externalParamsState.equip_face_img" />
                </template>
            </div>
            <!-- 全局设置 -->
            <el-form style="width: 100%;flex-shrink: 1;" :model="globalSettings" v-show="activeTab !== 'playwright'">
                <el-row :gutter="40">
                    <el-col :span="6">
                        <el-form-item label="📄 搜索页数" size="small">
                            <el-input-number v-model="globalSettings.max_pages" :min="1" :max="100"
                                controls-position="right" style="width: 100%"></el-input-number>
                        </el-form-item>
                    </el-col>
                    <el-col :span="8">
                        <el-form-item :label="`⏱️ 延迟范围：${globalSettings.delay_min} - ${globalSettings.delay_max} 秒`"
                            size="small">
                            <el-slider v-model="delayRange" range show-stops :min="8" :max="30" :step="1"
                                @change="onDelayRangeChange" style="width: 100%;display: inline-block;">
                            </el-slider>
                        </el-form-item>
                    </el-col>
                    <el-col :span="10">
                        <el-form-item label="⚡ 快速配置" size="small" style="width: 100%;">
                            <br>
                            <el-row type="flex" align="middle" style="height:32px;">
                                <el-tag size="mini" @click="quickConfig('small')" style="cursor: pointer;">10页</el-tag>
                                <el-divider direction="vertical"></el-divider>
                                <el-tag size="mini" @click="quickConfig('medium')" style="cursor: pointer;">50页</el-tag>
                                <el-divider direction="vertical"></el-divider>
                                <el-tag size="mini" @click="quickConfig('large')" style="cursor: pointer;">100页</el-tag>
                            </el-row>
                        </el-form-item></el-col>
                </el-row>
                <el-row type="flex" align="middle" v-if="activeTab !== 'role'">
                    <el-col :span="12">
                        <el-row type="flex">
                            <el-form-item label="🌎 全服搜索" size="small" style="width: 150px;">
                                <el-switch v-model="globalSettings.overall"></el-switch>
                            </el-form-item>
                            <el-form-item v-if="!globalSettings.overall" label=" 多区搜索" size="small"
                                style="width: 150px;">
                                <el-switch v-model="globalSettings.multi"></el-switch>
                            </el-form-item>
                        </el-row>
                    </el-col>
                    <el-col v-if="!globalSettings.overall" :span="12">
                        <el-form-item label="🎯 目标服务器" size="small">
                            <el-cascader v-show="globalSettings.multi" :options="hotServers" :props="{
                                value: 'server_id', label: 'server_name', multiple: true,
                                emitPath: false
                            }" collapse-tags size="mini" filterable v-model="target_server_list"
                                @change="onTargetServerChange" />
                            <el-cascader v-show="!globalSettings.multi" :options="server_data" size="mini" filterable
                                v-model="server_data_value" clearable @change="onServerDataChange" />
                        </el-form-item>
                    </el-col>
                </el-row>
                <el-row type="flex" align="middle">
                    <el-form-item label="最低价格" size="small">
                        <el-switch v-model="price_min_enable"> </el-switch>
                        <el-input-number v-model="price_min" :min="10" :controls="false" style="margin-left: 5px;">
                        </el-input-number>
                    </el-form-item>
                </el-row>
            </el-form>
        </el-row>
        <el-tabs v-model="activeTab" tab-position="left">
            <!-- Playwright半自动收集器 -->
            <el-tab-pane label="🖐️ 手动抓取" name="playwright" v-if="!isChromeExtension">
                <el-form :model="playwrightForm" label-width="120px" size="small">
                    <!-- <el-form-item label="无头模式">
                        <el-switch v-model="playwrightForm.headless" @change="onHeadlessToggle"></el-switch>
                        <span class="form-tip">关闭后可以看到浏览器操作过程</span>
                    </el-form-item> -->

                    <el-form-item label="目标URL">
                        <el-select v-model="playwrightForm.target_url" style="width: 100%" @change="onTargetUrlChange">
                            <el-option label="角色推荐搜索" value="role_recommend"></el-option>
                            <el-option label="装备推荐搜索" value="equip_recommend"></el-option>
                            <el-option label="召唤兽推荐搜索" value="pet_recommend"></el-option>
                            <el-option label="自定义URL" value="custom"></el-option>
                        </el-select>
                    </el-form-item>

                    <el-form-item label="自定义URL" v-if="playwrightForm.target_url === 'custom'">
                        <el-input v-model="playwrightForm.custom_url" placeholder="请输入完整的CBG URL" style="width: 100%">
                            <template slot="prepend">https://</template>
                        </el-input>
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" @click="startPlaywrightCollector" :loading="isRunning">
                            🚀 搜索
                        </el-button>
                    </el-form-item>
                </el-form>
            </el-tab-pane>
            <!-- 角色爬虫 -->
            <el-tab-pane label="👤 角色" name="role" v-if="!isChromeExtension">
                <el-form :model="roleForm" label-width="100px" size="small">
                    <!-- JSON参数编辑器 -->
                    <div class="params-editor">
                        <div class="params-actions">
                            <el-button type="text" size="mini" @click="() => resetParam('role')">重置</el-button>
                            <el-button type="primary" size="mini" @click="() => saveParam('role')" :loading="roleSaving"
                                :disabled="!!roleJsonError">
                                保存配置
                            </el-button>
                        </div>
                        <div class="json-editor-wrapper">
                            <el-input type="textarea" v-model="roleParamsJson" placeholder="请输入角色爬虫参数JSON" :rows="8"
                                @blur="() => validateParam('role')" class="json-editor">
                            </el-input>
                            <div v-if="roleJsonError" class="json-error">
                                <i class="el-icon-warning"></i> {{ roleJsonError }}
                            </div>
                        </div>
                    </div>

                    <el-form-item>
                        <el-button type="primary" @click="() => startSpiderByType('role')" :loading="isRunning">
                            🚀 搜索
                        </el-button>
                    </el-form-item>
                </el-form>
            </el-tab-pane>

            <!-- 装备爬虫 -->
            <el-tab-pane label="⚔️ 装备" name="equip"
                v-if="!(isChromeExtension && externalParamsState.action === 'similar_pet')">
                <el-form :model="equipForm" label-width="100px" size="small">
                    <el-form-item label="装备类型" v-if="externalParamsState.action !== 'similar_equip'">
                        <el-select v-model="equipForm.equip_type" @change="onEquipTypeChange" style="width: 100%">
                            <el-option label="普通装备" value="normal"></el-option>
                            <el-option label="灵饰装备" value="lingshi"></el-option>
                            <el-option label="召唤兽装备" value="pet"></el-option>
                        </el-select>
                    </el-form-item>
                    <el-form-item label="套装效果"
                        v-if="equipForm.equip_type === 'normal' && externalSearchParams.suit_effect">
                        <el-radio-group v-model="suit_effect_type">
                            <el-radio label=""><span
                                    v-html="formatSuitEffect({ suit_effect: externalSearchParams.suit_effect })"></span>
                            </el-radio>
                            <el-radio label="select">自选</el-radio>
                            <el-radio label="agility_detailed.A">敏捷A套</el-radio>
                            <el-radio label="agility_detailed.B">敏捷B套</el-radio>
                            <el-radio label="magic_detailed.A">魔力A套</el-radio>
                            <el-radio label="magic_detailed.B">魔力B套</el-radio>
                        </el-radio-group>
                        <el-cascader v-if="suit_effect_type === 'select'" :options="suitOptions" placeholder="请选择套装效果"
                            separator="" clearable filterable @change="handleSuitChange" />
                        <el-radio-group
                            v-if="suit_effect_type?.split('.').length > 1 && equipConfig?.suits?.[suit_effect_type.split('.')[0]]?.[suit_effect_type.split('.')[1]]"
                            v-model="select_suit_effect">
                            <el-radio
                                v-for="itemId in equipConfig.suits[suit_effect_type.split('.')[0]][suit_effect_type.split('.')[1]]"
                                :label="itemId.toString()" :key="itemId">{{ suit_transform_skills[itemId] }}</el-radio>
                        </el-radio-group>
                    </el-form-item>
                    <el-form-item label="属性加成"
                        v-if="equipForm.equip_type === 'normal' && externalSearchParams.sum_attr_value > 0">
                        <el-checkbox-group v-model="select_sum_attr_type">
                            <el-checkbox label="dex">敏捷</el-checkbox>
                            <el-checkbox label="endurance">耐力</el-checkbox>
                            <el-checkbox label="magic">魔力</el-checkbox>
                            <el-checkbox label="physique">体质</el-checkbox>
                            <el-checkbox label="power">力量</el-checkbox>
                        </el-checkbox-group>
                        <el-checkbox v-model="sum_attr_with_melt">计算熔炼效果</el-checkbox>
                    </el-form-item>
                    <el-form-item label="属性加成值"
                        v-if="equipForm.equip_type === 'normal' && externalSearchParams.sum_attr_value > 0">
                        <el-input-number v-model="select_equip_addon_sum" placeholder="请输入属性加成值"
                            controls-position="right" style="width: 100px;"></el-input-number>
                    </el-form-item>
                    <el-form-item label="开运"
                        v-if="equipForm.equip_type === 'normal' && externalSearchParams.hole_num !== undefined">
                        <el-input-number v-model="select_equip_hole_num" :min="0" :max="5" :step="1"
                            placeholder="请输入开运等级" controls-position="right" style="width: 100px;"></el-input-number>
                    </el-form-item>
                    <el-form-item label="特效"
                        v-if="equipForm.equip_type === 'normal' && externalSearchParams.special_effect !== undefined">
                        <el-radio-group v-model="select_equip_special_effect_enable">
                            <el-radio :label="true">
                                <el-select :disabled="!select_equip_special_effect_enable"
                                    v-model="select_equip_special_effect" placeholder="请选择特效" multiple clearable
                                    filterable>
                                    <el-option v-for="(label, value) in equip_special_effect" :key="value"
                                        :label="value === '1' ? label + '/超级简易' : label" :value="value">
                                    </el-option>
                                </el-select>
                            </el-radio>
                            <el-radio :label="false">无</el-radio>
                        </el-radio-group>
                    </el-form-item>
                    <el-form-item label="特技"
                        v-if="equipForm.equip_type === 'normal' && externalSearchParams.special_skill !== undefined">
                        <el-radio-group v-model="select_equip_special_skill_enable">
                            <el-radio :label="true">
                                <el-select :disabled="!select_equip_special_skill_enable"
                                    v-model="select_equip_special_skill" placeholder="请选择特技" clearable filterable>
                                    <el-option v-for="[value, label] in equip_special_skills" :key="value"
                                        :label="label" :value="value">
                                    </el-option>
                                </el-select>
                            </el-radio>
                            <el-radio :label="false">无</el-radio>
                        </el-radio-group>
                    </el-form-item>
                    <el-form-item label="属性">
                        <el-form-item :label="equip_attr_list_label[attr] || attr" label-width="50px"
                            v-for="attr in equip_attr_list.filter(a => isChromeExtension?externalSearchParams[a] !== undefined:true)"
                            :key="attr">
                            <el-input-number v-model="select_equip_attr_value[attr]" placeholder="请输入属性值"
                                controls-position="right" style="width: 100px;"></el-input-number>
                        </el-form-item>
                    </el-form-item>
                    <el-form-item label="附加属性" v-if="select_equip_addon_attr_type.length > 0">
                        <el-checkbox-group v-model="select_equip_addon_attr_type">
                            <template v-for="(attrNum, attr) in externalSearchParams">
                                <el-checkbox v-for="item in attrNum" :label="attr + (item > 1 ? '_' + (item - 2) : '')"
                                    :key="attr + item" v-if="attr.startsWith('added_attr.')">{{ getAddedAttrType(attr)
                                    }}</el-checkbox>
                            </template>
                        </el-checkbox-group>
                    </el-form-item>
                    <el-form-item label="宝石"
                        v-if="(externalSearchParams.gem_level !== undefined || externalSearchParams.jinglian_level !== undefined)">
                        <el-radio-group v-model="select_equip_gem_enable">
                            <el-radio :label="true">
                                <el-select v-if="equipForm.equip_type === 'normal'" v-model="select_equip_gem_value"
                                    placeholder="镶嵌宝石" clearable filterable :disabled="!select_equip_gem_enable"
                                    style="width: 120px">
                                    <el-option v-for="(gemName, value) in gems_name" :key="value" :value="value"
                                        :label="gemName">
                                        <el-row type="flex" justify="space-between">
                                            <el-col style="width: 34px; height: 34px; margin-right: 10px">
                                                <el-image style="width: 34px; height: 34px; cursor: pointer"
                                                    :src="getImageUrl(gem_image[value] + '.gif')" fit="cover"
                                                    referrerpolicy="no-referrer">
                                                </el-image>
                                            </el-col>
                                            <el-col style="width: 100px">
                                                {{ gemName }}
                                            </el-col>
                                        </el-row>
                                    </el-option>
                                </el-select>
                                <el-input-number v-model="select_equip_gem_level" size="mini" :min="1" :max="16"
                                    :step="1" style="width: 100px" placeholder="锻练等级"
                                    :disabled="!select_equip_gem_enable" controls-position="right"></el-input-number>
                            </el-radio>
                            <el-radio :label="false">无</el-radio>
                        </el-radio-group>
                    </el-form-item>

                    <!-- JSON参数编辑器 -->
                    <div v-if="!isChromeExtension" class="params-editor">
                        <div class="params-actions">
                            <el-button type="text" size="mini" @click="() => resetParam('equip')">重置</el-button>
                            <el-button type="primary" size="mini" @click="() => saveParam('equip')"
                                :loading="equipSaving" :disabled="!!equipJsonError">
                                保存配置
                            </el-button>
                        </div>
                        <el-row type="flex">
                            <div class="json-editor-wrapper" v-if="externalParamsState.action === 'similar_equip'">
                                <el-input type="textarea" v-model="externalSearchParamsJsonStr" placeholder="搜索指定参数"
                                    :rows="10" class="json-editor">
                                </el-input>
                                <div v-if="equipJsonError" class="json-error">
                                    <i class="el-icon-warning"></i> {{ equipJsonError }}
                                </div>
                            </div>
                            <div class="json-editor-wrapper">
                                <el-input type="textarea" v-model="equipParamsJson" placeholder="请输入装备爬虫参数JSON"
                                    :rows="10" @blur="() => validateParam('equip')" class="json-editor">
                                </el-input>
                                <div v-if="equipJsonError" class="json-error">
                                    <i class="el-icon-warning"></i> {{ equipJsonError }}
                                </div>
                            </div>
                            <div class="json-editor-wrapper">
                                <el-input type="textarea" readonly :value="cached_params" :rows="10"
                                    class="json-editor">
                                </el-input>
                            </div>
                        </el-row>
                    </div>

                    <el-form-item>
                        <el-button type="primary" @click="() => startSpiderByType('equip')" :loading="isRunning">
                            🚀 搜索
                        </el-button>
                    </el-form-item>
                </el-form>
            </el-tab-pane>

            <!-- 召唤兽爬虫 -->
            <el-tab-pane label="🐲 召唤兽" name="pet"
                v-if="!(isChromeExtension && externalParamsState.action === 'similar_equip')">
                <el-form :model="petForm" label-width="100px" size="small" inline>
                    <el-form-item label="技能" v-if="petForm.skill !== ''">
                        <el-cascader v-model="select_pet_skill" :options="skillOptions" :props="{
                            multiple: true,
                            checkStrictly: false, // 不允许选择非叶子节点，只能选择叶子节点
                            emitPath: false       // 只返回最后一级的值（技能ID），而不是完整路径
                        }" :show-all-levels="false" placeholder="🔧请选择技能" multiple clearable filterable
                            style="width:150px">
                            <template slot-scope="{ data }">
                                <el-row type="flex" align="middle">
                                    <el-image v-if="data.value" :src="getSkillImage(data.value)" fit="cover"
                                        referrerpolicy="no-referrer"
                                        style="display: block;width: 24px;height: 24px;margin-right: 4px;"></el-image>
                                    <span>{{ data.label }}</span>
                                </el-row>
                            </template>
                        </el-cascader>
                    </el-form-item>

                    <el-form-item label="成长">
                        <el-input-number v-model="select_pet_growth" :min="0" :max="2" :step="0.01" :precision="3"
                            placeholder="请输入成长值" controls-position="right" style="width: 100px;"></el-input-number>
                    </el-form-item>
                    <el-form-item label="灵性">
                        <el-input-number v-model="select_pet_lingxing" :min="0" :max="110" :step="1" placeholder="请选择灵性"
                            controls-position="right" style="width: 100px;"></el-input-number>
                    </el-form-item>
                    <el-form-item label="是否宝宝">
                        <el-switch v-model="select_pet_is_baobao" :active-value="1" :inactive-value="0"></el-switch>
                    </el-form-item>
                    <el-form-item>
                        <div slot="label"> <el-switch v-model="select_pet_level_enable"></el-switch>
                            等级</div>
                        <el-input-number :disabled="!select_pet_level_enable" v-model="select_pet_level[0]" :min="0"
                            :max="180" :step="1" placeholder="请输入最低等级" controls-position="right"
                            style="width: 90px;"></el-input-number>
                        <el-input-number :disabled="!select_pet_level_enable" v-model="select_pet_level[1]"
                            :min="select_pet_level[0]" :max="180" :step="1" placeholder="请输入最高等级"
                            controls-position="right" style="width: 90px;"></el-input-number>
                    </el-form-item>
                    <!-- JSON参数编辑器 -->
                    <div class="params-editor" v-if="!isChromeExtension">
                        <div class="params-actions">
                            <el-button type="mini" size="mini" @click="() => resetParam('pet')">重置</el-button>
                            <el-button type="primary" size="mini" @click="() => saveParam('pet')" :loading="petSaving"
                                :disabled="!!petJsonError">
                                保存配置
                            </el-button>
                        </div>
                        <el-row type="flex">
                            <div class="json-editor-wrapper" v-if="externalParamsState.action === 'similar_pet'">
                                <el-input type="textarea" v-model="externalSearchParamsJsonStr" :rows="10"
                                    class="json-editor">
                                </el-input>
                            </div>
                            <div class="json-editor-wrapper">
                                <el-input type="textarea" v-model="petParamsJson" placeholder="请输入召唤兽爬虫参数JSON"
                                    :rows="10" @blur="() => validateParam('pet')" class="json-editor">
                                </el-input>
                                <div v-if="petJsonError" class="json-error">
                                    <i class="el-icon-warning"></i> {{ petJsonError }}
                                </div>
                            </div>
                            <div class="json-editor-wrapper">
                                <el-input type="textarea" readonly :value="cached_params" :rows="10"
                                    class="json-editor">
                                </el-input>
                            </div>
                        </el-row>
                    </div>

                    <el-form-item>
                        <el-button type="primary" @click="() => startSpiderByType('pet')" :loading="isRunning">
                            🚀 搜索
                        </el-button>
                    </el-form-item>
                </el-form>
            </el-tab-pane>
        </el-tabs>
        <LogMonitor :maxLines="8" simpleMode :isRunning="isRunning" v-if="log && !isChromeExtension" />
    </el-card>
</template>

<script>
import { petMixin } from '@/utils/mixins/petMixin'
import EquipmentImage from '@/components/EquipmentImage/EquipmentImage.vue'
import PetImage from '@/components/PetImage.vue'
import LogMonitor from '@/components/LogMonitor.vue'
import windowReuseManager from '@/utils/windowReuseManager'
import { equipmentMixin } from '@/utils/mixins/equipmentMixin'
import { commonMixin } from '@/utils/mixins/commonMixin'

const server_data_list = []
for (let key in window.server_data) {
    let [parent, children] = window.server_data[key]
    const [label, , , , value] = parent
    children = children.map(([value, label]) => ({ value, label }))
    server_data_list.push({
        label,
        value,
        children
    })
}
export default {
    name: 'AutoParams',
    props: {
        log: {
            type: Boolean,
            default: true
        },
        externalParams: {
            type: Object,
            default: () => ({})
        },
        server_id: {
            type: [Number, String],
            default: null
        },
        server_name: {
            type: String,
            default: null
        }
    },
    mixins: [commonMixin, equipmentMixin, petMixin],
    components: {
        EquipmentImage,
        LogMonitor,
        PetImage
    },
    data() {
        return {
            gem_image: {
                1: '4011',
                2: '4002',
                3: '4012',
                4: '4004',
                5: '4003',
                6: '4010',
                7: '4005',
                8: '4007',
                9: '4006',
                10: '4008',
                11: '4009',
                12: '1108_4249',
                4244: '4244',
                '755_4036': '755_4036',
                '756_4037': '756_4037',
                '757_4038': '757_4038'
            },
            gems_name: window.AUTO_SEARCH_CONFIG.gems_name,
            equip_attr_list: [
                // 'init_damage', //all_damage已经包含init_damage
                'fangyu',
                'init_damage_raw',
                'init_defense',
                'init_hp',
                'init_dex',
                'init_wakan',
                'all_wakan',
                'all_damage',
                'damage', 'defense', 'magic_damage', 'magic_defense', 'fengyin', 'anti_fengyin', 'speed'
            ],
            equip_attr_list_label: {
                'init_damage_raw': '初伤',
                'init_defense': '初防',
                'init_hp': '初血',
                'init_dex': '初敏',
                'init_wakan': '初灵',
                'all_wakan': '总灵',
                'all_damage': '总伤',
                'damage': '伤害',
                'defense': '防御',
                'magic_damage': '法伤',
                'magic_defense': '法防',
                'fengyin': '封印',
                'anti_fengyin': '抗封印',
                'speed': '速度',
                'fangyu': '防御'
            },
            skillOptions: window.skillOptions,
            isChromeExtension: typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id,
            sum_attr_with_melt: true,
            select_equip_addon_attr_type: [],
            select_equip_special_effect_enable: true,
            select_equip_special_skill_enable: true,
            select_equip_gem_enable: true,
            select_pet_skill: [],
            select_pet_lingxing: 0,
            select_pet_growth: 1,
            select_pet_is_baobao: 1,
            select_pet_level_enable: false,
            select_pet_level: [0, 180],
            price_min: 1,
            price_min_enable: false,
            equip_special_effect: window.AUTO_SEARCH_CONFIG.equip_special_effect,
            equip_special_skills: window.AUTO_SEARCH_CONFIG.equip_special_skills,
            suit_transform_skills: window.AUTO_SEARCH_CONFIG.suit_transform_skills,
            suitOptions: [],
            suit_effect_type: '',
            select_suit_effect: '',
            equipConfig: {},
            hotServers: [],
            server_data: server_data_list,
            target_server_list: [], // 存储server_id的数组（用于el-cascader的v-model）
            target_server_objects: [], // 存储完整服务器对象的数组
            // 全局设置
            globalSettings: {
                max_pages: 5,
                delay_min: 8,
                delay_max: 20,
                overall: false,
                multi: false,
            },
            // 延迟范围滑块
            delayRange: [8, 20],
            // 角色爬虫表单
            roleForm: {
            },
            // 装备爬虫表单
            equipForm: {
                equip_type: 'normal',
            },
            // 召唤兽爬虫表单
            petForm: {
            },
            // 代理爬虫表单
            proxyForm: {},
            // Playwright收集表单
            playwrightForm: {
                headless: false,
                target_url: 'role_recommend',
                custom_url: ''
            },
            // JSON参数字符串
            roleParamsJson: '',
            equipParamsJson: '{}',
            petParamsJson: '{}',
            // JSON验证错误
            roleJsonError: '',
            equipJsonError: '',
            petJsonError: '',
            // 默认参数模板（将从API动态加载）
            defaultParams: {
                role: {},
                equip_normal: {},
                equip_lingshi: {},
                equip_pet: {},
                equip_pet_equip: {},
                pet: {}
            },
            // 加载状态
            isRunning: false,
            paramsLoading: false,

            // Tab相关
            activeTab: 'playwright',
            // 状态监控
            statusMonitor: null,
            // 保存状态
            roleSaving: false,
            equipSaving: false,
            petSaving: false,
            // 缓存清理定时器
            cacheCleanupTimer: null,
            // 延时定时器（用于取消延时）
            sleepTimer: null,

            // 外部参数
            externalSearchParamsJsonStr: '{}',
            targetFeatures: {},
            // 内部存储的外部参数（从props或路由获取）
            internalExternalParams: {},

            // 参数管理器配置 - 统一管理所有参数类型
            paramManager: {
                role: {
                    jsonKey: 'roleParamsJson',
                    errorKey: 'roleJsonError',
                    savingKey: 'roleSaving',
                    paramType: 'role',
                    successMessage: '角色参数配置保存成功',
                    spiderType: 'role',
                    spiderName: '角色爬虫',
                    getParams: () => ({
                        ...this.globalSettings,
                        ...this.roleForm,
                        cached_params: JSON.parse(this.roleParamsJson)
                    })
                },
                equip: {
                    jsonKey: 'equipParamsJson',
                    errorKey: 'equipJsonError',
                    savingKey: 'equipSaving',
                    paramType: 'equip',
                    successMessage: '装备参数配置保存成功',
                    spiderType: 'equip',
                    spiderName: '装备爬虫',
                    getParamType: () => this.getEquipParamKey(this.equipForm.equip_type),
                    getSuccessMessage: () => `${this.getEquipTypeName(this.equipForm.equip_type)}参数配置保存成功`,
                    getParams: () => {
                        //TODO:target_server_objects要把this.cached_params.server_id排序到第一个
                        const params = {
                            target_server_list: this.target_server_objects,
                            ...this.equipForm,
                            ...this.globalSettings,
                            cached_params: JSON.parse(this.cached_params)
                        }
                        if (params.overall) {
                            params.multi = false
                            params.target_server_list = undefined
                        }
                        return params
                    }
                },
                pet: {
                    jsonKey: 'petParamsJson',
                    errorKey: 'petJsonError',
                    savingKey: 'petSaving',
                    paramType: 'pet',
                    successMessage: '召唤兽参数配置保存成功',
                    spiderType: 'pet',
                    spiderName: '召唤兽爬虫',
                    getParams: () => ({
                        target_server_list: this.target_server_objects,
                        ...this.petForm,
                        ...this.globalSettings,
                        cached_params: JSON.parse(this.cached_params)
                    })
                }
            }
        }
    },
    computed: {
        select_equip_hole_num: {
            get() {
                const params = JSON.parse(this.equipParamsJson)
                return params.hole_num !== undefined
                    ? params.hole_num
                    : (this.externalSearchParams.hole_num ? parseInt(this.externalSearchParams.hole_num) : 0)
            },
            set(value) {
                const params = JSON.parse(this.equipParamsJson)
                params.hole_num = value !== undefined ? value : undefined
                this.equipParamsJson = JSON.stringify(params, null, 2)
            }
        },
        select_equip_addon_sum: {
            get() {
                const params = JSON.parse(this.equipParamsJson)
                return params.sum_attr_value !== undefined
                    ? params.sum_attr_value
                    : (this.externalSearchParams.sum_attr_value ? parseInt(this.externalSearchParams.sum_attr_value) : 0)
            },
            set(value) {
                const params = JSON.parse(this.equipParamsJson)
                params.sum_attr_value = value !== undefined ? value : undefined
                this.equipParamsJson = JSON.stringify(params, null, 2)
            }
        },
        select_sum_attr_type: {
            get() {
                const params = JSON.parse(this.equipParamsJson)
                if (params.sum_attr_type !== undefined) {
                    return params.sum_attr_type === '' ? [] : String(params.sum_attr_type).split(',')
                }
                const ext = this.externalSearchParams.sum_attr_type
                return ext ? String(ext).split(',') : []
            },
            set(value) {
                const params = JSON.parse(this.equipParamsJson)
                params.sum_attr_type = Array.isArray(value) && value.length > 0 ? value.join(',') : undefined
                this.equipParamsJson = JSON.stringify(params, null, 2)
            }
        },
        select_equip_special_effect: {
            get() {
                const params = JSON.parse(this.equipParamsJson)
                return params.special_effect !== undefined
                    ? (params.special_effect === '' ? [] : params.special_effect.split(','))
                    : (this.externalSearchParams.special_effect ? this.externalSearchParams.special_effect.split(',') : [])
            },
            set(value) {
                const params = JSON.parse(this.equipParamsJson)
                params.special_effect = Array.isArray(value) && value.length > 0 ? value.join(',') : undefined
                this.equipParamsJson = JSON.stringify(params, null, 2)
            }
        },
        select_equip_special_skill: {
            get() {
                const params = JSON.parse(this.equipParamsJson)
                return params.special_skill !== undefined
                    ? params.special_skill
                    : (this.externalSearchParams.special_skill ? parseInt(this.externalSearchParams.special_skill) : 0)
            },
            set(value) {
                const params = JSON.parse(this.equipParamsJson)
                params.special_skill = value !== undefined && value !== '' ? value : undefined
                this.equipParamsJson = JSON.stringify(params, null, 2)
            }
        },
        select_equip_gem_value: {
            get() {
                const params = JSON.parse(this.equipParamsJson)
                if (params.gem_value !== undefined) {
                    return params.gem_value
                }
                const externalValue = this.externalSearchParams.gem_value
                return externalValue !== undefined ? String(externalValue) : undefined
            },
            set(value) {
                const params = JSON.parse(this.equipParamsJson)
                params.gem_value = value !== undefined && value !== '' ? String(value) : undefined
                this.equipParamsJson = JSON.stringify(params, null, 2)
            }
        },
        select_equip_gem_level: {
            get() {
                const params = JSON.parse(this.equipParamsJson)
                if (params.gem_level !== undefined) {
                    return params.gem_level
                }
                if (params.jinglian_level !== undefined) {
                    return params.jinglian_level
                }
                const externalLevel = this.externalSearchParams.gem_level || this.externalSearchParams.jinglian_level
                return externalLevel !== undefined ? Number(externalLevel) : undefined
            },
            set(value) {
                const params = JSON.parse(this.equipParamsJson)
                if (value === undefined || value === null || value === '') {
                    delete params.gem_level
                    delete params.jinglian_level
                } else {
                    if (this.externalSearchParams.gem_level) {
                        params.gem_level = Number(value)
                    }
                    if (this.externalSearchParams.jinglian_level) {
                        params.jinglian_level = Number(value)
                    }
                }
                this.equipParamsJson = JSON.stringify(params, null, 2)
            }
        },
        select_equip_attr_value: {
            get() {
                const params = JSON.parse(this.equipParamsJson)
                const externalParams = this.externalSearchParams || {}
                const allowedKeys = new Set(this.equip_attr_list || [])
                const toNumber = (val) => {
                    if (val === null || val === undefined || val === '') return undefined
                    const num = Number(val)
                    return Number.isNaN(num) ? val : num
                }
                const self = this
                return new Proxy({}, {
                    get(_, prop) {
                        if (typeof prop === 'symbol') return undefined
                        const key = String(prop)
                        if (!allowedKeys.has(key)) return undefined
                        if (Object.prototype.hasOwnProperty.call(params, key) && params[key] !== undefined) {
                            return params[key]
                        }
                        const fallback = externalParams[key]
                        return toNumber(fallback)
                    },
                    set(_, prop, value) {
                        if (typeof prop === 'symbol') return true
                        const key = String(prop)
                        if (!allowedKeys.has(key)) return true
                        const current = JSON.parse(self.equipParamsJson)
                        if (value === undefined || value === null || value === '') {
                            delete current[key]
                        } else {
                            current[key] = value
                        }
                        self.equipParamsJson = JSON.stringify(current, null, 2)
                        return true
                    }
                })
            },
            set(value) {
                const params = JSON.parse(this.equipParamsJson)
                if (value && typeof value === 'object') {
                    Object.entries(value).forEach(([key, val]) => {
                        if (!this.equip_attr_list.includes(key)) {
                            return
                        }
                        if (val === undefined || val === null || val === '') {
                            delete params[key]
                        } else {
                            params[key] = val
                        }
                    })
                }
                this.equipParamsJson = JSON.stringify(params, null, 2)
            }
        },
        externalSearchParams() {
            return JSON.parse(this.externalSearchParamsJsonStr)
        },
        view_loc() {
            return {
                view_loc: this.globalSettings.overall ? 'overall_search' : 'search_cond'
            }
        },
        currentServerData() {
            // 优先级：1. 用户选择的（store中的server_data_value） 2. props传入的 3. store中的getCurrentServerData

            // 1. 优先使用用户选择的（store中的server_data_value）
            if (this.$store && this.$store.state && this.$store.state.server_data_value) {
                const storeValue = this.$store.state.server_data_value
                if (Array.isArray(storeValue) && storeValue.length >= 2) {
                    const [areaid, server_id] = storeValue
                    if (server_id && areaid) {
                        // 从store中获取server_name（如果存在）
                        let server_name = ''
                        if (this.$store.getters && this.$store.getters.getCurrentServerData) {
                            const storeData = this.$store.getters.getCurrentServerData
                            if (storeData && storeData.server_id === server_id) {
                                server_name = storeData.server_name || ''
                            }
                        }
                        // 如果store中没有server_name，尝试从server_data中查找
                        if (!server_name && window.server_data) {
                            server_name = this.getServerNameByServerId(Number(server_id)) || ''
                        }
                        return {
                            server_id: Number(server_id),
                            areaid: Number(areaid),
                            server_name: server_name
                        }
                    }
                }
            }

            // 2. 其次使用props传入的数据
            let server_id = this.server_id !== null && this.server_id !== undefined
                ? this.server_id
                : (this.externalParams?.serverid || this.externalParams?.server_id || this.externalParamsState?.serverid || this.externalParamsState?.server_id)

            let server_name = this.server_name !== null && this.server_name !== undefined
                ? this.server_name
                : (this.externalParams?.server_name || this.externalParamsState?.server_name)

            const hasServerId = server_id !== null && server_id !== undefined && server_id !== ''
            const hasServerName = server_name !== null && server_name !== undefined && server_name !== ''

            if (hasServerId || hasServerName) {
                let areaid = null

                // 如果传入了server_id，查找对应的areaid
                if (hasServerId && window.server_data) {
                    areaid = this.getAreaIdByServerId(Number(server_id))
                }

                // 只要有server_id或server_name，就返回结果
                return {
                    server_id: hasServerId ? Number(server_id) : 0,
                    areaid: areaid !== null && areaid !== undefined ? areaid : 0,
                    server_name: hasServerName ? server_name : ''
                }
            }

            // 3. 最后从store的getCurrentServerData获取（备用）
            if (this.$store && this.$store.getters && this.$store.getters.getCurrentServerData) {
                const { server_id, areaid, server_name } = this.$store.getters.getCurrentServerData
                if (server_id && areaid) {
                    return { server_id, areaid, server_name: server_name || '' }
                }
            }

            // store也不可用，返回默认值
            return { server_id: 0, areaid: 0, server_name: '' }
        },
        // 用于watch的props值（避免与computed同名冲突）
        externalParamsFromProps() {
            return this.$props.externalParams
        },
        externalParamsState() {
            // 返回内部存储的外部参数
            return this.internalExternalParams
        },
        // 从Vuex store获取server_data_valueTODO:::::
        server_data_value: {
            get() {
                // 优先使用currentServerData中的数据
                const serverData = this.currentServerData
                if (serverData && serverData.areaid && serverData.server_id) {
                    return [serverData.areaid, serverData.server_id]
                }
                // 如果没有，从store获取
                const storeValue = this.$store?.state.server_data_value
                if (storeValue && Array.isArray(storeValue) && storeValue.length > 0) {
                    return storeValue
                }
                // 默认返回空数组，而不是空对象
                return []
            },
            set(value) {
                if (this.$store && this.$store.dispatch) {
                    this.$store.dispatch('setServerDataValue', value)
                }
            }
        },
        // 检查cookies是否有效
        isCookieValid() {
            if (this.$store && this.$store.getters) {
                return this.$store.getters['cookie/isCookieCacheValid']
            }
            return false
        },

        cached_params() {
            try {
                let diyParams = JSON.parse(this.equipParamsJson)
                if (this.activeTab === 'pet') {
                    diyParams = JSON.parse(this.petParamsJson)
                }
                const mode_params = {
                    ...this.view_loc,
                    hide_lingshi: this.activeTab === 'equip' && this.equipForm.equip_type === 'normal' ? 1 : undefined
                }
                const currentServerData = this.globalSettings.overall ? { server_id: undefined, server_name: undefined, areaid: undefined } : this.currentServerData
                const externalParams = JSON.parse(this.externalSearchParamsJsonStr)

                // 根据select_equip_addon_attr_type过滤附加属性
                const filteredExternalParams = { ...externalParams }
                if (this.activeTab === 'equip') {
                    // 获取所有附加属性键（基础键，如 added_attr.1）
                    const allAddedAttrKeys = Object.keys(externalParams).filter(key => key.startsWith('added_attr.'))

                    // 统计每个基础属性类型被选中的数量
                    const selectedAttrCounts = {}
                    this.select_equip_addon_attr_type.forEach(selectedKey => {
                        // 提取基础键名（去掉后缀，如 added_attr.1_0 -> added_attr.1）
                        // 如果包含下划线且下划线后面是数字，则去掉下划线及后面的部分
                        let baseKey = selectedKey
                        const lastUnderscoreIndex = selectedKey.lastIndexOf('_')
                        if (lastUnderscoreIndex > 0) {
                            // 检查下划线后面是否是数字
                            const afterUnderscore = selectedKey.substring(lastUnderscoreIndex + 1)
                            if (/^\d+$/.test(afterUnderscore)) {
                                // 是数字，去掉下划线及后面的部分
                                baseKey = selectedKey.substring(0, lastUnderscoreIndex)
                            }
                        }
                        if (baseKey.startsWith('added_attr.')) {
                            selectedAttrCounts[baseKey] = (selectedAttrCounts[baseKey] || 0) + 1
                        }
                    })

                    // 更新或删除附加属性
                    allAddedAttrKeys.forEach(key => {
                        if (selectedAttrCounts[key] !== undefined) {
                            // 设置选中数量
                            filteredExternalParams[key] = selectedAttrCounts[key]
                        } else {
                            // 删除未选中的附加属性
                            delete filteredExternalParams[key]
                        }
                    })
                }

                const mergedParams = Object.assign(
                    {},
                    filteredExternalParams,
                    diyParams,
                    currentServerData,
                    mode_params
                )
                if (!this.select_equip_special_effect_enable) {
                    delete mergedParams.special_effect
                }
                if (!this.select_equip_special_skill_enable) {
                    delete mergedParams.special_skill
                }
                if (!this.select_equip_gem_enable) {
                    delete mergedParams.gem_value
                    delete mergedParams.gem_level
                    delete mergedParams.jinglian_level
                }
                return JSON.stringify(mergedParams, null, 2)
            } catch (error) {
                return '{}'
            }
        }
    },
    watch: {
        sum_attr_with_melt(newVal) {
            const params = JSON.parse(this.equipParamsJson)
            params.sum_attr_with_melt = newVal ? 1 : undefined
            params.sum_attr_without_melt = !newVal ? 1 : undefined
            this.equipParamsJson = JSON.stringify(params, null, 2)
        },
        select_equip_special_effect_enable(newVal) {
            if (!newVal) {
                this.select_equip_special_effect = undefined
            }
        },
        select_equip_special_skill_enable(newVal) {
            if (!newVal) {
                this.select_equip_special_skill = undefined
            }
        },
        select_equip_gem_enable(newVal) {
            if (!newVal) {
                this.select_equip_gem_value = undefined
                this.select_equip_gem_level = undefined
                this.select_equip_jinglian_level = undefined
            }
        },
        price_min(newVal) {
            if (this.price_min_enable) {
                const params = JSON.parse(this.equipParamsJson)
                params.price_min = this.price_min_enable ? newVal * 100 : undefined
                this.equipParamsJson = JSON.stringify(params, null, 2)
            }
        },
        price_min_enable(newVal) {
            const params = JSON.parse(this.equipParamsJson)
            params.price_min = newVal ? this.price_min * 100 : undefined
            this.equipParamsJson = JSON.stringify(params, null, 2)
        },
        select_suit_effect(newVal) {
            const params = JSON.parse(this.equipParamsJson)
            params.suit_effect = newVal ? newVal : undefined
            this.equipParamsJson = JSON.stringify(params, null, 2)
        },
        suit_effect_type(newVal) {
            if (!newVal) {
                this.select_suit_effect = ''
            }
        },
        select_pet_skill(newVal) {
            console.log(newVal)
            const params = JSON.parse(this.petParamsJson)
            params.skill = newVal.join(',')
            this.petParamsJson = JSON.stringify(params, null, 2)
        },
        select_pet_lingxing(newVal) {
            const params = JSON.parse(this.petParamsJson)
            // el-input-number 返回的是数字类型或null
            params.lingxing = (newVal !== null && newVal !== undefined&& newVal !== 0) ? String(newVal) : undefined
            this.petParamsJson = JSON.stringify(params, null, 2)
        },
        select_pet_growth(newVal) {
            const params = JSON.parse(this.petParamsJson)
            // CBG使用千分比，所以需要乘以1000
            if (newVal !== null && newVal !== undefined && !isNaN(newVal)) {
                params.growth = Math.floor(newVal * 1000)
            } else {
                params.growth = undefined
            }
            this.petParamsJson = JSON.stringify(params, null, 2)
        },
        select_pet_is_baobao(newVal) {
            const params = JSON.parse(this.petParamsJson)
            params.is_baobao = newVal ? 1 : 0
            this.petParamsJson = JSON.stringify(params, null, 2)
        },
        select_pet_level_enable(newVal) {
            const params = JSON.parse(this.petParamsJson)
            if (newVal) {
                params.level_min = this.select_pet_level[0]
                params.level_max = this.select_pet_level[1]
            } else {
                params.level_min = undefined
                params.level_max = undefined
            }
            this.petParamsJson = JSON.stringify(params, null, 2)
        },
        select_pet_level(newVal) {
            const params = JSON.parse(this.petParamsJson)
            params.level_min = newVal[0]
            params.level_max = newVal[1]
            this.petParamsJson = JSON.stringify(params, null, 2)
        },
        isRunning(newVal) {
            this.$emit('update:isRunning', newVal)
            if (newVal) {
                this.startStatusMonitor()
            } else {
                this.stopStatusMonitor()
            }
        },
        'globalSettings.multi'(val) {
            if (val) {
                // 多服务器模式开启时，自动设置同级别服务器
                const server_id = Number(this.externalParamsState.serverid)
                console.log('开启多服务器模式，当前服务器ID:', server_id)
                this.globalSettings.max_pages = 1
                // 根据server_id在hotServers中找到对应的同级别的服务器
                this.setTargetServersByLevel(server_id)
            } else {
                // 多服务器模式关闭时，清空目标服务器列表
                this.target_server_list = []
                this.target_server_objects = []
                console.log('关闭多服务器模式，清空目标服务器列表')
            }
        },
        // 监听props中的externalParams变化（Modal模式）
        externalParamsFromProps: {
            handler(newVal) {
                this.syncExternalParams()
            },
            immediate: true,
            deep: true
        },
        // 监听路由参数变化（页面模式）
        '$route.query'(newVal) {
            if (newVal && Object.keys(newVal).length > 0) {
                this.syncExternalParams()
            }
        }
    },
    async mounted() {
        // 等待Vuex状态恢复后再执行其他操作
        // 自动清理过期缓存（如果store可用）
        if (this.$store && this.$store.dispatch) {
            this.$store.dispatch('cookie/cleanExpiredCache')

            // 搜索缓存清理定时器（每分钟检查一次）
            this.cacheCleanupTimer = setInterval(() => {
                this.$store.dispatch('cookie/cleanExpiredCache')
            }, 60 * 1000)
        }

        this.loadHotServers()
        await this.loadSearchParams()
        // 页面加载时请求一次状态
        this.checkTaskStatus()
        // 初始化延迟范围滑块
        this.delayRange = [this.globalSettings.delay_min, this.globalSettings.delay_max]

        // 同步外部参数（会先初始化internalExternalParams）
        this.syncExternalParams()
        // 然后加载并应用外部参数
        this.loadExternalParams()

        // 调试：检查props的值
        console.log('AutoParams mounted - props:', {
            server_id: this.server_id,
            server_name: this.server_name,
            externalParams: this.externalParams
        })

        // 如果通过props传入了server_id和server_name，优先使用props的值
        // 或者从externalParams中获取（作为备用）
        const serverIdFromProps = this.server_id !== null && this.server_id !== undefined ? this.server_id : (this.externalParams.serverid || this.externalParams.server_id)
        const serverNameFromProps = this.server_name !== null && this.server_name !== undefined ? this.server_name : this.externalParams.server_name

        if (this.$store && (serverIdFromProps || serverNameFromProps)) {
            // 如果传入了server_id，需要查找对应的areaid
            const serverIdToUse = serverIdFromProps || this.currentServerData.server_id
            if (serverIdToUse && window.server_data) {
                let foundAreaid = null
                // 在server_data中查找对应的server_id，获取areaid
                for (let key in window.server_data) {
                    let [parent, children] = window.server_data[key]
                    const [label, , , , areaid] = parent
                    for (let child of children) {
                        const [serverId, serverName] = child
                        if (Number(serverId) === Number(serverIdToUse)) {
                            foundAreaid = areaid
                            break
                        }
                    }
                    if (foundAreaid) break
                }
                // 如果找到了areaid，更新store
                if (foundAreaid) {
                    const serverName = serverNameFromProps || this.currentServerData.server_name || ''
                    this.$store.dispatch('setServerDataValue', [foundAreaid, Number(serverIdToUse)])
                    // 同时直接设置server_data_value，确保选择器能回显
                    this.server_data_value = [foundAreaid, Number(serverIdToUse)]
                    if (serverName) {
                        this.$store.dispatch('setServerData', {
                            areaid: foundAreaid,
                            server_id: Number(serverIdToUse),
                            server_name: serverName
                        })
                    }
                }
            } else if (serverNameFromProps && !serverIdToUse) {
                // 如果只传入了server_name，尝试从currentServerData获取server_id
                if (this.currentServerData.server_id) {
                    this.$store.dispatch('setServerData', {
                        areaid: this.currentServerData.areaid,
                        server_id: this.currentServerData.server_id,
                        server_name: this.server_name
                    })
                }
            }
        } else if (
            // 初始化时设置默认的server_data_value（如果store中没有的话）
            this.externalParamsState.action &&
            this.$store &&
            (!this.$store?.state.server_data_value || this.$store?.state.server_data_value.length === 0)
        ) {
            this.$store.dispatch('setServerDataValue', [43, 77])
        }
        if (this.externalParamsState.action) {
            const { action } = this.externalParamsState
            this.getFeatures().then(() => {
                if (action === 'similar_equip') {
                    this.loadEquipConfig()
                } else if (action === 'similar_pet') {
                    this.loadPetConfig()
                }
            })
        }
        this.initSuitOptions()
        // 初始化窗口复用管理器
        this.initWindowReuseManager()
    },
    beforeDestroy() {
        this.stopStatusMonitor()
        // 清理缓存清理定时器
        if (this.cacheCleanupTimer) {
            clearInterval(this.cacheCleanupTimer)
        }
        // 清理延时定时器
        this.cancelSleep()
    },
    methods: {
        getAddedAttrType(attrName) {
            const labels = {
                1: '固伤', 2: '伤害', 3: '速度', 4: '法伤', 5: '狂暴', 6: '物理暴击', 7: '法术暴击',
                8: '封印', 9: '法伤结果', 10: '穿刺', 11: '治疗', 12: '气血', 13: '防御', 14: '法防',
                15: '抗物理暴击', 16: '抗法术暴击', 17: '抗封', 18: '格挡', 19: '回复'
            }
            return labels[Number(attrName.replace('added_attr.', ''))]
        },
        // 解析列表数据
        parseListData(responseDataStr) {
            // 解析响应数据 Request.JSONP.request_map.request_数字(xxxx) 中的xxxx
            const match = responseDataStr.match(/Request\.JSONP\.request_map\.request_\d+\((.*)\)/)
            let templateJSONStr = '{}'
            if (match) {
                templateJSONStr = match[1]
            } else {
                templateJSONStr = responseDataStr
            }
            try {
                let templateJSON = {}
                if (typeof templateJSONStr === 'string') {
                    templateJSON = JSON.parse(templateJSONStr)
                } else {
                    // h5
                    templateJSON = templateJSONStr
                }
                return templateJSON
            } catch (error) {
                console.error('解析响应数据失败:', error)
                return {}
            }
        },
        handleSuitChange(value) {
            const [, suitValue] = value
            const actualValue = suitValue?.split('_').pop() // 提取真实的套装ID
            this.select_suit_effect = actualValue || ''
        },
        onServerDataChange() {
            const { server_id, areaid, server_name } = this.$store.getters.getCurrentServerData
            console.log('server_data_value', { server_id, areaid, server_name })
        },
        // 处理目标服务器选择变化
        onTargetServerChange(selectedServerIds) {
            // 当服务器选择发生变化时，根据server_id查找完整的服务器对象
            this.target_server_objects = []

            if (selectedServerIds && selectedServerIds.length > 0) {
                // 遍历所有选中的server_id
                selectedServerIds.forEach(serverId => {
                    // 在hotServers中查找对应的完整服务器对象
                    this.findServerInHotServers(serverId)
                })
            }
        },
        // 在hotServers嵌套结构中查找服务器
        findServerInHotServers(serverId) {
            for (const area of this.hotServers) {
                if (area.children) {
                    for (const server of area.children) {
                        if (server.server_id === serverId) {
                            this.target_server_objects.push({
                                server_id: server.server_id,
                                areaid: area.areaid || server.areaid,
                                server_name: server.server_name
                            })
                            return
                        }
                    }
                }
            }
        },

        // 根据服务器ID找到同级别的服务器并设置为目标服务器
        setTargetServersByLevel(serverId) {
            if (!this.hotServers || this.hotServers.length === 0) {
                console.warn('hotServers数据未加载，无法设置目标服务器')
                return
            }

            // 查找当前服务器所在的烟花等级组
            let currentLevel = null
            let currentServer = null

            for (const level of this.hotServers) {
                if (level.children) {
                    for (const server of level.children) {
                        if (server.server_id === serverId) {
                            currentLevel = level
                            currentServer = server
                            break
                        }
                    }
                    if (currentLevel) break
                }
            }

            if (!currentLevel || !currentServer) {
                console.warn(`未找到服务器ID ${serverId} 对应的烟花等级组`)
                return
            }

            console.log(`找到服务器 ${currentServer.server_name} 在烟花等级组: ${currentLevel.server_name}`)

            // 设置同级别服务器的目标列表
            this.target_server_objects = []
            this.target_server_list = []

            // 遍历同级别的所有服务器
            currentLevel.children.forEach(server => {
                const serverObject = {
                    server_id: server.server_id,
                    areaid: currentLevel.areaid || server.areaid,
                    server_name: server.server_name
                }

                this.target_server_objects.push(serverObject)
                this.target_server_list.push(server.server_id)
            })

            console.log(`已设置 ${this.target_server_objects.length} 个同级别服务器为目标服务器:`, this.target_server_objects)

        },
        // 初始化窗口复用管理器
        initWindowReuseManager() {
            try {
                // 确保窗口复用管理器已正确初始化
                if (windowReuseManager && windowReuseManager.isSetup) {
                    console.log('窗口复用管理器已初始化，状态:', windowReuseManager.getStatus())
                } else {
                    console.log('窗口复用管理器正在初始化...')
                    // 等待初始化完成
                    setTimeout(() => {
                        if (windowReuseManager && windowReuseManager.isSetup) {
                            console.log('窗口复用管理器初始化完成，状态:', windowReuseManager.getStatus())
                        } else {
                            console.warn('窗口复用管理器初始化失败')
                        }
                    }, 1000)
                }

                // 监听参数更新事件
                window.addEventListener('params-updated', (event) => {
                    const { params, timestamp } = event.detail
                    console.log('窗口参数已更新:', params)

                    // 强制刷新组件数据
                    this.$forceUpdate()

                    // 重新加载外部参数
                    this.loadExternalParams()

                    // 重新获取特征
                    if (params.action) {
                        this.getFeatures()
                    }

                    // 重新初始化装备类型相关的配置
                    if (params.equip_type) {
                        this.equipForm.equip_type = params.equip_type
                        // 重新加载装备参数配置
                        this.loadSearchParams()
                    }

                    // 重新设置activeTab
                    if (params.activeTab) {
                        this.activeTab = params.activeTab
                    }

                    console.log('✅ 页面数据已刷新')
                })
            } catch (error) {
                console.warn('初始化窗口复用管理器失败:', error)
            }
        },

        // 停止任务
        async stopTask() {
            try {
                // 如果是Chrome插件模式，直接停止循环请求
                if (this.isChromeExtension && this.isRunning) {
                    // 设置停止标志
                    this.isRunning = false
                    // 取消正在执行的延时
                    this.cancelSleep()
                    // 显示停止提示
                    this.$notify.success({
                        title: '任务状态',
                        message: '循环请求已停止'
                    })
                    console.log('Chrome插件模式：循环请求已停止')
                    return
                }

                // 非Chrome模式或API模式，调用后端API停止
                const response = await this.$api.spider.stopTask()
                if (response.code === 200) {
                    this.$notify.success({
                        title: '任务状态',
                        message: response.data?.message || '任务已停止'
                    })
                    this.isRunning = false
                } else {
                    this.$notify.error({
                        title: '任务状态',
                        message: response.message || '停止失败'
                    })
                }
            } catch (error) {
                this.$notify.error({
                    title: '任务状态',
                    message: error.message
                })
                // 即使API调用失败，也尝试停止本地循环
                if (this.isChromeExtension) {
                    this.isRunning = false
                    this.cancelSleep()
                }
            }
        },

        // 重置任务状态
        async resetTask() {
            try {
                const response = await this.$api.spider.resetTask()
                if (response.code === 200) {
                    this.$notify.success({
                        title: '任务状态',
                        message: response.data?.message || '任务状态已重置'
                    })
                    this.isRunning = false
                } else {
                    this.$notify.error({
                        title: '任务状态',
                        message: response.message || '重置失败'
                    })
                }
            } catch (error) {
                this.$notify.error({
                    title: '任务状态',
                    message: error.message
                })
            }
        },

        genaratePetSearchParams() {
            console.log('生成宠物搜索参数, externalParamsState:', this.externalParamsState)
            const searchParams = {}

            // 检查必要的参数是否存在
            if (!this.externalParamsState.all_skill) {
                console.warn('缺少 all_skill 参数')
            }
            if (!this.externalParamsState.growth) {
                console.warn('缺少 growth 参数')
            }

            searchParams.skill = this.externalParamsState.all_skill?.replace(/\|/g, ',') || ''
            searchParams.texing = this.externalParamsState.texing?.id
            searchParams.lingxing = this.externalParamsState.lx
            searchParams.growth = this.externalParamsState.growth ? this.externalParamsState.growth * 1000 : undefined

            console.log('生成的宠物搜索参数:', searchParams)
            return searchParams
        },
        genarateEquipmentSearchParams({ kindid, ...features }) {
            const searchParams = {}
            if (window.is_pet_equip(kindid)) {
                this.equipForm.equip_type = 'pet'
                searchParams.level = features.equip_level
                searchParams.speed = features.speed > 0 ? features.speed : undefined
                searchParams.shanghai = features.shanghai > 0 ? features.shanghai : undefined
                searchParams.hp = features.qixue > 0 ? features.qixue : undefined
                searchParams.fangyu = features.fangyu > 0 ? features.fangyu : undefined
                searchParams.xiang_qian_level = features.xiang_qian_level > 0 ? features.xiang_qian_level : undefined
                let addon_sum = 0
                    ;['fali', 'liliang', 'lingli', 'minjie', 'naili'].forEach((item) => {
                        searchParams[`addon_${item}`] = this.targetFeatures[`addon_${item}`] > 0 ? 1 : undefined
                        if (item === 'minjie' && this.targetFeatures[`addon_${item}`] < 0) {
                            searchParams.addon_minjie_reduce = this.targetFeatures[`addon_${item}`] * -1
                        } else {
                            addon_sum += this.targetFeatures[`addon_${item}`]
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
            } else if (window.is_lingshi_equip(kindid)) {
                searchParams.kindid = kindid
                this.equipForm.equip_type = 'lingshi'
                if (features.equip_level) {
                    searchParams.equip_level_min = features.equip_level
                    searchParams.equip_level_max = features.equip_level * 1 + 9
                }
                // 灵饰附加属性配置
                const { lingshi_added_attr1, lingshi_added_attr2 } = window.AUTO_SEARCH_CONFIG

                // 属性名称映射表 - 前端显示名称到后端字段名的映射
                const attr_name_map = {
                    '法伤结果': '法术伤害结果',
                    '法伤': '法术伤害',
                    '固伤': '固定伤害',
                    '法术暴击': '法术暴击等级',
                    '物理暴击': '物理暴击等级',
                    '封印': '封印命中等级',
                    '狂暴': '狂暴等级',
                    '穿刺': '穿刺等级',
                    '治疗': '治疗能力',
                    '伤害': '伤害',
                    '速度': '速度',
                    '抗法术暴击': '抗法术暴击等级',
                    '抗物理暴击': '抗物理暴击等级',
                    '抗封': '抵抗封印等级',
                    '回复': '气血回复效果',
                    '法防': '法术防御',
                    '防御': '防御',
                    '格挡': '格挡值',
                    '气血': '气血'
                }

                // 构建属性值到搜索参数的映射
                const buildAttrValueMapping = () => {
                    const mapping = {}

                    // 合并两个属性配置
                    const allAttrs = { ...lingshi_added_attr1, ...lingshi_added_attr2 }

                    // 遍历所有属性，建立映射关系
                    Object.entries(allAttrs).forEach(([value, displayName]) => {
                        const backendFieldName = attr_name_map[displayName]
                        if (backendFieldName) {
                            mapping[backendFieldName] = value
                        }
                    })

                    return mapping
                }

                // 处理主属性
                const processMainAttributes = () => {
                    const mainAttrs = ['damage', 'defense', 'magic_damage', 'magic_defense', 'fengyin', 'anti_fengyin', 'speed']
                    mainAttrs.forEach(attr => {
                        if (features[attr] && features[attr] > 0) {
                            searchParams[attr] = features[attr]
                        }
                    })
                }

                // 处理精炼等级
                const processGemLevel = () => {
                    if (features.gem_level && features.gem_level > 0) {
                        searchParams.jinglian_level = features.gem_level
                    }
                }

                // 处理附加属性
                const processAddedAttributes = () => {
                    if (!features.attrs || !Array.isArray(features.attrs)) {
                        return
                    }

                    const attrValueMapping = buildAttrValueMapping()
                    const addedAttrsCount = {}

                    // 统计每种附加属性的出现次数
                    features.attrs.forEach(({ attr_type }) => {
                        const searchValue = attrValueMapping[attr_type]
                        if (searchValue) {
                            addedAttrsCount[searchValue] = (addedAttrsCount[searchValue] || 0) + 1
                        }
                    })

                    // 将统计结果添加到搜索参数
                    Object.entries(addedAttrsCount).forEach(([value, count]) => {
                        searchParams[`added_attr.${value}`] = count
                        for (let i = 0; i < count; i++) {
                            this.select_equip_addon_attr_type.push(`added_attr.${value}${i > 0 ? '_' + (i - 1) : ''}`)
                        }
                    })
                }

                // 执行处理
                processMainAttributes()
                processGemLevel()
                processAddedAttributes()
            } else {
                searchParams.kindid = kindid
                let sum_attr_value = 0
                const sum_attr_type_list = []
                    ;[['moli', 'magic'], ['liliang', 'power'], ['tizhi', 'physique'], ['minjie', 'dex'], ['naili', 'endurance']].forEach(([featureKey, searchKey]) => {
                        if (this.targetFeatures[`addon_${featureKey}`] > 0) {
                            sum_attr_type_list.push(searchKey)
                        }
                        sum_attr_value += this.targetFeatures[`addon_${featureKey}`]
                    })
                if (sum_attr_value > 0) {
                    searchParams.sum_attr_type = sum_attr_type_list.join(',')
                    searchParams.sum_attr_value = sum_attr_value
                }
                if (features.gem_level > 0) {
                    searchParams.gem_level = features.gem_level
                    searchParams.gem_value = features.gem_value.join(',')
                }
                if (features.equip_level) {
                    searchParams.level_min = features.equip_level
                    searchParams.level_max = features.equip_level * 1 + 9
                }
                if (features.special_effect && features.special_effect.length > 0) {
                    searchParams.special_mode = 'and'
                    searchParams.special_effect = features.special_effect.join(',')
                }
                if (features.suit_effect) {
                    searchParams.suit_effect = features.suit_effect
                }
                if (features.special_skill) {
                    searchParams.special_skill = features.special_skill
                }
                if (features.hole_num) {
                    searchParams.hole_num = features.hole_num
                }

                //如果是武器打只太阳石，则忽略all_damage
                if (searchParams.gem_value === '2') {
                    this.equip_attr_list.splice(this.equip_attr_list.indexOf('all_damage'), 1)
                } else if (searchParams.gem_value === '1') {
                    //如果是武器打只红玛瑙，则忽略init_damage
                    this.equip_attr_list.splice(this.equip_attr_list.indexOf('init_damage'), 1)
                }

                this.equip_attr_list.forEach((value) => {
                    if (features[value]) {
                        searchParams[value] = features[value]
                    }
                })
            }
            return searchParams
        },
        // 通过server_id在window.server_data中反查对应的areaid
        getAreaIdByServerId(serverId) {
            if (!window || !window.server_data) return undefined
            const sid = Number(serverId)
            for (let key in window.server_data) {
                const [parent, children] = window.server_data[key]
                const areaValue = parent && parent.length >= 5 ? parent[4] : undefined
                if (!Array.isArray(children)) continue
                for (const child of children) {
                    if (Array.isArray(child) && child[0] === sid) {
                        return areaValue
                    }
                }
            }
            return undefined
        },
        getServerNameByServerId(serverId) {
            if (!window || !window.server_data) return undefined
            const sid = Number(serverId)
            for (let key in window.server_data) {
                const [parent, children] = window.server_data[key]
                if (!Array.isArray(children)) continue
                for (const child of children) {
                    if (Array.isArray(child) && child[0] === sid) {
                        // child[0]是server_id, child[1]是server_name
                        return child[1] || undefined
                    }
                }
            }
            return undefined
        },
        async getFeatures() {
            let query = {}
            if (this.externalParamsState.action === 'similar_equip') {

                await this.$api.equipment
                    .extractFeatures({
                        equipment_data: {
                            kindid: this.externalParamsState.kindid * 1 || undefined,
                            type: this.externalParamsState.type * 1 || undefined,
                            large_equip_desc: this.externalParamsState.large_equip_desc
                        },
                        data_type: 'equipment'
                    })
                    .then((res) => {
                        if (res.code === 200 && res.data.features) {
                            // 在所有环境下都设置 targetFeatures（包括组件形式）
                            this.targetFeatures = res.data.features
                            query = this.genarateEquipmentSearchParams(res.data.features)

                            // 只在非Chrome环境下修改页面title和favicon（组件形式不需要）
                            if (!this.isChromeExtension) {
                                // 使用equip_name,large_equip_desc改变当前title
                                if (this.targetFeatures && this.targetFeatures.equip_level) {
                                    document.title = this.targetFeatures.equip_level + '级' + this.externalParamsState.equip_name + ' - ' + this.externalParamsState.large_equip_desc.replace(/#r|#Y|#G|#c4DBAF4|#W|#cEE82EE|#c7D7E82/g, '')
                                }
                                //使用 this.externalParamsState.equip_face_img动态改变网页的favicon.ico
                                const faviconLink = document.querySelector('link[rel="icon"]')
                                if (faviconLink && this.externalParamsState.equip_face_img) {
                                    faviconLink.href = this.externalParamsState.equip_face_img
                                }
                            }
                        }
                    })
            } else if (this.externalParamsState.action === 'similar_pet') {
                query = this.genaratePetSearchParams()
            }
            if (this.externalParamsState.serverid) {
                // 如果serverid存在，则设置server_id，并根据server_data计算areaid
                const server_id = Number(this.externalParamsState.serverid)
                const areaid = this.getAreaIdByServerId(server_id)
                query.server_id = server_id
                if (areaid !== undefined) {
                    query.areaid = areaid
                }
                this.server_data_value = [areaid, server_id]
                query.server_name = this.externalParamsState.server_name
            }
            this.externalSearchParamsJsonStr = JSON.stringify(query, null, 2)
        },
        /**
         * 同步外部参数（从props或路由）
         * 优先使用props中的externalParams（Modal模式），否则使用路由参数（页面模式）
         */
        syncExternalParams() {
            let params = {}

            // 优先使用props中的externalParams（从Modal传递）
            const propsParams = this.$props.externalParams
            if (propsParams && typeof propsParams === 'object' && Object.keys(propsParams).length > 0) {
                params = JSON.parse(JSON.stringify(propsParams))
                console.log('从props获取参数:', params)
            } else if (this.$route && this.$route.query) {
                // 使用路由参数（页面模式）
                params = JSON.parse(JSON.stringify(this.$route.query))
                console.log('从路由获取参数:', params)
            }

            // 处理similar_pet的JSON字符串参数
            if (params.action === 'similar_pet') {
                // 需要解析为JSON对象的字段列表
                const jsonFields = ['evol_skill_list', 'neidan', 'equip_list', 'texing']

                jsonFields.forEach(field => {
                    if (typeof params[field] === 'string') {
                        try {
                            params[field] = JSON.parse(params[field] || '{}')
                        } catch (e) {
                            params[field] = {}
                        }
                    }
                })
            }

            // 更新内部存储的外部参数
            this.internalExternalParams = params

            // 如果参数中有activeTab，更新activeTab
            if (params.activeTab) {
                this.activeTab = params.activeTab
            }
            // 如果参数中有equip_type，更新equipForm.equip_type
            if (params.equip_type) {
                this.equipForm.equip_type = params.equip_type
            }
        },

        async loadExternalParams() {
            // 先同步参数
            this.syncExternalParams()

            // 然后应用参数到组件状态
            if (this.externalParamsState.activeTab) {
                this.activeTab = this.externalParamsState.activeTab
            }
            if (this.externalParamsState.equip_type) {
                this.equipForm.equip_type = this.externalParamsState.equip_type
            }
        },
        // 快速配置方法 - 根据当前activeTab配置
        quickConfig(size) {
            const configs = {
                small: { max_pages: 10, delay_min: 10, delay_max: 15 },
                medium: { max_pages: 50, delay_min: 15, delay_max: 20 },
                large: { max_pages: 100, delay_min: 20, delay_max: 30 }
            }
            const system = configs[size]
            Object.assign(this.globalSettings, system)
            // 同步更新滑块值
            this.delayRange = [this.globalSettings.delay_min, this.globalSettings.delay_max]
        },

        // 延迟范围滑块变化处理
        onDelayRangeChange(value) {
            this.globalSettings.delay_min = value[0]
            this.globalSettings.delay_max = value[1]
        },
        async loadEquipConfig() {
            const response = await this.$api.equipment.getEquipConfig()
            this.equipConfig = response.data
            if (this.targetFeatures.suit_effect) {
                this.suit_effect_type = ''
            }
            if (this.targetFeatures.addon_total > 0) {
                [['liliang', 'power'], ['minjie', 'dex'], ['moli', 'magic'], ['naili', 'endurance'], ['tizhi', 'physique']].forEach(([attr, key]) => {
                    if (this.targetFeatures[`addon_${attr}`] > 0) {
                        this.select_sum_attr_type.push(key)
                    }
                })
                // 通过设置equipParamsJson来更新select_equip_addon_sum
                if (this.targetFeatures.addon_total > 0) {
                    const params = JSON.parse(this.equipParamsJson)
                    params.sum_attr_value = this.targetFeatures.addon_total
                    this.equipParamsJson = JSON.stringify(params, null, 2)
                }
            }
        },
        loadPetConfig() {
            console.log(this.externalParamsState)
            this.select_pet_skill = this.externalParamsState.all_skill.split('|')
            // 灵性转换为数字类型
            this.select_pet_lingxing = this.externalParamsState.lx ? parseInt(this.externalParamsState.lx) : null
            // 成长值从 externalParamsState 中获取，不需要除以1000因为外部传入的就是原始值，转换为数字类型
            this.select_pet_growth = this.externalParamsState.growth ? parseFloat(this.externalParamsState.growth) : null
            this.select_pet_is_baobao = this.externalParamsState.is_baobao === '是' ? 1 : 0
            this.select_pet_level = [this.externalParamsState.equip_level, this.externalParamsState.equip_level]
        },
        async loadHotServers() {
            try {
                const response = await this.$api.system.getHotServers()
                this.hotServers = response
                console.log('热门服务器数据加载完成:', this.hotServers)

                // 在热门服务器数据加载完成后，处理可能已存在的target_server_list
                if (this.target_server_list && this.target_server_list.length > 0) {
                    this.onTargetServerChange(this.target_server_list)
                }

                // 如果多服务器模式已开启，自动设置同级别服务器
                if (this.globalSettings.multi && this.externalParamsState.serverid) {
                    const server_id = Number(this.externalParamsState.serverid)
                    console.log('数据加载完成后，自动设置多服务器模式的目标服务器:', server_id)
                    this.setTargetServersByLevel(server_id)
                }
            } catch (error) {
                console.error('加载热门服务器数据失败:', error)
                this.$notify.error('加载热门服务器数据失败: ' + error.message)
            }
        },
        // 加载搜索参数配置
        async loadSearchParams() {
            try {
                this.paramsLoading = true
                const response = await this.$api.system.getSearchParams()

                if (response.code === 200) {
                    // 更新默认参数
                    this.defaultParams = {
                        role: response.data.role || {},
                        equip_normal: response.data.equip_normal || {},
                        equip_lingshi: response.data.equip_lingshi || {},
                        equip_pet: response.data.equip_pet || {},
                        equip_pet_equip: response.data.equip_pet_equip || {},
                        pet: response.data.pet || {}
                    }

                    // 初始化JSON编辑器
                    this.initializeDefaultParams()
                } else {
                    this.$notify.error(response.message || '加载搜索参数配置失败')
                    // 使用默认值
                    this.initializeDefaultParams()
                }
            } catch (error) {
                console.error('加载搜索参数配置失败:', error)
                this.$notify.error('加载搜索参数配置失败: ' + error.message)
                // 使用默认值
                this.initializeDefaultParams()
            } finally {
                this.paramsLoading = false
            }
        },

        // 初始化默认参数
        initializeDefaultParams() {
            this.roleParamsJson = JSON.stringify(this.defaultParams.role, null, 2)
            // 根据当前装备类型初始化装备参数
            const equipParamKey = this.getEquipParamKey(this.equipForm.equip_type)
            this.equipParamsJson = JSON.stringify(this.defaultParams[equipParamKey], null, 2)
            this.petParamsJson = JSON.stringify(this.defaultParams.pet, null, 2)
        },
        // Playwright收集相关方法
        onHeadlessToggle(headless) {
            if (headless) {
                this.$notify.info({
                    title: '无头模式',
                    message: '浏览器将在后台运行，不会显示界面'
                })
            } else {
                this.$notify.info({
                    title: '有头模式',
                    message: '浏览器将显示界面，可以看到操作过程'
                })
            }
        },

        onTargetUrlChange(value) {
            if (value === 'custom') {
                this.playwrightForm.custom_url = ''
            }
        },

        onEquipTypeChange() {
            // 装备类型改变时切换对应的默认参数
            this.resetParam('equip')
        },

        // 获取装备参数键
        getEquipParamKey(equipType) {
            const paramKeyMap = {
                normal: 'equip_normal',
                lingshi: 'equip_lingshi',
                pet: 'equip_pet_equip'  // 修复：召唤兽装备应该使用equip_pet_equip
            }
            return paramKeyMap[equipType] || 'equip_normal'
        },

        // 通用参数操作方法
        getParamConfig(type) {
            return this.paramManager[type]
        },

        // 验证指定类型的参数
        validateParam(type) {
            const config = this.getParamConfig(type)
            if (!config) return false

            this[config.errorKey] = this.validateJson(this[config.jsonKey], type)
            return !this[config.errorKey]
        },

        // 重置参数方法 - 统一处理所有类型的参数重置
        resetParam(type) {
            const config = this.getParamConfig(type)
            if (!config) return

            const paramKey = config.getParamType ? config.getParamType() : config.paramType
            this[config.jsonKey] = JSON.stringify(this.defaultParams[paramKey], null, 2)
            this[config.errorKey] = ''
        },

        // 保存参数方法 - 统一处理所有类型的参数保存
        async saveParam(type) {
            const config = this.getParamConfig(type)
            if (!config) return false

            // 检查JSON错误
            if (!this.validateParam(type)) {
                this.$notify.error('请先修复JSON格式错误')
                return false
            }

            this[config.savingKey] = true
            try {
                const params = JSON.parse(this[config.jsonKey])
                const paramType = config.getParamType ? config.getParamType() : config.paramType
                const response = await this.$api.system.updateSearchParam(paramType, params)

                if (response.code === 200) {
                    const successMessage = config.getSuccessMessage ? config.getSuccessMessage() : config.successMessage
                    this.$notify.success(successMessage)
                    // 更新本地默认参数
                    this.defaultParams[paramType] = params
                    return true
                } else {
                    this.$notify.error({
                        title: '保存失败',
                        message: response.message || '保存失败'
                    })
                    return false
                }
            } catch (error) {
                console.error(`保存${type}参数失败:`, error)
                this.$notify.error({
                    title: '保存失败',
                    message: '保存失败: ' + error.message
                })
                return false
            } finally {
                this[config.savingKey] = false
            }
        },

        // JSON验证方法 - 统一处理所有类型的JSON验证
        validateJson(jsonStr, type) {
            try {
                if (!jsonStr.trim()) {
                    return `${type}参数不能为空`
                }
                const parsed = JSON.parse(jsonStr)
                if (typeof parsed !== 'object' || parsed === null) {
                    return 'JSON必须是一个对象'
                }
                return ''
            } catch (e) {
                return `JSON格式错误: ${e.message}`
            }
        },



        // 加载缓存参数
        async loadCachedParams() {
            try {
                await this.loadSearchParams()
                this.$notify.success({
                    title: '缓存参数',
                    message: '缓存参数已刷新'
                })
            } catch (error) {
                this.$notify.error({
                    title: '获取失败',
                    message: '获取缓存参数失败: ' + error.message
                })
            }
        },

        // 根据activeTab和equipForm.equip_type计算search_type
        //'search_role_equip',search_pet,search_pet_equip,search_lingshi
        //overall_search_pet,overall_search_equip,overall_search_pet_equip,overall_search_lingshi
        getSearchType() {
            const prefix = this.globalSettings.overall ? 'overall_' : ''

            if (this.activeTab === 'equip') {
                switch (this.equipForm.equip_type) {
                    case 'normal':
                        return `${prefix}search_${prefix ? '' : 'role_'}equip`
                    case 'lingshi':
                        return `${prefix}search_lingshi`
                    case 'pet':
                        return `${prefix}search_pet_equip`
                    default:
                        return `${prefix}search_equip`
                }
            } else if (this.activeTab === 'pet') {
                return `${prefix}search_pet`
            } else {
                // 默认值
                return `${prefix}search_${prefix ? '' : 'role_'}equip`
            }
        },

        // 通用搜索爬虫方法
        async startSpiderByType(type) {
            if (this.isRunning) return

            const config = this.paramManager[type]
            console.log('config', config)
            if (!config) return

            // 检查JSON错误
            if (this[config.errorKey]) {
                this.$notify.error('请先修复JSON格式错误')
                return
            }

            try {
                const params = config.getParams()
                const searchType = this.getSearchType()

                if (this.isChromeExtension) {
                    try {
                        const [activeTab] = await chrome.tabs?.query({ active: true, currentWindow: true }) || []
                        if (!activeTab) {
                            this.$notify && this.$notify.warning('未找到活动标签页')
                            return
                        }
                        // 设置运行状态
                        this.isRunning = true
                        this.activeTab = type

                        // 开始多页随机延时请求（支持多区搜索）
                        await this.doMultiPageRequest(
                            activeTab.id,
                            searchType,
                            params.cached_params,
                            params.multi,
                            params.target_server_list
                        )
                    } catch (error) {
                        console.error('搜索爬虫失败:', error)
                        this.isRunning = false
                    }
                } else {
                    const response = await this.$api.spider[`start${config.spiderType.charAt(0).toUpperCase() + config.spiderType.slice(1)}`](params)
                    if (response.code === 200) {
                        this.$notify.success({
                            title: '爬虫搜索',
                            message: `${config.spiderName}已搜索`
                        })
                        this.activeTab = type // 确保切换到对应tab
                        this.isRunning = true // 立即设置运行状态
                    } else {
                        this.$notify.error({
                            title: '搜索失败',
                            message: response.message || '搜索失败'
                        })
                    }
                }

            } catch (error) {
                this.$notify.error({
                    title: '搜索失败',
                    message: '搜索失败: ' + error.message
                })
            }
        },
        // 单页请求方法
        async doRequestInCBG(tabId, params) {
            return await chrome.debugger.sendCommand(
                { tabId: tabId },
                'Runtime.evaluate',
                {
                    expression: `(function() {ApiRecommd.queryList(${JSON.stringify(params)})})()`
                }
            )
        },
        // 多页随机延时请求（支持多区搜索）
        async doMultiPageRequest(tabId, searchType, cachedParams, multi = false, targetServerList = []) {
            let maxPages = this.globalSettings.max_pages || 5
            const delayMin = this.globalSettings.delay_min || 8
            const delayMax = this.globalSettings.delay_max || 20

            // 如果启用多区搜索且有目标服务器列表
            if (multi && targetServerList && targetServerList.length > 0) {
                console.log(`🌍 多区搜索模式，共 ${targetServerList.length} 个服务器，每个服务器 ${maxPages} 页`)

                let totalCompleted = 0
                for (let i = 0; i < targetServerList.length; i++) {
                    const server = targetServerList[i]

                    // 检查是否被停止
                    if (!this.isRunning) {
                        console.log(`请求已停止，已完成 ${i}/${targetServerList.length} 个服务器`)
                        break
                    }

                    console.log(`\n📍 [${i + 1}/${targetServerList.length}] 开始请求服务器: ${server.server_name} (ID: ${server.server_id})`)

                    // 合并服务器参数到 cached_params
                    const serverParams = {
                        ...cachedParams,
                        server_id: server.server_id,
                        areaid: server.areaid,
                        server_name: server.server_name
                    }

                    // 为当前服务器执行多页请求
                    const completed = await this.doSingleServerMultiPageRequest(
                        tabId,
                        searchType,
                        serverParams,
                        maxPages,
                        delayMin,
                        delayMax,
                        `[${i + 1}/${targetServerList.length}]`
                    )

                    totalCompleted += completed
                    console.log(`✅ 服务器 ${server.server_name} 完成 ${completed} 页请求`)

                    // 如果不是最后一个服务器，等待随机延时
                    if (i < targetServerList.length - 1 && this.isRunning) {
                        const serverDelay = Math.floor(Math.random() * (delayMax - delayMin + 1)) + delayMin
                        console.log(`⏱️ 等待 ${serverDelay} 秒后请求下一个服务器...`)
                        await this.sleep(serverDelay * 1000)
                    }
                }

                console.log(`\n🎉 多区搜索完成，共处理 ${targetServerList.length} 个服务器，总计 ${totalCompleted} 页`)
                this.$notify.success({
                    title: '多区搜索完成',
                    message: `已完成 ${targetServerList.length} 个服务器的搜索，共 ${totalCompleted} 页数据`
                })
                this.isRunning = false

                // Chrome插件模式下，发出搜索完成事件，触发相似装备模态框刷新
                if (this.isChromeExtension) {
                    this.$root.$emit('search-task-completed')
                    console.log('已发出搜索完成事件')
                }
                return
            }

            // 单区搜索模式
            console.log(`开始多页请求，总共 ${maxPages} 页，延时范围：${delayMin}-${delayMax} 秒`)
            await this.doSingleServerMultiPageRequest(tabId, searchType, cachedParams, maxPages, delayMin, delayMax)
        },

        // 单个服务器的多页请求
        async doSingleServerMultiPageRequest(tabId, searchType, cachedParams, maxPages, delayMin, delayMax, prefix = '') {
            let completedPages = 0
            let actualTotalPages = null // 实际总页数
            try {
                for (let page = 1; page <= maxPages; page++) {
                    // 检查是否被停止
                    if (!this.isRunning) {
                        completedPages = page - 1
                        console.log(`请求已停止，已完成 ${completedPages}/${actualTotalPages || maxPages} 页`)
                        break
                    }

                    // 如果已经知道实际总页数，且当前页超过了总页数，则停止
                    if (actualTotalPages !== null && page > actualTotalPages) {
                        console.log(`⏭️ 跳过第 ${page} 页（超出实际总页数 ${actualTotalPages}）`)
                        break
                    }

                    // 构建请求参数
                    const chromeParams = {
                        act: 'recommd_by_role',
                        page: page,
                        count: 15,
                        server_type: 3,
                        view_loc: this.view_loc.view_loc,
                        search_type: searchType,
                        ...cachedParams
                    }

                    // 发送请求
                    const displayMaxPages = actualTotalPages !== null ? actualTotalPages : maxPages
                    console.log(`${prefix}[${page}/${displayMaxPages}] 正在请求第 ${page} 页...`)
                    try {
                        const result = await this.doRequestInCBG(tabId, chromeParams)
                        console.log(`${prefix}[${page}/${displayMaxPages}] 第 ${page} 页请求已发送`)
                        completedPages = page

                        // 等待一段时间让响应数据被处理（1秒，给足够的时间）
                        await this.sleep(1000)

                        // 尝试从 Vuex 获取最新的响应数据并检查 pager 信息
                        if (this.$store && this.$store.getters['chromeDevtools/getEquipsAndPetsData']) {
                            const latestData = this.$store.getters['chromeDevtools/getEquipsAndPetsData']
                            if (latestData && latestData.length > 0) {
                                // 获取最新的一条数据
                                const latestItem = latestData[0]
                                if (latestItem.responseData && latestItem.status === 'completed') {
                                    try {
                                        // 解析响应数据
                                        const parsedData = this.parseListData(latestItem.responseData)
                                        if (parsedData && parsedData.pager) {
                                            const { cur_page, total_pages } = parsedData.pager

                                            // 第一次获取到 total_pages 时，更新 actualTotalPages
                                            if (actualTotalPages === null) {
                                                actualTotalPages = total_pages
                                                console.log(`${prefix}📊 检测到实际总页数：${total_pages}`)
                                                // 如果实际页数小于设置的页数，更新 maxPages
                                                if (total_pages < maxPages) {
                                                    maxPages = total_pages
                                                    console.log(`${prefix}📉 调整请求页数从原始设置到 ${total_pages}`)
                                                }
                                            }

                                            console.log(`${prefix}📄 页码信息：当前页 ${cur_page}/${total_pages}`)

                                            // 如果当前页已经是最后一页，停止请求
                                            if (cur_page >= total_pages) {
                                                console.log(`${prefix}✅ 已到达最后一页 (${cur_page}/${total_pages})，停止继续请求`)
                                                break
                                            }
                                        }
                                    } catch (parseError) {
                                        console.warn('解析 pager 信息失败:', parseError)
                                    }
                                }
                            }
                        }
                    } catch (requestError) {
                        console.error(`[${page}/${displayMaxPages}] 第 ${page} 页请求失败:`, requestError)
                        // 请求失败不中断循环，继续下一页
                        completedPages = page
                    }

                    // 如果不是最后一页，等待随机延时
                    if (page < maxPages) {
                        // 再次检查是否被停止
                        if (!this.isRunning) {
                            console.log(`请求已停止（延时前），已完成 ${completedPages}/${actualTotalPages || maxPages} 页`)
                            break
                        }
                        const delay = Math.floor(Math.random() * (delayMax - delayMin + 1)) + delayMin
                        console.log(`${prefix}[${page}/${actualTotalPages || maxPages}] 等待 ${delay} 秒后请求下一页...`)
                        await this.sleep(delay * 1000)
                        // 延时后再次检查是否被停止
                        if (!this.isRunning) {
                            console.log(`请求已停止（延时后），已完成 ${completedPages}/${actualTotalPages || maxPages} 页`)
                            break
                        }
                    }
                }

                const finalTotalPages = actualTotalPages || completedPages
                console.log(`${prefix}所有页面请求完成，共完成 ${completedPages}/${finalTotalPages} 页`)

                // 只在单区模式下显示通知（多区模式在外层显示）
                if (!prefix) {
                    this.$notify.success({
                        title: '爬虫搜索',
                        message: `已完成 ${completedPages}/${finalTotalPages} 页请求`
                    })

                    // Chrome插件模式下，发出搜索完成事件，触发相似装备模态框刷新
                    if (this.isChromeExtension) {
                        this.$root.$emit('search-task-completed')
                        console.log('已发出搜索完成事件')
                    }
                }

                return completedPages
            } catch (error) {
                console.error(`${prefix}多页请求失败:`, error)
                if (!prefix) {
                    this.$notify.error({
                        title: '请求失败',
                        message: '多页请求失败: ' + error.message
                    })
                }
                return 0
            } finally {
                // 只在单区模式下重置运行状态（多区模式在外层重置）
                if (!prefix) {
                    this.isRunning = false
                    console.log('多页请求任务结束')
                }
            }
        },
        // 延时工具方法（可取消）
        sleep(ms) {
            return new Promise((resolve) => {
                // 清除之前的定时器
                if (this.sleepTimer) {
                    clearTimeout(this.sleepTimer)
                }
                // 创建新的定时器
                this.sleepTimer = setTimeout(() => {
                    this.sleepTimer = null
                    resolve()
                }, ms)
            })
        },
        // 取消延时
        cancelSleep() {
            if (this.sleepTimer) {
                clearTimeout(this.sleepTimer)
                this.sleepTimer = null
                console.log('延时已取消')
            }
        },
        // 搜索Playwright收集
        async startPlaywrightCollector() {
            if (this.isRunning) return

            try {
                const params = {
                    headless: this.playwrightForm.headless
                    // 不传递target_url，使用后端默认值
                }

                console.log('搜索Playwright收集，参数:', params)

                const response = await this.$api.spider.startPlaywright(params)
                if (response.code === 200) {
                    this.$notify.success('Playwright收集已搜索')
                    this.activeTab = 'playwright'
                    this.isRunning = true
                } else {
                    this.$notify.error(response.message || '搜索失败')
                }
            } catch (error) {
                this.$notify.error('搜索失败: ' + error.message)
            }
        },

        // 获取装备类型名称
        getEquipTypeName(type) {
            const names = {
                normal: '普通装备',
                lingshi: '灵饰装备',
                pet: '召唤兽装备'
            }
            return names[type] || '装备'
        },
        // 检查任务状态
        async checkTaskStatus() {
            // Chrome插件模式下，不通过API检查状态，由本地循环控制
            if (this.isChromeExtension) {
                return
            }

            try {
                const response = await this.$api.spider.getStatus()
                if (response.code === 200) {
                    const status = response.data.status

                    // 更新运行状态
                    this.isRunning = (status === 'running')

                    // 如果任务完成或出错，显示消息并停止监控
                    if (status === 'completed' || status === 'error' || status === 'stopped') {
                        if (status === 'error') {
                            this.$notify.error(response.data.message || '任务执行出错')
                        } else if (status === 'stopped') {
                            this.$notify.info(response.data.message || '任务已停止')
                        }
                        this.isRunning = false
                    }
                }
            } catch (error) {
                console.error('状态监控错误:', error)
            }
        },
        // 状态监控方法
        startStatusMonitor() {
            // 清除可能存在的旧定时器
            this.stopStatusMonitor()

            // 搜索状态监控定时器
            this.statusMonitor = setInterval(async () => {
                await this.checkTaskStatus()
            }, 5000) // 每2秒检查一次状态
        },
        stopStatusMonitor() {
            if (this.statusMonitor) {
                clearInterval(this.statusMonitor)
                this.statusMonitor = null
            }
        },
    }
}
</script>

<style scoped>
/* 参数编辑器样式 */
.params-editor {
    background-color: #f9f9f9;
    padding: 15px;
    border-radius: 6px;
    margin: 15px 0;
    border-left: 4px solid #409eff;
}

.params-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #e4e7ed;
}

.json-editor-wrapper {
    position: relative;
    width: 100%;
}

.json-editor {
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.4;
}

.json-editor textarea {
    background-color: #2d3748;
    color: #e2e8f0;
    border: 1px solid #4a5568;
    border-radius: 4px;
    padding: 12px;
}

.json-editor textarea:focus {
    border-color: #409eff;
    box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.json-error {
    margin-top: 8px;
    padding: 8px 12px;
    background-color: #fef0f0;
    border: 1px solid #fbc4c4;
    border-radius: 4px;
    color: #f56c6c;
    font-size: 12px;
    line-height: 1.4;
}

.json-error i {
    margin-right: 4px;
}
</style>