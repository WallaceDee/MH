/**
 * 装备相关公用方法Mixin
 */
export const equipmentMixin = {
  data() {
    return {
      lingshiKinds:window.lingshiKinds
    }
  },
  methods: {
    /**
     * 获取装备图片属性
     * @param {Object} eItem - 装备项
     * @returns {Object} 装备图片属性
     */
    getEquipImageProps(eItem) {
      if(eItem.large_equip_desc&&eItem.equip_name&&eItem.equip_face_img&&eItem.equip_type_desc){
        return eItem
      }
      return {
        ...eItem,
        equip_face_img: eItem.icon,
        equip_type_desc: eItem.static_desc,
        large_equip_desc: eItem.desc,
        equip_name: eItem.name
      }
    },

    /**
     * 获取装备套装效果
     * @param {string} equipList - 装备列表JSON字符串
     * @returns {string} 套装效果描述
     */
    getEquipSuitEffect(equipList) {
      if (!equipList) return ''

      try {
        const equipArray = JSON.parse(equipList).filter((equip) => equip)

        // 用于存储套装效果及其出现次数
        const suitEffects = {}

        // 遍历装备数组，提取套装效果
        equipArray.forEach((equip) => {
          if (equip.desc) {
            // 匹配套装效果：套装效果：附加状态 + 技能名称
            const suitMatch = equip.desc.match(/#c4DBAF4套装效果：附加状态#c4DBAF4([^#]+)/)
            if (suitMatch && suitMatch[1]) {
              const suitName = suitMatch[1].trim()
              suitEffects[suitName] = (suitEffects[suitName] || 0) + 1
            }
          }
        })

        // 检查是否有达到3件套的效果
        for (const [suitName, count] of Object.entries(suitEffects)) {
          if (count >= 3) {
            return suitName
          }
          // 如果没有达到3件套，返回装备数量
          return suitName + `(${count}/3)`
        }

        return ''
      } catch (error) {
        console.error('解析装备列表失败:', error)
        return ''
      }
    },
    isLingshi(kindid) {
      return this.lingshiKinds.some(([id]) => id === kindid)
    },
    // 获取特效名称
    getSpecialEffectName(id, isLingshi = false) {
      if (isLingshi) {
        if (id === 1) {
          return '超级简易'
        }
      } else {
        // 直接使用全局变量
        if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.equip_special_effect) {
          const effectName = window.AUTO_SEARCH_CONFIG.equip_special_effect[id.toString()]
          if (effectName) return effectName
        }
      }
      return `特效${id}`
    },
    // 解析特技特效
    formatSpecialSkillsAndEffects({
      special_effect: specialEffect,
      special_skill: specialSkill,
      kindid,
      large_equip_desc
    }) {
      const specials = []
      if (specialEffect && specialEffect !== '') {
        try {
          const effects = JSON.parse(specialEffect)
          const isLingshi = this.isLingshi(kindid)
          if (Array.isArray(effects)) {
            effects.forEach((effect) => {
              if (isLingshi) {
                // 在large_equip_desc中提取特效
                // 支持两种格式：
                // 1. #c4DBAF4特效：超级简易#r (无等级)
                // 2. #c4DBAF4特效：锐不可当（3级）#r (有等级)

                // 先尝试匹配有等级的特效
                const effectWithLevelMatch = large_equip_desc.match(
                  /#c4DBAF4特效：([^#]+)（(\d+)级）#r/
                )
                if (effectWithLevelMatch) {
                  const effectName = effectWithLevelMatch[1]
                  const effectLevel = effectWithLevelMatch[2]
                  specials.push(`${effectName}（${effectLevel}级）`)
                } else {
                  // 再尝试匹配无等级的特效
                  const effectWithoutLevelMatch = large_equip_desc.match(/#c4DBAF4特效：([^#]+)#r/)
                  if (effectWithoutLevelMatch) {
                    const effectName = effectWithoutLevelMatch[1]
                    specials.push(`${effectName}`)
                  } else {
                    // 如果都没有匹配到特效，使用默认处理方式
                    const effectName = this.getSpecialEffectName(parseInt(effect), isLingshi)
                    if (effectName) specials.push(`${effectName}`)
                  }
                }
              } else {
                const effectName = this.getSpecialEffectName(parseInt(effect), isLingshi)
                if (effectName) specials.push(`${effectName}`)
              }
            })
          }
        } catch (e) {
          console.warn('解析特效JSON失败:', e, specialEffect)
        }
      }

      // 处理特技
      if (specialSkill && specialSkill !== 0) {
        const skillName = this.getSpecialSkillName(specialSkill)
        if (skillName) specials.push(`${skillName}`)
      }

      return specials.join('<br />')
    },

    // 获取特技名称
    getSpecialSkillName(id) {
      // 直接使用全局变量
      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.equip_special_skills) {
        const skills = window.AUTO_SEARCH_CONFIG.equip_special_skills
        if (Array.isArray(skills)) {
          const skill = skills.find((item) => item[0] === parseInt(id))
          if (skill) return skill[1]
        }
      }

      return `特技${id}`
    },

    /**
     * 格式化套装效果
     * @param {number} suitEffect - 套装效果ID
     * @returns {string} 套装效果名称
     */
    // 解析套装信息
    formatSuitEffect({ suit_effect: suitEffect, addon_status, kindid }) {
      if (kindid === 29) {
        return addon_status
      }
      if (!suitEffect) return ''

      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.suit_added_status) {
        const suitName = window.AUTO_SEARCH_CONFIG.suit_added_status[suitEffect.toString()]
        if (suitName) return `附加状态${suitName}`
      }

      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.suit_append_skills) {
        const suitName = window.AUTO_SEARCH_CONFIG.suit_append_skills[suitEffect.toString()]
        if (suitName) return `追加法术${suitName}`
      }
      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.suit_transform_skills) {
        const suitName = window.AUTO_SEARCH_CONFIG.suit_transform_skills[suitEffect.toString()]
        if (suitName) return `变身术之${suitName}`
      }
      if (window.AUTO_SEARCH_CONFIG && window.AUTO_SEARCH_CONFIG.suit_transform_charms) {
        const suitName = window.AUTO_SEARCH_CONFIG.suit_transform_charms[suitEffect.toString()]
        if (suitName) return `变化咒之${suitName}`
      }

      return `套装${suitEffect}`
    },

    /**
     * 获取宝石图片
     * @param {Object} equipment - 装备对象
     * @returns {Array} 宝石图片URL数组
     */
    getGemImageByGemValue(equipment) {
      const gemImages = []

      // 处理宝石数据
      if (equipment.gem_value) {
        try {
          const gemData = JSON.parse(equipment.gem_value)
          if (Array.isArray(gemData)) {
            gemData.forEach((gemId) => {
              if (gemId && this.gem_image && this.gem_image[gemId]) {
                const gemImg = this.gem_image[gemId]
                gemImages.push(this.getImageUrl(`${gemImg}.gif`, 'small'))
              }
            })
          }
        } catch (e) {
          console.error('解析宝石数据失败:', e)
        }
      }

      return gemImages
    }
  }
}
