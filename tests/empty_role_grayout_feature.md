# 空号角色卡片置灰功能

## 功能概述
当角色为空号时，自动将对应的角色卡片置灰显示，提供视觉上的区分效果。

## 实现原理

### 1. 空号判断逻辑
使用`isEmptyRole()`方法判断角色是否为空号：
```javascript
isEmptyRole(roleInfo) {
  const noEquip = this.get_equip_num(roleInfo) === 0
  let noPet = true
  for (let pet of roleInfo.pet_info) {
    if (pet.pet_grade > 100 && pet.is_baobao === '是') {
      noPet = false
      break
    }
    if (pet.pet_grade > 100 && pet.is_baobao === '否' && pet.all_skills.length > 4) {
      noPet = false
      break
    }
  }
  return noEquip && noPet
}
```

**判断条件**：
- 装备数量为0 (`get_equip_num(roleInfo) === 0`)
- 宠物数量为0 或 没有有价值的宠物

### 2. 动态CSS类绑定
```vue
<el-card class="role-card" :class="{ 'empty-role': isEmptyRole(parserRoleData(role)) }">
```

当`isEmptyRole()`返回`true`时，自动添加`empty-role`CSS类。

### 3. 置灰样式设计
```css
/* 空号卡片置灰样式 */
.role-card.empty-role {
  opacity: 0.6;                    /* 整体透明度降低 */
  filter: grayscale(0.8);          /* 灰度滤镜 */
  background-color: #f5f5f5;       /* 浅灰色背景 */
  border: 1px solid #d9d9d9;       /* 灰色边框 */
  transition: all 0.3s ease;       /* 平滑过渡动画 */
}

.role-card.empty-role:hover {
  opacity: 0.8;                    /* 悬停时稍微恢复 */
  filter: grayscale(0.6);
}
```

## 视觉效果

### 1. 置灰效果
- **透明度**：降低到60%，营造"褪色"效果
- **灰度滤镜**：80%灰度，去除彩色
- **背景色**：浅灰色背景
- **边框**：灰色边框

### 2. 交互效果
- **悬停恢复**：鼠标悬停时透明度提升到80%，灰度降低到60%
- **平滑过渡**：0.3秒的过渡动画，提升用户体验

### 3. 内部元素处理
```css
.role-card.empty-role .el-tag {
  opacity: 0.7;
}

.role-card.empty-role .el-link {
  opacity: 0.7;
}

.role-card.empty-role span {
  opacity: 0.7;
}
```

卡片内的标签、链接、文本等元素也会相应置灰。

## 用户体验

### 1. 视觉区分
- **清晰标识**：空号角色一目了然
- **非干扰性**：置灰效果不会完全隐藏信息
- **一致性**：所有空号角色使用相同的视觉样式

### 2. 交互友好
- **可点击**：置灰的卡片仍然可以点击查看详情
- **悬停反馈**：鼠标悬停时有视觉反馈
- **平滑动画**：过渡效果自然流畅

### 3. 信息保留
- **完整信息**：所有角色信息仍然可见
- **标签提示**：保留"空号"标签作为额外提示
- **功能完整**：所有功能按钮仍然可用

## 技术特点

### 1. 响应式设计
- 动态绑定CSS类，实时响应数据变化
- 基于Vue的响应式系统，自动更新

### 2. 性能优化
- 使用CSS滤镜和透明度，GPU加速
- 避免复杂的DOM操作

### 3. 可维护性
- 集中的样式定义
- 清晰的条件判断逻辑
- 易于扩展和修改

## 扩展可能性

### 1. 更多状态
可以扩展支持更多角色状态：
- 高价值角色（金色高亮）
- 普通角色（默认样式）
- 低价值角色（浅灰色）

### 2. 自定义样式
可以添加用户设置：
- 置灰程度调节
- 颜色主题选择
- 动画效果开关

### 3. 筛选功能
基于视觉状态添加筛选：
- 只显示空号角色
- 隐藏空号角色
- 按价值分组显示

## 相关代码

### 模板部分
```vue
<el-card class="role-card" :class="{ 'empty-role': isEmptyRole(parserRoleData(role)) }">
  <!-- 卡片内容 -->
</el-card>
```

### 样式部分
```css
.role-card.empty-role {
  opacity: 0.6;
  filter: grayscale(0.8);
  background-color: #f5f5f5;
  border: 1px solid #d9d9d9;
  transition: all 0.3s ease;
}
```

### 逻辑部分
```javascript
isEmptyRole(roleInfo) {
  // 判断逻辑
}
```

这个功能提升了用户界面的可用性，让用户能够快速识别空号角色，同时保持了良好的视觉体验。
