/**
 * 宠物相关公用方法Mixin
 */
export const petMixin = {
  methods: {
    /**
     * 获取技能图片URL
     * @param {number} skillId - 技能ID
     * @returns {string} 技能图片URL
     */
    getSkillImage(skillId = 0) {
      if (skillId === 0) {
        return ''
      }
      // skillId少于4位数要补0
      const paddedId = skillId.toString().padStart(4, '0')
      return `https://cbg-xyq.res.netease.com/images/skill/${paddedId}.gif`
    },

    /**
     * 解析宠物信息
     * @param {string} desc - 宠物描述
     * @returns {Object} 解析后的宠物信息
     */
    parsePetInfo(desc) {
      const pet_desc = window.parse_desc_info(desc)
      const newLinliData = this.parse_fashang_fafang(desc)
      const pet_attrs = window.get_pet_attrs_info(pet_desc, {
        only_basic_attr: false,
        fashang: newLinliData.fashang,
        fafang: newLinliData.fafang
      })
      return pet_attrs
    },

    /**
     * 解析法术伤害和法术防御
     * @param {string} desc_info - 描述信息
     * @returns {Object} 解析结果
     */
    parse_fashang_fafang(desc_info) {
      try {
        const data = JSON.decode(window.decode_desc(desc_info)) // 对内容解码
        return {
          fashang: data.fashang,
          fafang: data.fafang
        }
      } catch (e) {
        return {}
      }
    },

    /**
     * 格式化技能
     * @param {Object} pet - 宠物对象
     * @returns {string} 格式化后的技能HTML
     */
    formatSkills({ petData },row=2,col=8) {
      try {
        // 创建一个临时的容器元素
        const tempContainer = document.createElement('div')

        // 调用原始函数，传入临时容器
        const { pet_tip_skill_grid: result } = window.show_pet_skill_in_grade(
          petData.all_skill,
          petData.sp_skill,
          row,
          col,
          {
            pet_skill_url: 'https://cbg-xyq.res.netease.com/images/skill/',
            notice_node_name: 'pet_tip_notice_msg',
            skill_panel_name: 'pet_tip_skill_grid',
            enhance_skills: [],
            table_class: 'tb03'
          },
          petData
        )
        // 如果返回的是DOM节点，将其添加到临时容器
        result.forEach((node) => {
          if (node) {
            tempContainer.appendChild(node)
          }
        })
        // 返回HTML字符串，去掉所有空的td标签
        return tempContainer.innerHTML
      } catch (error) {
        console.error('格式化技能失败:', error)
        return ''
      }
    },
    /**
     * 获取增强信息
     * @param {Object} pet - 宠物对象
     * @returns {Object} 增强信息
     */
    getEnhanceInfo(pet) {
      var equip_display_conf = {
        // 高亮技能
        pet: { skill_id_list: [571, 661], is_baobao: 1 },
        search: { is_hide_unreasonable_price_equips: 1 }
      }
      var enhanceInfo = equip_display_conf.pet || {}
      var time_lock = pet.is_time_lock
      time_lock = time_lock > 0 || time_lock == 'true'
      var time_lock_days
      if (time_lock) {
        time_lock_days = pet.time_lock_days
      }
      enhanceInfo.time_lock = time_lock
      enhanceInfo.time_lock_days = time_lock_days
      return {
        time_lock: pet.time_lock || false,
        time_lock_days: pet.time_lock_days || 90,
        is_baobao: pet.petData.is_baobao === '是' || false,
        skill_id_list: enhanceInfo.skill_id_list || []
      }
    },

    /**
     * 格式化宠物技能差异（用于相似宠物表格）
     * @param {string} allSkill - 当前宠物技能
     * @param {Object} targetPet - 目标宠物
     * @returns {string} 差异技能描述
     */
    formatSkillsDiff(allSkill, targetPet) {
      if (!allSkill || !targetPet || !targetPet.all_skill) return ''

      const targetPetSkill = targetPet.all_skill

      // 将技能字符串转换为数组
      const targetSkills = targetPetSkill.split('|').filter((skill) => skill.trim())
      const currentSkills = allSkill.split('|').filter((skill) => skill.trim())

      // 找出当前宠物有但目标宠物没有的技能
      const diffSkills = currentSkills.filter((skill) => !targetSkills.includes(skill))

      // 如果有差异技能，返回差异技能列表
      if (diffSkills.length > 0) {
        return (
          '+' +
          diffSkills
            .map((skillId) => {
              return window.CBG_GAME_CONFIG.xyq_pet_skills[skillId]
            })
            .join('|')
        )
      }

      // 如果没有差异，返回空字符串
      return ''
    },

    /**
     * 格式化特性
     * @param {string} texing - 特性JSON字符串
     * @returns {string} 特性名称
     */
    formatTexing(texing) {
      if (!texing) return ''
      try {
        const texingObj = JSON.parse(texing)
        return texingObj.name || ''
      } catch (e) {
        return ''
      }
    }
  }
}
