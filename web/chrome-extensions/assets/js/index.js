var ResUrl = 'https://cbg-xyq.res.netease.com'
var ServerCurrentTime = new Date()
  .toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })
  .replace(/\//g, '-')
var EquipRequestTime = '2024-01-13 16:26:35'
// 添加 $ 函数（MooTools兼容）
window.$ = function (id) {
  var element
  if (typeof id === 'string') {
    element = document.getElementById(id)
  } else {
    element = id
  }

  // 为元素添加 MooTools 方法
  if (element && !element.addEvents) {
    element.addEvents = function (events) {
      for (var type in events) {
        this.addEvent(type, events[type])
      }
      return this
    }

    element.addEvent = function (type, fn) {
      if (typeof fn === 'function') {
        this.addEventListener(type, fn)
      }
      return this
    }

    element.removeEvent = function (type, fn) {
      if (typeof fn === 'function') {
        this.removeEventListener(type, fn)
      }
      return this
    }

    element.fireEvent = function (type, args) {
      var event = new Event(type)
      if (args) {
        for (var key in args) {
          event[key] = args[key]
        }
      }
      this.dispatchEvent(event)
      return this
    }
  }

  return element
}

// 添加 $$ 函数（MooTools兼容）
window.$$ = function (selector) {
  if (typeof selector === 'string') {
    return document.querySelectorAll(selector)
  }
  return selector
}

// 添加 Cookie 对象（MooTools兼容）
window.Cookie = {
  write: function (name, value, options) {
    options = options || {}
    var expires = ''

    if (options.expires) {
      var date = new Date()
      date.setTime(date.getTime() + options.expires * 24 * 60 * 60 * 1000)
      expires = '; expires=' + date.toUTCString()
    }

    var path = options.path ? '; path=' + options.path : ''
    var domain = options.domain ? '; domain=' + options.domain : ''
    var secure = options.secure ? '; secure' : ''

    document.cookie = name + '=' + encodeURIComponent(value) + expires + path + domain + secure
  },

  read: function (name) {
    var nameEQ = name + '='
    var ca = document.cookie.split(';')
    for (var i = 0; i < ca.length; i++) {
      var c = ca[i]
      while (c.charAt(0) === ' ') c = c.substring(1, c.length)
      if (c.indexOf(nameEQ) === 0) {
        return decodeURIComponent(c.substring(nameEQ.length, c.length))
      }
    }
    return null
  },

  dispose: function (name, options) {
    options = options || {}
    options.expires = -1
    this.write(name, '', options)
  }
}

window.addEvent = function () {}
window.Events = {}

// 添加缺失的typeOf函数
function typeOf(obj) {
  if (obj === null) return 'null'
  if (obj === undefined) return 'undefined'
  return Object.prototype.toString.call(obj).slice(8, -1).toLowerCase()
}

// 添加mergeOne辅助函数
function mergeOne(source, key, value) {
  if (value !== undefined) {
    source[key] = value
  }
  return source
}

// 实现Object.merge静态方法（而不是原型方法）
Object.merge = function (destination, source) {
  if (arguments.length === 2 && typeOf(source) === 'string') {
    // 处理两个参数的情况，第二个参数是字符串
    return mergeOne(destination, source, arguments[2])
  }

  // 处理多个对象合并的情况
  for (var i = 1, l = arguments.length; i < l; i++) {
    var object = arguments[i]
    if (object) {
      for (var key in object) {
        if (object.hasOwnProperty(key)) {
          mergeOne(destination, key, object[key])
        }
      }
    }
  }
  return destination
}

// 为数组添加contains方法（MooTools兼容）
if (!Array.prototype.contains) {
  Array.prototype.contains = function (item, from) {
    return this.indexOf(item, from) != -1
  }
}

// MooTools Class 实现
;(function () {
  // 基础函数
  var typeOf = function (item) {
    if (item == null) return 'null'
    if (item.$family) return item.$family()
    if (item.nodeName) {
      if (item.nodeType == 1) return 'element'
      if (item.nodeType == 3) return /\S/.test(item.nodeValue) ? 'textnode' : 'whitespace'
    } else if (typeof item.length == 'number') {
      if (item.callee) return 'arguments'
      // 修复：安全地检查 'item' 属性
      try {
        if ('item' in item) return 'collection'
      } catch (e) {
        // 如果 'in' 操作符失败，继续检查其他类型
      }
    }
    return typeof item
  }

  var instanceOf = function (item, object) {
    if (item == null) return false
    var constructor = item.$constructor || item.constructor
    while (constructor) {
      if (constructor === object) return true
      constructor = constructor.parent
    }
    return item instanceof object
  }

  // Type 实现
  var Type = function (name, object) {
    if (name) {
      var lower = name.toLowerCase()
      var typeCheck = function (item) {
        return typeOf(item) == lower
      }
      Type['is' + name] = typeCheck
      if (object != null) {
        object.prototype.$family = function () {
          return lower
        }
        object.type = typeCheck
      }
    }
    if (object == null) return null
    object.extend = function (key, value) {
      this[key] = value
    }
    object.$constructor = Type
    object.prototype.$constructor = object
    return object
  }

  // 辅助函数
  var reset = function (object) {
    for (var key in object) {
      var value = object[key]
      switch (typeOf(value)) {
        case 'object':
          var F = function () {}
          F.prototype = value
          object[key] = reset(new F())
          break
        case 'array':
          object[key] = value.clone ? value.clone() : value.slice()
          break
      }
    }
    return object
  }

  var wrap = function (self, key, method) {
    if (method.$origin) method = method.$origin
    var wrapper = function () {
      if (method.$protected && this.$caller == null)
        throw new Error('The method "' + key + '" cannot be called.')
      var caller = this.caller,
        current = this.$caller
      this.caller = current
      this.$caller = wrapper
      var result = method.apply(this, arguments)
      this.$caller = current
      this.caller = caller
      return result
    }
    wrapper.$owner = self
    wrapper.$origin = method
    wrapper.$name = key
    return wrapper
  }

  var implement = function (key, value, retain) {
    if (Class.Mutators && Class.Mutators.hasOwnProperty(key)) {
      value = Class.Mutators[key].call(this, value)
      if (value == null) return this
    }
    if (typeOf(value) == 'function') {
      if (value.$hidden) return this
      this.prototype[key] = retain ? value : wrap(this, key, value)
    } else {
      Object.merge(this.prototype, key, value)
    }
    return this
  }

  var getInstance = function (klass) {
    klass.$prototyping = true
    var proto = new klass()
    delete klass.$prototyping
    return proto
  }

  // Class 实现
  var Class = function (params) {
    if (instanceOf(params, Function)) params = { initialize: params }
    var newClass = function () {
      reset(this)
      if (newClass.$prototyping) return this
      this.$caller = null
      var value = this.initialize ? this.initialize.apply(this, arguments) : this
      this.$caller = this.caller = null
      return value
    }
    newClass.extend = function (key, value) {
      this[key] = value
    }
    newClass.implement = implement
    newClass.extend(this)
    newClass.implement(params)
    newClass.$constructor = Class
    newClass.prototype.$constructor = newClass
    newClass.prototype.parent = parent
    return newClass
  }

  // parent 函数
  var parent = function () {
    if (!this.$caller) throw new Error('The method "parent" cannot be called.')
    var name = this.$caller.$name,
      parent = this.$caller.$owner.parent,
      previous = parent ? parent.prototype[name] : null
    if (!previous) throw new Error('The method "' + name + '" has no parent.')
    return previous.apply(this, arguments)
  }

  // Class 静态方法
  Class.implement = function (key, value) {
    implement.call(this, key, value)
    return this
  }

  // Class.Mutators
  Class.Mutators = {
    Extends: function (parent) {
      this.parent = parent
      this.prototype = getInstance(parent)
    },
    Implements: function (items) {
      var itemsArray = Array.isArray(items) ? items : [items]
      itemsArray.forEach(function (item) {
        var instance = new item()
        for (var key in instance) {
          implement.call(this, key, instance[key], true)
        }
      }, this)
    }
  }

  // 暴露到全局
  window.Class = Class
  window.Type = Type
  window.typeOf = typeOf
  window.instanceOf = instanceOf
})()

// 添加 Object.clone 方法
if (!Object.clone) {
  Object.clone = function (object) {
    if (object == null) return object

    var clone
    var objType = typeof object

    if (Array.isArray(object)) {
      clone = []
      for (var i = 0, l = object.length; i < l; i++) {
        clone[i] = Object.clone(object[i])
      }
    } else if (objType === 'object') {
      clone = {}
      for (var key in object) {
        if (object.hasOwnProperty(key)) {
          clone[key] = Object.clone(object[key])
        }
      }
    } else {
      clone = object
    }
    return clone
  }
}

window.lingshiKinds = [
  [61, '戒指'],
  [62, '耳饰'],
  [63, '手镯'],
  [64, '佩饰']
]
window.is_lingshi_equip = function (kindid) {
  return window.lingshiKinds.some((item) => item[0] == kindid)
}

window.get_role_icon=function(raw_info) {
  var role_info = js_eval(lpc_2_js(decode_desc(raw_info)))
  return get_role_iconid(role_info['iIcon'])
}
window.weapon_kinds = [
  [10, '扇'],
  [6, '剑'],
  [14, '刀'],
  [5, '斧'],
  [15, '锤'],
  [4, '枪'],
  [13, '双环'],
  [7, '双剑'],
  [12, '鞭子'],
  [9, '爪刺'],
  [11, '魔棒'],
  [8, '飘带'],
  [52, '宝珠'],
  [53, '弓箭'],
  [54, '法杖'],

  [72, '灯笼'],
  [73, '巨剑'],
  [74, '伞'],
  [83, '双斧']
]
window.armor_kinds = [
  [20, '腰带'],
  [19, '鞋子'],
  [21, '饰品']
]
window.cloth_kinds = [
  [18, '男衣'],
  [59, '女衣']
]
window.helmet_kinds = [
  [17, '男头'],
  [58, '女头']
]
window.is_shoes_equip = function (kindid) {
  return kindid == 19
}
window.is_belt_equip = function (kindid) {
  return kindid == 20
}
window.is_necklace_equip = function (kindid) {
  return kindid == 21
}
window.is_helmet_equip = function (kindid) {
  return window.helmet_kinds.some((item) => item[0] == kindid)
}
window.is_weapon_equip = function (kindid) {
  return window.weapon_kinds.some((item) => item[0] == kindid)
}

window.is_cloth_equip = function (kindid) {
  return window.cloth_kinds.some((item) => item[0] == kindid)
}

window.is_armor_equip = function (kindid) {
  return window.weapon_kinds.some((item) => item[0] == kindid)
}
